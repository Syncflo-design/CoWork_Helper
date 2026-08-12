# `frappe.db.set_value` writes the row but skips everything that makes the change take effect

**Date:** 2026-08-12
**Domain:** Frappe / Server Scripts / metadata
**Severity:** day-killer — it cost three separate rounds of "I fixed it" / "no you didn't" in one session

## Symptom

Change something, verify it in the database, hand it over — and the user sees no change at all.

It happened three times in one afternoon, each looking like a different bug:

| What was changed | Written with | What the user saw |
|---|---|---|
| Client Script (Stock Transfer item query) | `db.set_value` | Old script still running after a hard refresh |
| Property Setter (`standard_rate` hidden) | `frappe_update` (db-level) | Field still visible |
| Custom Field fieldtype Int → Float | Property Setter insert | Form accepted 2.5, database stored 2 |

Each time the row was correct. Each time the site kept serving the old thing.

## Cause

`frappe.db.set_value` is a raw column write. It does not run `on_update`, so none of the
things that *publish* a change happen:

* **No cache rebuild.** Doctype meta — which carries Custom Fields, Property Setters AND
  Client Scripts to the browser — stays as it was. Hard-refreshing the browser does
  nothing, because it is the *server* holding the stale copy.
* **No schema sync.** A fieldtype change alters the form only. The column keeps its old
  type and silently truncates — an Int column given 2.5 stores 2.
* **No Version record.** Nothing is written to the audit trail, so the previous value is
  unrecoverable. A bulk `db.set_value` over 5,000 items is irreversible.

## Fix

For anything that is metadata, script, or layout — load the document and save it:

```python
sd = frappe.get_doc("Client Script", "Stock Transfer - Pretty UI")
sd.script = new_text
sd.save(ignore_permissions=True)   # on_update fires, cache rebuilds
```

Then **verify against what the browser is actually served**, not the database row:

```python
frappe.desk.form.load.getdoctype   # returns the meta the client downloads, __js included
```

Grep that payload for your change. A row in `tabClient Script` proves nothing.

`db.set_value` is still the right tool for plain data on many rows — it is fast and skips
validation deliberately (see `2026-08-03-frappe-child-row-insert-bypasses-parent-validation.md`).
Just know you are also skipping the audit trail: **snapshot before a bulk field update, or
use `doc.save()` so Versions exist.** 116 price fields were overwritten this way and could
not be recovered, precisely because no Version was written.

## Why this is non-obvious

- The verification lies. You read the value back, it is correct, so you report it fixed.
  The mistake is verifying the same layer you wrote to.
- "Hard refresh" feels like the definitive test and is not — browser cache is not the
  problem, the server-side meta cache is.
- The failure is *silent and partial*: the form changes but the column does not; the row
  changes but the served payload does not. Nothing errors.
- `frappe.clear_cache(doctype=...)` is **not available in the Server Script sandbox**
  (`module has no attribute 'clear_cache'`), so the obvious workaround is closed. Saving the
  document is the way.

## See also

- `gotchas/2026-08-12-customize-form-blocks-int-to-float.md`
- `gotchas/2026-08-03-frappe-child-row-insert-bypasses-parent-validation.md`
- `gotchas/2026-06-10-server-script-sandbox-and-xlsx.md`
