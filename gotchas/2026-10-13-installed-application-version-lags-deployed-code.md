# Installed Application's version can lag the code that is actually deployed

**Date:** 2026-10-13
**Domain:** Frappe Cloud / Frappe v16
**Severity:** annoying

## Symptom

Installed Applications (and the version in a user's `last_known_versions`) shows an older app
version than the one just pushed and deployed — on 13 Oct, fuse_water_chemical showed 0.1.0 while
0.1.2's fix was demonstrably running. Conversely, on 14 Oct the loader that ran was the pre-0.1.4
one (it said "role and module profile" and re-added module blocks), whatever the listing said.

## Cause

Installed Application is refreshed by migrate, not by the code swap; a deploy whose migrate is
skipped or deferred updates the code but not the row.

## Fix

Do not trust the listing. Check behaviour: call something only the new version does (a changed
return string, a new field), or read the deployed asset/py from the bench.

## Why this is non-obvious

The version number looks authoritative and sits right where you would check.

## See also

- `gotchas/2026-05-06-frappe-cloud-update-vs-deploy-assets.md`
