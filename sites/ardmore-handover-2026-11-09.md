# Ardmore: hand-over, 9 Nov 2026

Read this first on any machine, then `sites/ardmore.md` (latest entries) and
`sites/ardmore-sunday-2026-11-08/README.md` (the step-by-step log of the 8 Nov work).

Site: `ardmoreceramics.c.frappe.cloud` (MCP `frappe-ardmore`). Helpdesk: `www.nesterp.co.za`
(MCP `frappe-nesterp`). Live and trading: nothing on Live during trading hours except what
Russell names.

## Picking up on another machine

1. Pull or clone the repos into `C:\ClaudeCode`: `CoWork_Helper`, `nest_support`,
   `nest_stock_request`, `nest_sales_history`, `nest_account_sale`, `nest_home`, `nest_help`
   (all `Syncflo-design`, HTTPS, branch `main`).
2. Copy `S:\_laptop_move\memory\` over `C:\Users\<you>\.claude\projects\C--ClaudeCode\memory\`
   (see `S:\_laptop_move\PLACE_THESE.txt`).
3. If `S:` is not mapped, the same share is `\\SYNCFLO-DESKTOP\S_Drive_Claude`.
4. The MCP connectors `frappe-ardmore` and `frappe-nesterp` must exist on that machine.
5. Pharoh's source (`SageErpNextAPI`) is on the other machine, not in `C:\ClaudeCode`.

## State, checked on Live 9 Nov

- Apps: `nest_support` 0.1.4, `nest_help` 0.0.12, `nest_stock_request` 0.7.2,
  `nest_sales_history` 0.1.5, `nest_account_sale` 0.1.1, `nest_home` 0.0.32. All pushed.
- KSI-00018 repair: all 85 items done, none failed, nothing queued.
- Open Ardmore tickets: 0128 (Quotes) and 0148 (Online stock), left open until staff have
  tried them. Everything else Resolved or Closed.
- The three scripts below were last saved 8 Nov 12:37. The copies in
  `sites/ardmore-sunday-2026-11-08/server/` and `patched/` match them.

## What runs now

**Imports to Sage.** Server Script `post-pending-items-to-sage`, cron `*/5`, `PHAROH_READY = 1`.
`Item.custom_sage_post_status` says what an item needs:
- `Create`: created in Home, Fashion and Ceramics with qty 0, then the opening qty is added in its
  own company by stock adjustment at the sheet's Item Cost.
- `Update`: re-imported item; category and the sheet's wholesale go to Sage.
- `Repair`: one-off (KSI-00018): created where missing, then category, wholesale, retail.

`Item.custom_sage_adjust_qty` is stock still owed to Sage, with its own try counter
`custom_sage_adjust_attempts`. Pharoh calls: `post-new-item-to-sage`, `update-item-in-sage`,
`post-item-adjustment-to-sage`.

**Importers** (`Kiln Sheet Importer - Import`, `Home Fashion Importer - Import`):
- Kiln: one piece per SKU. An existing code never adds stock. Imports into `Main Distribution - A`.
- Home/Fashion: new code is created; an existing code has the sheet qty added, in ERPNext and Sage.
  Imports into `JHB Atrium Home - A` or `JHB Atrium Fashion - A`.
- Item Category and wholesale follow the sheet on existing items. Retail never does (Sage owns it).

**Sage cost.** A create with qty above 0 makes Sage cost the stock from the selling price, and Pharoh
will not change that, hence qty 0 then adjustment. The adjustment's cost REPLACES Sage's average
(Russell chose the sheet cost, not a weighted average).

**Till tickets.** `POS Profile.custom_till_login` marks a shared login (Hyde Park = hdsqpos).
`nest_support` asks "Who is logging this?" and raises the ticket with that
`Sales Person.custom_email`, so replies go to that rep only. Staff add their own email on their
Sales Person record.

**Also switched on 8 Nov:** Quote button, Sales Other line (Home account 2468754 only), Online
auto-transfer, receipt layout and footer, End of Day reports.

## Open

1. **Price sync adds VAT twice? Waiting on Russell.** `get-additional-prices-for-erpnext` multiplies
   the list rate by 1.15, but on Sage TEST that rate is already the inclusive price (sent 250 incl /
   217.39 excl, Sage holds both, endpoint returns 250). Overnight it wrote SMA503NOV26 to
   `Fashion - Wholesale - Local` at R10,120; the sheet says R8,800. Sage itself is right. Question
   put to him: is TABPPR's Home wholesale in Sage R2,100 or R2,415 (ERPNext shows R2,415)? If R2,100,
   every extra price list has been 15% high. He has said no changes to the price sync, so ask first.
2. **Ceramics/ACA till.** Russell: use the Sage Item price, price lists only if it is 0. Catch:
   Ceramics' default list is Wholesale, so that price is wholesale (SMA503NOV26 R8,800 against R14,000
   retail). Settle before building. `Ardmore - Retail` holds that wholesale figure; left as is.
3. **Ticket page not tested on a real till login.** Log one ticket as hdsqpos.
4. **Godin Ndlovu and Leah Masoka have no email** on their Sales Person records. Until they do, their
   tickets stay on hdsqpos and replies bounce.
5. **0150 count sheet:** 0.7.2 is installed; nobody has opened a sheet to confirm.
6. **Staff try 0128 and 0148**; the first real Online sale proves the auto-transfer.
7. **Delete test items** ZZCOST0811A, ZZCAT0811B, ZZFIX0811C (TEST company, came in through the Sage
   TEST sync). Not during trading.
8. **New imported items' prices are still stamped** `custom_from_sheet`, so the price sync skips
   them. Re-imports are no longer stamped. Russell has not decided.
9. **Pharoh:** at its last report the deployed code was an uncommitted working copy. Not checked since.
10. **Staff guides out of date** (`S:\Ardmore`, generators in `_uatdoc\`): Getting Stock In still says
    the sheet never changes a price and still names the training company and warehouses; the POS
    guide has no Quotes, Sales Other or ticket logging. In-app help for the two importers has the
    same old price wording.
11. Not requested yet: Sales Other accounts for Ceramics and Fashion; Home till prices refresh only
    once a day, so a new piece has no till price until the next morning.

## Working rules that bit us

- Check live data before repeating any claim from a note or another session.
- Keep it simple. Do what was asked, and raise other findings in one line.
- Russell runs all git. Never touch `Item.custom_category`. Sage drives the price lists.
- Patching a Live script: temp API Server Script, anchor replace, compare a fingerprint before and
  after, delete the temp script. Test by ending the request in `frappe.throw` so it rolls back.
  Anything sent to Sage is not rolled back, so use the Sage TEST company.
