# "The warehouse only has ceramics" — a link query that ignores the typed text

**Date:** 2026-08-12
**Domain:** Frappe / link fields / third-party apps
**Severity:** day-killer in disguise — it presents as a data problem, twice over

## Symptom

Two users, three weeks apart, reported the same thing: a warehouse "only contains
ceramics". Brittany said it about the stock list; Russell said it about the Stock Transfer
item picker, where typing `fab` changed nothing at all.

Main Distribution - ACT actually held **2,204 SKUs** including 30 fabrics, 24 cushions and
10 scarves.

## Cause

The Stock Transfer form points its Item field at a query in the third-party
`server_scripts` app:

```js
frm.set_query("item", "items", function () {
    return {
        query: "server_scripts...stock_transfer.in_stock_items",
        filters: { warehouse: frm.doc.source_warehouse },
    };
});
```

That query filters by warehouse stock correctly — and **ignores its `txt` argument
entirely**. It returns all 2,212 in-stock items on every keystroke. The dropdown shows the
first handful, which are ceramics by sort order, and typing never changes them.

Nothing is missing. Nothing errors. The search box simply does not search.

## How to prove it in one call

Do not reason about it — call the query method directly with a search term and see whether
the result changes:

```python
frappe.call("server_scripts...stock_transfer.in_stock_items", {
    "doctype": "Item", "txt": "FAB", "searchfield": "name",
    "start": 0, "page_len": 20, "filters": {"warehouse": "Main Distribution - ACT"},
})
```

It returned 2,212 rows with `FAB*` sitting at position ~855. That is the whole diagnosis.

## Fix

The app is not ours, so the query was replaced from the site's own Client Script — which
runs after the app's and can re-register `set_query`. Two things were needed:

1. **Register on the next tick.** The app sets its query inside its own
   `source_warehouse` handler; a plain call can land before it. `setTimeout(..., 0)`
   guarantees ours is last, whatever order the handlers run in.
2. **Keep the stock filter.** ERPNext's `erpnext.controllers.queries.item_query` honours
   typed text but knows nothing about warehouses. So: read the warehouse's in-stock item
   codes once when the source warehouse is chosen, then restrict the standard query with
   `name: ["in", codes]`. Search works, and only stock in that warehouse is offered.

Read the codes **straight from `Bin`**, not from the app's function:

```js
frappe.call({ method: 'frappe.client.get_list', args: {
    doctype: 'Bin',
    filters: { warehouse: wh, actual_qty: ['>', 0] },
    fields: ['item_code'], limit_page_length: 0 } });
```

Calling the app's function from JS fails with `'str' object has no attribute 'get'` —
`frappe.call` sends nested objects as a **JSON string**, and the function does
`filters.get("warehouse")`. Frappe's own link machinery passes a dict; a hand-rolled
`frappe.call` does not.

## Why this is non-obvious

- **It looks exactly like missing data.** Two different people concluded the warehouse was
  empty of everything but ceramics. Nobody suspects the search box.
- The query is *half* right — warehouse filtering works perfectly — which makes it read as
  trustworthy.
- An empty search returning everything is normal Frappe behaviour, so the first page of
  results looks legitimate.
- **Removing the stock filter is not a free fix.** Doing that first meant staff could pick
  items with no stock and get "No stock available" on selection — a regression that was
  reported within minutes. Keep both properties.

## See also

- `gotchas/2026-08-12-db-set-value-skips-the-hooks-that-make-a-change-real.md` — the first
  attempt at this fix appeared not to work at all, for that reason.
- `sites/ardmore.md` — the `server_scripts` app (Paul Christian Mata) owns Stock Transfer.
