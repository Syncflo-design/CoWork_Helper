# Frappe Insights v3 — Playbook

End-to-end guide to building dashboards in Frappe Insights v3 via the REST API or Frappe MCP. This is the model-neutral version of the `frappe-insights-v3-dashboard` skill — same content, plain Markdown, drop into any LLM session.

## Prerequisites

- Site is on Insights **v3** (has `Insights Query v3`, `Insights Chart v3`, `Insights Dashboard v3` doctypes — not the v2 doctypes without the suffix)
- A connector that can call Frappe's REST API or `run_doc_method` — for Claude this is the Frappe MCP; for ad-hoc work it's `frappe.client.*` REST endpoints
- Workbook ID for the workbook you're targeting

## Mental model

A chart in Insights v3 is a **two-query sandwich**:

```
[ Source Query ]  →  [ Data Query ]  →  [ Chart ]
  type:"sql"           type:"source"      chart_type + config
  raw native SQL       points at source   measure/dimension bindings
```

The source query runs the native SQL and produces tabular data. The data query is a thin wrapper that references the source as a `source` op; chart-specific transforms (sort/filter/aggregate for the chart axes) would also go here. The chart binds to both: `query` (source) and `data_query` (the wrapper). Its `config` JSON tells the renderer which columns are measures/dimensions.

The dashboard then references chart names in its `items` JSON. **Every chart on the dashboard needs all four pieces wired** (source query operations, data query operations, chart config, and a unique `layout.i` on the dashboard item) or the tile renders blank.

## End-to-end recipe — adding one new KPI card

### 1. Create the source query

```
frappe_create("Insights Query v3", {
  "title": "Active Work Orders",
  "workbook": "<workbook_id>",
  "is_native_query": 1,
  "use_live_connection": 1,
  "operations": "[{\"type\": \"sql\", \"raw_sql\": \"SELECT COUNT(*) AS active_work_orders FROM `tabWork Order` WHERE status IN ('In Process', 'Not Started')\", \"data_source\": \"Site DB\"}]"
})
```

Save the returned `name` as `<SRC>`.

### 2. Verify it executes

```
frappe_call("run_doc_method", {"dt": "Insights Query v3", "dn": "<SRC>", "method": "execute"})
```

Confirm rows are non-empty and note the column names + types — you'll bind them in the chart config.

### 3. Create the data query

```
frappe_create("Insights Query v3", {
  "title": "Active Work Orders (data)",
  "workbook": "<workbook_id>",
  "operations": "[{\"type\": \"source\", \"table\": {\"type\": \"query\", \"query_name\": \"<SRC>\", \"workbook\": <workbook_id_int>}}]"
})
```

`workbook` inside the source op is an integer. Save the returned `name` as `<DATA>`.

### 4. Create the chart

```
frappe_create("Insights Chart v3", {
  "title": "Active Work Orders",
  "workbook": "<workbook_id>",
  "query": "<SRC>",
  "data_query": "<DATA>",
  "chart_type": "Number",
  "config": "<see config shape below, JSON-stringified>"
})
```

Number config shape:

```json
{
  "date_column": {},
  "filters": {"filters": [], "logical_operator": "And"},
  "limit": 100,
  "number_column_options": [],
  "number_columns": [
    {"aggregation": "sum", "column_name": "active_work_orders", "data_type": "Integer", "measure_name": "Active Work Orders"}
  ],
  "order_by": []
}
```

`measure_name` is the displayed label. Make it friendly. `column_name` must match the column produced by the data query.

### 5. Append to dashboard items

```python
existing = json.loads(dashboard.items or "[]")
existing.append({
    "type": "chart",
    "chart": "<CHART>",
    "layout": {"i": "<CHART>", "x": 0, "y": <next_y>, "w": 3, "h": 3}
})
frappe_update("Insights Dashboard v3", "<DASHBOARD>", {"items": json.dumps(existing)})
```

The `layout.i` is required (vue-grid-layout key). Use the chart name.

### 6. Refresh the dashboard tab

`linked_charts` rebuilds automatically on save.

## Common variants

**Bar / Line chart** — `chart_type: "Bar"` or `"Line"`. Config uses `x_axis.dimension` (one column) and `y_axis.series` (array of measures). Stacked: `y_axis.stack: true`. See `skills/frappe-insights-v3-dashboard/templates/chart_bar.json`.

**Table chart** — `chart_type: "Table"`. **Must** have `rows` (dimensions) and `values` (measures) arrays in config — without them the dashboard shows "No data to display" (see [`gotchas/2026-05-06-insights-table-needs-rows-values.md`](../gotchas/2026-05-06-insights-table-needs-rows-values.md)).

**Reusing a source query** — multiple charts can point their `query` at the same source. Each still needs its own data_query and chart config.

**Existing chart, change SQL** — update the source query's `operations`. The data_query and chart auto-pick up the new schema; you only need to update the chart config if the columns changed.

## Gotchas

- [`2026-05-06-insights-code-vs-sql.md`](../gotchas/2026-05-06-insights-code-vs-sql.md) — `code` op is Python, not SQL. Use `type:"sql"` with `raw_sql`.
- [`2026-05-06-insights-data-query-empty-stub.md`](../gotchas/2026-05-06-insights-data-query-empty-stub.md) — chart `data_query` is auto-created empty; populate `operations` with a `source` op.
- [`2026-05-06-insights-dashboard-layout-i-key.md`](../gotchas/2026-05-06-insights-dashboard-layout-i-key.md) — items need unique `layout.i` or canvas stays blank.
- [`2026-05-06-insights-table-needs-rows-values.md`](../gotchas/2026-05-06-insights-table-needs-rows-values.md) — Table charts need explicit `rows`+`values` in config to render on a dashboard.
- [`2026-05-06-insights-kpi-friendly-label.md`](../gotchas/2026-05-06-insights-kpi-friendly-label.md) — Number-card label comes from `measure_name`, set it to a friendly string.

## Reference

JSON templates in [`../skills/frappe-insights-v3-dashboard/templates/`](../skills/frappe-insights-v3-dashboard/templates/):

- `source_query.json` — KPI count, sum, list, join, LIKE-filtered
- `data_query.json` — source-op wrapper
- `chart_number.json` — Number/KPI card
- `chart_bar.json` — Bar/Line single + multi-series
- `chart_table.json` — Table chart
- `dashboard_items.json` — full layout with `i` keys
- `full_build_recipe.md` — concrete one-chart recipe

## Diagnostic ladder

When a chart doesn't render, check in order — fix the first failure:

1. Source query `execute()` returns rows? (`run_doc_method` → execute)
2. Data query `execute()` returns the same rows?
3. Chart `config.column_name` / `config.values[].column_name` exactly matches a column from step 2?
4. Dashboard `items[].layout.i` is set and unique?
5. For Table: `config.rows` and `config.values` are non-empty?
6. Browser hard-refresh the dashboard tab?
