# Sage takes an item's cost from its selling price; three more Server Script traps

**Date:** 2026-11-08
**Where:** Ardmore, Pharoh `post-new-item-to-sage`, Frappe v16 Server Scripts

## Sage item cost

Creating a Sage item with a quantity above 0 ignores `LastCost` and `AverageCost`: Sage works the cost
out from the selling price. Create with quantity 0, then send `post-item-adjustment-to-sage` with the
quantity and cost.

The adjustment's `averageCost` replaces the item's average. It does not blend (2 at R100, then 2 at
R200, gave R200).

## Sage additional price lists

`get-additional-prices-for-erpnext` returns the VAT-inclusive price as `priceListRate`. Check any code
that multiplies it by 1.15.

## Server Script sandbox

- `datetime.strftime()` fails with `KeyError: '__import__'`. Use `frappe.utils.format_datetime`.
- `out["x"] += 1` is a SyntaxError. Write `out["x"] = out["x"] + 1`.
- `frappe.cache.set_value` fails with `'NoneType' object is not callable`.
