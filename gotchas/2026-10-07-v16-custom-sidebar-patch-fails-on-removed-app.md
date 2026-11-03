# Frappe v16 migrate dies in convert_custom_sidebars when a site-made sidebar belongs to a removed app

**Date:** 2026-10-07
**Domain:** Frappe v16 / Frappe Cloud deploy / migrate
**Severity:** annoying (blocks every deploy until cleaned up)

## Symptom

Deploy to the NestERP demo site (`nesterpdemo.c.frappe.cloud`) after Frappe was moved forward and
HRMS + Helpdesk were taken off the bench. Migrate stops in a Frappe patch:

```
Executing frappe.patches.v16_0.convert_custom_sidebars ...
Sidebar 'Frappe CRM': carried into custom module 'Frappe CRM'
Sidebar 'Helpdesk': carried into custom module 'Helpdesk'
...
  File ".../frappe/patches/v16_0/convert_custom_sidebars.py", line 75, in add_to_site_dock
  File ".../frappe/desk/doctype/dock/dock.py", line 1237, in check_docked_app
frappe.exceptions.ValidationError: <strong>helpdesk</strong> is not an app on this site.
```

## Cause

The patch turns every **site-made** Workspace Sidebar (`standard = 0`) into a custom module and adds
it to the dock of the sidebar's app. A site-made sidebar left behind by an app that is no longer
installed (here Helpdesk; also a `Compliance` sidebar from Nest QMS, whose module no longer existed)
has no app to dock into, so `check_docked_app` throws and the whole migrate fails.

## Fix

Before redeploying, delete the orphaned site-made sidebars and their desktop icons:

```python
# Workspace Sidebar with standard = 0 whose module/app is not installed
frappe.delete_doc("Workspace Sidebar", "Helpdesk")
frappe.delete_doc("Desktop Icon", "Helpdesk")
frappe.delete_doc("Workspace Sidebar", "Compliance")   # Nest QMS leftover
frappe.delete_doc("Desktop Icon", "Compliance")
```

Find candidates first: `Workspace Sidebar` where `standard = 0`, and check each one's `module` still
exists in Module Def with an installed `app_name`. Sidebars of installed apps (e.g. `Frappe CRM` →
module `FCRM`, app `crm`) migrate fine and stay.

## Why this is non-obvious

- The first deploy failed for a different reason (newer HRMS needs Frappe ≥ 16.50), so the fix there
  was to drop HRMS/Helpdesk; this second failure only appears once the newer Frappe actually migrates.
- The traceback names the app ("helpdesk is not an app on this site"), not the record, and the
  sidebar is a site-made record most people never look at.
- Removing an app from a bench does not remove its site-made sidebars or desktop icons; they sit
  harmless until a patch like this walks them.

## See also

- Gotcha: `gotchas/2026-05-08-frappe-patches-txt-needs-both-section-headers.md` (another migrate-time trap)
