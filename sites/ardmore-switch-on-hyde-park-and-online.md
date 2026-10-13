# Ardmore: switching on Hyde Park (Joburg till) and the online tills only

**Date:** 2026-10-13 · Site `ardmoreceramics.c.frappe.cloud` · Status: planning, nothing changed yet.
Facts below were read off the live site on 2026-10-13. Re-check before acting.

> **Structure agreed with Russell on 2026-10-13 (supersedes sections 1-3 below):** everything
> under ERPNext company **Ardmore**. `Main - A` = "Ardmore Main Distribution", the single
> warehouse all stock moves through and where the Sage on-hand of all three Sage companies
> lands. One till + one warehouse per store: Hyde Park (`HDSQ - A`, re-enable), Online (new
> `Online - A`, replaces OL_C/OL_F/OL_H), later Airport (`AORT - A`) and Caversham (`ACA - A`).
> Stock reaches a store only by Stock Transfer from Main - A. Sale recorded once under Ardmore,
> then split by item category into tax invoices for Sage Home / Ceramics / Fashion.
> Price list decision parked until Russell's Ardmore meeting on 2026-10-14. The client-facing
> plan is `S:\Ardmore\Ardmore Go-Live Plan - Hyde Park and Online.docx` (v0.3, builder
> `_uatdoc\build_golive_plan.js`); Appendix A there is the technical checklist for this model.
> Next deliverable after approval: a task-list guide for users for the switch-on.

## 1. What "one till" means

| | Hyde Park | Online |
|---|---|---|
| POS Profile | `Joburg` | `OL_H`, `OL_C`, `OL_F` (one per company) |
| Company | Home | Home / Ceramics / Fashion |
| Warehouse | `HDSQ - H` | `ONL - H`, `ONL - C`, `ONL - F` |
| Users | `hdsqpos@ardmore-design.com` (Role Profile POS Manager - Joburg) | `ol_h@`, `ol_c@`, `ol_f@` (no role profile, never logged in) |
| Cash-sale customer | CASH01 - Speedpoint Sales | none set |

Airport (`AORT - H`) and Caversham (`ACA - C`) stay dark simply by not handing out logins.
Their stock stays in Sage's company totals and, in ERPNext, sits in the company's main
warehouse until those stores are counted in.

**The Sage link is per company, not per store.** A till sale is split by item category:
Home lines -> Sage Home, Ceramics lines -> Sage Ceramics, Fashion lines -> Sage Fashion.
Hyde Park sells all three categories, so all three Sage companies go live on day one.

## 2. Stock model the client has to understand

- Sage holds ONE on-hand figure per item per company. It does not know stores.
- ERPNext holds the figure per warehouse. The QOH sync (`get-inventory-qtyonhand-for-erpnext`,
  every 5 min) sets each company's **default warehouse** = Sage on-hand minus what is in the
  company's other warehouses, never below 0.
- So a store's stock is whatever has been **counted or transferred into that store's
  warehouse**. The sync never invents store stock, and it never takes it away.
- A till sells only what is in its own warehouse (`hide_unavailable_items` on Joburg).
- A sale posts to Sage within a minute; the next sync lowers the company warehouse
  accordingly. A return raises it again (credit note in Sage since 2026-09-29).
- Daily rhythm: open the till, sell, close the till. Unclosed tills block the next day.

### Opening stock for Hyde Park
1. Physical count at Hyde Park.
2. Stock Reconciliation into `HDSQ - H` (all categories, one document; the tile exists on
   the Stock Controller screen). Valuation = item cost.
3. The sync balances the remainder into each company's default warehouse.
4. From then on stock reaches Hyde Park only by Stock Transfer (Issued -> Received) from
   the company warehouse. Physically moving stock without a transfer = till cannot sell it.

### Opening stock for Online
Same, into `ONL - H` / `ONL - C` / `ONL - F`. Note the ceramics/fashion/home split: an online
ceramics order must come out of `ONL - C`, so each online till only sells its own company's
items unless the cross-company fix in 3.3 is applied and one online profile is used.

## 3. Gaps found on the live site (must be fixed before switch-on)

### 3.1 Company Sage Integration (Home, Ceramics, Fashion)
All three are missing, as of 2026-10-13:
- `custom_default_warehouse` (blank -> the QOH sync skips the company entirely). Proposed:
  `Main - H`, `Kiln Sheet - C` or `Hub - C` (client to say which is the real stockroom),
  `Main - F`.
- `sage_pos_customer_id` / `sage_pos_customer_name` (the cash-sale customer in that Sage
  company). Without it every till sale posts as Failed.
- `custom_sage_pos_sales_rep_id` (0). Without it every return posts as Failed.
TEST has all of these (customer 66381317, rep 740886, warehouse Main Distribution - ACT).

### 3.2 Joburg till configuration
- `selling_price_list` = **Standard Selling, which is disabled**. The 4,472 retail prices
  loaded on 2026-07-28 sit on that list; `Home - Retail Price` has no prices at all;
  `Ceramics - Retail` has 801 of 6,419 ceramics. Decision needed: one enabled retail list
  that covers everything Hyde Park sells (re-enable Standard Selling, or build one list the
  way `Ardmore Ceramics TEST - Retail` was built). Otherwise the till shows the R0.01 marker.
- `taxes_and_charges` = `South Africa Tax - A` (company Ardmore) on a Home-company till.
  Must be `South Africa Tax - H`.
- `write_off_account` = `Write Off - A`, `write_off_cost_center` = `Main - A`: wrong company.
  Must be `Write Off - H` / `Main - H`.
- `validate_stock_on_save` = 0 (the TEST till has 1). Set to 1 or the till will sell what
  is not there.
- Same checks on OL_H (write-off is `Temporary Opening - H`, price list Standard Selling),
  OL_C, OL_F.

### 3.3 Cross-company stock (code change in the QOH sync)
`other_whs` is built from `Warehouse.company == sage.company` only. Ceramics stock counted
into `HDSQ - H` (a Home warehouse) is therefore NOT subtracted from the Ceramics default
warehouse: ERPNext over-counts ceramics by exactly what Hyde Park holds, for ever. Fix: sum
Bins across **every** non-group warehouse except the default, regardless of company. One
line. Same applies to fashion at Hyde Park and to any online profile selling across
companies.

### 3.4 Items
- Sage ids per company (`Sage Item Selection`): Home 1,626, Ceramics 3,198 (of 6,419
  ceramics items), Fashion 233. An item without an id in its category's company sells on
  the till but Fails at Sage, is retried 8 times, then needs Send to Sage. Before go-live:
  list the items that will be counted into HDSQ/ONL and confirm each has an id in the right
  company; fix the rest in Sage or by category.
- Category decides the Sage company. 6 items still carry category `Ardmore Ceramics TEST`;
  spot-check Home/Ceramics/Fashion before the first live sale.
- `custom_qty_pending_sage` is set on the 100 UAT items (and others). Flagged items are
  skipped by the sync. Clear the flag on anything that will trade live once Sage holds the
  right figure.
- Fabric items are now in Meter (2026-09-30); Sage's unit on those items was not changed.

### 3.5 Scripts (the lock register, `gotchas/2026-09-22-ardmore-uat-sage-test-lock-register.md`)
- `post-taxinvoice-to-sage` and `post-customerreturn-to-sage`: `SAGE_FORCE_COMPANY = ""`,
  together, never one without the other. `FORCE_TAX_TYPE_ID` then falls back to the item's
  own tax type id.
- `post_new_item_to_sage`: remove the TEST-only company filter.
- `retry-failed-sage-sync`: `START_DATE` = go-live date so UAT leftovers never post live.
- `uat-push-items-to-sage-test`: delete.
- Leftovers to delete: `tmp-ft`, `tmp-sagedupes` (API scripts, owner unknown here).

### 3.6 Users and screens
- `hdsqpos@` has the POS Manager - Joburg layout (Open POS, POS Closing, Stock Transfer,
  Our Items, Sales Persons, Sales Invoices, Guides). Sales Persons for the Select POS User
  dropdown must exist for the Joburg profile.
- `ol_h@`, `ol_c@`, `ol_f@` have **no role profile**: no home layout, no till. Give them
  the Sales Assistant role (till + closing + Our Items) or a POS Manager profile.
- Passwords: the client sets them; never in a document.
- Receipt: `Ardmore POS Receipt` is on all profiles. Hyde Park's receipt printer and the
  Zebra label printer (Browser Print) are the store's to install.

### 3.7 Importers in live
`Main Distribution - ACT` exists only on TEST. The Home/Fashion and Kiln importers default
to it. For live, the target warehouse must be the company's default warehouse from 3.1 and
the importer defaults changed to match.

## 4. Order of work
1. Client decisions: default warehouse per company, retail price list for the till, cash-sale
   customer and rep per Sage company, physical count date.
2. 3.3 code fix, 3.2 till fixes, 3.1 integration fields, 3.6 users.
3. Item checks (3.4) on the counted list.
4. Lift the lock (3.5) at close of business, run one real sale and one return from Hyde Park,
   check both in Sage, then open the doors.
