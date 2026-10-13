# Updating Frappe/ERPNext on the bench: 16.51 dropped Font Awesome and every `fa fa-*` icon went blank

**Date:** 2026-10-13
**Domain:** Frappe Cloud / Frappe v16 / nest_home / custom desk pages
**Severity:** looks like a broken release to the client (home screen with no icons); one deploy cycle to fix
**Site:** ardmoreceramics.c.frappe.cloud (bench Ardmore_KZN)

## Symptom

Right after a Deploy that was meant to ship two small app changes (nest_home 0.0.26,
nest_stock_request 0.1.2), the Nest Home screen showed every tile without an icon and the
two round header buttons (Home, Refresh) empty. The layout change in the same deploy
(attention panel hidden, tiles 4-wide) was fine. No console error, no 404 on the
page's own stylesheets.

## Cause

Two things stacked:

1. **Frappe and ERPNext were updated on the bench in the same Deploy** (Russell pressed
   Update on them while adding the new app): Frappe 16.35.1 -> 16.51.1, ERPNext 16.36.1
   -> 16.50.0. `frappe.utils.change_log.get_versions` shows it.
2. Frappe 16.5x no longer ships Font Awesome on the desk. nest_home's tiles are stored
   with Font Awesome names (`fa fa-credit-card` ...) and the page passed them straight
   through as `<i class="fa fa-...">`. The page JS vendors Phosphor (since 0.0.25) but
   only used it when a tile already carried a `ph-` class. The header buttons used
   `fa fa-home` / `fa fa-refresh` directly.

## Fix (nest_home 0.0.27)

- `nh_fa_to_ph(name)`: a table of the Font Awesome 4 names in use -> Phosphor glyph
  (credit-card, calculator, truck, cubes, users, file-text-o, book, upload, plus-circle,
  bar-chart, cog, shopping-basket, share-square-o ...), fallback `squares-four`.
- `nh_tile_icon` draws any `fa fa-X` as `<i class="ph-duotone ph-<mapped>">`; stored tile
  data is untouched, so nothing had to change on the sites.
- Header buttons and the empty-list tick use `ph ph-house`, `ph ph-arrow-clockwise`,
  `ph ph-check`.
- The function sits ABOVE `class NestHome`: a `function` declaration inside a class body
  is a syntax error (`node --check` caught it before the push).

## Why this is non-obvious

- The icons had worked an hour earlier; the only "known" change was a CSS tweak, so the
  first suspicion was the page's own stylesheet or its cache-buster (gotcha 2026-08-18).
  The page's CSS and the Phosphor CSS both probed fine with `?probe=1`.
- No app in the bench vendors Font Awesome, so grep finds nothing to blame; the font came
  from Frappe itself and left with Frappe.
- The app deploy and the framework update looked like one event in the dashboard.

## Rule

Update Frappe/ERPNext in a deploy of their own, not alongside an app change, and say so.
After any deploy call `get_versions` (MCP `frappe_call`) and compare with the previous note
in `sites/<site>.md`. A framework jump means re-testing the till (POS client scripts,
opening dialog, returns, Sage posting) before go-live, not just the feature shipped.

## The second casualty: every `/app/` link is dead (Frappe 16.5x serves the desk at `/desk/`)

Found by Russell an hour later: the Guides page's "Back to the home screen" (`/app/nest-home`)
gave "Page not found". Sweep of the site and the apps on 2026-10-13 evening:

| Where | Fix |
|---|---|
| Web Page `guides` back link | `/desk/nest-home` (temp server script; API user has no Web Page role) |
| Nest Home Tiles NEST-TILE-0001..0006 (`/app/...`, re-created by nest_home's fixture on every migrate) | routes made relative on the site AND in `nest_home/fixtures/nest_home_tile.json` |
| Nest Home tile opened in a new tab (Insights) | `nest_home.js` built `origin + '/app/' + route`; 0.0.28 builds `/desk/` and accepts `/desk` or `/app` in stored routes. Site workaround until deploy: route `/desk/insights` (an absolute non-desk path is opened as-is) |
| nest_help: 31 help pages, "Back to Home" and "navigate to /app/x" | sed `/app/` -> `/desk/`, 0.0.7 (needs push + Deploy; help pages are static assets) |
| Role home_page: Ardmore Finance `/app/accounting`, Ardmore Marketing `/app/selling` | `/desk/...` |
| Custom HTML Block `CustomBlock1` (POS tile on a workspace) | `/desk/point-of-sale` |
| Client Script `nest-crm-todo-intercept` (fixture of nest_crm_tasks) | `/desk/party-activity/` on the site and in the app (0.0.22, incl. my_activities.js / party_activity.js) |
| Workspace shortcuts/links, Print Formats, Email Templates, Notifications, Web Pages, User home_settings | scanned, clean |

Rule: after a framework update grep every app and the site for `'/app/` and `"/app/`. Tile routes
and in-app links must be relative (`sales-order/new`); only website pages are absolute (`/guides`).

## See also

- `gotchas/2026-05-10-frappe-v16-page-api-drift.md` (the same kind of framework drift,
  v15 -> v16)
- `gotchas/2026-08-18-page-css-served-stale-when-the-cache-buster-is-not-bumped.md`
  (nest_home's stylesheets are linked WITHOUT a cache-buster, still open)
