# Insights v3 dashboard filters require the column to live in the SOURCE query's output

**Date:** 2026-05-06
**Domain:** Insights v3
**Severity:** annoying

## Symptom

A dashboard date filter is added with the right `links` map and applied operator/value, but the linked KPI charts stay frozen at their full-time totals — the filter has no effect.

## Cause

Insights' dashboard filter mechanism (see `frontend/src2/dashboard/dashboard.ts` → `getAdhocFilters`) builds adhoc filters keyed by **the source query name** and pushes them into `dataQuery.adhocFilters`. The filter is applied as an early `where` against the source's output rows.

That means the column you're filtering on (e.g., `posting_date`) **must exist as a column in the source query's result set**. If the source query is `SELECT SUM(grand_total) AS revenue FROM \`tabSales Invoice\``, there is no `posting_date` to filter on — the filter silently does nothing.

## Fix

Refactor the source to return raw rows including the date column, and move aggregation into the data_query.

```diff
- -- Source (etmsud9nfl):
- SELECT SUM(grand_total) AS revenue FROM `tabSales Invoice` WHERE docstatus = 1
+ -- Source (etmsud9nfl):
+ SELECT name, customer, posting_date, grand_total AS revenue
+ FROM `tabSales Invoice` WHERE docstatus = 1
```

Data_query keeps the existing `summarize` op (`sum(revenue)`) — sum-of-rows yields the same KPI value, but now `posting_date` survives as a filterable column.

## Why this is non-obvious

The filter's `links` map looks like a chart-to-column binding (`{ chart_name: "\`query\`.\`column\`" }`), so it's tempting to think the filter is doing template substitution against the data_query, or wiring directly into the chart's config — neither is true. The filter is injected as a WHERE upstream of every operation in the data_query, so the column has to be in the SQL's SELECT clause for the filter to bite.

If the source is already aggregated, the filter sees no matching column and quietly skips — no error, just no effect.

## See also

- Playbook: [`playbooks/insights-v3.md`](../playbooks/insights-v3.md)
- Related gotcha: [`2026-05-06-insights-data-query-empty-stub.md`](2026-05-06-insights-data-query-empty-stub.md)
- Source: `insights/frontend/src2/dashboard/dashboard.ts` lines ~220-260
