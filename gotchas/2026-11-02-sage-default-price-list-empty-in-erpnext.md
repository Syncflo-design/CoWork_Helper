# Sage default price list never syncs (Ardmore, 2 Nov 2026)

**Symptom:** Hyde Park till rang wrong prices on go-live day; `Home - Retail Price` in ERPNext had
0 Item Prices although Sage Home's Retail Price list is full. Its `custom_sage_sync_offset` stayed 0
with `custom_sage_sync_done=1` every night.

**Cause:** Sage Business Cloud keeps a company's DEFAULT price list (`custom_is_default=1`) on the
item itself (`standard_rate_incl` in Pharoh's inventory feed). `AdditionalItemPricesSync` only
returns the non-default lists, so `get-additional-prices-for-erpnext` gets zero rows for any
default list: Home "Retail Price" 130577, Ceramics "Wholesale" 130535, Fashion "Retail - Local".

**Second trap:** `Ardmore - Retail` is filled by `get-inventory-for-erpnext` with the standard price
of the item's OWN category company only. Ceramics' default list is Wholesale, so Ceramics-category
items carry roughly half the retail price there.

**Fix:** Server Script `sync-home-retail-prices` (Daily Long) pages the Home inventory feed
(`lastDate=1970-01-01&InclZeroOnHand=true`) and upserts every item's `standard_rate_incl` into
`Home - Retail Price`. POS Profile `Hyde Park` (custom_sage_entity = Home) now sells from that list.
Run it on demand from Scheduled Job Type -> Execute.

**Also seen:** Stock Settings `auto_insert_price_list_rate_if_missing=1` lets a till create R0.01
Item Prices for unpriced items. Two at once makes duplicates that block saves
(ItemPriceDuplicateItem). Without deleting, expire one of the pair (valid_from = valid_upto =
yesterday), then the other saves.
