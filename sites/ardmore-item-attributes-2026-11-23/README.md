# Ardmore: item attributes (tickets 0164, 0165, 0166) - 23 Nov 2026

## Live now
- **0164 Stock Items tile** (08:50): tile `NEST-TILE-WS-OUR_ITEMS` renamed "Stock Items", enabled, icon
  `ph-duotone ph-package`, route `query-report/Stock Balance`. Removed from layouts Sales Assistant,
  POS Manager - Airport, POS Manager - Caversham. On: Senior Manager - Online (Cheri), POS Manager - Online,
  POS Manager - Joburg (Brittany, Hyde Park Manager), Administrator. Stock Controller keeps its own
  "Stock Balance" tile.
- **0165/0166 Download Current Items** (10:27): nest_help 0.0.13 `nest_help.api.download_import_sheet`
  + Client Script "Home Fashion Importer - Download Template" (copy here; `BEFORE_...js` = rollback).
  Checked as cheri@: Home 2,472 rows, Fashion 490, template 3 sample rows, prices/qty empty,
  Allowed values "as at 23 November 2026".
- **Upload test** (on Russell's word, 10:34): HFI-00010 (5 rows, <1 s, 5 updated) and HFI-00011
  (300 rows, 21.5 s, 297 updated, 3 refused "Value cannot be negative for Quantity On Hand":
  Bush Baby 119/7035, CUSHMBNV50, CUSHMBT60 - negative Sage on hand, pre-existing). No Sage queue,
  no stock entries. Side effect: those items' Ardmore default warehouse -> JHB Atrium Home - A.

## Not live
- **Hide the left menu** (nest_home 0.0.40, pushed 09:42): the deploy did not include nest_home
  (Live still serves the 0.0.39 bundle `nest_home_redirect.bundle.ABVT7IIU.js`, settings field absent).
  Needs Pull Updates for nest_home + fresh Deploy, then tick Nest Home Settings > Hide the left menu.

## Findings for Ardmore
- 1,523 of 2,472 Home items carry exactly Bonnie / Acacia / Amber / Acrylic / Small = the FIRST option
  of each Select. Frappe gives a new doc the first option of a Select with no default
  (`get_static_default_value`), so every item created by the Sage item sync or an importer without
  values gets them. An empty first line in the options stops it (Sub Category already has one).
- Every current attribute value is on its list (a download re-uploads cleanly).
- Item Default warehouse for company Ardmore: 1,501 Home items still Main Distribution - A; a
  correction upload moves the uploaded items to JHB Atrium Home/Fashion (importer behaviour since 1 Nov).

## Round 2 (plan approved 23 Nov) - built, applied after close
- **nest_help 0.0.14** (not pushed yet): `home_fashion_import.py` + `doc_events` hook. A sheet over
  300 rows is imported in a background job; the user gets a bell notification (done / failed).
- **Server Script** "Home Fashion Importer - Import": new version `Home_Fashion_Importer_-_Import.py`,
  rollback `BEFORE_Home_Fashion_Importer_-_Import.py` (= Live as of 10 Nov, checked against the 8 Nov
  copy). Apply ONLY after nest_help 0.0.14 is deployed, or big sheets stay QUEUED.
- **Categories**: `build_category_lists.py` -> `category_changes.json` (1,350: A 110 Home + 6 Fashion,
  B 1,234 Ceramics) and `S:\Ardmore\Ardmore Item Categories to Confirm.xlsx` (107 items + 4 list values
  for Cheri). Nothing held: Hyde Park and Online have allow_rate_change = 1, so category does not
  decide till price editing there. CUSHMBAV50, CUSHMBN60, PVTEA will not save (negative Quantity On
  Hand from Sage). Before applying: re-pull live category for every code, skip any that changed since
  the 23 Nov check, save the before list.
- **What the category change does (checked 23 Nov, script by script):** Hyde Park/Online till sales and
  returns: no change (post by store, Sage Item Selection per company). Online auto transfer: a ceramic
  piece now draws from Atrium Ceramics / Main Distribution first -> tax invoice in Sage Ceramics billed
  to Home + supplier invoice in Sage Home; the shopper's sale stays in Sage Home (as Fashion today, e.g.
  JSSA-00216 -> Sage Home JSSA27294, transfer MAT-STE-2026-00663 -> Fashion INV0002229 / Home SIV0010800).
  The shopper's sale going straight to Sage Ceramics is the Shopify split (built 20 Nov, not switched on).
  RULE (Russell, 23 Nov): Online sales never raise intercompany; each item is billed to the shopper by its
  own company. Live breaks it until the split is on: 18 Fashion -> Home pairs from Online sales, 9-23 Nov
  (Stock Entries with For Sale set and intercompany status Synced). After the split, the ERPNext Category
  decides which company bills the shopper, so the 1,234 ceramic pieces bill from Ceramics only once fixed.
  Item sync: own-company fields (item_group, selection id, tax type, retail/wholesale fields, Ardmore -
  Retail) switch to the new company as Sage touches each item; Home - Retail Price unaffected.
  Ardmore - Wholesale (Account Sale) for the ceramics -> Ceramics wholesale. Sales History company for
  those sales -> Ceramics. Account Sales to multi-account customers route by the new category.
  No script runs on Item save.
- **Lists**: empty first line on Collection, Design, Colour, Base Cloth, Size; merge Camp Criters,
  Bushbandits, Limelight, Butterdust, Refelctions into the right spelling, then remove them.

### Done after close, 23 Nov (18:35-19:48, Russell's go)
- Server Script "Home Fashion Importer - Import" -> background version (checked patch: Live matched the
  rollback copy exactly, result matched the new copy exactly), 19:48 wording "the bell, top left"
  (Frappe 16 shows notifications in the left strip). Rollback = `BEFORE_...py`.
- Tests: HFI-00012 (5 rows, straight away, 5 updated); HFI-00013 Administrator, Fashion Download
  Current Items 490 rows -> QUEUED -> 490 updated, bell; HFI-00014 cheri@, Fashion download now 496
  rows (6 moved to Fashion) -> QUEUED -> 496 updated, bell in her Notifications. No items created, no
  stock entries, nothing queued for Sage. Side effect: Fashion items' Ardmore default warehouse ->
  JHB Atrium Fashion - A (importer behaviour).
- Categories: 1,347 changed (item save, re-checked against the 23 Nov list first, none had moved);
  CUSHMBAV50, CUSHMBN60, PVTEA refused (negative QOH). Before list `categories_before_2026-11-23.csv`
  + `S:\Ardmore\Ardmore Item Categories BEFORE 2026-11-23.csv`.
- Lists: FURPOUFCCMV Camp Critters, CARQSTRE02 Reflections, FABHANGCCLLV Lime Light, FABHANGMBBDL
  Butter Dust; Camp Criters/Bushbandits/Refelctions/Limelight/Butterdust removed; empty first line on
  Collection/Design/Colour/Base Cloth/Size (new Item now starts blank in all six). Rollback copy of the
  options: `lists_before_2026-11-23.json`.
- 19:44:13 the five lists were REVERTED to their pre-18:47 text (misspellings back, no empty first
  line) by a Customize Form save under cheri@ (Custom Field db_update, no Version rows; Sub Category
  untouched). Source = a Customize Form screen loaded before 18:47 and then Updated; not found which.
  Re-applied 20:31 (no item had moved back). Customize Form loaded fresh DOES keep the leading empty
  line, so Cheri's own Updates are safe; only a stale screen reverts it.
- Left menu: ticked 18:48, FAILED Cheri's click-through (0.0.40 hid the whole menu = search, bell and
  log-out gone on Home and the importers), unticked 18:52. nest_home 0.0.41 folds it to Frappe's
  narrow strip instead (Russell approved). Deployed, ticked 20:15. Click-through as cheri@: Home,
  every tile (Open POS -> Not now, POS Closing, Stock Transfer, Request Stock, Reports, Import
  Home/Fashion, Issue Stock + back arrow, Stock Items, Sales Persons, Export Proof, Guides), Support
  Tickets icon + Back to home, green Home buttons, search, bell, user menu (Logout shown). Narrow
  48px strip on Home/importers/stock-request pages, dock only on ERPNext pages. NOT done: phone
  width (Chrome window would not resize), Administrator not re-clicked on 0.0.41 (flag never set
  for Administrator; checked with the setting on at 18:48 under 0.0.40).
- Guide: wording (bell top left, Search icon, 593 / 358 counts) + 4 screenshots retaken as cheri@
  with the narrow menu (old shots in `shots\_before_2026-11-23_narrow_menu\`). Stock In guide: one
  line on background imports. In-app help `import-home-fashion.html` updated in nest_help 0.0.15
  (NOT pushed: rides with the next deploy).

### Download Current Items: choose + rows to check (Russell, 23 Nov 21:00, once-off clean-up)
- nest_help 0.0.15 deployed; Client Script updated 21:14 (rollback = the 10:27 text, same as
  `BEFORE_...Download_Template.js` plus the Current Items button). Box: Only items with stock
  (default) / All items. Rows that look wrong are yellow, reason in last column `check`.
- As cheri@ 21:15: Home in stock 1,004 rows / 372 yellow; Fashion in stock 248 / 192; Fashion all
  496 / 422. HFI-00015 = the Fashion in-stock sheet uploaded unchanged, Update Only: 241 updated,
  7 "modified after you have opened it" (a scheduled Sage job saved those items as Administrator at
  the same second); `check` column ignored. Re-upload clears such rows.
- Pre-filled sheets / name-based auto-fixes: dropped on Russell's word. Cheri downloads, fixes, uploads.

### Tomorrow morning, 24 Nov (Russell: "do it tomorrow morning")
- Send the three ticket replies (nesterp HD Ticket 0164/0165/0166, agent reply), texts as agreed
  23 Nov 21:3x:
  - 0164: "Hi Cheri, this is done. The Stock Items tile on your home screen shows every item's stock
    in each warehouse. Regards, Russell"
  - 0165: "Hi Cheri, we checked every item against the Sage company that holds it and corrected the
    ERPNext Category on 1,347 items. 107 items need your answer; they are on the sheet "Ardmore Item
    Categories to Confirm", which Russell is sending you. You can now correct the item details
    yourself: on Import Home/Fashion, Download Current Items gives you the items with stock, with the
    rows we think are wrong in yellow. Fix those rows and upload the sheet. The guide "Ardmore Item
    Clean-up" shows the steps. Regards, Russell"
  - 0166: "Hi Cheri, the template now always shows the lists as they are in ERPNext. The misspelt
    values are corrected (Camp Critters, Bush Bandits, Lime Light, Butter Dust, Reflections), and new
    items no longer default to Bonnie, Acacia, Amber, Acrylic and Small. Three values we're not sure
    about (Sampe Critters, Silver Rippler, Rippler) are on the second tab of the confirm sheet.
    Regards, Russell"
  SENT 24 Nov 08:22 on Russell's word: Communications 7gmi3bq88n (0164), agpdg1j92c (0165),
  8gq2m66940 (0166), from hello@syncflo.co.za to cheri@, via frappe.core...communication.email.make.
  HD Ticket reply_via_agent refused ("At least one recipient is required": these tickets were logged
  by ardmore-support@syncflo.co.za, the support mailbox). Tickets left Open.
- Russell emails Cheri: `S:\Ardmore\Ardmore Item Clean-up.docx` (generator `_uatdoc\build_item_cleanup_guide.js`)
  + `S:\Ardmore\Ardmore Item Categories to Confirm.xlsx`.
- When Cheri returns the confirm sheet: apply her 107 answers + the 4 list values.

### After close, in this order (original plan)
1. Russell: push nest_help; Pull Updates for nest_home + nest_help; one fresh Deploy.
2. Check: nest_home bundle hash changed, Nest Home Settings has Hide the left menu; nest_help 0.0.14.
3. Update the Server Script; test 5 rows (straight away) and the Fashion download (490, queued).
4. Before list to S:, then the 1,347 category changes; recount.
5. Lists: empty first lines, misspelling merges.
6. Tick Hide the left menu; click-through as Cheri and Administrator.
7. Retake the guide screenshots (no left menu now) and rebuild the guide.
8. Message to Cheri (Russell, 23 Nov): download fresh Home and Fashion sheets on the morning of 24 Nov
   before making any changes.

## Guide
`S:\Ardmore\Ardmore Item Attributes Guide.docx`, built by `S:\Ardmore\_uatdoc\build_item_attributes_guide.js`,
shots `shots\ia-*.png`. Rebuilt 23 Nov afternoon: one upload of any size (background over 300 rows),
categories fixed by us + Cheri's list, lists fixed by us. Screenshots still show the left menu.
