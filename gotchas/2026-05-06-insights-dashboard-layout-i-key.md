# Insights v3 dashboard `items` layout needs unique `i` key

**Date:** 2026-05-06
**Domain:** Frappe Insights v3
**Severity:** day-killer

## Symptom

Dashboard saves cleanly, `linked_charts` populates with all the right chart names, but the canvas is **completely blank**. No error, no warning, just empty grid.

## Cause

The dashboard uses vue-grid-layout under the hood, which requires a unique `i` (item key) per layout entry to track and render items. Without it, the items mount and immediately get garbage-collected.

## Fix

Add `i` to every item's `layout`. Using the chart name is fine:

```diff
{
  "type": "chart",
  "chart": "3q9k2se8it",
  "layout": {
+   "i": "3q9k2se8it",
    "x": 0, "y": 0, "w": 3, "h": 3
  }
}
```

## Why this is non-obvious

Frappe's REST API accepts the items JSON without complaint, the parent doc saves, the `linked_charts` child table even auto-populates correctly from the items. Everything *looks* right at the data layer. The failure is purely in the frontend grid library, and it fails silently — no console error in the obvious place. The only way to find this is to look at the actual TypeScript type for `WorkbookDashboardItem` in `frontend/src2/dashboard/dashboard.ts`.

## See also

- [`gotchas/2026-05-06-insights-data-query-empty-stub.md`](2026-05-06-insights-data-query-empty-stub.md)
- [`skills/frappe-insights-v3-dashboard/templates/dashboard_items.json`](../skills/frappe-insights-v3-dashboard/templates/dashboard_items.json)
