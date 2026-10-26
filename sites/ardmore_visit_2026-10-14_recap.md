# Ardmore on-site visit (14 Oct 2026) - recap notes (dictated by Russell, 16 Oct)

Working list. Feeds the summary to send Ardmore. Add to it as Russell dictates.

## To send Ardmore: what we need from them
- Users: full list of logins per store/role (names, emails, roles). Passwords set by Russell in one sitting.
- Ken: the Sage accounts for each entity (Home, Ceramics, Fashion) - the cash-sale account and the online-store account that sales will run through.

## Structure
- New Joburg holding warehouse (JHB Main Holding) that stock moves through: Main Distribution -> JHB Main Holding -> Hyde Park / Airport. DONE 16 Oct (JHBM - A).

## Kiln sheets
- Check one issue with Nozy on the kiln-sheet import (details to come).
- Ceramics rule: a kiln-sheet re-import updates details, never price, never quantity (one piece only). DONE 16 Oct.
- Home/Fashion: re-import updates details and ADDS quantity, never price. DONE 16 Oct.
- Pricing rule (16 Oct): the sheet prices an item only when it creates it (and creates it in Sage with that price); after that Sage owns the price and the item sync carries Sage's standard selling price to the till price list every 15 minutes. DONE.

## Decided on site
- **Multi-entity sale at the till:** when one sale has items from more than one entity, the Sage invoice is raised through Ardmore HOME (one invoice, all lines) and the receipt is posted to Ardmore Home too; Ardmore sorts the inter-entity split internally. CONFIRMED (Russell, 16 Oct): a single-entity sale still posts to its own entity. So the posting rule at go-live = one entity on the sale -> that entity; more than one -> the whole sale to Home. BUILT 16 Oct in post-taxinvoice-to-sage / post-customerreturn-to-sage (lines to Home carry Home's VAT type; returns follow the original sale). Not yet exercised against Sage.
- **Price list:** one price list for every till, the standard retail price list, fed from Sage. (Live POS profiles currently carry the placeholder `Ardmore - Retail`.)
- **Airport (AORT) sells at retail excluding VAT.** VAT does not apply at the airport but does everywhere else. The cashier must be able to raise an invoice with or without VAT (or pick a VAT profile). DESIGN NOT AGREED YET. Open question put to Russell 16 Oct: does the airport customer pay the same number as the retail list (R1 000, no VAT) or the list price with VAT stripped (R869.57)? **Russell: "Do not update anything on this front until I confirm."**

## What we still need from Ardmore (added 16 Oct)
- Sage sales rep ids per till name, per entity (returns need them).
- Surnames for Kelly and Oscar.
- Whose VAT number, address and bank details print on the tax invoice.
- Go-live date: TARGET Monday 2 November 2026 (Russell, 16 Oct; 1 Nov is a Sunday, no trading).

## Go-live weekend (set 16 Oct)
- Sat 31 Oct: Ardmore counts Hyde Park + JHB Holding, corrects Sage.
- Sun 1 Nov: on-site training (JHB Holding + Hyde Park staff). Sage accurate by the afternoon -> switch-on Sunday afternoon/evening (lock lift, integrations' default warehouse + cash customer + rep, first full stock pull, count sheets moved in as transfers, training company retired, passwords).
- Mon 2 Nov: start of business live.

## Still to come
- Rest is in Russell's notebook / the Go-Live Plan document.
