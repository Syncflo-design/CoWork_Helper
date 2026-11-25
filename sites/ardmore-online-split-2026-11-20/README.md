# Ardmore: Shopify orders split by company (built 20 Nov 2026, NOT applied)

Plan approved by Russell 20 Nov 2026 (`~/.claude/plans/merry-yawning-sunbeam.md`). Requirements:
`S:\Ardmore\Requierments.docx`, proposal `S:\Ardmore\Ardmore - Shopify Online Orders Proposal.docx`.
Russell's answers: Shopify orders are paid by a new payment method "Shopify" (Online till only); online reps
are set by Russell on Company Sage Integration; an email matching several customers links the FIRST
(oldest); email matching only among till customers (Cash, Online Sales); money-only refunds ignored for now.

The Online till is trading. Everything below is applied outside trading hours on Russell's word, in this
order. Nothing here has touched Live yet.

## What is where

| Piece | Where |
|---|---|
| Paid-only import, go-live cut-off, shipping off, email match, marketing consent, customer pre-load | fork `nesterp_ecommerce_integrations` (version-16) |
| End of Day: Shopify order number, Sage number per company | app `nest_stock_request` 0.7.3 |
| Till button, company warehouse, Sage split, returns, category hold, Omnisend email, close order | Live site scripts (this folder) |

`base/` = Live text the patches were made from (8 Nov copies; Live last saved 8 Nov 07:13 / 08:31).
`patched/` = the replacements. `server/`, `client/` = new scripts.

## Apply (outside trading, Russell calls each step)

1. **Fresh copy** of every Server and Client Script (rollback). Compare each Live script in `base/` with its
   copy here (md5 via a temp API script); any difference = someone changed it, stop and look.
2. **Push + fresh Deploy** both apps (fork, nest_stock_request). Fork: Shopify Setting gets the new fields.
3. **Custom fields** from `custom_fields.json` (before any patched script: the Sage scripts write Sage Companies).
4. **Mode of Payment "Shopify"**: type Bank, account for company Ardmore = `Cash - A` (as Credit Card).
   Add it to POS Profile **Online** payments, Allow in Returns ticked. Online only.
5. **Company Sage Integration** (on screen):
   Online sales rep for all three = Kelly Nkomo (Russell, 23 Nov 2026), each company's own Sage rep ID:
   - Home: Online Customer ID 4171600, name Online Sales, Online Sales Rep ID 822273 (replaces 622508).
   - Ceramics: 414595, Website Sales, Online Sales Rep ID 822276.
   - Fashion: 498720, ONLINE SALES, Online Sales Rep ID 822274.
6. **New scripts**, created DISABLED (they do nothing until the till is ticked anyway, but stay off until step 9):
   - Server: `Sales Invoice - Sell From Item Company` (Sales Invoice, Before Validate),
     `Sales Order - Shopify Category Check` (Sales Order, Before Validate),
     `Customer - Mailing List Email` (Customer, Before Save),
     `Sales Invoice - Close Shopify Order` (Sales Invoice, After Submit),
     `pos-shopify-orders` (API, method `ardmore_pos_shopify_orders`).
   - Client: `POS Shopify Orders` (DocType POS Invoice, Form; the Till Scripts Loader runs it once enabled).
7. **Patch** (anchor replace, fingerprint before/after, temp script deleted): `post-taxinvoice-to-sage`,
   `post-customerreturn-to-sage`, `post-intercompany-sale-to-sage`, `Sales Invoice - Online Auto Transfer`,
   `pos-pool-stock`, `pos-pool-items`. With the POS Profile box unticked every till behaves exactly as today,
   except that each Sage post now also records Sage Companies.
8. **Shopify Setting**: Customer Group `Online Sales`; Default Customer `Online Sales`; Match groups
   `Cash` and `Online Sales` (one per line); marketing field `add_to_mailing_list`; Leave Shipping off Orders
   ticked; First Order Number = the agreed go-live number. Enable Shopify stays OFF.
9. **Switch on**: enable the new scripts; tick **Post Each Item to Its Own Company** on POS Profile Online.
10. **Customer pre-load** (any time after step 8): Shopify Setting > Load Shopify Customers. Needs the Shopify
    app to have customer read access. Result in Ecommerce Integration Log.
11. **Go-live**: Enable Shopify (5 webhooks become 4: orders/create is no longer registered).

Same push, separate items (23 Nov): nest_home 0.0.40 (ticket 0164) adds Nest Home Settings > "Hide the left
menu"; nest_help 0.0.13 (tickets 0165/0166) adds Download Current Items - after the deploy, replace the Client
Script "Home Fashion Importer - Download Template" with `../ardmore-item-attributes-2026-11-23/` copy. After the deploy, tick it on Ardmore: the wide left menu disappears for every login except Administrator.
Untick to undo. (The Stock Items tile itself went live 23 Nov 08:50, no deploy needed.)

## Rollback

Untick the POS Profile box (Online till back to Home + auto-transfer + intercompany at once), disable the new
scripts, untick Enable Shopify. Patched scripts can stay: unticked they behave as before. Full rollback =
restore the step-1 copies.

## Click-through (before anything is called ready)

The six client scenarios, as online@ and as cheri@ on the Online till: single company, combined (Home +
Fashion + Ceramics), international (VAT 0%), discount code, full and partial return, End of Day for the day.
Plus: a held order (bad SKU, no Category), alert arrives, fix, Retry, order appears on the till; a hand-typed
combined sale with Shopify switched off; Hyde Park sale + return unchanged. Where the Sage side is proven is
still open (Russell: TBA).

## Break tests (offline, no Frappe needed)

Run from this folder with Python 3.13 (full path, see memory python_toolchain):
`python -I tests/test_site_scripts.py` (34 tests) and `python tests/test_connector.py` (27 tests).
They run the real script and connector code against test data. The shop tests run the 8 Nov Live text and the
new text side by side and require identical Sage traffic for Hyde Park sales and returns. Rerun after any edit.
They do not replace the click-through on the site.

## Known limits

- A multi-unit line with a discount that does not divide evenly can differ from Shopify by a cent (till price
  per unit is rounded to the cent).
- An order cancelled in Shopify while its sale is open on the till keeps its Sales Order: discard the draft.
- A Shopify refund to the card is still done in Shopify; the till return does the ERPNext + Sage side.
