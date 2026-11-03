# Ardmore first live stock pull: one bad line fails a whole batch; Pharoh ID lookup caps below 25 codes

**Date:** 2026-11-01 · **Site:** ardmoreceramics.c.frappe.cloud · **Area:** Sage QOH sync / count loader / Pharoh · **Severity:** blocks a first pull until fixed

## What bit us

1. **Half units in Sage.** Sage Home held 153.5 napkins, 28.5 placemat pairs, etc. on items whose
   ERPNext UOM is `each` (Must be Whole Number). One such line made its whole 25-line Stock
   Reconciliation fail ("Quantity (1.5) cannot be a fraction"), taking 24 good items with it:
   350 of 1,320 Home lines missing after the first run.
2. **Negative Sage average cost.** An item with no `custom_item_cost` fell back to Sage's
   `averageCost`, which was negative: "Negative Valuation Rate is not allowed", whole batch failed.
3. **Pharoh `get-item-selectionid-for-erpnext` returns nothing for 25+ codes per call** (works at
   10, fails at 25) and still reports a "complete" answer, so the count loader's align listed 450
   real Home items as "not in Sage". Nothing was changed (align never deletes), but it looks alarming.

## Fixes (live, in Server Scripts)

- `get-inventory-qtyonhand-for-erpnext`: a fractional Sage quantity on a whole-number UOM is
  rounded DOWN (Russell: only fabrics, in Meter, take decimals; everything else is integers), and a
  negative valuation goes in at 0.
- 7 fabrics set up as `each` (FABCDOD, FABDRALON14/34/44/60/64/77) changed to `Meter` before they
  had stock (UOM cannot change once stock exists); FABCDOD's retail price uom changed to Meter too.
- `ardmore-count-load` align: 10 codes per Pharoh call.

## Result

Home 1,301/1,320 match (rest = 16 negative in Sage, 3 disabled), Fashion 192/192, Ceramics
1,819/1,883 (rest = 58 disabled SAMPLE/DISPLAY, 2 negative, 4 ACF/ codes not in ERPNext). Compared
with a fresh Pharoh pull per company (temporary API script `tmp-compare-sage-stock`).

## Lesson

Before switching a company's stock sync on, look for fractional quantities on whole-number UOMs
and negative average costs in Sage; and never trust a Pharoh batch lookup without testing the batch
size it actually handles.
