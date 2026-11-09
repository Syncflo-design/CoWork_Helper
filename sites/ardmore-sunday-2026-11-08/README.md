# Ardmore: Sunday 8 Nov 2026 step list

Russell calls every step. Nothing here runs by itself and nothing has been applied. Pharoh is the other machine's job; this covers the Ardmore instance only.

Everything in this folder is offline. `patched/` holds the changed copies of the Live scripts, made from a copy taken on 6 Nov. Before applying anything, take a fresh copy and rerun `make_patched.py`: an anchor that no longer matches means someone changed that script, so stop and look.

## Steps, in order

Each step is applied on his word, then checked before the next one.

1. **Fresh copy of all Server and Client Scripts.** This is the rollback for everything below.
2. **Switch-on (the 3 Nov work).**
   - Enable: `pos-pool-items`, `pos-pool-stock`, `Sales Invoice - Online Auto Transfer`, `POS Sell From Several Warehouses`, `POS Customer UX v4`, `POS Order Number`.
   - Disable: `POS Customer UX`, `sage-home-backfill`, `tmp-home-backfill`.
   - Rollback: reverse each one.
3. **Tills read Sage Home.** This must come before any Ceramics wholesale goes to Sage.
   - Patch `get-inventory-for-erpnext` and `sync-home-retail-prices`.
   - Run `sync-home-retail-prices` once.
   - Set POS Profile Online `selling_price_list` to `Home - Retail Price` (Hyde Park is already on it).
   - Rollback: set Online back to `Ardmore - Retail`, restore the two scripts.
4. **Sales Other.**
   - Create the Company Sage Integration fields in `custom_fields.json`, `sage-accounts-for-company`, the company picker script, `pos-sales-other-setup` and `Sales Invoice - Sales Other`.
   - Patch `post-taxinvoice-to-sage`, `post-customerreturn-to-sage`, `post-intercompany-sale-to-sage`, `POS Cart Quantity` and `POS Return Item Picker`.
   - Create `POS Sales Other` last. It is the switch: without it, no such line can exist.
   - Russell picks each company's account on the company screen. Fashion has no "Sales - Other" (read from Sage on 6 Nov). Exact matches: Home 2468754, Ceramics 20051653.
   - Rollback: disable `POS Sales Other`, then restore the patched scripts.
5. **Kiln import.**
   - Create the Item fields in `custom_fields.json` and `post-pending-items-to-sage` (cron `*/5 * * * *`).
   - Replace `post_new_item_to_sage`.
   - Patch both importers.
   - `PHAROH_READY` stays 0 until step 7, so new items post to Sage as they do today, only in batches of 25.
   - Rollback: restore those scripts, disable the cron script.
6. **App deploy.** The two small changes below are NOT in the repos yet. Russell says when to make them, then pushes and runs a fresh Deploy.
7. **Once Pharoh is deployed and proven on Sage TEST:**
   - Set `PHAROH_READY = 1`.
   - Repair the 85 items of KSI-00018 from `data/ksi-00018-from-workbook.csv`: Item Category and wholesale in ERPNext, then status `Repair` so Sage gets category, wholesale and retail.
   - All 18 categories already exist as Item Groups, and no row has a blank price or category.

## Deploy changes, not yet made

**`nest_stock_request/api.py`, `_end_of_day_rows`:** show Sales Other lines in Notes. Goes in with 0.7.0, which is still uncommitted.

**`nest_sales_history/api.py`, `_sage_company`:** before `return doc.company`, return the POS Profile's `custom_sage_entity` if it has one. Bump to 0.1.5. Without this, an invoice holding only Sales Other reports under company "Ardmore".

## For Russell to decide on the day

- **Item screen Retail field.** The sync copies the Sage item price of the item's own company into `custom_retail_price_incl_vat` and `Ardmore - Retail`. For Ceramics items that figure is now wholesale. Tills no longer read it, but Nozy will see wholesale in that Retail box, as she already does on older Ceramics pieces. Not changed here.
- **What tests may post to live Sage.** Any sale on a real till posts there.
- **Quotes.** A quote holding a Sales Other line is unproven: a Quotation line probably needs an item code.

## Known limits

- A credit note can't mix Sales Other with stock lines, because ERPNext refuses it at submit. The return picker tells the cashier to do two.
- `data/online-no-home-price.csv`: 450 in-stock items with no Home price, so no price on either till. 68 are new pieces the refresh hadn't reached on 6 Nov; 35 of the older ones have an Online price today.
- `data/online-price-changes.csv`: 294 items whose Online price changes in step 3.
- The picker and the till button have only been syntax-checked. They need testing on the real screens.
- The patched importers and `post-pending-items-to-sage` have not been run. The first run needs a small sheet.

## Done on Sunday 8 Nov 2026 (applied on Live)

- Step 1: fresh copy of all scripts in `snapshot-2026-11-08/` (the rollback).
- Step 2: switch-on at 07:13, all nine changes.
- Step 3 (partly): Online till reads `Home - Retail Price` (07:22). The `get-inventory-for-erpnext` / `sync-home-retail-prices` patches are NOT applied: Home prices still refresh daily (05:00), so a newly imported piece has no till price until the next morning.
- Step 4: Sales Other installed 08:35, Home account 2468754; proven with a R1 sale + credit note (Sage JSSA27080 / CRN0002003). Ceramics and Fashion accounts left blank.
- Step 5 stage 1: Item fields, `post-pending-items-to-sage` (cron */5, PHAROH_READY = 0), new `post_new_item_to_sage` (queue only), both importers patched (09:45). Tested: kiln and Home/Fashion imports in rolled-back requests (new item queued Create, existing item category + wholesale updated and marked Update); the job's create call against Sage TEST only (SNE324NOV26, SelectionID 103990823, rolled back in ERPNext).
- Step 6: nest_stock_request 0.7.1 and nest_sales_history 0.1.5 deployed. 0.7.2 (count sheet on-hand, ticket 0150) built, not pushed.
- Step 7: waits for Pharoh. NOTE before switching it on: the 85 KSI-00018 items have Home and Ceramics links but no Fashion link in ERPNext, and the Repair path only calls update-item-in-sage (404 where the item is missing), so the repair must create them in Fashion where Sage lacks them.
- Item cost (11:00): the job sends the sheet's Item Cost as LastCost (was last_purchase_rate, always 0). Sage TEST shows Pharoh's create ignores it and writes PriceExclusive as the opening cost (GM175NOV26: sent 472.83, Sage 1391.30): Pharoh fix handed to Russell.
- Stock added to EXISTING Home/Fashion items now reaches Sage (11:33): new Item field `custom_sage_adjust_qty`; the importer adds the sheet qty to it; `post-pending-items-to-sage` sends it after the creates through Pharoh `post-item-adjustment-to-sage` (body `{credentials, adjustment: {id 0, date, itemID, averageCost, quantity, reason, created}}`) to the item's own Sage company at the sheet's Item Cost, then clears the field and unticks "Qty Added Locally". Sage takes the adjustment cost as the new average (2 @ 100 then 2 @ 200 gave 200); Russell chose to send the sheet cost. Tested: rolled-back import of TEAPPA + the job section against Sage TEST only (NX550NOV26R now qty 6, avg 90 in Sage TEST). Live scripts byte-match `patched/` and `server/`.
- Pharoh report (11:37): adjustment throttle returns 200 + success false until Pharoh's next deploy; the job now treats errorMessage "rate-limit"/"pacing limit" as stop-and-retry.
- New items' cost (11:41): Pharoh confirmed Sage costs a create with qty > 0 from the selling price and Pharoh will not correct it. The job now creates every new item with QuantityOnHand 0; when its own company's create is new (not alreadyExisted) the opening qty goes into `custom_sage_adjust_qty`, and the same run re-reads the queue and sends it as an adjustment at the sheet's Item Cost. Tested on Sage TEST, rolled back in ERPNext: ZZCOST0811A (opening 2, cost 40) -> Sage TEST qty 2, avg 40, status Done. Live `post-pending-items-to-sage` byte-matches `server/` (13245 chars).
- STAGE 2 ON (11:49): PHAROH_READY = 1. Repair now uses the create path (create where Sage lacks the item, e.g. Fashion; alreadyExisted -> update with category + wholesale + retail) and records Sage Item Selection rows; Update treats a 404 as "not in that company"; a 503 part-way through an own-company create still queues the opening qty. Tested first on Sage TEST with the flag on in a rolled-back copy: new ZZCAT0811B (category created, 605949/605950 saved, qty 2 @ 40 by adjustment) and NX550NOV26R as Repair (category set, both lists saved, qty 6 / avg 90 untouched). Live byte-matches `server/` (14179 chars).
- KSI-00018 repair queued (11:50): 85 items set to Repair with item_group = sheet Type and wholesale (incl + ex) from the sheet (71 had none). All 85 are Ceramics, linked in Sage Home + Ceramics, none in Fashion.
- NOTE: the TEST company's inventory sync still imports new Sage TEST items into ERPNext (custom_category "Ardmore Ceramics TEST"). Test items ZZCOST0811A (deleted) and ZZCAT0811B came back that way.
- nesterp tickets (12:08): visible notes (no email) posted on 0128, 0129, 0137, 0148, 0150 saying what is done and what is outstanding; statuses unchanged.
- nesterp Server Script "Email Queue - shared till logins" (12:12, Email Queue Before Insert): mail addressed to hdsqpos@ardmore-design.com goes to the Hyde Park sales people instead (today only brittany@ardmore-design.com; Godin Ndlovu and Leah Masoka have no email in Ardmore or Sage yet). Local copy server/nesterp-email-queue-shared-till-logins.py. Tested in rolled-back sendmail calls: hdsqpos swapped for Brittany, CC kept, body untouched, other mail untouched.
- REPLACED (12:24): the nesterp Email Queue redirect above was removed (with its API script and HD Customer field). Russell: replies go to the SELECTED sales rep only, and no list is kept by hand. Now: Ardmore fields Sales Person `custom_email` + POS Profile `custom_till_login` (Hyde Park = hdsqpos, Brittany's email filled), and nest_support 0.1.4 (uncommitted in C:\ClaudeCode\nest_support) asks a till login "Who is logging this?" and raises the ticket with that person's email. Needs push + fresh Deploy.
- Review fixes (12:37), Live byte-matches `server/` and `patched/` (job 14876, Home/Fashion 25681, Kiln 22191 chars): adjustment queue leaves out items waiting for Create or given up (they can no longer fill the batch); own counter `custom_sage_adjust_attempts`; opening qty committed as soon as Sage creates the item; selection-row failures and a bad Sage id are recorded, not fatal; Create with a category that is not Home/Fashion/Ceramics stops before any Sage call; re-imported wholesale is written without `custom_from_sheet` so the Sage price sync keeps owning it (new items are still stamped); import warnings for an unknown Item Category and a blank kiln wholesale. Tested on Sage TEST, rolled back in ERPNext. Not changed: `Ardmore - Retail` holds Ceramics wholesale after the repair (would need a price sync change; no reader found). nest_support 0.1.4 also only pre-fills this shift's till selection and lowercases emails.
- TEST company sync brings Sage TEST test items back into ERPNext for the day: ZZCOST0811A, ZZCAT0811B, ZZFIX0811C (custom_category "Ardmore Ceramics TEST"). Delete them after today.
- Review fixes (12:37, tested 12:40): job, both importers byte-match Live (job 14876, HFI 25681, Kiln 22191 chars). New Item field custom_sage_adjust_attempts. owed_stock() leaves out items waiting in Create or given up; opening qty committed as soon as owed; selection-row errors become item problems; blank/unknown category stops a Create before any Sage call. Re-imported wholesale written with custom_from_sheet 0. Tested with Pharoh stubbed and rolled back (ZZFIX1-4, TEAPPA, THO435NOV26). Read-back on live Sage: SMA503NOV26 and THO435NOV26 show category and retail own price in Home and Fashion, wholesale own price in Ceramics. nest_support 0.1.4 still needs push + fresh Deploy. Left as is on Russell's word: Ardmore - Retail holds Ceramics wholesale (price sync not touched).
