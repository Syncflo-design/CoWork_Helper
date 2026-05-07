# Full Build Recipe — One Chart, Start to Finish

Concrete sequence for adding a new KPI card to an existing dashboard. Numbers in `<>` are placeholders.

## Step 1 — Create the source query

```
frappe_create("Insights Query v3", {
  "title": "Active Work Orders",
  "workbook": "<workbook_id>",
  "is_native_query": 1,
  "use_live_connection": 1,
  "operations": "[{\"type\": \"sql\", \"raw_sql\": \"SELECT COUNT(*) AS active_work_orders FROM `tabWork Order` WHERE status IN ('In Process', 'Not Started')\", \"data_source\": \"Site DB\"}]"
})
```

→ Returns `{"name": "<SRC>", ...}`. Save `<SRC>`.

## Step 2 — Verify it executes

```
frappe_call("run_doc_method", {"dt": "Insights Query v3", "dn": "<SRC>", "method": "execute"})
```

→ Confirm `rows` non-empty, `columns[0].name` is what you'll bind in the chart config (`active_work_orders`), `columns[0].type` is `Integer`/`Decimal`/`String`/`Date`.

## Step 3 — Create the data query (wrapper)

```
frappe_create("Insights Query v3", {
  "title": "Active Work Orders (data)",
  "workbook": "<workbook_id>",
  "operations": "[{\"type\": \"source\", \"table\": {\"type\": \"query\", \"query_name\": \"<SRC>\", \"workbook\": <workbook_id_int>}}]"
})
```

→ Returns `{"name": "<DATA>", "linked_queries": "[\"<SRC>\"]", ...}`. Save `<DATA>`.

## Step 4 — Create the chart

```
frappe_create("Insights Chart v3", {
  "title": "Active Work Orders",
  "workbook": "<workbook_id>",
  "query": "<SRC>",
  "data_query": "<DATA>",
  "chart_type": "Number",
  "config": "{\"date_column\": {}, \"filters\": {\"filters\": [], \"logical_operator\": \"And\"}, \"limit\": 100, \"number_column_options\": [], \"number_columns\": [{\"aggregation\": \"sum\", \"column_name\": \"active_work_orders\", \"data_type\": \"Integer\", \"measure_name\": \"active_work_orders\"}], \"order_by\": []}"
})
```

→ Returns `{"name": "<CHART>", ...}`. Save `<CHART>`.

## Step 5 — Append to dashboard items

Read the current `items` (it's a JSON-encoded string), parse, append, restringify, write back.

```python
# pseudo-code, actual MCP calls below
existing = json.loads(dashboard.items or "[]")
existing.append({
    "type": "chart",
    "chart": "<CHART>",
    "layout": {"i": "<CHART>", "x": 0, "y": <next_y>, "w": 3, "h": 3}
})
frappe_update("Insights Dashboard v3", "<DASHBOARD>", {"items": json.dumps(existing)})
```

## Step 6 — Reload the dashboard tab in the browser

`linked_charts` rebuilds automatically on save.

---

## Common variants

**Bar chart instead of Number** — same steps 1–3. In step 4 set `chart_type: "Bar"` and use the bar config from `templates/chart_bar.json`. Also typically use `w: 12, h: 7` for a hero bar or `w: 6, h: 6` for a side-by-side.

**Table instead of Number** — same steps 1–3. In step 4 set `chart_type: "Table"` and you can omit `config` entirely. Use a wide layout slot.

**Reusing an existing source query** — skip steps 1–2. Point a new chart's `query` at an existing source name and create only its own data_query (step 3).
