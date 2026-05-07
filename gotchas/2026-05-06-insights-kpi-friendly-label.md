# Insights v3 Number-card KPI label is `measure_name`, not chart title

**Date:** 2026-05-06
**Domain:** Frappe Insights v3
**Severity:** trivial

## Symptom

KPI cards on the dashboard display ugly auto-generated labels like `sum_of_active_work_orders` above the value. The chart's `title` field ("Active Work Orders") is not used.

## Cause

Number cards render the measure's `measure_name` as the small label, not the chart title. When you set `measure_name` to the same string as `column_name` (e.g. `active_work_orders`), the renderer derives `sum_of_active_work_orders` from the aggregation function + column.

## Fix

Set `measure_name` to a friendly display string:

```diff
"number_columns": [
  {
    "aggregation": "sum",
    "column_name": "active_work_orders",
    "data_type": "Integer",
-   "measure_name": "active_work_orders"
+   "measure_name": "Active Work Orders"
  }
]
```

`column_name` still has to match the actual column the data_query produces. Only `measure_name` is for display.

## Why this is non-obvious

You'd reasonably expect Insights to use the chart's `title` field as the card heading. It uses it for Bar/Line/Table charts, but Number cards are special — they show the measure label instead, presumably because a single-number card has no axis to label.

## See also

- [`skills/frappe-insights-v3-dashboard/templates/chart_number.json`](../skills/frappe-insights-v3-dashboard/templates/chart_number.json)
