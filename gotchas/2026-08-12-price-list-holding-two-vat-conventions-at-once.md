# One price list, two VAT conventions — the till charging 15% wrong depending on who wrote last

**Date:** 2026-08-12
**Domain:** ERPNext / pricing / Sage integration
**Severity:** day-killer — this is real money, in both directions

## Symptom

Two identical Pangolin Teapots priced differently, and no obvious reason:

| Item | Item Price on the retail list | Item's Incl field | What it is |
|---|---|---|---|
| `MBU542AUG25R` | 17,808.70 | 20,480.01 | the **ex**-VAT figure |
| `QQKHU366AUG26` | 17,000 | 17,000 | the **incl**-VAT figure |

**2,114 items** had an Item Price that disagreed with their own incl-VAT field.

## Cause

Two processes write to the same price lists on different bases:

* **The Sage price sync** (`get-additional-prices-for-erpnext`) copies Sage's
  `priceListRate` straight through, with no VAT arithmetic. Sage sends **ex-VAT**.
* **The kiln / Home-Fashion importers** write `retail_incl` to the same list. That is
  **incl-VAT**.

So an item's price depended on which process touched it last, and the two differ by 15%.

Worse, the till was adding VAT on top: every VAT template except Ardmore's had
**"Is this Tax included in Basic Rate?" switched off**. A price list rate of 17,000 rang up
as 19,550 — which is also why round shelf prices never rang as round numbers.

## Fix

Ardmore price goods **including VAT, in round numbers**, and the till must ring exactly
that. Working backwards from there:

1. **`included_in_print_rate` = 1 on every company's VAT template.** The price list rate
   becomes the incl figure and VAT is extracted from within it. 17,000 rings as 17,000.
2. **Gross the Sage sync up by 1.15** as it writes, so its ex-VAT figures land on the same
   basis.
3. **The sheet price wins.** A `custom_from_sheet` flag on Item Price, stamped by both
   importers; the nightly sync skips any row carrying it and only fills gaps.

Order matters. Step 3 before step 1 would have **locked the overcharge in permanently** —
the sync was the only thing correcting those prices, and switching precedence first removes
the correction while leaving the cause.

## Why this is non-obvious

- Each process is individually correct. Neither has a bug. The fault only exists in the
  overlap, which no single script can see.
- The ex/incl distinction is invisible in the data — both are just numbers on an Item Price
  row. The only tell is `rate * 1.15 == the other figure`, and you have to think to check it.
- **`Retail Price Excl Vat` on the Item form was a decoy.** The visible field was ERPNext's
  `standard_rate`, relabelled and always R0.00; the populated custom field of the same name
  was hidden. Two fields, one label, and the wrong one on screen — which sent the
  investigation the wrong way twice.
- `standard_rate` must stay empty: filling it writes an Item Price to **Standard Selling**,
  which is disabled here, and the item then refuses to save (the 2026-07-28 bug).

## The mistake worth not repeating

Faced with excl and incl disagreeing on 116 items, the assumption was "incl is live, derive
excl from it" — and 116 pre-existing values were overwritten with `db.set_value`, which
writes no Version. They were unrecoverable. **The sheet was the authority all along, and a
snapshot would have cost nothing.**

## See also

- `gotchas/2026-08-12-db-set-value-skips-the-hooks-that-make-a-change-real.md`
- `sites/ardmore.md` — 2026-08-12 work log
