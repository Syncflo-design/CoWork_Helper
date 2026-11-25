# Frappe v16: boot.home_page must be a desk Page name, not a route

**Date:** 2026-11-11
**Bit me on:** nest_home 0.0.33 (per-layout Landing Page). Partner layout landed on
`query-report/Project Tracker`; clicking the breadcrumb Home icon showed
"User ... does not have doctype access via role permission for document Page / No permission for Page".

## Cause

The breadcrumb Home icon is `<a href="/desk">`. The desk renders an empty route with
`frappe.router.render()` -> `frappe.views.pageview.show("")`, which falls back to
`frappe.boot.home_page` and calls `frappe.desk.desk_page.getpage` for a **Page doc of that name**.
`query-report/Project Tracker` is not a Page, so getpage 403s. `nest-home` worked only because it IS a Page.

## Fix (nest_home 0.0.34)

- Only put single-segment Page names in `bootinfo["home_page"]` (leave Frappe's default, `desktop`, otherwise).
- For route landings, wrap `frappe.views.pageview.show` in an app_include script: empty name + route
  landing -> `frappe.set_route(landing)` and return, so no Page is fetched and nothing races the redirect.

## Also seen

`nest_home_redirect.js` is a plain (non-bundle) app_include asset with no version stamp, so browsers
kept running the cached old copy after the Deploy (transferSize 0, old byte size in
`performance.getEntriesByName`). See `2026-05-06-frappe-cloud-cdn-stale-assets.md` - a `.bundle.js`
name gets a hashed URL. The server-side half of the fix covered stale browsers.
