# Lead status won't stay on "Do Not Contact" / "Dead" — StatusUpdater overwrites it every save

**Date:** 2026-08-24
**Domain:** ERPNext v16 CRM (nesterp)
**Severity:** annoying (looks like a UI/permission bug, is core behaviour)

## Symptom

A Lead sitting on status **Opportunity** is changed to **Do Not Contact** or **Dead**.
Save. The status snaps straight back to **Opportunity**. No error, no validation message.

Sales reps can never retire a lead that has an open Opportunity against it.

## Cause

Nothing to do with the status field options, Property Setters, permissions or Client
Scripts. It is core ERPNext.

`Lead.validate()` calls `self.set_status()`, inherited from
`erpnext/controllers/status_updater.py`. That method **recomputes** the status from a
hard-coded map and overwrites whatever the user picked:

```python
status_map = {
	"Lead": [
		["Lost Quotation", "has_lost_quotation"],
		["Opportunity", "has_opportunity"],
		["Quotation", "has_quotation"],
		["Converted", "has_customer"],
	],
	...
}
```

```python
def get_status(self):
	sl = status_map[self.doctype][:]
	sl.reverse()
	for s in sl:
		...
		elif getattr(self, s[1])():
			return {"status": s[0]}
	return {"status": self.status}   # <- only reached if NOTHING matches
```

`has_opportunity()` is `frappe.db.get_value("Opportunity", {"party_name": self.name,
"status": ["!=", "Lost"]})`. So while any non-Lost Opportunity exists, `get_status()`
returns "Opportunity" and the user's choice is discarded. `"Do Not Contact"` and
`"Dead"` are not in the map at all, so they can never survive. (`"Dead"` is not even a
standard option — it was added on nesterp via a Property Setter on `Lead.status.options`.)

Same trap applies to a Lead with a linked Customer (`has_customer` → "Converted").

## Fix

Two Server Scripts on **Lead**. You need both: the user's choice is destroyed inside
`validate()`, so it has to be captured *before* and reapplied *after*.

Frappe's save order is `before_validate` → `validate` (controller) → `before_save`.

**`Lead - Sticky Status (capture)`** — DocType Event, Lead, **Before Validate**

```python
STICKY = ("Do Not Contact", "Dead")

if doc.status in STICKY:
    doc.flags.sticky_lead_status = doc.status
    if not doc.is_new():
        doc.status = doc.get_status()["status"]
else:
    doc.flags.sticky_lead_status = None
```

**`Lead - Sticky Status (restore)`** — DocType Event, Lead, **Before Save**

```python
kept = doc.flags.get("sticky_lead_status")

if kept and doc.status != kept:
    doc.status = kept
```

Two details that are easy to get wrong:

1. **Always reassign the flag in capture** (the `else: ... = None` branch). `doc.flags`
   is not cleared by `doc.reload()`. If a caller reuses one doc object across saves, a
   stale flag pins the old status forever — in testing, a lead moved off "Do Not Contact"
   silently stayed on it.
2. **The `doc.status = doc.get_status()["status"]` line is not redundant.** `set_status()`
   calls `self.add_comment("Label", new_status)` whenever the status *changes*, so without
   it every save of a Dead lead drops another "Opportunity" entry on the timeline —
   5 junk comments in a 4-save test. Pre-setting the value it is about to compute means
   it sees no change and stays quiet. Calling the core `get_status()` avoids duplicating
   the map logic.

Behaviour after the fix (verified on a throwaway Lead + Opportunity):

| Action | Result |
|---|---|
| Set Dead | Dead |
| Set Do Not Contact | Do Not Contact |
| Unrelated re-save while Dead | Dead |
| Set back to Open / Lead | Opportunity — standard auto-status resumes |

That last row is deliberate: only the two terminal statuses are made sticky, everything
else keeps stock ERPNext behaviour.

## Why this is non-obvious

- The field *accepts* the value in the UI and the save succeeds. It looks like the write
  never happened, so the instinct is to chase permissions, workflow, or a Client Script.
- Nothing on the site was to blame — checked Property Setters, Client Scripts and Server
  Scripts on Lead first, all clean. The answer was only in ERPNext core.
- `set_status` is not defined in `lead.py`. Grepping the Lead controller finds
  `self.set_status()` in `validate()` and no definition — it is inherited from
  `StatusUpdater` two files away, via `SellingController`.
- The status *is* correctly persisted for a moment; it is overwritten during validate,
  so any timestamp/version check looks normal.
- **Tell:** the timeline fills up with repeated "Opportunity" label comments. That's
  `set_status` announcing each overwrite, and it's the fingerprint of this bug.

## Reading core source without bench access

`frappe.get_app_path` and `frappe.read_file` are **not** in the safe_exec namespace, so
System Console can't read app source. Get the app version out of the DB, then pull the
exact file from GitHub:

```python
frappe.db.sql('select app_name, app_version from `tabInstalled Application`', as_dict=True)
```

```
https://raw.githubusercontent.com/frappe/erpnext/v16.31.1/erpnext/controllers/status_updater.py
```

## See also

- Related: `gotchas/2026-06-10-server-script-sandbox-and-xlsx.md` (safe_exec limits —
  no imports, and `frappe.db.sql` is read-only)
- Related: `gotchas/2026-08-24-frappe-grid-columns-overridden-by-user-settings.md`
  (same shape of problem — core/user layer silently overriding your change)
- Core source: `erpnext/controllers/status_updater.py` (`status_map`, `get_status`,
  `set_status`), `erpnext/crm/doctype/lead/lead.py` (`has_opportunity`, `has_quotation`,
  `has_lost_quotation`, `has_customer`)
