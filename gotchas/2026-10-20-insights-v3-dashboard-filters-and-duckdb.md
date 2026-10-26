# Insights v3 (3.12.2): dashboard filters, chart labels, and the DuckDB trap for raw SQL

Learned building the Ardmore sales dashboards (workbook 4 on ardmoreceramics) on 2026-10-20.
Extends the `frappe-insights-v3-dashboard` skill.

## Dashboard filters (the pill bar)

A filter is a dashboard item, not a doc:

```json
{"type":"filter","filter_name":"Colour","filter_type":"String",
 "links":{"<chart_name>":"`<query_name>`.`colour`"},
 "layout":{"i":"filter_colour","x":6,"y":1,"w":2,"h":1}}
```

- `filter_type` is `String` or `Date` (Number exists too).
- `links` is keyed by CHART name; the value is the query NAME (doc name, not title) and column in
  backticks. The backend only honours a link whose query is the chart's `query` or in that
  query's upstream closure (`insights_dashboard_v3.py: routed_filter_links`).
- So: build ONE raw-SQL source query with every column you will ever filter on, point every
  chart's `query` at it, let each chart aggregate in its own `config`, and link every filter to
  that one query. The filter then lands before the aggregation and every tile narrows together.
- Pills at `h:1` render fine; the grid is 20 columns wide (see below), so six pills a row = w 3-4.
- Preset a pill with `default_operator` + `default_value` (both needed; the front end ignores one without the other). Date `between` takes `["YYYY-MM-DD","YYYY-MM-DD"]`, `within` takes a relative string, String `in` takes a list.
- Russell found the Date `between` pill (one range box) confusing: use TWO Date pills on the same column instead, "From date" preset `>=` and "To date" preset `<=`, each a plain single-date picker. Two filters on one column AND together.

## Labels

`measure_name` / `dimension_name` in the chart config are what the user sees (KPI caption,
table header, legend). Use words ("Sales excl VAT"), never the column name.

## Raw SQL is NOT run on MariaDB when a chart reads it

A query-sourced data query (`{"type":"source","table":{"type":"query",...}}`) is compiled by
ibis and executed in DuckDB: Insights pulls the tables the raw SQL names into DuckDB as CTEs
named after the table, and transpiles the SQL with sqlglot (so `CURDATE()`, `DATE_FORMAT`,
`YEAR()` are fine). Two consequences:

1. A raw SQL that references the same table TWICE (self-join, two subqueries) fails in the
   dashboard with `Parser Error: Duplicate CTE name "tabSales History"` even though
   `run_doc_method execute` on the source query itself succeeds (that one runs live on
   MariaDB). Rewrite as one pass with conditional aggregation (`SUM(CASE WHEN yr = ...)`).
2. Test the DATA query (`execute` on the wrapper), not only the source query, before trusting
   a tile.

## Other
- `preview_image` on the dashboard doc is written when someone opens it; a thumbnail with
  bars = it rendered.
- `is_public` dashboards are served without login (SharedDashboard) - never for sales data.
- The dashboard grid is **20 columns** in 3.12.2 (`cols:20` in the served Dashboard chunk), not 12: a 12-wide layout fills only 60% of the page. Lay out on 20. The Insights sidebar collapses with the
  toggle in its header and the browser remembers it.
- Insights caches query results per session; after a re-load of the table, hard-refresh.
