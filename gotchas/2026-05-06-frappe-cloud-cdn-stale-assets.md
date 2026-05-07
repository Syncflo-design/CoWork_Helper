# Frappe Cloud CDN serves stale CSS/JS even after a clean Deploy

**Date:** 2026-05-06
**Bit me on:** `quick_purchase_invoice` v0.0.2 → v0.0.3. Successfully redeployed via Frappe Cloud, confirmed on the bench that the new `quick_pi.css` was on disk, but `https://<site>/assets/quick_purchase_invoice/css/quick_pi.css` kept serving the old v0.0.1 content. The new content WAS retrievable via `?v=99` cache-bust query string.

## Symptom

Direct hit of `<site>/assets/<app>/css/<file>.css`:

- No query string → returns OLD content (200, but stale).
- `?v=99` (or any new query) → returns NEW content.

This means the file on the bench is correct, but a CDN / edge cache between the user and the bench is holding the previous version under the un-suffixed URL.

## Why a fresh Deploy doesn't fix it

Frappe Cloud uses a CDN in front of static `/assets/`. The CDN keys on URL. Deploying re-uploads the asset to origin, but the cached entry under the same URL keeps serving the old bytes until its TTL expires (potentially hours).

There's no "purge CDN" button exposed in the Frappe Cloud UI as of 2026-05.

## Fix — rename the asset file

Best workaround: change the asset URL itself. Two-line change in your app:

1. Rename `public/css/<old>.css` → `public/css/<new>.css` (and/or `public/js/<old>.js`).
2. Update `hooks.py`:
   ```python
   app_include_css = "/assets/<app>/css/<new>.css"
   ```
3. Bump app version, push, redeploy.

The new URL has no CDN entry, so it fetches origin first time. From now on, every CSS/JS change can use the rename trick if you suspect cache.

## Better long-term — use Frappe's `.bundle.css` convention

Files named with `.bundle.css` / `.bundle.js` go through Frappe's asset bundler, which fingerprints the build with a hash and rewrites `app_include_css` references at build time. Each bundle build produces a new URL automatically, so cache-busting is implicit.

To migrate:

1. Rename `public/css/foo.css` → `public/css/foo.bundle.css`.
2. Set `app_include_css = "foo.bundle.css"` (note: just the filename, no leading `/assets/...` — bundler resolves it).
3. `bench build --app <app>` to generate the hashed output.

This is the official pattern; the rename trick is a quick stopgap.

## Don't waste time on

- Hard-refresh in the browser (Ctrl+Shift+R) → only clears LOCAL browser cache, doesn't touch CDN.
- Setting `Cache-Control: no-cache` headers in your app → Frappe Cloud's CDN ignores response headers from origin for known asset paths.
- Clicking "Clear Cache" in Site Actions → clears Frappe's internal Redis cache, not the CDN.

## Detection recipe

Whenever a CSS/JS update doesn't seem to land:

1. Direct-hit the asset URL.
2. If old → also try `<url>?v=<random>`. If THAT shows new → CDN cache. Apply the rename fix.
3. If both show old → bench build didn't run. Apply the "Update vs Deploy" gotcha fix instead.

## Cross-reference

- `gotchas/2026-05-06-frappe-cloud-update-vs-deploy-assets.md` — the prior layer (build pipeline). This gotcha is about the layer in front of it.
