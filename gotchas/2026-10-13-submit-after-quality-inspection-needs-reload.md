# Submitting a parent after submitting its Quality Inspection needs a reload (TimestampMismatchError)

**Date:** 2026-10-13
**Domain:** ERPNext / custom-app server code (fuse_manufacturing 0.10.3)
**Severity:** annoying

## Symptom

Code saves a Stock Entry (or receipt / delivery) draft, creates and submits its Quality
Inspection, then calls `entry.submit()` and gets:

```
frappe.exceptions.TimestampMismatchError: Error: Document has been modified after you have opened it
```

## Cause

Submitting the inspection writes back to its parent (the line's `quality_inspection` link), which
changes the parent's `modified`. The parent object still in memory carries the old timestamp, so
its submit looks like an edit over someone else's change.

## Fix

```diff
 quality.create_for_line(doc=entry, row=line, captured=inspection)
+entry.reload()
 entry.submit()
```

## Why this is non-obvious

Nothing in your code touched the parent between save and submit; the write happens inside
ERPNext's Quality Inspection submit.

## See also

- `gotchas/2026-10-13-validate-check-refusing-drafts-blocks-inspected-lines.md`
