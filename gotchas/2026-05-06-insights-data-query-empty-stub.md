# Insights v3 chart `data_query` is auto-created empty

**Date:** 2026-05-06
**Domain:** Frappe Insights v3
**Severity:** annoying

## Symptom

Chart opens fine standalone but renders blank on a dashboard. The chart's `query` field points at a working source query, but `data_query` references an `Insights Query v3` doc whose `operations` is `null`.

## Cause

In Insights v3 every chart is a two-query sandwich: one source query (with the SQL/ibis), and one **data query** that wraps the source and applies chart-specific transforms. When the UI creates a chart it auto-creates the data_query but leaves its `operations` empty — you have to populate it.

## Fix

Set the data_query's `operations` to a single `source` op pointing back at the source:

```json
[{"type": "source", "table": {"type": "query", "query_name": "<source_query_name>", "workbook": 1}}]
```

`workbook` is an **integer**, not a string. After saving, the data_query's `linked_queries` field auto-populates with `["<source_query_name>"]` — that's how you know it parsed.

## Why this is non-obvious

The chart works perfectly when opened from the workbook (the workbook view runs the source query directly). It only breaks on the dashboard, and even there the dashboard `linked_charts` table is populated and looks fine. There's no error message — just empty tiles. You only spot the empty data_query if you go look at the `Insights Query v3` doc whose name matches the chart's `data_query` field and notice `operations: null`.

## See also

- [`gotchas/2026-05-06-insights-code-vs-sql.md`](2026-05-06-insights-code-vs-sql.md)
- [`gotchas/2026-05-06-insights-table-needs-rows-values.md`](2026-05-06-insights-table-needs-rows-values.md)
- [`skills/frappe-insights-v3-dashboard/templates/data_query.json`](../skills/frappe-insights-v3-dashboard/templates/data_query.json)
