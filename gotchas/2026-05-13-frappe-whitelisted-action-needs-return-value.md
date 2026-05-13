# Frappe whitelisted-action method returning None silently kills the client-side success callback

**Date:** 2026-05-13
**Domain:** Frappe / ERPNext / custom-app / Client Script
**Severity:** day-killer (looks broken, isn't, breaks user trust)

## Symptom

A custom button on a Frappe form opens a confirmation dialog. The user fills it in and clicks the primary action ("Queue Cleanup", "Apply", whatever). **Nothing visible happens** — no toast, no dialog closing, no form reload. From the seat of the user it looks like the button does nothing.

Server side, the action *actually succeeded* — the DB write happened, the integration row got ticked, the cron will pick it up. But the UX says "nothing happened" and the user clicks the button repeatedly assuming it's broken.

## Cause

The whitelisted Python method on the server-side returns `None` (implicit, no `return` statement). On the wire that becomes `r.message = null`. The client-side callback typically gates the success path with `if (r.message) { ... }` — and `null` is falsy — so the toast / `d.hide()` / `frm.reload_doc()` block never runs.

In `erpnext_sbca` we hit this exactly on `account.apply_account_cleanup` — the function called `frappe.db.set_value(...)` then `frappe.db.commit()` and ended. No return. The JS:

```javascript
frappe.call({
    method: "erpnext_sbca.API.account.apply_account_cleanup",
    args: { company: company },
    callback: function (r) {
        if (r.message) {
            frappe.show_alert({...});
            d.hide();
            frm.reload_doc();
        }
    },
});
```

`r.message === null`, the `if` skips everything, dialog sits open, no toast.

## Fix

Always return a truthy payload from any whitelisted method that's called by a client-side button + success callback. Even `True` works, but a small dict is friendlier for future debugging.

```diff
@frappe.whitelist()
def apply_account_cleanup(company):
    ...
    frappe.db.commit()
+   # Return a truthy payload so the Client Script's `if (r.message)` branch
+   # fires (shows the green toast, hides the dialog, reloads the form).
+   return {"queued": True, "company": company, "integration": integration_name}
```

Alternative (less reliable, requires touching every client-side caller): change the client to `if (r.message !== undefined)` or `if (!r.exc)`. Worse because it scatters the assumption across multiple files.

## Why this is non-obvious

Three things converge:

1. **The server-side worked.** `frappe.db.set_value` + `frappe.db.commit` did persist, so a database check confirms the action ran. No exception in the error log. No clue from the backend.
2. **The browser shows nothing wrong.** No console error. No 4xx in the Network tab — the call succeeded with HTTP 200 and `{"message": null}`. The success callback fires, but the inner `if (r.message)` no-ops silently.
3. **Repeated clicks compound the confusion.** The user clicks "Queue Cleanup" five times. Server-side, the same idempotent set_value runs five times (harmless). User assumes broken. Investigator assumes the click handler isn't firing.

The false lead I chased: thought the v15→v16 Frappe dialog API had changed `primary_action(values)` signature. Verified the JS file parsed cleanly, the dialog opened, all upstream UI worked. Only after grepping for `apply_account_cleanup` on the server side and noticing no `return` statement did the penny drop.

**The rule:** every `@frappe.whitelist()` method that has a UI side should return something truthy. `return True` minimum; ideally a dict with whatever the JS might want to render. Free, defensive, and removes a whole class of "looks broken" support tickets.

## See also

- Related gotcha: `gotchas/2026-05-07-frappe-v16-realtime-registration-timing.md` — different mechanism (silently-dropped event listeners), same family of "the call succeeded but nothing visible happened".
- Related project: `projects/erpnext_sbca/TECHNICAL.md` — Section on Account Sync covers the cleanup button flow end to end.
