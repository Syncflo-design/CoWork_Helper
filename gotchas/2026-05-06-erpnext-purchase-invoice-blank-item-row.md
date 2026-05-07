# ERPNext Purchase Invoice — posting a row with no item (direct GL expense)

**Date:** 2026-05-06
**Bit me on:** `quick_purchase_invoice` — wanted QuickBooks-style "Account row" support where the user picks an expense account directly without having to create a non-stock Item.

## What works

A `Purchase Invoice Item` child row CAN omit `item_code` if you set:

- `item_name` (string ≤ 140 chars; ERPNext requires *something* here)
- `description`
- `qty` (typically 1)
- `rate`
- `expense_account` (a non-group leaf Account in the right company, root_type Expense / Asset / Liability)
- `uom` (set to `"Nos"` if you don't have a better default)
- `is_stock_item = 0` (defensive — keeps stock-related defaults from firing)

Set `pi.update_stock = 0` on the parent unless any other row is a stock item.

## What doesn't work

- Leaving both `item_code` AND `expense_account` blank → ERPNext throws "Expense account required for row N".
- Setting `item_code` to a placeholder/dummy value to dodge the rule → fragile, and the row ends up with whatever default expense account the dummy item has, which is rarely what you want.
- Trying to post via Journal Entry instead → loses the supplier-level reporting that Purchase Invoice gives you (AP aging, supplier ledger, payment matching).

## Snippet (Python)

```python
pi = frappe.new_doc("Purchase Invoice")
pi.supplier = supplier
pi.bill_no = bill_no
pi.posting_date = posting_date

# Account row (no item)
pi.append("items", {
    "item_name": (description or account_name)[:140],
    "description": description,
    "qty": 1,
    "rate": amount,
    "expense_account": account,
    "uom": "Nos",
    "is_stock_item": 0,
})

pi.update_stock = 0
pi.insert()
pi.submit()
```

## Caveats

- **Tax category** on item-less rows: ERPNext applies the header tax template fine; per-row item-tax templates are ignored (no item, no item-tax mapping). For mixed tax rates, use the row's tax-template lookup OR a header template that handles your common case.
- **Multi-currency**: still fully supported; the row's `rate` is in document currency, conversion happens at the header level via `conversion_rate`.
