# A standard Print Format's JSON change never reaches the site unless `modified` is bumped

**Date:** 2026-10-14
**Domain:** Frappe v16 / custom-app / print formats (fuse_manufacturing 0.10.3 → 0.10.4)
**Severity:** day-killer (silent, found the day before a demo)

## Symptom

0.10.3 fixed the Certificate of Analysis template (`reading_1` for numbers). Deployed, migrated —
and the certificate on the site still printed `None` for every numeric result and blank for every
check. The site's Print Format record still held the old HTML.

## Cause

On migrate, Frappe syncs a standard doc from its JSON only when the file's `modified` is newer
than the database row's. The commit changed `html` but left `"modified": "2026-08-24 12:00:00"`,
so the sync skipped it.

## Fix

Bump `modified` in the JSON whenever you change it (0.10.4):

```diff
- "modified": "2026-08-24 12:00:00.000000",
+ "modified": "2026-10-14 08:00:00.000000",
```

The record cannot be patched by API in the meantime: a standard Print Format refuses edits
outside developer mode.

## Why this is non-obvious

Every other check passed: the inspection data was right, the template in git was right, the
deploy was green. Only rendering on the site (`frappe.www.printview.get_html_and_style`) and
comparing the stored `html` showed it.

## See also

- `gotchas/2026-10-13-erpnext-v16-qi-reading-1-vs-reading-value.md`
- Same rule for Page, Report, DocType JSON.
