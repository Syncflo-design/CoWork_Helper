Pharoh (SageErpNextAPI): finish, deploy and prove the item category + price-list changes for Ardmore ERPNext

Context
- Ardmore's ERPNext now sends imported items to Sage through a background job (Server Script
  "post-pending-items-to-sage", every 5 minutes, 25 items per run, one Sage company at a time:
  Home, then Fashion, then Ceramics). Stage 1 is live and uses post-new-item-to-sage exactly as it is today.
- Stage 2 switches on once Pharoh does what is below and it is proven on Sage TEST. The work was
  started on this machine on 6 Nov 2026 in SageErpNextAPI (it built, but was not committed or deployed,
  and its Sage TEST run was not finished). Check that work against this list; finish what is missing.
- Do not commit, push or deploy yourself. Give Russell the exact Git Bash commands and the deploy steps.

Every call: POST https://pharoh.co.za/api/InventorySync/<endpoint>?apikey=<company api key>
body: {"credentials": {"loginName": "...", "loginPwd": "...", "useOAuth": false, "sessionToken": null, "provider": null},
       "item": {...}}

1. post-new-item-to-sage (exists - extend it, do not break it)
   - item, as today: ID (0), Code, Description, Active, Physical, Unit, PriceExclusive, PriceInclusive,
     TaxTypeIdSales, TaxTypeIdPurchases, LastCost, AverageCost, QuantityOnHand, Created, Modified.
   - NEW, optional:
     - category: text, the Sage item category name. Create it in that Sage company when it does not exist.
     - prices: [{"priceListId": int, "priceInclusive": number, "priceExclusive": number}]
   - A call WITHOUT category and prices must behave exactly as it does today (stage 1 depends on it).
   - If the item code already exists in that Sage company: write nothing, return HTTP 200 with
     alreadyExisted: true (ERPNext then calls update-item-in-sage).

2. update-item-in-sage (new)
   - item: {"code": "...", "category": "..." (optional), "prices": [...] (optional)}  (id instead of code also fine)
   - Changes ONLY the category and the price lists sent. Never quantity, cost, description, other price lists.
   - Item not found in that Sage company: HTTP 404.

3. Response, both endpoints (ERPNext reads exactly these keys)
   - The Sage item id as one of: SelectionID / selectionId / id / ID
   - success: true/false   (HTTP 200 with success false is treated as a failure)
   - alreadyExisted: true/false
   - categoryResult: {"status": "set" | "created" | "unchanged" | "notFound" | "failed" | "notApplied", ...}
     (ERPNext treats notFound and failed as a problem)
   - priceResults: [{"priceListId": int, "status": "saved" | "unchanged" | "failed" | "notApplied", "message": "..."}]
     (ERPNext treats failed as a problem and shows the message)

4. Throttling and timing
   - When Sage asks to slow down, answer HTTP 503 (or 429) with Retry-After. ERPNext stops that run and
     retries on the next one; never retry immediately inside Pharoh.
   - Keep every call well under 60 seconds. ERPNext's run has 240 seconds for up to 25 items x 3 companies.

5. Price rules ERPNext follows (confirm Pharoh handles them)
   - Each price entry has both prices above zero and inclusive not below exclusive.
   - New items and repairs send the wholesale AND retail list of that company; a re-import update sends
     wholesale only.
   - The company's DEFAULT list entry sets the item's own price; when prices are sent, the top-level
     PriceInclusive/PriceExclusive is ignored.
   - Price list ids (default first):
     Home: Retail Price 130577 (default), Wholesale Price 130578
     Fashion: Retail - Local 256723 (default), Wholesale - Local 356625 (the workbook wholesale goes here)
     Ceramics: Wholesale 130535 (default), Retail 130536
     TEST: Default 605948, Retail 605949, Wholesale 605950

6. Look-up by code (exists - confirm it works for all three companies, Fashion included)
   - get-item-selectionid-for-erpnext, 10 codes per call, returns the Sage ids of the codes that exist.
   - Needed for the repair: 85 items from kiln sheet KSI-00018 (6 Nov) exist in Sage Home and Ceramics but
     have no Fashion link in ERPNext. The repair will look each one up in Fashion and create it there if missing.

Prove it on Sage TEST (the "Ardmore Ceramics TEST" credentials) after deploying, and report each result:
 a. Create a new code with a new category name and prices for TEST Retail 605949 and Wholesale 605950,
    plus Default 605948. Check in Sage: category created and set, all three lists, own price = the default
    entry, quantity and cost as sent.
 b. Create the same code again: alreadyExisted true, nothing changed in Sage.
 c. update-item-in-sage with only the Wholesale list: wholesale changed; retail, default/own price, quantity
    and cost unchanged.
 d. update-item-in-sage with a different category: category changed, nothing else.
 e. update-item-in-sage for a code that does not exist: 404.
 f. A create WITHOUT category/prices still works exactly as before (what stage 1 sends today).
 g. Rapid calls: confirm 503 + Retry-After comes back rather than a hang or a 500.
 h. Nothing else changed for the other calls ERPNext already uses: post-taxinvoice-to-sage (including
    lineType 1 account lines), post-customerreturn-to-sage, the intercompany posts, the inventory and
    qty-on-hand syncs, get-item-selectionid-for-erpnext.

Report back (I will paste it into the ERPNext session):
- the commit and version deployed to pharoh.co.za;
- the result of a-h with the values Sage shows;
- any key or field name that differs from this list, and anything that could not be proven
  (for example whether saving touches other lists, quantity or cost).
