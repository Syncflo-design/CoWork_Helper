# Ardmore UAT: every block that isolates ERPNext from the three live Sage companies, and how to remove each one at go-live

**Date:** 2026-09-22 · **Site:** ardmoreceramics.c.frappe.cloud · **Area:** Sage bridge (Pharoh) / POS / stock · **Severity:** go-live blocker if forgotten

Russell (2026-09-22): trim UAT to 100 SKUs on one till, make sure every one of
them reaches the Sage TESTING company, and *"disconnect any touch point which
adds/edits/posts to Sage for the 3 other Sage instances"*. This file is the
register of what was put in place. **Work through the Go-live section in order
when he says the word.** Nothing here reverts on its own.

## What talks to Sage, and what each one does now (audit 2026-09-22)

| Script | Direction | Live companies? | State during UAT |
|---|---|---|---|
| `post-taxinvoice-to-sage` (Sales Invoice, After Submit) | writes | **locked to TEST** | `SAGE_FORCE_COMPANY = "Ardmore Ceramics TEST"` + hard check before the HTTP call + `FORCE_TAX_TYPE_ID` (TEST tax type 9990328 on every line) |
| `post_new_item_to_sage` (Item, After Insert, `custom_from_import`) | writes | **locked to TEST** (2026-09-22) | same constant filters the `Company Sage Integration` loop to TEST only |
| `post-salesorder-to-sage`, `post-purchase-order-to-sage`, `post-purchase-invoice-to-sage`, `post-purchase-invoice-return-to-sage`, `post-customerreturn-to-sage` | write | **no** | unchanged. They use the single `Sage Integration` login, and its API key **is the TEST company's key** (verified by comparing the stored secrets, temp script deleted). They cannot reach a live company as written. |
| `get-inventory-for-erpnext` (*/5), `get-inventory-qtyonhand-for-erpnext` (*/5), `get-pricelists-for-erpnext` (hourly), `get-additional-prices-for-erpnext` (nightly), `get-accounts-for-erpnext`, `get-suppliers-for-erpnext`, `get-purchaseorders-for-erpnext`, `get-categories-for-erpnext` | read only | yes (pull from all 4) | untouched: they write nothing into Sage. QOH sync only processes companies with `custom_default_warehouse` set, which is TEST alone. |
| `uat-push-items-to-sage-test` (API) | writes | **TEST only by construction** | temporary loader, now **disabled**. Enable, call, disable again to add more UAT items. |
| Importers (Kiln Sheet / Home Fashion) | via `post_new_item_to_sage` | covered by the lock | – |

`server_scripts` app on the bench holds no Sage code (grepped the local repo).

## The UAT data set (100 SKUs, one till)

- Till: **POS_Test2** (users testpos@mail.com, happiness@test.com, sharon@test.com), warehouse **POS Store - ACT**, price list *Ardmore Ceramics TEST - Retail*, Credit Card + Voucher, `hide_unavailable_items = 1` so only stocked items show.
- Items: 37 Ceramics, 33 Home, 30 Fashion, all with an image, a real retail price (none at R0.01) and range/colour/design/size/artist data. Full list: `sites/ardmore-uat-items-2026-09-22.md`.
- Each holds **20 in POS Store - ACT** (MAT-RECO-2026-00369 topped 8 of them up from 2) and **20 on hand in Sage TEST** (created via the loader, Sage TEST ids 102889457–102889626, recorded in `Sage Item Selection` with company = Ardmore Ceramics TEST). `custom_qty_pending_sage` unticked on all 100, so the 5-minute QOH sync now owns them: Main Distribution = Sage QOH − POS Store = 0.
- Everything else in the TEST company was zeroed: 64 Stock Reconciliations MAT-RECO-2026-00368, 00370–00431 (6,375 bins in POS Store - ACT plus the four fabrics in Main Distribution / Online Store). Cheri's four fabrics (FABCBBR/PI/PU/TU) still show 249/250 in Sage TEST, so they were flagged `custom_qty_pending_sage = 1` to stop the sync writing that back.
- Proof: ACC-SINV-2026-00053 (CARBOX7 × 1) → Sage TEST order 3551608852 / **INV0000032**, status Synced, seconds after submit. Next QOH sync left Main Distribution at 0 and no reconciliation was generated, i.e. the stock leak of 2026-09-21 is closed for the UAT set.

## Things learned on the way

- **Item creation and the inventory pull race.** The */5 `get-inventory-for-erpnext` ran while the loader was inserting `Sage Item Selection` rows and logged `Duplicate entry ... for key 'PRIMARY'` for ~10 items. Harmless (the rows exist), but load items in one go and expect a burst of those Error Logs.
- **Stock Reconciliation > 100 rows is queued**, not submitted inline (`docstatus` stays 0 until the background job runs). Batches of 100 submit synchronously; a 12-batch call (1,200 rows) was enough to time out the MCP client while the server carried on. 8–10 batches per call is the sweet spot.
- Items store the **live** Sage tax type ids (4849096 / 2704020 / 5698238). The TEST company only knows 9990328. Hence `FORCE_TAX_TYPE_ID` while locked.
- The three Pharoh pushes ran in parallel and one got a 502 from the Frappe Cloud gateway; the server had finished the batch anyway. Always re-check `Sage Item Selection` before re-running a loader batch.

## Go-live: remove the blocks in this order

1. **Categories first.** `custom_category` decides which Sage company a sale posts to once the lock is off. Several UAT cushions and napkins sit under *Ceramics* (e.g. CUSHFRGV, CUSHMBFV, NAPTSMPL) and their Type/Design fields are default junk ("Butter Dishes", "Monkey Weights"). Fix the data before step 2 or sales will post to the wrong Sage company.
2. `post-taxinvoice-to-sage`: set `SAGE_FORCE_COMPANY = ""`. `FORCE_TAX_TYPE_ID` becomes 0 automatically and the item's own tax type is used again.
3. `post_new_item_to_sage`: set `SAGE_FORCE_COMPANY = ""` so new items are created in all four Sage companies again.
4. `Company Sage Integration` Home / Ceramics / Fashion: fill `sage_pos_customer_id` + `sage_pos_customer_name` (TEST uses 66381317 "CASH01 - Speedpoint Sales"). Without these every live till sale fails at the Sage step.
5. Decide what the five single-login scripts (sales order, purchase order, purchase invoice, supplier return, customer return) should do. Today they all post to the TEST company because that is the login on `Sage Integration`. Either repoint that record or rewrite them to resolve `Company Sage Integration` by `doc.company` / item category. Till returns are still not sent at all (`is_return and is_pos` is skipped) — separate job.
6. Delete `uat-push-items-to-sage-test`.
7. Stock: the TEST company data is disposable. For the live companies set `custom_default_warehouse` on each `Company Sage Integration` so the QOH sync starts feeding them, and untick `custom_qty_pending_sage` only on items whose Sage quantity is authoritative.
8. Update `sites/ardmore.md` and the memory note `ardmore-sage-test-only-lock` to say the lock is off.

## See also

- `gotchas/2026-09-21-pos-sales-never-reached-sage-stock-leak.md` (why the lock exists, POS = Sales Invoice mode)
- `gotchas/2026-07-28-*` (post-new-item-to-sage duplicates an existing Sage item — the loader checks `Sage Item Selection` first for exactly that reason)
- `sites/ardmore-uat-items-2026-09-22.md`
