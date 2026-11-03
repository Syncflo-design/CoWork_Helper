# Ardmore go-live: requirements and Sunday runbook

Written 31 Oct 2026, from the review and decisions of 31 Oct. Site `ardmoreceramics.c.frappe.cloud`
(MCP `frappe-ardmore`, logged in as erpnext@ardmore-design.com). Training Sunday 1 Nov morning on
the training company; switch-on Sunday afternoon; trading Monday 2 Nov. Run from laptop RUSSELL-I5.
Background and history: `ardmore-handover-2026-10-27.md` (same folder).

## 0. Warehouse structure (decided with Russell, 1 Nov 2026, go-live day - supersedes older notes)

Each warehouse belongs to ONE Sage company (Warehouse "Sage entity"). Ownership is the warehouse's
company; a move between warehouses of different companies posts the intercompany pair (tax invoice
in the seller, supplier invoice in the buyer, each with its own company's SelectionID).

| Warehouse | Owned by | Stock comes from |
|---|---|---|
| **Main Distribution - A** (the Ceramics holding store; ERPNext does not allow renaming it) | Ceramics | Sage Ceramics stock sync |
| **JHB Atrium Home - A** | Home | Sage Home stock sync |
| **JHB Atrium Fashion - A** | Fashion | Sage Fashion stock sync |
| **JHB Atrium Ceramics - A** (transit, "goods in transit" for ceramics) | Ceramics | Transfers from Ceramics Holding |
| **Online Store - A** (new; the Online till sells only from here) | Home | Transfers from the JHB Atrium warehouses |
| **Hyde Park HDSQ - A** | Home | Count load, then transfers from the JHB Atrium warehouses |
| Caversham ACA - A | Ceramics | later (its own count) |
| Airport AORT - A | Home | later (its own count) |

- **JHB Main Holding (JHBM - A) is retired:** disabled 1 Nov (no stock, no documents). It cannot be
  deleted until ERPNext's queued revaluation jobs from the cleanup have run; delete it later.
- **Stock sync rule (built 1 Nov):** each company's Sage quantity lands in its own warehouse, less
  that company's stock held elsewhere. JHB Atrium Home = Sage Home - (Hyde Park + Online Store +
  Airport); JHB Atrium Fashion = Sage Fashion; Main Distribution = Sage Ceramics - (JHB Atrium
  Ceramics + Caversham). The sync refuses a target warehouse owned by a different company. The
  order of the first pulls no longer matters.
- **Moves:** Main Distribution -> JHB Atrium Ceramics posts nothing. JHB Atrium Ceramics -> Hyde
  Park / Online posts Ceramics -> Home. JHB Atrium Fashion -> Hyde Park / Online posts Fashion ->
  Home. JHB Atrium Home -> Hyde Park / Online posts nothing. Online sales and returns stay inside
  Home (no reverse intercompany needed).
- **Stock requests (nest_stock_request 0.3.0):** a store chooses which JHB Atrium warehouse it
  requests from (Home, Fashion or Ceramics). JHB Atrium Ceramics requests from Main Distribution.
  Cheri runs the three JHB Atrium warehouses (issues from them). Settings rows needed AFTER 0.3.0
  is deployed (the old app allows one source per store): HDSQ, Online Store and AORT each from
  JHB Atrium Home, JHB Atrium Fashion and JHB Atrium Ceramics; JHB Atrium Ceramics from Main
  Distribution (user Cheri); JHB Atrium Home -> itself and JHB Atrium Fashion -> itself (user Cheri,
  "who runs it"). Until then each store draws from JHB Atrium Home only.
- **Online till** sells from **Online Store - A** (set 1 Nov). It starts empty: stock must be
  transferred in from the JHB Atrium warehouses before Online can sell it.
- **Count load:** everything at Hyde Park belongs to Home, so the Hyde Park count comes out of
  the warehouse Home's stock syncs into (JHB Atrium Home); the loader reads it from Home's sync
  target and refuses to load before Home's sync is switched on. The Hyde Park count sheet is the
  source of truth for Hyde Park.
- **Importers:** the Kiln Sheet Importer imports into Main Distribution only. The Home Fashion
  Importer imports Home sheets into JHB Atrium Home and Fashion sheets into JHB Atrium Fashion
  only. Any other warehouse is refused.
- **Accepted for the first weeks:** Sage totals include stock at locations not yet in ERPNext
  (Airport, Caversham, others), so the JHB Atrium / Ceramics Holding balances are overstated until
  each location is counted in; shortages are corrected in Sage. Ceramics without a wholesale price
  or without a Home Sage ID cannot be transferred to Home yet; fixed as we go.

## 1. Rules that hold throughout

1. The Sage TEST lock is lifted only on Russell's word, never by Claude on its own.
2. The training company **Ardmore Ceramics TEST** never talks to Sage: not on submit, retry or the
   Send to Sage button.
3. Anything that writes to live Sage happens only on Russell's word.
4. If unsure about scope or behaviour, ask first; never widen scope to work around an unknown.
5. Git is run by Russell only. Claude gives single-line commands in fenced bash blocks.

## 2. Requirements

### Item link between ERPNext and Sage
- The **item code is the only link** between ERPNext and each Sage company (Home, Ceramics,
  Fashion). Each Sage company has its own SelectionID for the same code, and a SelectionID is
  never duplicated in Sage.
- ERPNext stores one SelectionID per item per Sage company in the doctype **Sage Item Selection**
  (item_code + company -> selection_id, named `<item_code>-<company>`). This is what the posting
  and sync scripts read. `Item.custom_sage_selection_id` is a single legacy field, not per company.

### Which Sage company a document posts to, and with which SelectionID
- **Till sale and till return:** the Sage company that owns the till (POS Profile "Sage entity",
  else the till's warehouse). Hyde Park and Online both belong to **Home**. Every line carries
  the item's Home SelectionID. A missing ID does not block the sale: it is flagged Failed and
  retried every 15 minutes.
- **Intercompany** (stock moving from one owner to another, by Stock Transfer or by a sale out of
  another owner's stock): a tax invoice in the SELLING company carrying the seller's SelectionID,
  plus a supplier invoice in the BUYING company carrying the buyer's SelectionID. Both IDs must
  exist; if either is missing the posting stops with the reason on the document (the stock move
  stands). Verified in both intercompany scripts. Never proven with different IDs, because the
  lock forces TEST on both sides, so it is checked on Sunday's live transfer test.
- **Ownership:** a warehouse with "Sage entity" set belongs to that company (Hyde Park HDSQ - A
  and JHB Main Holding JHBM - A = Home; Caversham ACA - A = Ceramics). Main Distribution - A has
  none, so there an item belongs to the company in its Category.

### Sales rep
- The rep sent to Sage is the person picked in the till's **Select POS User** dropdown (their
  Sales Person "Sage rep id"), never the login. If that person has no rep id, the till's rep is
  used (Hyde Park and Online: Godin Ndlovu, 622508).
- Pharoh's TaxInvoice endpoint now passes the rep to Sage (fixed by Russell 31 Oct; proven:
  ACC-SINV-2026-00102 -> INV0000082 reads back with a rep). Returns already carried it.
- Live tills: Hyde Park = Brittany (815483), Godin (622508), Leah (622507); Online = Kelly
  (77485) plus Cheri and Oscar, who have no Home rep id yet and post under Godin. The hourly rep
  sync matches by name, so their names in Home's Sage must match ERPNext exactly (Russell is
  fixing this with them on Sunday). Fisokuhle, Megan, Happiness and Sharon hold TEST rep ids but
  are on the TEST tills only, which never post to Sage.

### Count sheets (Hyde Park and JHB Holding)
- Used after training on Sunday to put the counted stock into each store warehouse.
- Only items on the sheet are touched. Never read or process whole item lists.
- For each counted code, look it up in **the warehouse owner's Sage only** (Home for both stores)
  and make ERPNext's Home SelectionID match what Sage returns: add it if missing, correct it if
  different. Codes Sage does not return are listed. **Nothing is created in Sage** (the sheet has
  too little data to create an item).
- Lookups go to Pharoh in batches of **50 codes per call**, one call at a time.
- The stock move is a Material Transfer Main Distribution -> store with **"Stock already owned"**
  ticked, so nothing posts to Sage (the store's company already owns that stock in Sage).

### Not used at go-live
Sales Orders, Purchase Orders, Purchase Invoices, non-till returns, Account Sale, the Airport till
and wholesale prices. The old SO/PO/PI posting scripts are disabled.

## 3. Decisions made 31 Oct

- **Online items missing from Home's Sage:** no till block and no bulk create. Such a sale goes
  through, shows Failed on the invoice with the reason, and keeps retrying.
- **Count sheets:** align Home only (the owner of both stores).
- **Rep ids:** left as they are; Russell fixes Cheri and Oscar's Sage names on Sunday.
- **Live test plan (to confirm with Russell):** the transferred item stays at Hyde Park (there is
  no automatic transfer back), and the Online tests use Home items.

## 4. Before Sunday

- [ ] Russell: fresh **Deploy** (not Update) of nest_help 0.0.10 on Frappe Cloud. It is pushed;
      local main = origin/main at commit 130890f.
- [ ] Ardmore, Saturday: count Hyde Park and JHB Holding, correct Sage **Home** to the counts, and
      send both count sheets as item code + quantity.

## 5. Sunday, after training

State checked on 31 Oct: all three live Sage integrations have Default Warehouse and Last QOH Sync
EMPTY (stock sync off; the first pull will be full); no item is flagged "Qty Added Locally";
delete_linked_ledger_entries = 0; 62 non-zero stock balances on company Ardmore.

**Step 1. Training cleanup** (company Ardmore Ceramics TEST). **Not done, on purpose (1 Nov):** its
59 sales are tied into 77 till closings going back to March; unwinding them is not needed for
go-live. The training company never talks to Sage. Raise with Russell if a clean slate is wanted.

**Step 2. Test cleanup on company Ardmore. DONE 1 Nov (lock still on).** Removed: 6 till closings,
43 sales and returns, 2 Stock Transfers, 17 Stock Entries, 5 Material Requests, 8 till openings
(including today's test sales 00102-00107). Checked: Ardmore has no Sales Invoices, Stock Ledger
Entries or GL Entries left, every stock balance is 0. delete_linked_ledger_entries back OFF.
Warehouse structure built the same evening (section 0).

**Step 3. Lift the TEST lock.** Claude, on Russell's word. **DONE 1 Nov, 20:58** (Russell: "Yes, lift
it"): `SAGE_FORCE_COMPANY = ""` in all five scripts, nothing waiting to resend. The lock-only row
"Home-Ardmore Ceramics TEST" was KEPT (Russell: block the TEST company, don't delete it; the row is
never used once the lock is off). TEST company blocked by disabling its three tills: POS_Test2,
Online Store Test, Cermaics_User2.
- Set `SAGE_FORCE_COMPANY = ""` in: post-taxinvoice-to-sage, post-customerreturn-to-sage,
  post-intercompany-transfer-to-sage, post-intercompany-sale-to-sage, post_new_item_to_sage.
- Delete Sage Intercompany Account **"Home-Ardmore Ceramics TEST"** (exists only for the lock).
- Already in place: the 15-minute retry only resends documents from 1 Nov on, so test documents
  are never resent live; after the lift, new items are never created in the Sage TEST company.

**Step 4. Stock from Sage (switching the stock sync ON).** Claude, on Russell's word. Setting a
company's Default Warehouse IS the switch; nothing syncs until it is set.
- Company Sage Integration **Home**: Default Warehouse = **JHB Atrium Home - A**.
- **Fashion**: Default Warehouse = **JHB Atrium Fashion - A**.
- **Ceramics**: Default Warehouse = **Main Distribution - A**.
- The sync runs every 5 minutes; a first pull loads only items with stock. Each company is done
  when its Last QOH Sync is set. Check the Error Log for "Sage QOH". Order does not matter any
  more (each company fills only its own warehouse); one at a time is still kinder to Pharoh.

**Step 5. Count load, Hyde Park (HDSQ - A).** Claude, with the count sheet.
1. `check`: lists codes not in ERPNext, disabled items, counted items with no Home ID, and counts
   larger than JHB Atrium Home holds. Exceptions go to Russell before loading.
2. `align`: looks the counted codes up in Sage Home and adds or corrects the Home SelectionIDs.
3. `load`: Material Transfers JHB Atrium Home -> Hyde Park, "Stock already owned", 100 lines per
   Stock Entry, nothing to Sage.
- JHB has no count load any more: its stock is whatever Sage Home / Sage Fashion hold, less the
  stores. Online Store starts empty and is filled by transfers from the JHB Atrium warehouses.

**Step 6. Live tests.** Russell rings them up on the tills; Claude reads each document back from
live Sage (the readback script is pointed at the live company, read only). **Moved to Monday 2 Nov
morning, in store, BEFORE trading starts (Russell), so any roadblock is fixed before the doors open.** Until then keep tmp-sage-test-readback and tmp-compare-sage-stock.
- Hyde Park: sale of a Home item, then its return.
- Online: a sale at VAT 15% and a sale at VAT 0% (with a flight number), using Home items, then a
  return.
- Stock requests from Hyde Park, one item from each JHB warehouse (Russell, 1 Nov). Two requests,
  because each request draws from one warehouse ("Request from" picker); each goes Request ->
  Issue -> Receive:
  - from **JHB Atrium Home**: a Home item. Home to Home, posts nothing to Sage ("Not needed").
  - from **JHB Atrium Fashion**: a scarf. Posts Fashion -> Home in live Sage at the Fashion
    wholesale price (tax invoice in Fashion with Fashion's ID, supplier invoice in Home with
    Home's ID). The scarf stays at Hyde Park.
- Check each document: right Sage company, right SelectionID on each side, the picked sales rep,
  totals, and stock back where it should be.

**Step 7. Close-out.** Claude, except the till browsers.
- Close the till sessions used for the tests, so Monday opens fresh.
- Delete the temporary script **tmp-sage-test-readback**.
- Set the erpnext@ login's default company to **Ardmore**.
- Clear Cache in each till browser: both Hyde Park laptops and Online.

## 6. Monday: what to watch

- Sales Invoices with Sage status **Failed** or **Check Sage**. Sales and returns retry every 15
  minutes. Online sales of items missing from Home's Sage will sit here (decided).
- **Intercompany Failed** status on a Stock Entry or invoice. This has **no automatic retry**;
  someone must check it and resend.
- The Error Log.
- **Hyde Park count lines NOT loaded on 1 Nov** (fix, then load just these lines into HDSQ - A):

  | Code | Counted | Sage Home holds | What to do |
  |---|---|---|---|
  | TRAMM01 | 6 | not in ERPNext | Wrong code on the sheet: find the right one |
  | CUSHTPNV | 4 | 2 | Correct the quantity in Sage Home, or recount |
  | CUSHMTP50 | 8 | 5 | Correct the quantity in Sage Home, or recount |
  | RUNPPRR | 2 | -6 | Fix the negative in Sage Home, then load |

## 7. Reference

**Count loader:** API Server Script `ardmore-count-load`, method `ardmore_count_load`, System
Manager only.
- Args: `mode` (check | align | load), `warehouse` (HDSQ - A or JHBM - A), `rows` = JSON
  `[[item_code, qty], ...]`. Duplicate lines are summed and lines with qty 0 or less skipped.
- `align` also takes `start` (default 0) and `count` (default 200 codes per call): call again with
  start = next_start until next_start is empty. `company = Ardmore Ceramics TEST` runs it against
  Sage TEST instead.
- Tested 31 Oct on Sage TEST: a deleted ID was added back (ABE162NOV19 = 96556328), a wrong ID
  corrected (ABE167DEC19R 1 -> 96556329), and 2 codes reported not in Sage.

**Pharoh endpoints used:**
- `POST /api/InventorySync/get-item-selectionid-for-erpnext?apikey=` with body = credentials +
  `itemCodes`. Reply: `totalResults` = codes sent, `returnedResults` = codes found, `items` =
  `[{item_code, custom_sage_selection_id}]`. A code not returned is not in that Sage company.
- `POST /api/TaxInvoice/post-taxinvoice-to-sage`: rep sent as `invoice.salesRepresentative.id`.
- `POST /api/CustomerReturn/post-customerreturn-to-sage`: rep sent as
  `customerReturn.salesRepresentative.id`.
- `POST /api/SupplierInvoice/post-supplierinvoice-to-sage`: the buyer's side of an intercompany
  move.
- `POST /api/InventorySync/get-inventory-qtyonhand-for-erpnext`: stock sync, every 5 minutes.
- `POST /api/TaxInvoice/get-sales-history-for-erpnext`: readback.

**Intercompany accounts:** all six company pairs are filled in (customer and supplier ids, price
list and discount: Ceramics and Home 15% off wholesale, Fashion 0%).
