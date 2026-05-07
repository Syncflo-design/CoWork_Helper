# Insights v3 `order_by` op crashes the data_query with `'NoneType' object has no attribute 'column_name'`

**Date:** 2026-05-06
**Domain:** Insights v3
**Severity:** trivial

## Symptom

Tried to add an `order_by` operation to a data_query (after `source` + `summarize`). Execute fails with:

```
AttributeError: 'NoneType' object has no attribute 'column_name'
```

Shape that crashed:
```json
{
  "type": "order_by",
  "order_by": [
    {"column": {"column_name": "posting_month", "data_type": "String"}, "direction": "asc"}
  ]
}
```

## Cause

The `order_by` op in v3 doesn't accept the `{column: {...}}` wrapper shape used in chart `config.order_by`. It expects something else (likely flat `column_name` + `direction`, or a top-level `dimension`-style key). Backend dereferences a `None` and dies.

## Fix

Don't add `order_by` as a data_query operation. Put it in the chart's `config.order_by` instead — the chart config wrapper does take the `{column: {column_name, data_type}, direction}` shape correctly.

```diff
  // data_query operations
  [
    { "type": "source", "table": {...} },
    { "type": "summarize", "dimensions": [...], "measures": [...] },
-   { "type": "order_by", "order_by": [{ "column": {...}, "direction": "asc" }] }
  ]

  // chart config
  {
    ...,
+   "order_by": [{ "column": { "column_name": "posting_month", "data_type": "String" }, "direction": "asc" }]
  }
```

For a Line chart, putting `order_by` in the chart `config` sorts the x-axis correctly. The data_query can return rows in any order; the chart re-sorts before render.

## Why this is non-obvious

The error message points at "column_name" but doesn't tell you where the bad shape is. Stack only shows the failure inside the operations executor; doesn't say "your op shape is wrong." First instinct is to fix the column object, when actually the whole op shouldn't be there in the first place.

If the correct data_query `order_by` shape is documented somewhere, I haven't found it yet. The chart-config shape works and is sufficient for line/bar charts.

## See also

- Playbook: [`playbooks/insights-v3.md`](../playbooks/insights-v3.md)
