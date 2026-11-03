# New desk forms send numbers as 0; a Workflow without a Cancelled state can't cancel

**Date:** 2026-10-08
**Domain:** Frappe v16 / custom app (found building fuse_construction)
**Severity:** annoying (silently wrong defaults; stuck documents)

## 1. Defaults applied only when a field is None never fire for desk-created docs

A controller that fills defaults in `before_insert` with `if self.x is None:` works for
documents created in Python (`frappe.new_doc`) but not for ones created in the desk: a new
form sends Int/Float/Currency/Percent fields as `0`, not null. Retention, margin and terms
came through as 0.

**Fix:** fill visible defaults in the form's `onload` when `frm.is_new()` (read the settings
single with `frappe.db.get_doc`), and keep the Python `None` fallback for server-created docs.

## 2. A Workflow with no docstatus-2 state offers no Cancel at all

With a workflow active, Cancel is only available as a transition to a state with
`doc_status = 2`. Without one, a wrongly approved document can never be cancelled and
amended. **Fix:** ship a `Cancelled` state (doc_status 2) and Cancel transitions, and include
it in the workflow state field's Select options.
