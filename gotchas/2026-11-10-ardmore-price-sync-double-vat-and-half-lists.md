# Ardmore price sync: VAT added twice, lists read half way, retail taken from Sage's default list (10 Nov 2026)

**Domain:** ERPNext / Sage price sync (Server Scripts on ardmoreceramics.c.frappe.cloud)
**Supersedes:** step 2 of `2026-08-12-price-list-holding-two-vat-conventions-at-once.md` ("gross the sync up by 1.15").

## Three faults, one symptom

Nozy saw Ceramics items with Retail = Wholesale in ERPNext. Behind it:

1. **VAT added twice.** Pharoh's `get-additional-prices-for-erpnext` feed returns Sage's **PriceInclusive**
   (proven: SMA503NOV26's Fashion wholesale comes back as 8,800, exactly what was posted as priceInclusive). The sync
   still multiplied by 1.15 (the August fix, when the feed was believed to be ex-VAT), so every additional list in
   ERPNext was 15% high, e.g. Fashion wholesale 10,120 instead of 8,800.
2. **Lists read half way.** That feed's `totalResults` is what is LEFT after `skipQty`, not the list total (27,772 at
   skip 0, 13,772 at skip 14,000). The old end test `skip >= total` stopped every list half way, so the newest
   items (highest Sage ids, e.g. a new kiln sheet) never arrived. A list now ends at an empty page.
3. **Retail taken from Sage's default list.** `get-inventory-for-erpnext` wrote the price on the Sage item itself into
   Retail. That price belongs to the company's default list, which is Retail for Home and Fashion but **Wholesale for
   Ceramics**, so Ceramics items showed wholesale as retail.

## Fix (Russell's rules: incl VAT is the price, ex VAT worked backwards; prices go to lists by NAME)

- Price sync stores the feed's incl price as it comes; ends a list at an empty page.
- Both syncs route by list name: `RETAIL_LIST` / `WHOLESALE_LIST` per company (the same names
  `post-pending-items-to-sage` sends the kiln sheet's prices to). The price on the Sage item goes to whichever list
  Sage flags as the company's default (`Price List.custom_is_default`, refreshed hourly), so Ardmore can change the
  default in Sage and retail and wholesale never swap.
- **Consumers that compensated for the +15% had to change with it.** `post-intercompany-transfer-to-sage` divided
  the list price by 1.15 TWICE (ticket 0138, 3 Nov) - now once. `post-intercompany-sale-to-sage` already divided once
  (so before this fix it would have posted 15% high; nothing had posted). Search for `VAT_RATE / 100)` before
  touching the price basis again.
- Price sync schedule `*/5 0-11 * * *`: idles once a day's refresh is done.

## Recovery

Snapshot of every touched price before the change: private file
`/private/files/price-snapshot-before-fix-2026-11-10.json` (23,657 Item Prices, 11,855 Ceramics items).
Disabled helpers left on the site: `tmp-price-probe`, `tmp-price-snapshot`, `tmp-ceramics-wholesale`,
`tmp-script-patch`.

## Import path checked the same day

- `post-pending-items-to-sage` sent the sheet's RETAIL as the price on the new Sage item. That price belongs to the
  company's default list, so a Ceramics create put retail into Sage's Wholesale. It now sends the default list's price
  (`DEFAULT_LIST` from `custom_is_default`). The `prices` array already routed retail and wholesale by list name.
- `Home Fashion Importer - Import` now always works ex VAT back from incl (an ex-only cell still works).
- The sheet's Fashion wholesale now also goes to "Fashion - Wholesale - Ardmore standalone stores" (the list the
  intercompany Fashion pairs read): `EXTRA_WHOLESALE` in post-pending-items-to-sage for Sage, and an unstamped row
  written by the Home Fashion importer so ERPNext has it at once (Russell, 10 Nov 2026).
