# Bulk-updating 6,000 Items: insert the child row directly instead of `item.save()`

**Date:** 2026-08-03
**Domain:** Frappe / ERPNext / bulk data
**Severity:** annoying (silently loses most of a batch if you get it wrong)

## Symptom

Backfilling a generated barcode onto every Item meant writing two things per item: a
custom field, and a row in the standard `Item Barcode` child table.

The obvious implementation is:

```python
item = frappe.get_doc("Item", code)
item.custom_pos_barcode = number
item.append("barcodes", {"barcode": number})
item.save(ignore_permissions=True)
```

On this site that would have failed for a large slice of the 6,404 items — `item.save()`
re-runs the full Item validation, and any item carrying a stale Select value throws:

```
Size cannot be "Ardmore Jewellery"
Base Cloth cannot be "Cotton"
```

Exactly the class of failure that broke the bulk-enable on 2026-07-28. In a batched loop
one bad item takes its whole batch with it.

## Cause

`Document.save()` is not a targeted write — it revalidates every field on the parent,
including fields you never touched. Data that was legal when it was written (or that
arrived from Sage) can be illegal today, so a save fails for reasons unrelated to your
change.

## Fix

Write the parent field with `db.set_value` and insert the child row as its own document,
with the parent link set explicitly:

```python
frappe.db.set_value("Item", code, "custom_pos_barcode", number, update_modified=False)

row = frappe.new_doc("Item Barcode")
row.parent = code
row.parenttype = "Item"
row.parentfield = "barcodes"
row.barcode = number
row.insert(ignore_permissions=True)
```

Both bypass parent validation entirely. Result: **6,463 items, zero failures.**

Leave `barcode_type` blank — ERPNext validates the value against the chosen symbology
(EAN, UPC-A, ...) and CODE-128 is not in that Select. Blank means no format check.

`update_modified=False` keeps `modified` untouched, so a mass backfill doesn't look like
6,000 user edits in the audit trail or trip `modified`-based syncs.

**The trade-off is real:** you are skipping validation deliberately. Only do this when the
value you are writing is generated and known-good, and when the parent's *other* fields
are the untrustworthy part. Never for user-supplied input.

## Why this is non-obvious

- `item.save()` is the idiomatic, documented way to touch a child table, and it works
  perfectly at low volume. The failure only appears at scale, on dirty data, in batches.
- Frappe child DocTypes look like they can't be inserted standalone. They can — set
  `parent`, `parenttype` and `parentfield` and `insert()` works normally.
- The failure is *not* in the field you're writing, so the error message points at
  `custom_size` or `custom_base_cloth` and sends you off auditing Select options again.
- Same batch-poisoning shape as the Stock Reconciliation and Material Receipt bugs on
  2026-07-28: **one bad row failing a batch is the recurring failure mode on this site.**
  Either avoid validation, or retry per item on batch failure. Preferably both.

## Verification that this actually worked

Saving proves nothing (see `2026-06-10-server-script-sandbox-and-xlsx.md`). Create a real
Item and confirm the After Insert hook populated both places, then delete it:

```
ZZ-BCTEST-1 -> custom_pos_barcode = 10006464, barcodes[0].barcode = 10006464
```

## See also

- `gotchas/2026-06-10-server-script-sandbox-and-xlsx.md`
- `gotchas/2026-08-03-label-width-caps-barcode-character-count.md`
- `sites/ardmore.md` — 2026-08-03 work log
