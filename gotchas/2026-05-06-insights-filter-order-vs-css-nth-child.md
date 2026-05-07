# Insights v3 filter items shift `:nth-child` indices — keep filter LAST in items array

**Date:** 2026-05-06
**Domain:** Insights v3 (Soft Professional theme / fork CSS)
**Severity:** annoying

## Symptom

Add a dashboard filter at items[0] so it visually anchors at the top — and every KPI gradient on the dashboard shifts by one. KPI 1 gets KPI 2's colour, KPI 2 gets KPI 3's, etc. The hero-chart top-border lands on the wrong tile.

## Cause

The Soft Professional theme (in `frontend/src2/syncflo-custom-overrides.css`) targets tiles by `.vgl-item:nth-child(N)`. `:nth-child` counts DOM order — which is the items-array order — not the layout grid coordinates. Putting a filter at `items[0]` makes it `:nth-child(1)` even if its `layout.y` is 0 like the KPIs.

Filters render through `<DashboardFilter>` instead of `<DashboardChart>`, so the inner Tailwind selectors (`[class*="rounded"][class*="bg-white"][class*="shadow"]`) don't match the filter's DOM — the gradient rule does NOT visually apply to the filter slot. But the index shift is real, and every chart after it gets the wrong colour.

## Fix

Push the filter to the **end** of the `items` array. Visual position stays at the top thanks to `layout.x = 0, layout.y = 0`. DOM order — which is what `:nth-child` reads — is preserved.

```diff
  items: [
-   { type: "filter",  layout: {x:0, y:0, w:4, h:1} },
    { type: "chart", chart: "kpi_1", layout: {x:0,  y:1, w:5, h:3} },
    { type: "chart", chart: "kpi_2", layout: {x:5,  y:1, w:5, h:3} },
    { type: "chart", chart: "kpi_3", layout: {x:10, y:1, w:5, h:3} },
    { type: "chart", chart: "kpi_4", layout: {x:15, y:1, w:5, h:3} },
    /* ...other charts... */
+   { type: "filter",  layout: {x:0, y:0, w:4, h:1} },
  ]
```

That's also the natural pattern Insights' `addFilter()` uses — `dashboard.doc.items.push(newFilter)` appends, then `positionNewFilter()` sets `layout` to the top.

## Why this is non-obvious

Visually placing the filter "first" makes it tempting to put it at `items[0]`. The CSS works fine in isolation — there's no error — but every gradient is off-by-one. You only spot it if you remember the theme is position-based, OR you compare against the dashboard before the filter was added.

vue-grid-layout will happily render items out of array order based on layout coordinates, hiding the DOM-order coupling entirely.

## See also

- Theme file: `insights/frontend/src2/syncflo-custom-overrides.css`
- Playbook: [`playbooks/insights-fork-themeing.md`](../playbooks/insights-fork-themeing.md)
- Source: `insights/frontend/src2/dashboard/dashboard.ts` `addFilter()`
