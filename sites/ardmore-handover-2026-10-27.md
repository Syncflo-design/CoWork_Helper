# Ardmore: hand-over to the site laptop, 27 Oct 2026 (go-live Mon 2 Nov)

**For Sunday 1 Nov, use `sites/ardmore-golive-requirements-2026-11-01.md`** (requirements, decisions
and the step-by-step runbook, 31 Oct). This file is the history behind it.

Read this first on the laptop, then `sites/ardmore.md` (2026-10-21 to 27 entries) and the
lock register `gotchas/2026-09-22-ardmore-uat-sage-test-lock-register.md` (steps 1-11).

## Where we stopped

Russell: "let us be 100% certain of the stock movements between now and go live", then
"move this over to the other machine". The stock-movement sequence below was put to him;
he has NOT yet said "agreed". Re-confirm it with him first, one step at a time, numbered.

## Roadmap (Russell, 27 Oct)

1. Staff training on the testing profile, Sunday morning (company Ardmore Ceramics TEST; no Sage).
2. Upload the Hyde Park and JHB Holding counts (Caversham too if supplied), Sunday afternoon.
3. Switch testing off and go-live on, Sunday afternoon.
4. Transaction slate clean.

## Final testing this week: option 1

Real Hyde Park + Online tills and the Account Sale screen on company **Ardmore**, under the
TEST lock: everything posts to Sage TEST, the live entities cannot be reached, and it is
Monday's exact configuration. The training company is not touched. Russell wants it driven
through HIS Chrome (claude-in-chrome), selling items that have images, Hyde Park from
`HDSQ - A`, Online from `Main Distribution - A`. Open before starting: which login
(erpnext@ is not on the Hyde Park till's user list; hdsqpos / brittany@ / cheri@ are) - ask.
Test stock already in Main Distribution - A: FABCBBOR 41, FABCBMY 46, FABCBPOM 48, UAT-H01 /
UAT-C01 / UAT-F01 20 each (UAT-C01 now 19, one moved to HDSQ by MAT-STE-2026-00539).
**Final-testing stock loaded 27 Oct (laptop):** 25 UAT items (9 Ceramics, 8 Home, 8 Fashion; all
with image, live Ardmore - Retail price and a Sage TEST selection row) - MAT-STE-2026-00540
(Material Receipt, 40 each into Main Distribution - A) + MAT-STE-2026-00541 (transfer 20 each to
HDSQ - A, "already owned" ticked -> "Not needed (already owned)", count-load rehearsal). Result:
20 of each at Online and 20 at Hyde Park. Both are test documents: cancel Sunday with the rest.
Draft MAT-STE-2026-00530 (13 Oct) and ACA - A test stock (FABCBBOR 1, FABCBMY 4) also go Sunday.
UAT-* items exist only in ERPNext, not in Sage TEST, so a till sale of them FAILS at the Sage
step ("No Sage SelectionID") - sell the FABCB fabrics (they exist in Sage TEST) or create the
UAT items in Sage TEST first (the loader script for that was deleted; rebuild if needed).

## Final-test results (27 Oct, laptop, driven in Russell's Chrome as hdsqpos@)

- HYDE PARK PASSED. Sale ACC-SINV-2026-00079 (Kudu Nut Bowl = Ceramics, CUSHCCD50 = Home,
  SCAPPFL90 = Fashion; R10,636.00 incl) -> Sage TEST INV0000058, read back: 9,248.70 / 1,387.30 /
  10,636.00, every line to the cent, intercompany "Not needed" (Home store selling own stock).
  Partial return ACC-CRN-2026-00002 (Kudu only, R-4,536) -> CRN0000009, 3,944.35 / 591.65 /
  4,536.00. HDSQ stock 20 -> 19 -> 20 on the Kudu, 19 on the other two; Main Distribution untouched.
- Training point: after Complete Order, press **New Order** before opening Recent Orders. If the
  finished sale is still on screen, ERPNext v16 hides the order panel (toggle_recent_order_list
  skips order_summary when frm.docstatus == 1). Standard behaviour, not Ardmore's script.
- Recent Orders lists EVERY company's POS Invoices (the Sept training sales on Ardmore Ceramics
  TEST show on the Hyde Park till). Sunday's training sales will appear there too - the training
  company cleanup must remove them, or staff see them on Monday.
- Sage reports unitCost = 20 x selling price on TEST items: Sage uses its OWN item cost, not the
  valuation we send; the TEST items got a bad cost from the 22 Sep loader. TEST data only.
- Training clips (silent GIFs, Claude in Chrome recorder, no watermark) go to
  `\\SYNCFLO-DESKTOP\S_Drive_Claude\Ardmore\_uatdoc\till_clips` (share reachable from the laptop;
  also copied to the C:\S_Drive mirror).
  Done: 1 sale (ACC-SINV-2026-00080 -> INV0000059), 2 card + voucher (ACC-SINV-2026-00081 /
  00082 -> INV0000060 / 61, split R2,700 card + R1,000 voucher), 3 return (ACC-CRN-2026-00003,
  scarf off ACC-SINV-2026-00080 -> CRN0000010), 4 close the till (POS-CLO-2026-00084 for opening
  POS-OPE-2026-00087: expected = closing, card R15,200 + voucher R2,000 = R17,200; all test docs).
  Closing needs "Feet Through Door" (customer count) and Save submits it in one step.
  Hyde Park's session for 27 Oct is CLOSED - open the till again for more Hyde Park testing. `slow_gif.py` (same folder) sets the frame timing after export.
  Recorder facts: it keeps only the LAST 50 frames; every click, wait and type is a frame, a
  scaled screenshot is not; captions are generic ("Clicked", "wait"), not our action text. Start
  each recording with a wait so the opening screen is frame 0, and keep pauses to page changes.
- RE-RECORDED 27 Oct ~14:40 as hdsqpos@, each from Nest Home, with the sales person picked
  (old clips replaced): 1 sale ACC-SINV-2026-00085 (Leah -> INV0000064), 2 card+voucher 00086
  (Godin, voucher V1042, card auto-balanced -> INV0000065), 3 return ACC-CRN-2026-00004 (->
  CRN0000011 - NOTE: the return carries NO sales person), 4 close via the POS Closing tile
  POS-CLO-2026-00085 (card R12,636 + voucher R1,000), 5 stock request MAT-MR-2026-00008 (Kudu 5,
  Bonnie Pearl 3). All test docs for Sunday. Opened from the tile the autobalance and voucher
  prompt DO work. Training till POS-OPE-2026-00085 (POS_Test2, happiness@) has been open since
  6 Oct and shows in Hyde Park's closing picker - close it before Sunday's training.
- STOCK REQUEST FLOW (Russell 27 Oct: "leave it as is for now, as it works"): one request = one
  hop. Hyde Park requests from JHB Holding (Cheri issues, Britt receives). If JHB lacks it, Cheri
  first requests for JHB from Main Distribution (Nozy issues, Cheri receives) - two separate
  requests. Search already shows stock at every Ardmore warehouse. Caversham is not a source
  (manual Stock Transfer). A one-request-from-wherever-it-sits design was offered, not taken.
  Issuers: Nozy (Stock Controller, head office: all sources), Cheri (JHBM + Main Distribution;
  her Online layout already has Issue Stock + Stock Transfer). MAT-MR-2026-00008 (Hyde Park, sent
  while JHB was empty) is a test doc to close Sunday.
- STOCK FLOW CLIPS 27 Oct: 2 Cheri requests for JHB from Main Dist (MAT-MR-2026-00009, Kudu 5 +
  Bonnie Pearl 3), 3 Nozy issues (MAT-STE-2026-00542), 4 Cheri receives at JHB - stock moved, but
  the intercompany post FAILED: "AM748AUG26 has no price on Ceramics - Wholesale" (Ceramics-Home
  row prices from that list) and the receiver gets a red Sage popup. No auto-retry for intercompany.
  5 Cheri issues MAT-MR-2026-00008 to Hyde Park (MAT-STE-2026-00543), 6 Britt receives
  (intercompany "Not needed", Home -> Home). Flow clips complete.
- TILL FIXES 27 Oct (client scripts, live): voucher autobalance + voucher ref check the till's
  page element (visible) instead of the route; "POS No Submit Confirm" holds the savesubmit
  promise when the server refused the sale (no false "created successfully"); "POS Sales Person"
  REQUIRES a name before Checkout ("Sales person missing"). Tested on the Online till as Cheri
  (ACC-SINV-2026-00090 draft from the block test, 00091 sold with Cheri).
- MISSING WHOLESALE PRICE BLOCKS THE SALE (Russell 27 Oct): Server Script
  `block-sale-without-wholesale-price` (Sales Invoice, **Before Save**, acts only when docstatus 1 =
  submitting; "Before Submit" did NOT fire on this site). Same seller/owner rules as
  post-intercompany-sale-to-sage; throws "Wholesale price missing" listing the items. Proven on the
  Online till: Kudu -> blocked, ACC-SINV-2026-00089 stays Draft. BUT the till still shows a "created
  successfully" toast + summary behind the message - misleading for a cashier. Transfers: Server
  Script `block-transfer-without-wholesale-price` (Stock Entry, Before Save, every save - so a
  request is stopped at ISSUE, not at receive; skips "already owned" count loads and same-entity
  moves). Proven: Kudu Main Dist -> JHBM refused, nothing created. Before the block worked, two Online test sales went through
  (ACC-SINV-2026-00087, 00088 -> Sage TEST, intercompany Failed) - test docs for Sunday.
  Gap measured: of items with a retail price, Ceramics 10,054/10,308, Home 1,501/1,739, Fashion
  75/145 have no wholesale price. Jon's 26 Oct email: intercompany = Wholesale list, 15% off
  Ceramics + Home, Fashion just wholesale; nothing on missing prices.
- TILE COUNT BADGES live 27 Oct (nest_home 0.0.29 + nest_stock_request 0.2.1, deployed):
  Nest Home Tile.count_method; Issue Stock = nest_stock_request.api.issue_count (requests waiting
  for the user to issue), Request Stock = nest_stock_request.api.receive_count (stock on its way
  to the user's store). Proven: Cheri's Issue Stock shows 1 (MAT-MR-2026-00008).
- Till training points from the clips: the payment keypad enters CENTS (R1,000 = 1 0 0 0 0 0);
  keying a voucher does NOT reduce the card - delete the card to R0.00 and key the balance, and
  Remaining must read R0.00 before Complete Order (otherwise the till shows "Change").
- ACCOUNT SALE TEST 27 Oct (Nozy; Account Sale Settings roles + Stock Manager): ACACIA House,
  1 x CUSHCCDS from Main Distribution, R1,063.75 -> ACC-SINV-2026-00093 -> Sage TEST INV0000072
  (925.00 + 138.75) + intercompany Home -> TEST INV0000071 / SIV0000013 (547.83 cost, lock row).
  Read back exact. Test doc for Sunday.
- STOCK TRANSFER CLIP 27 Oct: Paul's `Stock Transfer` doctype (workflow Issued = draft ->
  Received = submit, makes the Stock Entry; role POS User A). Clip `ardmore-stock-transfer-1-issue`
  = Nozy, Main Distribution -> JHBM, 2 x CUSHCCD50, A_Main Distribution - A_JHBM - A_2026-10-27-0001
  (Issued). Receive at JHB = Cheri (POS User A). The Stock Transfer tile opens a NEW form, so a
  receiver has no direct way to the transfers waiting for them (only via the list).
  Part 2 `ardmore-stock-transfer-2-receive` = Cheri: Home -> tile -> list -> Actions -> Received;
  made MAT-STE-2026-00544, intercompany "Not needed" (Home -> Home). Tile now has a waiting badge:
  API Server Script `stock-transfer-receive-count` (method `stock_transfer_receive_count`) counts
  Issued transfers into the caller's stores (POS Profiles + Stock Request Settings, same rule as
  nest_stock_request); set as the tile's Count Method. Positive count not yet seen live.
- POS TAX INVOICE PRINT 27 Oct (`Ardmore POS Receipt`, checked on ACC-SINV-2026-00086): VAT is
  NOT printed (prices VAT-inclusive, Accounts Settings show_inclusive_tax_in_print = 0); lines show
  ex-VAT but Sub Total is incl., so the slip does not add up; no seller name / address / VAT number
  (letter head is the logo only); every store prints Ardmore Ceramic Art Studio although Hyde Park
  posts as Home. Minor: "Discount (0.0%) R0.00", blank Bill to, Payment Due Date.
  FIXED same evening: lines print VAT-inclusive price/amount; totals = Total excl. VAT + VAT 15% +
  Total incl. VAT (adds up); seller = the till's Sage entity (POS Profile custom_sage_entity, else
  warehouse, else company) -> name/address from the Address linked to that ERPNext Company, VAT no.
  from Company.tax_id; Served by (sales person); customer only when not the till's cash customer;
  discount/rounding/change rows only when non-zero; due date gone. Verified on 00086, CRN-00004,
  00092 and training 00068 (training shows the full seller block). **DATA STILL NEEDED: Ardmore
  Home's registered name, address and VAT number** (Company `Home` has no tax_id and no Address,
  so the slip prints just "Home"). The A4 `Ardmore Tax Invoice` (account sales) was NOT changed.
- TILL RECENT ORDERS 27 Oct (Client Script `POS Sales Person`): order summary shows "Sales person:"
  under Sold by; item name wraps, qty and amount stay on one line. Verified in the till as Cheri.
- TESTS 28 Oct (passed): Nozy issued A_Main Distribution - A_JHBM - A_2026-10-28-0001 -> Cheri's
  tile badge showed 1 -> received (MAT-STE-2026-00545) -> badge 0. Cheri returned 00092 on the
  Online till -> ACC-CRN-2026-00005 carries "Cheri Marshall", Synced to Sage TEST as CRN0000012,
  slip shows Served by. Found: a till left open overnight blocks the next day ("Outdated POS
  Opening Entry") - closed POS-OPE-2026-00089 as POS-CLO-2026-00086 (00087/00091/00092; 00088 was
  made by the admin login, so it is not on any closing). TRAINING POINT: close the till every day.
  Add to Sunday cleanup: the transfer + MAT-STE-2026-00545, ACC-CRN-2026-00005, POS-CLO-2026-00086.
- VAT SELECTOR BUILT 28 Oct (Russell: customer pays the full price at 0%). Tills whose POS Profile
  has "Zero-rated VAT Template" (Online, Airport, Online Store Test) show VAT 15% / VAT 0% on the
  cart's VAT line (Client Script `POS VAT Selector`). 0% = tax category `Zero Rated` + template
  `South Africa Zero Rated - A` (- ACT for training), item VAT cleared (Server Script
  `zero-rated-sale-vat`, Before Validate); new sale starts at 15%; a return keeps the sale's VAT and
  the selector is locked. Sage: sale + return scripts send Company Sage Integration
  `custom_sage_zero_tax_id` = Sage "Zero Rate Exports" (Home 690655, Ceramics 4849099, Fashion
  5698241, TEST 9990331; pulled via Pharoh SalesTaxSync). Intercompany unaffected (stays 15%).
  Tested: ACC-SINV-2026-00094 R1,500 VAT 0 -> Sage TEST INV0000073 (excl 1500, tax 0); return
  ACC-CRN-2026-00006 -> CRN0000013 (tax 0); slip prints VAT 0%. Loader `POS Till Scripts Loader` now
  fetches the till scripts fresh (cached meta hid the new script). **Each till needs avatar menu >
  Clear Cache once** to pick up the new loader.
- EXPORT PROOF BUILT 28 Oct: at VAT 0% the till shows "Flight no." + "Comment" boxes under the VAT
  line (Sales Invoice custom_export_flight_no / custom_export_comment); one is required on submit
  (Server Script zero-rated-sale-vat; message tells the cashier to use Edit Cart). Dispatch adds
  "Export Waybill No." (custom_export_waybill, allow on submit) on the invoice and clicks Update - no
  Sage re-post. Nest Home tile "Export Proof" (NEST-TILE-0011, on layout POS Manager - Online) opens
  the list (new tab; tile route max 140 chars, desk router mangles ?query so it must be a new tab)
  of Paid 0% sales with no flight no and no waybill; badge = API Server Script export-proof-count.
  Slip prints Flight No / Waybill No / Comment. Tested: ACC-SINV-2026-00095 blocked without details,
  completed with a comment (Sage TEST INV0000074, VAT 0), badge 1 -> Cheri added waybill -> badge 0,
  reprint shows it. NEST-TILE series counter was stuck (fixed: set to 10 via Document Naming
  Settings). Russell: "everyone needs to be able to print" - POS Manager + Sales Assistant got Print
  on Sales Invoice (Custom DocPerm; they had none, so the invoice screen had no Print button) and
  Sales Invoice default print format = Ardmore POS Receipt (Property Setter). Verified as Cheri.
  Test docs for Sunday cleanup: ACC-SINV-2026-00094/00095, ACC-CRN-2026-00006.
- SELLER DETAILS ON INVOICE + CN 28 Oct: Company Sage Integration got Registered Name, VAT Number,
  Postal Address, Physical Address (section at the end of the form). Ardmore POS Receipt now prints
  them for the till's Sage entity (Hyde Park/Online -> Home), postal + physical side by side like the
  Sage invoice. Home filled from Sage invoice JSSA26758 (ARDMORE HOME PTY LTD, VAT 4840257192, PO Box
  273 Nottingham Road 3280 / Unit 3 Hyde Square Centre ... Johannesburg 2196); TEST filled from its
  old address. Verified on ACC-CRN-2026-00004. **Ceramics + Fashion still empty** (need their Sage
  details). No Pharoh endpoint returns Sage company info (checked all known endpoints) - an automatic
  pull needs a new Pharoh endpoint (Sage Company/Get); until then the fields are typed once.
  Russell (28 Oct): he will add it to the Pharoh controller so it can be automated.
- TESTS 28 Oct (2): Hyde Park till - no VAT selector (correct), sale ACC-SINV-2026-00096 (Leah
  Masoka, 15%) -> Sage TEST INV0000075; return ACC-CRN-2026-00007 (Leah carried) -> CRN0000014.
  FOUND + FIXED: after Complete Order, ERPNext opened Recent Orders with the order summary hidden
  (no way to open/return a sale until reload) - Client Script "POS New Invoice From Recent Orders" v3
  forces the summary visible. Stock request Home button works (0.2.2 live). Draft checks (deleted):
  training 0% invoice = VAT 0; normal account invoice still 15%. Add to Sunday cleanup:
  ACC-SINV-2026-00096, ACC-CRN-2026-00007, Hyde Park opening entry of 28 Oct.
- TEST RECORD for users (28 Oct): https://claude.ai/artifact/E7yaewvefVAnvrTGxnG5nH (by login:
  Hyde Park hdsqpos@/Britt, Cheri, Nozy, behind the scenes, still to do). Russell shares it.
- CLIPS 28 Oct (share + mirror, 18 in all): ardmore-till-0-open-the-till (Hyde Park, opening + POS
  user), ardmore-till-5-vat-zero-export (Cheri, ACC-SINV-2026-00098), ardmore-till-6-export-waybill
  (Export Proof tile -> waybill DHL 9876543210 -> badge clears), ardmore-stock-4-jhb-receives
  RE-RECORDED clean (MAT-MR-2026-00010 / MAT-STE-2026-00546, CUSHCCD50 x2, Home -> Home, no Sage
  popup). FOUND + FIXED while recording: typing in the till's Flight no./Comment boxes also filled
  the item search (the POS barcode-scanner listener) - POS VAT Selector now stops key events on its
  boxes. Hyde Park 28 Oct session closed as POS-CLO-2026-00087, reopened in the clip. Sunday cleanup
  adds: ACC-SINV-2026-00098, MAT-MR-2026-00010, MAT-STE-2026-00546, POS-CLO-2026-00087 and today's
  Hyde Park + Online openings.
- GUIDES UPDATED 28 Oct (share + mirror): POS guide v1.5 (new Part 6 VAT 0% export + dispatch
  waybill, shots 40-42; sales person required; receipt contents + reprint; transfer tile badge and
  how to reach the list; Recent Orders glitch note removed; FAQ rows), Stock Requests v1.2 (tile
  counts, Home button), Getting Stock In v1.6 (transfer badge). render_check.ps1 now checks the
  Stock Requests guide instead of UAT Round 3. In-app help nest_help 0.0.9: open-pos, stock-transfer,
  sales-invoices updated + new export-proof.html - **needs Russell's push + fresh Deploy.**
- TWO LAPTOPS AT HYDE PARK (Britt, 28 Oct): both use the till login hdsqpos@ (simultaneous_sessions
  stays 2 - Russell; a 3rd login signs one out). One opening, one closing per day (close after both
  stop selling). Client Script `POS Sales Person` now keeps the picked name per browser in
  localStorage keyed by the POS Opening Entry: survives reload, clears on a new till day. Verified
  on hdsqpos@ / POS-OPE-2026-00092 (picked Leah, reloaded, still Leah; test choice cleared).
- LOCAL S: MIRROR REMOVED 28 Oct (Russell): C:\S_Drive, its subst and the Startup .cmd go. Checked
  first: nothing on it was missing from the share. All Ardmore documents and clips are on the share
  only (\\SYNCFLO-DESKTOP\S_Drive_Claude\Ardmore). Earlier "+ mirror" notes here are history.
- VAT SELECTOR (old note): was not built - Airport excl-VAT waits on Russell's price-basis answer; Airport is
  not in go-live.
- Temp read-back script `tmp-sage-test-readback` (API, System Manager only, read only) created
  for the tests - **DELETE it when final testing is done.**

## Go-live review 31 Oct (Russell: plan 1-5 confirmed "as written")

Russell's answers: live tests = Hyde Park sale, Online sale (15% + 0%), one intercompany stock
transfer, each with a return; I lift the lock on his word; test docs on Ardmore = cancel AND delete;
training sales deleted after training, logins/tills kept; Hyde Park + JHB counts come as a
spreadsheet; SO/PO/PI/non-till returns + Account Sale NOT used at go-live; wholesale prices not
loaded yet; fix simple gaps, report decisions.

FIXED + VERIFIED on Sage TEST:
- Discounts: sale + return scripts sent discountPercentage as 10 (Sage wants 0.10) - Sage booked
  1000% = a NEGATIVE invoice (ACC-SINV-2026-00099 -> INV0000077, -13,500). Now /100: 00100 ->
  INV0000078 and return ACC-CRN-2026-00008 -> CRN0000015 both 1,173.91 + 176.09 = 1,350.00.
- Online cross-entity sale (Fashion scarf from Main Distribution) + 1.5 m fabric: ACC-SINV-2026-00101
  -> INV0000080 (11,350.00, qty 1.5) + intercompany INV0000079 / SIV0000014 (3,438.50 wholesale).
- Intercompany transfer MD -> HDSQ: MAT-STE-2026-00547 -> INV0000081 / SIV0000015.
- QOH sync: a failed Stock Reconciliation batch no longer advances custom_last_qtyonhand_sync (those
  items would have stayed out of Main Distribution until they changed in Sage); zero-cost lines
  pass with allow_zero_valuation_rate instead of failing their batch of 25.
- Rep sync collapses spaces (Sage has "Kelly  Blakemore"); Sales Person "Kelly TBA" renamed
  "Kelly Blakemore", rep 77485.
- retry-failed-sage-sync START_DATE = 2026-11-01 (test-period docs never resent live).
- post_new_item_to_sage: after the lift, never creates items in the Sage TEST company.
- Disabled (not used at go-live, posted to the TEST login): post-salesorder-, post-purchase-order-,
  post-purchase-invoice-, post-purchase-invoice-return-to-sage.
Test docs from this review for Sunday: ACC-SINV-2026-00099/00100/00101, ACC-CRN-2026-00008,
MAT-STE-2026-00547.

OPEN (decisions / data):
- Home's Sage lacks most Ceramics items: of 289 Ceramics items WITH a wholesale price, 220 have no
  Home Sage Item Selection (Fashion 7/76, Home 20). Online sells them, then the Sage post fails
  silently AND the QOH sync puts the sold unit back into Main Distribution (oversell). Proposed:
  block at the till like the wholesale block.
  CHECKED 31 Oct against Sage: the cross-company item create (post_new_item_to_sage) only runs for
  items made by the ERPNext importers (and only into TEST during the lock). The ~11,900 Ceramics
  items that came FROM Sage were never created in Home. Home's Sage holds 6,917 items (1,321 with
  stock); ERPNext already had every Home link that exists (30 missing rows added). Items WITH STOCK
  that Home's Sage lacks: Ceramics 1,582 of 1,891, Fashion 113 of 192 (only 17 + 4 have a wholesale
  price today, so the wholesale block stops the rest for now). Fix = one-off create of those items
  in Home's Sage (QOH 0) via Pharoh post-new-item-to-sage, saving the SelectionID as the Home row -
  writes to live Sage, so only on Russell's word.
  DECIDED 31 Oct (Russell): no till block and no bulk create for go-live - leave it. Such a sale
  shows Failed on the invoice (reason recorded) and the 15-min retry keeps trying.
- Transfer back HDSQ -> MD is BLOCKED (no "Home - Wholesale Price" on Fashion/Ceramics items) and
  would invoice at Home's list, not the forward price. Online returns post no reverse intercompany.
  => live test: keep the transferred item at Hyde Park; Online test with a Home item.
- Cheri and Oscar are NOT reps in Home's Sage (reps there: Brittany 815483, Kelly 77485, Leah,
  Godin, others) - their sales post under Godin until Ardmore adds them.
- FIXED 31 Oct: Sage invoices showed salesRep = null (Pharoh's TaxInvoice dropped
  salesRepresentative). Russell fixed Pharoh; ACC-SINV-2026-00102 -> INV0000082 reads back with
  salesRep "Fisokuhle Radebe" (the TEST default 740886, as expected while locked). The rep sent is
  the person picked in Select POS User (Sales Person.custom_sage_rep_id), else the till's rep.
  Fisokuhle/Megan/Happiness/Sharon hold TEST rep ids but sit on TEST tills only - harmless.
- Accounts Settings delete_linked_ledger_entries = 0: switch it on for the cleanup, else deleted
  test docs leave cancelled ledger rows.

## Count loader (built 31 Oct, API Server Script `ardmore-count-load`, System Manager only)

Used on Sunday after training to put the counted stock into each store warehouse. Per sheet
(warehouse HDSQ - A or JHBM - A, rows = [[item_code, qty], ...]), in this order:
1. check - unknown codes, disabled, counted items with no owner ID in ERPNext, more than Main
   Distribution holds, more than the owner holds in Sage.
2. align - looks the counted codes up in the WAREHOUSE OWNER's Sage only (Home for both stores,
   Russell 31 Oct) via Pharoh `POST /api/InventorySync/get-item-selectionid-for-erpnext` (body:
   credentials + itemCodes; reply: totalResults = codes sent, returnedResults = codes found,
   items = [{item_code, custom_sage_selection_id}]). 50 codes per Pharoh call, one call at a time;
   200 codes per loader call (repeat with start = next_start). Adds the owner's Sage Item Selection
   row if missing, corrects it if different, lists codes Sage did not return. NOTHING is created
   in Sage (Russell: the sheet has too little data to create an item). Read-only on Sage, so it
   works under the TEST lock.
3. load - "already owned" Material Transfers MD -> store, 100 lines per entry, nothing to Sage.
Item code is the ONLY link between companies; each Sage company has its own SelectionID.
Tested 31 Oct on TEST (company = Ardmore Ceramics TEST): a deleted row re-added (ABE162NOV19 =
96556328), a wrong id corrected (ABE167DEC19R 1 -> 96556329), 2 codes reported not in Sage.
Why only the owner: a store's till sale and return send only the owner's ID. Intercompany
transfers/sales send the seller's ID on the tax invoice and the buyer's ID on the supplier
invoice (checked in both scripts) - never proven with different ids because the lock forces TEST
on both sides; read both back on Sunday's live transfer test.

## Sunday plan (final, 31 Oct)

Before Sunday: Russell fresh-Deploys nest_help 0.0.10 (pushed, in sync). Saturday Ardmore counts
Hyde Park + JHB Holding, corrects Sage HOME to the counts, and sends both sheets (code + qty).
Russell makes Cheri/Oscar names in Home's Sage match ERPNext (hourly rep sync fills the ids).
Live state 31 Oct: all 3 live integrations have custom_default_warehouse and
custom_last_qtyonhand_sync EMPTY (sync off, first pull will be full); no Item has
custom_qty_pending_sage; delete_linked_ledger_entries = 0; 62 non-zero Bins on Ardmore.

1. Training cleanup (company Ardmore Ceramics TEST): delete_linked_ledger_entries ON; cancel +
   delete its Sales Invoices (59 on 31 Oct), then cancel opening POS-OPE-2026-00093 (delete the
   sales FIRST - a closing would link them). Logins, tills, items, stock stay.
2. Test cleanup on company Ardmore - while the lock is still ON, so nothing can reach live Sage:
   cancel + delete POS Closing (4) -> returns -> Sales Invoices (37 incl drafts 00089/00090 and
   test docs 00099-00102) -> Ardmore Stock Transfers -> Stock Entries (16 incl draft 00530 and
   00547) -> Material Requests (4) -> POS Openings (6 incl open 00090 Online, 00092 Hyde Park).
   Check every Ardmore Bin = 0, then delete_linked_ledger_entries OFF.
3. Lock lift, on Russell's word: SAGE_FORCE_COMPANY = "" in post-taxinvoice-to-sage,
   post-customerreturn-to-sage, post-intercompany-transfer-to-sage, post-intercompany-sale-to-sage,
   post_new_item_to_sage; delete Sage Intercompany Account "Home-Ardmore Ceramics TEST".
4. Stock from Sage, ONE company at a time: Default Warehouse = Main Distribution - A on Home ->
   wait for Last QOH Sync to be set (cron every 5 min; first pull = items with stock only, ~1,300
   for Home) -> Error Log "Sage QOH" clean -> Ceramics -> Fashion. Main Distribution then = Home +
   Ceramics + Fashion on-hand. Later runs subtract every other Ardmore warehouse (verified 31 Oct:
   all enabled non-group warehouses of the company, i.e. HDSQ, JHBM, ACA, AORT).
5. Count loads, Hyde Park then JHB: check (exceptions to Russell) -> align -> load.
6. Live tests, Russell on the tills, readback from LIVE Sage (point tmp-sage-test-readback at the
   live company, read only): Hyde Park sale of a Home item + return; Online sale at 15% and at VAT 0%
   (flight no.) with Home items + a return; Stock Transfer MD -> Hyde Park of one Ceramics or
   Fashion item Hyde Park needs anyway (it stays - no automatic transfer back). Check: right Sage
   company, right SelectionID on each side, the picked sales rep, totals, stock back where it was.
7. Close-out: close the POS openings used for the tests; delete tmp-sage-test-readback;
   erpnext@ session default company -> Ardmore; Clear Cache on each till browser (2 Hyde Park
   laptops, Online).
Monday watch: invoices with Sage status Failed / Check Sage (sales + returns retry every 15 min;
Online items missing from Home's Sage will sit here - decided); intercompany Failed has NO
automatic retry (status on the Stock Entry / invoice); Error Log.

## Found 27 Oct (Russell: "where is the sales person selector / the VAT changer?")

- SALES PERSON SELECTOR IS GONE. It was Paul's code in the Page doc `point-of-sale` (script field)
  calling `server_scripts.public.py.pos.get_sales_reps`, saving `custom_sales_representative`.
  Page script is NULL since 2026-07-20 (Administrator) and the method no longer exists on the bench
  ("No module named server_scripts.public.py.pos"). Sales Person records (pos_profile = till) are
  still there: Hyde Park Leah / Godin / Brittany, Online Cheri / Kelly TBA / Oscar TBA. Today every
  Hyde Park sale is just hdsqpos@ and posts to Sage under the till rep (Godin). Needs a rebuild as a
  POS Invoice client script (loader picks it up) - design to agree with Russell.
  **REBUILT 27 Oct:** Client Script `POS Sales Person` (POS Invoice, loaded by the loader) puts a
  "Select POS User" dropdown in the till header, list from API Server Script `pos-sales-people`
  (method `ardmore_pos_sales_people`, Sales Person.pos_profile = till); the choice stays for the
  session and is stamped on each sale in `custom_sales_representative` on validate. Proven:
  ACC-SINV-2026-00083 = Godin Ndlovu (-> INV0000062), 00084 = Leah Masoka (-> INV0000063).
  **Sage rep follows the selected person (Russell 27 Oct: "for reporting they want to see who sold
  what"):** hourly Scheduler script `get-sales-rep-ids-from-sage` reads Pharoh
  `SalesReps/get-salesperson-for-erpnext` for the Sage company on the person's till (POS Profile
  custom_sage_entity) and sets Sales Person.custom_sage_rep_id by name match (read only). First run:
  Godin 622508, Leah 622507; Brittany, Cheri, Kelly, Oscar, Airport staff not in Home's Sage yet.
  `post-taxinvoice-to-sage` rep order is now: selected Sales Person > User > POS Profile > entity
  default (only when the lock is off - under the lock the TEST default rep is sent). **Returns
  fixed 27 Oct:** Sales Invoice custom field `custom_sales_representative` was no_copy, so credit
  notes came out blank; now no_copy 0 (proven: make_sales_return of 00086 carries Godin Ndlovu), and
  `post-customerreturn-to-sage` sends the original sale's person's Sage rep first (then User > till >
  entity default, lock-off only). Add people at /app/sales-person: name
  exactly as the rep in Sage, Parent = Sales Team, POS Profile = till, Enabled.
- VAT CHANGER: never built - Airport excl-VAT design still waits on Russell's price-basis answer.
- `POS Split Payment Autobalance` and `POS Voucher Ref` LOAD but do nothing when the till is
  opened by URL (/app/point-of-sale): the nest_home landing redirect leaves frappe.get_route() =
  ["nest-home"] and both gate on route[0] == "point-of-sale". Opened via frappe.set_route the route
  is right. The loader already warns about this and checks #page-point-of-sale instead. Fix = same
  check in both scripts; then clip 2 (card + voucher) must be re-recorded (card would auto-balance
  and the voucher number would be asked).

## Stock movements, now to go-live (to be confirmed by Russell)

1. This week: test documents on Ardmore only. Sunday: cancel them, zero Ardmore's stock.
2. Saturday: Ardmore counts Hyde Park + JHB Holding and corrects SAGE. ERPNext untouched.
3. Sunday switch-on: first FULL QOH pull -> Main Distribution - A = Home + Ceramics + Fashion
   on-hand per item. Check the three live integrations' `custom_last_qtyonhand_sync` are EMPTY.
4. Count loads = Material Transfers OUT of Main Distribution into HDSQ - A / JHBM - A (/ ACA - A),
   Stock Entry box **"Stock already owned by the receiving entity"** TICKED on every one
   (built + proven today: status "Not needed (already owned)", nothing to Sage). The entities
   already own that stock in Sage, so NO intercompany invoices. Exceptions (count > Sage total)
   go back to Ardmore.
5. Monday on: the 5-minute sync keeps Main Distribution = Sage total minus every other Ardmore
   warehouse. **VERIFY THIS in `get-inventory-qtyonhand-for-erpnext` before calling it certain**
   (does the subtraction cover HDSQ, JHBM, AORT, ACA?).

## Done today on the site

- Session default company for erpnext@ set to Ardmore Ceramics TEST (POS dialog shows the
  training till). Set back to Ardmore at switch-over.
- Stock Entry Custom Field `custom_stock_already_owned` + guard in
  `post-intercompany-transfer-to-sage`; Select option "Not needed (already owned)".
- Temp scripts deleted: tmp-uat-items-test, tmp-ping, tmp-patch-owned-flag.
- Test Item Prices (Ardmore - Retail etc.) for FABCBMY / UAT items created earlier today.

## Still open

- Confirm steps 1-5 with Russell; verify step 5 in the script.
- Chrome-driven final test (login to be chosen), then read each document back from Sage TEST.
- nest_account_sale 0.1.1: Russell to push + fresh Deploy.
- Britt's Sage rep (Ardmore creates it in Home's Sage), then set on brittany@.
- No automatic retry for a Failed intercompany post - decide who watches the status field.
- Sunday: "every Hyde Park / online item exists in Home's Sage" check; lift the lock in FOUR
  scripts; delete lock-only row `Home-Ardmore Ceramics TEST`; switch the stock sync on;
  retire the training company; remove test documents.
