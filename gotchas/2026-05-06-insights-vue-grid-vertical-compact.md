# Insights v3 dashboards vertically compact items by default — fill empty grid space with spacer items

**Date:** 2026-05-06
**Domain:** Insights v3 (vue-grid-layout / DashboardBuilder)
**Severity:** annoying

## Symptom

You set carefully chosen `y` coordinates on dashboard items — say, filters at y=0, KPIs at y=1, line+donut "AR row" at y=4 — but the rendered dashboard ignores them. KPI tiles bunch up alongside the filters; the donut on the right of the AR row floats above the line chart on the left, even though both are configured at the same y/h. The two halves of a row visually drift to different heights.

## Cause

vue-grid-layout has `verticalCompact: true` by default. Insights' `Dashboard.vue` and `DashboardBuilder.vue` both wire this to `useStorage('dashboard_vertical_compact', true)` — i.e., the toggle lives in **localStorage**, not on the dashboard document. The `vertical_compact_layout` field that exists on the workbook/dashboard doctype is NOT what the renderer reads; the renderer reads localStorage and defaults to `true`.

`verticalCompact: true` means: at render time, every item is pulled upward to the closest non-overlapping y-slot. If a row has empty x-space, items below get hoisted up to fill it. So:

- y=0: From filter (x=0–3, w=4), To filter (x=4–7, w=4) — empty x=8–19
- y=1: KPIs at x=0,5,10,15

Compact runs → KPIs at x=10 and x=15 see empty slots directly above → they bump up to y=0. Then the AR-row donut at y=4 x=10–19 sees empty space at y=1–3 x=10–19 → it bumps up too. The line chart on the left can't bump because KPIs 1 & 2 are above it. Result: donut starts at y=1 while line chart starts at y=4 — visually misaligned, even though both have the same `h`.

## Fix

Fill any empty x-spans on partial rows with a `type: "text"` spacer item that has empty content. The text item occupies grid cells but renders nothing, blocking the compact pass from pulling items up through it.

For the MD Overview filter row (filters take x=0–7), add:

```json
{
  "type": "text",
  "text": "",
  "layout": { "i": "spacer_filter_row", "x": 8, "y": 0, "w": 12, "h": 1 }
}
```

Place the spacer at the **end** of the `items` array so the soft-professional theme's `:nth-child(N)` selectors keep targeting the correct chart positions (same reason filters go at the end — see [`2026-05-06-insights-filter-order-vs-css-nth-child.md`](2026-05-06-insights-filter-order-vs-css-nth-child.md)).

## Why this is non-obvious

- The dashboard JSON has a `vertical_compact_layout` field. It's tempting to assume setting that to 0 disables compaction. It does not — the renderer reads localStorage instead.
- vue-grid-layout's compaction is silent. Items move at render time without any indication that y/x weren't honored.
- Each browser has its own localStorage, so one user's dashboard could compact while another's doesn't if anyone toggled the option. Server-side spacers are the only stable fix.

## Source pointers

- `insights/frontend/src2/dashboard/Dashboard.vue` line 39: `useStorage('dashboard_vertical_compact', true)`
- `insights/frontend/src2/dashboard/DashboardBuilder.vue` line 59: same
- `insights/frontend/src2/dashboard/VueGridLayout.vue` line 53: `verticalCompact?: boolean`

## See also

- [`2026-05-06-insights-filter-order-vs-css-nth-child.md`](2026-05-06-insights-filter-order-vs-css-nth-child.md) — same problem space (DOM order vs visual position)
- [`2026-05-06-insights-dashboard-layout-i-key.md`](2026-05-06-insights-dashboard-layout-i-key.md) — every layout item needs a unique `i`
