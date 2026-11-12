# Plain app_include_js files are cached "immutable" for a year: deploys don't reach browsers

**Date:** 2026-11-12
**Domain:** Frappe v16 custom app / Frappe Cloud assets
**Severity:** annoying

## Symptom

nest_home 0.0.38 added a header Home button through its `app_include_js`. The deploy
succeeded and `curl` of the asset showed the new code. In my browser the button showed after
Ctrl+Shift+R, but Russell's browser showed nothing on the Sales Invoice list or the Accounting
workspace.

## Cause

`hooks.app_include_js = ["/assets/nest_home/js/nest_home_redirect.js"]` is a plain file with an
unchanging URL, and Frappe Cloud serves `/assets/...` with:

```
Cache-Control: max-age=31536000, immutable
```

Every browser that loaded the file before keeps its old copy for a year, even across deploys.

## Fix

Ship it as a bundle so `bench build` gives it a hashed URL that changes with every build:

```diff
- app_include_js = ["/assets/nest_home/js/nest_home_redirect.js"]
+ app_include_js = ["nest_home_redirect.bundle.js"]
```

Rename `public/js/nest_home_redirect.js` -> `public/js/nest_home_redirect.bundle.js`. The bundle
resolves through `assets.json` to `/assets/nest_home/dist/js/nest_home_redirect.bundle.<HASH>.js`.
Needs a full Deploy (build), not Update. Same pattern already live: `nest_assistant.bundle.js`,
`nest_theme` `syn_boot.bundle.js`.

## Why this is non-obvious

- Server-side checks all pass: the deploy is green and the asset URL serves the new code.
- The developer's own browser usually has been hard-refreshed, so it "works on my machine".
- Still plain on 2026-11-12: `nest_help` (`/assets/nest_help/js/nest_help.js`) and `nest_sheets`
  (`/assets/nest_sheets/js/nest_sheets.js`). Their next change will hit the same wall.

## See also

- `gotchas/2026-11-12-frappe-16-56-page-header-has-no-navbar.md`
