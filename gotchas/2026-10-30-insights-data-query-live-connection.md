# Insights v3: a chart's data query must be live, or every native-SQL chart fails with "Duplicate CTE name"

**Date:** 2026-10-30 · **Site:** fuse-manufacturing-demo (Syncflo fork 3.12.2) · **Severity:** blocks every chart built over the API

## Symptom

Native-SQL source queries execute fine (`run_doc_method execute`), but each chart's data query
(`[{"type": "source", "table": {"type": "query", ...}}]`) fails with
`_duckdb.ParserException: Duplicate CTE name "tabWork Order"` — even for a one-table SELECT.

## Cause

An `Insights Query v3` created over the API defaults to `use_live_connection = 0`. A data query that
is not live runs its source's raw SQL in DuckDB (`ibis_utils.apply_sql`: transpile + prepend a
CTE per table), and that path duplicates the CTE. The UI never hits it because `chart.ts refresh()`
copies the source's `use_live_connection` onto the data query before executing.

## Fix

Create every data query with `"use_live_connection": 1` (same as its source). Live queries run on
MariaDB directly, so explicit JOINs, self-joins and child tables all work too.

## Also learned

- The front end rebuilds the data query's operations from the chart `config` on every refresh, so
  storing just the `source` op is enough; no `summarize` needed.
- After the chart's summarize, columns are named by `measure_name` / `dimension_name`, so a chart
  `order_by` must name the label ("Hours to do"), not the raw column. A wrong name is ignored silently.
- Share with everyone: `run_doc_method update_access` on the dashboard with
  `{"is_shared_with_organization": 1}`. Viewers also need the `Insights User` role.
- Insights reads the DB directly: Frappe User Permissions (company) are NOT applied. Use a Company
  filter pill with a default.
