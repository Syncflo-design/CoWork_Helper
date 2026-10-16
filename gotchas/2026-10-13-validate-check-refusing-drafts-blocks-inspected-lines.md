# A validate-time "inspection required" check that refuses drafts makes inspected lines unrecordable

**Date:** 2026-10-13
**Domain:** ERPNext / custom-app doc_events (fuse_manufacturing 0.10.3)
**Severity:** day-killer

## Symptom

Every run, receipt or delivery with an inspected item fails on save with "inspection required",
including from the floor screen that creates the inspection itself. The line can never be recorded.

## Cause

A Quality Inspection links to its parent (`reference_type` / `reference_name`), so the parent
must exist — be saved as a draft — before the inspection can be made. A `validate` hook that
demanded the inspection on every save refused the draft, so the inspection could never be
created. Chicken and egg.

## Fix

Gate the **submit**, not the draft:

```diff
 def check_inspections(doc, method=None):
+    if doc.docstatus != 1:
+        return
```

ERPNext's own `validate_inspection` does the same: on a draft it only shows a message, on submit it
throws.

## Why this is non-obvious

The check reads correctly in isolation ("no inspection, no save"). It only fails when you follow
the order the documents must be created in.

## See also

- `gotchas/2026-10-13-submit-after-quality-inspection-needs-reload.md` — the next trap on the same path.
