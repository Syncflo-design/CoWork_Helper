# Customize Form refuses Int → Float, and forcing it past the check corrupts the data

**Date:** 2026-08-12
**Domain:** Frappe / DocType customisation
**Severity:** annoying — but the workaround is worse than the problem

## Symptom

Ardmore sell fabric by the metre, but the Stock Transfer quantity field is an `Int`, so
2.5 m cannot be transferred. Changing it in Customize Form gives:

```
Fieldtype cannot be changed from Int to Float in row 2
```

## Cause

Frappe only permits field-type changes within compatible groups. Its allowed set groups
`Currency` / `Float` / `Percent` together — **`Int` is not in that group**, so the change is
refused by design, not by accident.

## Fix

There is no clean in-site fix. The field type lives in the app's DocType JSON, so the real
change is one line there plus a deploy — the migrate alters the column at the same time.

**Do not force it with a Property Setter.** That is possible:

```python
frappe.get_doc({"doctype": "Property Setter", "doc_type": "Stock Transfer Items",
                "field_name": "quantity", "property": "fieldtype",
                "property_type": "Select", "value": "Float"}).insert()
```

…and it is a trap. The Property Setter changes the **form** only. The database column stays
`int(11)`, so the form cheerfully accepts 2.5 and stores 2. Verified live: a Stock Transfer
saved with quantity 2.5 read back as 2.

That is strictly worse than the original problem, because it now looks like it worked.

## Why this is non-obvious

- Int and Float are both numbers; the restriction feels arbitrary until you realise it is
  about column types, not about values.
- The Property Setter route succeeds silently. Nothing warns you that the column was not
  altered — you have to go and look:
  ```sql
  SELECT COLUMN_TYPE FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_NAME = 'tabStock Transfer Items' AND COLUMN_NAME = 'quantity'
  ```
- The Server Script sandbox cannot rescue you: `frappe.db.updatedb` is not exposed
  (`module has no attribute 'updatedb'`), and raw `ALTER TABLE` is rejected with
  "Read-Only queries are allowed". Both routes to the column are closed from inside.

## See also

- `gotchas/2026-08-12-db-set-value-skips-the-hooks-that-make-a-change-real.md` — same
  family: the form and the schema are two different things.
- `sites/ardmore.md` — the `server_scripts` app owns this doctype.
