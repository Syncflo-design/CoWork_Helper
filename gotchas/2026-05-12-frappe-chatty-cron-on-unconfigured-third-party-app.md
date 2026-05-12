# When auditing an inherited Frappe app, the Scheduled Job Type listing is where integration apps' real behaviour lives

**Date:** 2026-05-12
**Domain:** Frappe / inherited benches / audit
**Severity:** annoying (if you misjudge it) — easy to wrongly dismiss a critical integration app as cruft

## Symptom

You take over a Frappe bench someone else built. One of the installed apps has only a tiny on-disk presence — say, a single Settings doctype and a credentials child table — and zero Workspaces, Reports, Custom Fields, or Client Scripts. From the standard "what does this app do?" audit it looks almost empty.

But it has a bunch of scheduled jobs, all at `frequency: "All"` (run every scheduler tick — ~every 4 min), all enabled. If the app is also unconfigured, the jobs fire every tick but no-op silently.

In the case that prompted this gotcha (`erpnext_sbca` on `syncflo-internal.c.frappe.cloud`):

- 2 DocTypes (Settings single + credentials child table)
- 11 scheduled jobs under `erpnext_sbca.API.*`
- Settings panel empty, credentials table empty → jobs no-op every tick

The temptation is to write the app off as cruft and recommend disabling the jobs or uninstalling.

**Don't.** Apps shaped like this are usually **integration bridges** — small UI surface, big background sync engine. If you uninstall one, you may have just killed the bridge between ERPNext and an external system the business relies on.

## Cause

Apps that integrate ERPNext with an external system (accounting, e-commerce, payment gateway, etc.) typically have:

- A small Settings doctype to hold credentials + endpoints
- A child table for per-Company (or per-tenant) credentials
- A bunch of scheduled jobs that do the actual syncing
- Optionally a few OAuth callback endpoints in Python (whitelisted methods)

The DocType audit will only show you the first two. The scheduled jobs are where the actual behaviour is. The Python code is unreachable from MCP — you need bench SSH or the source repo to see it.

## Audit recipe

Run this on any inherited Frappe app before forming an opinion:

```python
# What apps + modules are on the bench
frappe_list("Module Def",
    filters=[["app_name", "=", "<app_name>"]],
    fields=["name", "module_name", "app_name"])

# DocType surface (often small for integration apps — that's normal)
frappe_list("DocType",
    filters=[["module", "=", "<Module Name>"]],
    fields=["name", "issingle", "istable", "is_submittable"])

# THE REVEAL — scheduled jobs are where integration logic lives
frappe_list("Scheduled Job Type",
    filters=[["method", "like", "%<app_name>%"]],
    fields=["name", "method", "frequency", "stopped"])

# Are those jobs actually running?
frappe_list("Scheduled Job Log",
    filters=[["scheduled_job_type", "in", [<job_type_names>]]],
    order_by="creation desc",
    fields=["scheduled_job_type", "status", "creation", "details"],
    limit=20)

# Is the app configured?
frappe_get("<App> Settings", "<App> Settings")
```

Read the method paths — they're the table of contents for the app's actual job. Names like `get_x_from_<system>` and `update_x_to_<system>` tell you it's a two-way sync with `<system>`.

## What NOT to do

Do not stop, uninstall, or "tidy up" scheduled jobs from an inherited app until you have:

1. Confirmed with the bench owner that the app is not strategic infrastructure.
2. Checked whether the app is unconfigured (no work to do) vs. configured-and-broken (real work failing silently).
3. Found the original author if the source repo isn't in your GitHub org — they'll know what credentials to plug in.

If the app *is* strategic and just unconfigured, the right move is to **configure it**, not silence it.

## What's fine to do

- Read `Scheduled Job Log` to see if jobs are actually executing and what their status is.
- Read the Settings doc to see if credentials are populated.
- Take notes — write a `projects/<app>/ASSESSMENT.md` so future-you knows what the app does and that it's strategic.

## Why this is non-obvious

When you `frappe_list("DocType", ...)` to map an app's surface area, you only see Frappe-stored UX (Settings doctype, child tables). Apps that are 95% Python in scheduled jobs look almost empty from a DocType audit. The `Scheduled Job Type` listing is where the actual behaviour shows up. Easy to miss because:

- It's not part of the Module view in desk.
- The MCP user has access to it (unlike Server Script), so it works through the connector — but only if you remember to query it.
- `Scheduled Job Log` may be empty (logs pruned, or the job exits before logging) so you can't always confirm activity from there.

The mistake mode here is **wrongly classifying a keystone integration app as cruft** because the DocType-only audit makes it look thin. Doubly so when the bench has unconfigured credentials → the jobs no-op, and you can't tell from the audit whether that's deliberate-quiet or about-to-be-configured.

## See also

- `projects/erpnext_sbca/ASSESSMENT.md` — full audit of the specific app that prompted this gotcha. Critical infrastructure on the nesterp bench — Russell's Sage ↔ ERPNext bridge, written by Doreen at 9t9it.
- `gotchas/2026-05-06-mcp-user-restricted-doctypes.md` — why you can't read Server Script through MCP, so you sometimes can't see the actual callback code.
- `sites/nesterp.md` — the bench's Apps installed list.
