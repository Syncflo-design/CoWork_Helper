# Insights v3 Table charts need `rows` + `values` config on dashboard

**Date:** 2026-05-06
**Domain:** Frappe Insights v3
**Severity:** annoying

## Symptom

A `chart_type: "Table"` chart renders fine when opened standalone from the workbook (shows all source columns and rows). On a dashboard it shows "No data to display" — even though the underlying query returns rows.

## Cause

Standalone view falls back to "show all columns from the source"; dashboard view requires the chart to declare what to display via the `config` field. Without `rows` and `values` arrays, the dashboard renderer has nothing to draw.

## Fix

Set `config` with explicit `rows` (dimensions, usually string columns) and `values` (measures, usually numeric columns):

```json
{
  "filters": {"filters": [], "logical_operator": "And"},
  "limit": 100,
  "order_by": [{"column": {"column_name": "projected_qty", "data_type": "Decimal"}, "direction": "asc"}],
  "rows": [
    {"column_name": "item_code", "data_type": "String", "dimension_name": "item_code"}
  ],
  "columns": [],
  "values": [
    {"aggregation": "sum", "column_name": "actual_qty",    "data_type": "Decimal", "measure_name": "actual_qty"},
    {"aggregation": "sum", "column_name": "reserved_qty",  "data_type": "Decimal", "measure_name": "reserved_qty"},
    {"aggregation": "sum", "column_name": "projected_qty", "data_type": "Decimal", "measure_name": "projected_qty"}
  ]
}
```

Use `aggregation: "sum"` even when the source already aggregated — sum-of-pre-summed is identity.

## Why this is non-obvious

The table works in the standalone preview. The dashboard error is "No data to display" — the same message you'd see if the query genuinely returned zero rows. So you check the query (returns 14 rows ✓), check the data_query (returns 14 rows ✓), and conclude there's nothing wrong with the data path. The actual issue is config-shape, not data.

## The data_query also needs a `summarize` op — not just `source`

A data_query with only `{"type": "source", ...}` will cause the same "No data to display" on dashboard tables. The data_query must also have a `summarize` operation listing the same dimensions and measures as the chart config:

```json
[
  {"type": "source", "table": {"type": "query", "query_name": "SOURCE_QUERY_ID", "workbook": 2}},
  {
    "type": "summarize",
    "dimensions": [
      {"column_name": "supplier", "data_type": "String", "dimension_name": "supplier"}
    ],
    "measures": [
      {"aggregation": "sum", "column_name": "outstanding", "data_type": "Decimal", "measure_name": "outstanding"}
    ]
  }
]
```

Both must be consistent: chart config `rows` = data_query `dimensions`, chart config `values` = data_query `measures`.

## See also

- [`skills/frappe-insights-v3-dashboard/templates/chart_table.json`](../skills/frappe-insights-v3-dashboard/templates/chart_table.json) — needs updating with rows/values shape
