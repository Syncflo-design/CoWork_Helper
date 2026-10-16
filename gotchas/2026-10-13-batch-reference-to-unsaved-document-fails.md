# A Batch created with `reference_name` pointing at a not-yet-saved document fails with DoesNotExistError

**Date:** 2026-10-13
**Domain:** ERPNext v16 / custom-app doc_events (fuse_water_chemical 0.1.1 → 0.1.2)
**Severity:** day-killer

## Symptom

A `Stock Entry` validate hook that creates the run's Batch (so the inspection taken before submit
can name it) fails every save: first `LinkValidationError`, then, with `ignore_links`,
`DoesNotExistError: Stock Entry ... not found`.

## Cause

The Batch was given `reference_doctype = "Stock Entry"` / `reference_name = doc.name` while that
Stock Entry was still being saved. ERPNext reads the batch's source document while saving the
batch, and the row is not in the database yet. `flags.ignore_links` skips the link check but not
that read.

## Fix

Create the Batch with no reference back. The run's line and its stock ledger name the batch; if
the save fails, the batch rolls back with it. ERPNext fills the reference itself once the entry
is submitted (seen on the demo site: batch CSL25-2610-004 → MAT-STE-2026-00008).

```diff
 frappe.get_doc({"doctype": "Batch", "item": row.item_code, "manufacturing_date": doc.posting_date,
-    "reference_doctype": "Stock Entry", "reference_name": doc.name,
     "wc_strength": strength}).insert(ignore_permissions=True)
```

## Why this is non-obvious

`ignore_links` looks like it should cover it, and the first fix (0.1.1) did exactly that and
still failed on the next run.

## See also

- `fuse_water_chemical/dilution.py` `number_batch`.
