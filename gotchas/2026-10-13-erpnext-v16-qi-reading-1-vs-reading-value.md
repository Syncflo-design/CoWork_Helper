# ERPNext v16 Quality Inspection: numbers go in `reading_1`, text goes in `reading_value`

**Date:** 2026-10-13
**Domain:** ERPNext / quality / custom-app (fuse_manufacturing 0.10.3)
**Severity:** day-killer

## Symptom

Inspections created in code with the right results reject themselves, and the Certificate of
Analysis prints blank or `None` for every result. Nothing errors.

## Cause

On a Quality Inspection Reading, ERPNext v16 judges a **numeric** specification (`numeric = 1`)
on `reading_1` against `min_value` / `max_value`, and a **non-numeric** check on `reading_value`
against the expected `value`. fuse_manufacturing wrote them the other way round, so every result
was read as blank and failed.

## Fix

```diff
 if parameter.numeric:
-    line["reading_value"] = taken
-else:
     line["reading_1"] = taken
+else:
+    line["reading_value"] = taken
```

Print formats follow the same rule: `{{ row.reading_1 if row.numeric else (row.reading_value or "") }}`.

## Why this is non-obvious

`reading_value` sounds like "the value read" and is the field you would pick for a number. The
inspection still saves and submits; only its status (Rejected) and the certificate give it away.

## See also

- `gotchas/2026-10-14-standard-print-format-change-needs-modified-bump.md` — the certificate fix
  that then never reached the site.
- `fuse_manufacturing/quality.py` `create_for_line`.
