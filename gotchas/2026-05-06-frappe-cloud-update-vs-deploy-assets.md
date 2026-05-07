# Frappe Cloud "Update" doesn't rebuild static assets — use "Deploy"

**Date:** 2026-05-06
**Bit me on:** `quick_purchase_invoice` — pushed v0.0.2 with a heavily-rewritten `public/css/quick_pi.css`, clicked **Update** in Frappe Cloud Apps tab, the form opened with the new DocType-JSON behaviour (Series hidden, Tax collapsed) but the page was still served with the v0.0.1 CSS — old 3-rule placeholder.

## Symptom

Hit `https://<site>/assets/<app_name>/css/<file>.css` directly in the browser. It returns 200 with the **old** CSS content. Same for any other `app_include_css` / `app_include_js` asset that changed in the latest commit. DocType JSON changes (which go through `bench migrate`) ARE applied — only static assets are stale.

## Root cause

In Frappe Cloud, the **Apps tab → Update** action pulls the new git commit into the bench AND runs `bench migrate` for DocType + Custom Field changes, but does **not** run `bench build`. Static assets stay frozen at whatever was bundled the last time a full **Deploy** was run.

## Fix (preferred)

Bench dashboard → **Deploys** tab → **New Deploy**. This rebuilds the bench image including a fresh `bench build`, so all `public/` assets get re-bundled and the new content is served. ~5 min.

## Fix (faster, if SSH available)

Bench → **Settings** → SSH (web console). Then:

```bash
bench build --app <app_name>
```

~30 sec, no full deploy needed. Hard-refresh the browser after.

## Why "Update" exists at all if it skips assets

Update is meant for fast iteration on Python/JSON/server-side changes — schema migrations, server scripts, hooks.py logic. The whole point is to skip the slow image-rebuild step. So this is by design, not a bug. Once you change anything under `public/` you have to either Deploy or `bench build` explicitly.

## Tell-tale that you're hitting this

Direct-hit the asset URL: `https://<site>/assets/<app>/<path>`. If the content is stale (old CSS / old JS), it's this gotcha. If it's 404, the asset doesn't exist on disk yet — also fixed by Deploy / `bench build`. If it's the new content, the issue is browser cache or selector mismatch, not asset bundling.

## Cross-reference

- `playbooks/frappe-custom-app-v16.md` — should mention "after editing public/, redeploy not just update".
