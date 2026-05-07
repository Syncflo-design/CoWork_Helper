---
name: frappe-insights-v3-dashboard
description: Build dashboards in Frappe Insights v3 via the Frappe MCP/API. Use this skill any time the user wants to create, fix, or modify charts and dashboards on a Frappe site that uses Insights v3 — including writing native SQL queries, wiring chart configs, and laying out the dashboard. Triggers on mentions of "Insights", "Insights v3", "Insights Query v3", "Insights Chart v3", "Insights Dashboard v3", "Frappe dashboard", or related doctypes. Do NOT use for Insights v2 (different doctypes/architecture) or for non-Insights ERPNext dashboards (Number Card / Dashboard Chart doctypes).
---

# Frappe Insights v3 Dashboard Construction

This skill captures the exact doctype shapes, gotchas, and working JSON used to build dashboards in Frappe Insights v3 over the Frappe REST API / MCP. Treat the patterns here as authoritative — every shape was learned from production failures.

## Before you start

Confirm the site is on Insights **v3**, not v2. Quick check via the MCP:

```
frappe_call("frappe.client.get_value", {"doctype": "DocType", "filters": {"name": "Insights Query v3"}, "fieldname": "name"})
```

If that returns a name, you're on v3 and the doctypes below apply. v2 uses `Insights Query`, `Insights Chart`, `Insights Dashboard` (no `v3` suffix) and a totally different operations format — do not mix them.

The v3 doctypes you'll touch:

- `Insights Workbook` — the container; you need its name (usually a small integer like `"1"`)
- `Insights Query v3` — both **source queries** (with native SQL) and **chart data queries** (which source from another query)
- `Insights Chart v3` — chart config, references one source query and one data query
- `Insights Dashboard v3` — the canvas; holds an `items` JSON for layout

## Architectural model — read this once

A chart in Insights v3 is a **two-query sandwich**:

```
[ Source Query ]  →  [ Data Query ]  →  [ Chart ]
  type:"sql"           type:"source"      chart_type + config
  raw native SQL       points at source   measure/dimension bindings
```

- The **source query** runs the native SQL and produces tabular data.
- The **data query** is a thin wrapper that references the source as a `source` op; chart-specific transforms (sort/filter/aggregate for the chart axes) would also go here.
- The **chart** binds to both: `query` (source) and `data_query` (the wrapper). Its `config` JSON tells the renderer which columns are measures/dimensions.

The dashboard then references chart names in its `items` JSON. Every chart on the dashboard needs both queries wired and the config bound to real columns, or it won't render.

## The five mistakes that wasted a day

These are the actual failure modes encountered. Skip them.

### 1. `type: "code"` does NOT mean "raw SQL"

The `code` operation type expects **Python/ibis code**, not SQL. The backend runs your string through Python's parser. Symptom: any SQL keyword fails with `Line 1: SyntaxError: invalid syntax at statement: 'SELECT ...'`. The cure is **always** to use `type: "sql"` with a `raw_sql` field.

```json
// WRONG — Python SyntaxError
{"type": "code", "code": "SELECT COUNT(*) FROM `tabBin`"}

// RIGHT
{"type": "sql", "raw_sql": "SELECT COUNT(*) FROM `tabBin`", "data_source": "Site DB"}
```

Once you're in `type: "sql"`, the SQL is plain MariaDB: backticks for spaced identifiers (`` `tabWork Order` ``), single `%` in `LIKE`, `<` / `>` / `IN(...)` all work normally. Don't double-`%` — that was a workaround for the Python `%`-formatter, which is not in the path here.

### 2. The chart's `data_query` is auto-created EMPTY

When the UI creates a chart, it spawns a sibling `Insights Query v3` doc with `operations: null` to act as the data_query. **You must populate it.** The minimum is a single `source` op pointing back at the source query:

```json
[{"type": "source", "table": {"type": "query", "query_name": "<source_query_name>", "workbook": <workbook_id_int>}}]
```

`workbook` here is an **integer** (e.g. `1`), not a string.

After you save, `linked_queries` on the data_query auto-populates. That's how you know it parsed the source op correctly.

### 3. Chart `config` columns are blank by default

Number/Bar/Line/Pie configs ship with empty `column_name` and `aggregation`. The chart will show "No data" until you bind real columns. For a Number card the shape is:

```json
{
  "date_column": {},
  "filters": {"filters": [], "logical_operator": "And"},
  "limit": 100,
  "number_column_options": [],
  "number_columns": [
    {"aggregation": "sum", "column_name": "active_work_orders", "data_type": "Integer", "measure_name": "active_work_orders"}
  ],
  "order_by": []
}
```

Bar/Line:

```json
{
  "filters": {"filters": [], "logical_operator": "And"},
  "limit": 100,
  "order_by": [],
  "x_axis": {"dimension": {"column_name": "item_name", "data_type": "String", "dimension_name": "item_name"}},
  "y_axis": {
    "series": [{"measure": {"aggregation": "sum", "column_name": "actual_qty", "data_type": "Decimal", "measure_name": "actual_qty"}}],
    "stack": false
  }
}
```

`aggregation: "sum"` is safe even when the source query already aggregated — summing a single row gives the same number.

### 4. The dashboard `items` JSON needs `i` in every layout

The dashboard renderer is vue-grid-layout, which **requires** a unique `i` per item to track and render it. Items without `i` save fine, link to charts fine in `linked_charts`, but the canvas stays blank. Use the chart name as `i`:

```json
{"type": "chart", "chart": "3q9k2se8it", "layout": {"i": "3q9k2se8it", "x": 0, "y": 0, "w": 3, "h": 3}}
```

### 5. `chart_type` mismatches the slot

A `Line` chart in a 3×3 KPI slot renders nothing usable. Match the type to the data shape:

- 1 row × 1 numeric column → `chart_type: "Number"`
- N rows × 1 dimension + 1+ measures → `Bar`, `Line`, `Pie`, `Donut`
- N rows × N columns → `Table`
- Tables and Pivot Tables don't need a `config` to render — they just show the source columns.

## Reference layouts

12-col grid. KPI strip on top is the strongest opener; tables go to the bottom; bars sit between. h is roughly "rows" — 3 = squat KPI card, 6–7 = a real chart.

```
KPI strip → hero chart → comparison row → detail table

y=0  h=3: [KPI w=3][KPI w=3][KPI w=3][KPI w=3]
y=3  h=7: [hero bar/line w=12]
y=10 h=6: [bar w=6][bar-or-table w=6]
y=16 h=7: [detail table w=12]
```

## End-to-end build sequence

For each KPI/chart, do these in order. Skipping any of the first four leaves a blank tile.

1. **Create / update the source query** — `Insights Query v3` with `operations` = `[{type:"sql", raw_sql:"...", data_source:"..."}]`.
2. **Verify it executes** — `frappe_call("run_doc_method", {dt:"Insights Query v3", dn:<name>, method:"execute"})`. Confirm rows + column types.
3. **Create / update the data query** — `Insights Query v3` with `operations` = `[{type:"source", table:{type:"query", query_name:"<source>", workbook:<int>}}]`.
4. **Bind the chart** — set `query` (source name), `data_query` (wrapper name), `chart_type`, and `config` with real column_names matching what step 2 returned.
5. **Place on dashboard** — append to `Insights Dashboard v3.items`, including `layout.i` = chart name.
6. **Refresh the dashboard in the browser.** The dashboard's `linked_charts` table auto-rebuilds on save, so you don't manage it manually.

## Templates

Working JSON for each piece is in `templates/`:

- `templates/source_query.json` — KPI count, sum, list, join, LIKE-filtered list
- `templates/data_query.json` — source-op wrapper (paste-ready)
- `templates/chart_number.json` — Number/KPI card config
- `templates/chart_bar.json` — Bar chart config (with multi-series example)
- `templates/chart_table.json` — Table chart (config can be empty)
- `templates/dashboard_items.json` — full 8-tile layout with `i` keys

All templates were copied from a verified-working production dashboard (`blomoplastics.jh.frappe.cloud` workbook 1, Manufacturing Operations).

## Quick MCP recipes

Most calls go through the Frappe MCP connector for the target site. Replace `frappe-blomo` with whichever site you're on.

Find a workbook by name:
```
frappe_list("Insights Workbook", filters=[["title","=","..."]], fields=["name"])
```

Update a query's SQL:
```
frappe_update("Insights Query v3", "<name>", {"operations": "<json string>"})
```

Run a query and inspect the result:
```
frappe_call("run_doc_method", {"dt":"Insights Query v3", "dn":"<name>", "method":"execute"})
```

The `operations` field is `JSON` typed at the doctype level but Frappe stores and returns it as a JSON-encoded **string**. Always pass a stringified array, not a raw array.

## When something doesn't render

Diagnostic ladder, top to bottom — fix the first one that fails:

1. Does the source query execute and return rows? (`run_doc_method` → execute)
2. Does the data query execute and return the same rows?
3. Does the chart's `config` have non-empty `column_name` values that match the columns in step 2?
4. Does the dashboard `items` entry for this chart have `layout.i` set?
5. Hard refresh the dashboard tab — Insights v3 caches chart data per session.
