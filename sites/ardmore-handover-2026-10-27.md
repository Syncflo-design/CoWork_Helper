# Ardmore: hand-over to the site laptop, 27 Oct 2026 (go-live Mon 2 Nov)

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
UAT-* items exist only in ERPNext, not in Sage TEST, so a till sale of them FAILS at the Sage
step ("No Sage SelectionID") - sell the FABCB fabrics (they exist in Sage TEST) or create the
UAT items in Sage TEST first (the loader script for that was deleted; rebuild if needed).

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
