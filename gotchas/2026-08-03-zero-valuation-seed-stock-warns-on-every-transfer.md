# Stock seeded at valuation rate 0 makes every later transfer warn — re-value it, don't tick "Allow Zero Valuation Rate"

**Date:** 2026-08-03
**Domain:** ERPNext / stock
**Severity:** annoying (looks like a day-killer to the user — it isn't)

## Symptom

Users transferring stock between warehouses see a stack of orange banners, one per row:

```
Row #1: Item VIR663JUL25 has zero rate but 'Allow Zero Valuation Rate' is not enabled.
Row #2: Item VIR674AUG25 has zero rate but 'Allow Zero Valuation Rate' is not enabled.
```

Russell reported this as "found the error, when trying to receive a transfer". It is
**not** an error. The Stock Entry submits, `docstatus = 1`, and the stock moves. Verify
before diagnosing: check the Bin quantities and the Stock Entry docstatus first.

Confusingly, the Item records *do* carry a cost — `Item.valuation_rate` on the affected
items was R1,951.74, R1,211.96, R298.91. Only the stock ledger was at zero.

## Cause

The stock was created by a bulk seed load — a Stock Reconciliation (`MAT-RECO-2026-00096`,
14 Jul) that booked 20 units of ~2,200 items with `valuation_rate = 0`.

**`Item.valuation_rate` is only a default for future receipts.** Once a Stock Ledger Entry
exists, the Bin's valuation comes from the ledger, not the Item. So every subsequent
movement of that stock inherits the zero and warns, forever.

Two upstream sources of zero-valued stock on a Frappe/ERPNext site with a Sage bridge:

1. a hand-built seed/reconciliation that omits `valuation_rate` (this case), and
2. `get-inventory-qtyonhand-for-erpnext`, which *does* set `valuation_rate` from Sage's
   `averageCost` — so if Sage reports 0, the recon books 0 and you get the same result.

## Fix

Re-value the existing stock from each Item's own cost, in batched Stock Reconciliations:

```python
bins = frappe.get_all(
    "Bin",
    filters={"warehouse": ["in", warehouses], "actual_qty": [">", 0], "valuation_rate": 0},
    fields=["item_code", "warehouse", "actual_qty"],
    limit_page_length=0,
)
# per bin: look up Item.valuation_rate; skip disabled / non-stock / zero-cost items
# then submit in chunks of 25 with qty = current actual_qty and the item's rate
```

Chunk at 25 and commit per batch — same lock-contention lesson as the QOH sync
(`2026-07-28`). 2,162 of 2,177 bins fixed; the 15 that remained had no cost on the Item
either, which is the correct outcome — they need a real cost, not a fake one.

**Do not "fix" this by setting `allow_zero_valuation_rate = 1` on the transfer rows.**
That silences the warning and permanently bakes zero-cost stock into the ledger, so COGS
and stock value stay wrong. The warning is doing its job.

## Why this is non-obvious

- **It presents as a blocking error but isn't.** Orange banner, several of them, right at
  the moment a user is trying to finish a task. The instinct is to make the message go
  away. Check `docstatus` and the Bin first — we nearly "fixed" a working transfer.
- **The Item shows a cost**, so `Item.valuation_rate` looks fine and you go hunting in
  the wrong place. The distinction between the Item default and the ledger valuation is
  the whole bug.
- **`allow_zero_valuation_rate` is right there** and makes the symptom vanish in one
  tick. It is the wrong fix and it is not reversible in the ledger.
- The real question is always *which voucher created this stock* — trace it with a Stock
  Ledger Entry query on the item, ordered by `posting_date asc`. The first row names the
  culprit.

## See also

- `gotchas/2026-07-28-*` (Sage QOH sync: lock timeouts, chunking, disabled items)
- `sites/ardmore.md` — 2026-08-03 work log
