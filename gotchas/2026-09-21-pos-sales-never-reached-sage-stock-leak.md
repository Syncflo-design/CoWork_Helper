# Till sales never reached Sage, so the Sage QOH sync wrote every sold unit back into the main warehouse

**Date:** 2026-09-21 · **Site:** ardmoreceramics.c.frappe.cloud · **Area:** ERPNext v16 POS / Sage bridge · **Severity:** day-killer at go-live (caught in UAT)

## Symptom

Cheri (UAT, 16 Sept): sold 2 units from Online Store - ACT, closed the till.
Online dropped 150 -> 148 as expected, but one minute later **Main Distribution - ACT
rose 100 -> 102** (`MAT-RECO-2026-00367`, owner Administrator). Total stock on hand
unchanged after a sale.

## Cause

Two things combined:

1. `get-inventory-qtyonhand-for-erpnext` (cron */5) sets
   `default warehouse qty = Sage quantityOnHand - sum(other warehouses)`.
   It is only correct if Sage knows about every sale.
2. Sage never heard about till sales. `post-taxinvoice-to-sage` had
   `elif doc.get("is_pos"): pass  # reach Sage via the day-end consolidated invoice`
   — but the day-end consolidated Sales Invoice is ALSO `is_pos = 1`, so it hit the
   same skip. All 8 consolidated invoices since 3 Sept had blank `custom_sage_order_id`.

Also: with POS Settings > Invoice Type = "POS Invoice", stock only posts when the till
is CLOSED (consolidation creates the Sales Invoice that writes the Stock Ledger), which
is why Cheri saw no movement until closing.

## Fix (2026-09-21, Russell's decision: NOT optional for Ardmore)

1. **POS Settings > Invoice Type = "Sales Invoice".** Each till sale is a real tax
   invoice (`ACC-SINV-…`, `is_pos=1`, `is_consolidated=0`), stock posts immediately,
   no day-end consolidation. ERPNext refuses the switch while a POS Opening Entry is
   open — close tills first.
2. **`post-taxinvoice-to-sage`**: till sales now sync; only legacy consolidated
   invoices and returns are skipped. `soft_fail` for `is_pos`: log + status "Failed",
   never block or roll back a sale. Inside the try, `raise Exception(...)` instead of
   `frappe.throw(...)` — frappe.throw queues its popup even when caught, and the cashier
   saw "No Sage SelectionID…" after a successful sale.
3. **Till Client Scripts:** the till's hidden form is now a *Sales Invoice*, so scripts
   on POS Invoice stopped loading. `Client Script.dt` is set-once (CannotChangeConstantError),
   so a new `POS Till Scripts Loader` (dt Sales Invoice) evals
   `frappe.get_meta('POS Invoice').__custom_js`. One copy of each script. Guard the
   loader on `#page-point-of-sale`, NOT `frappe.get_route()` (nest_home's landing
   redirect reports "nest-home" while the till boots).
4. Custom Fields `custom_voucher_ref` + `custom_sales_representative` added to Sales
   Invoice; Print Format `Ardmore POS Receipt` re-pointed to Sales Invoice
   (its doc_type IS editable).

Tested as happiness@test.com: ACC-SINV-2026-00049 (split voucher/card, stock 143->138
instantly), -00050, return -00051 via the item picker, closing POS-CLO-2026-00067
(lists Sales Invoice Transactions, prefill + one-click still work).

## TEST-ONLY LOCK (in force from 2026-09-21 until Russell says otherwise)

`post-taxinvoice-to-sage` has `SAGE_FORCE_COMPANY = "Ardmore Ceramics TEST"` at the top.
Every tax invoice (till or back office, any ERPNext company, any item category) posts to
the Sage TESTING company using that integration's credentials, POS customer and the
item's TEST `Sage Item Selection`. A second check right before `make_post_request`
raises if the resolved integration is anything else. Items with no TEST selection ID
are flagged "Failed", never sent elsewhere. It is the ONLY enabled script that calls the
tax-invoice endpoint (`post-pos-sales-invoice-to-sage` and `post-taxinvoice-to-sage-pos.py`
are disabled and on POS Invoice, which the till no longer creates).
**Go-live:** set `SAGE_FORCE_COMPANY = ""` -> routing returns to the item's ERPNext
Category; the Home / Ceramics / Fashion integrations then each need a `sage_pos_customer_id`.
Proved 2026-09-21: ACC-SINV-2026-00052 (1 x FABCBBR, R4500) -> Sage order 3550467502,
document INV0000031, status Synced, no popup at the till.

## Still open

- Home / Ceramics / Fashion `Company Sage Integration` records have no
  `sage_pos_customer_id` - needed before the TEST-only lock is lifted. Many TEST-stock
  items (the NF… ceramics seed, FABCBBLUE) have no TEST `Sage Item Selection`, so they
  flag "Failed"; Cheri's imported fabrics (FABCBBR/PI/PU/TU) do have one.
- **Till RETURNS still do not reach Sage.** `post-customerreturn-to-sage` skips
  `is_return and is_pos`, and cannot simply be un-skipped: it uses the single
  `Sage Integration` doc, the customer's own `custom_sage_customer_id` (walk-ins have
  none) and `Item.custom_sage_selection_id`, not the per-category grouping the invoice
  script uses. Needs a rewrite mirroring the invoice script + a real Sage test. Until
  then a returned unit is +1 in ERPNext, unknown to Sage, and the QOH sync will
  subtract it from the main warehouse.
- No retry job for "Failed" till invoices (Server Scripts cannot share code; would be
  a Scheduler Event duplicating the post logic).
- The Sage error log stores the payload including the Sage login password.

## See also

- `gotchas/2026-07-20-sage-return-script-blocks-pos-closing.md` (asymmetric guard)
- `gotchas/2026-09-07-pos-invoice-client-scripts-run-inside-pos-page.md`
