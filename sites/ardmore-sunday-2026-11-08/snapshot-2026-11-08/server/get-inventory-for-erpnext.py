def sage_number(val):
    # Sage sends decimals with a COMMA separator: "208,696" means 208.696.
    # Frappe's flt() treats a comma as a THOUSANDS separator and strips it,
    # turning that into 208696 - a x1000 valuation error (seen on FABFCJ /
    # FABCCAV). Parse it explicitly instead of letting flt() guess.
    if val is None:
        return 0.0
    s = str(val).strip().replace(' ', '').replace(u'\xa0', '')
    if not s:
        return 0.0
    if (',' in s) and ('.' in s):
        # Both present - whichever comes last is the decimal separator.
        if s.rfind(',') > s.rfind('.'):
            s = s.replace('.', '').replace(',', '.')
        else:
            s = s.replace(',', '')
    elif ',' in s:
        s = s.replace(',', '.')
    try:
        return float(s)
    except Exception:
        return 0.0

now = frappe.utils.now_datetime()
default_company = frappe.db.get_single_value("Global Defaults", "default_company")
# The one retail price list every till sells from (agreed on site 14 Oct 2026). The Sage
# standard selling price of the item's OWN company lands here within one sync run.
TILL_PRICE_LIST = "Ardmore - Retail"

def dedupe_item_defaults(idoc):
    seen = []
    kept = []
    for d in (idoc.item_defaults or []):
        if d.company and d.company not in seen:
            seen.append(d.company)
            kept.append(d)
    idoc.set("item_defaults", kept)

company_integrations = frappe.get_all("Company Sage Integration", fields=["name", "company"])

for integration in company_integrations:
    try:
        sage = frappe.get_doc("Company Sage Integration", integration.name)

        retry_after = sage.custom_sage_retry_after
        if retry_after and now < frappe.utils.get_datetime(retry_after):
            continue

        apikey = sage.get_password("api_key")
        loginName = sage.username
        loginPwd = sage.get_password("password")

        sync_start = frappe.utils.nowdate()
        lastDate = sage.custom_last_inventory_sync or "1970-01-01"

        # BACKFILL (Russell, 2026-10-20): a date in custom_backfill_created_since switches this
        # company to a one-off pull of EVERY Sage item created on/after it - sold and inactive
        # included, they land disabled - 400 a run, resuming from custom_backfill_skip, until
        # Sage runs out; then the date clears itself and the normal pull resumes.
        backfill_since = sage.get("custom_backfill_created_since")
        backfill = 1 if backfill_since else 0
        skipQty = int(sage.get("custom_backfill_skip") or 0) if backfill else 0
        pages_left = 4
        has_more = True
        throttled = False

        while has_more:
            if backfill:
                url = f"https://pharoh.co.za/api/InventorySync/get-inventory-for-erpnext?apikey={apikey}&lastDate=1970-01-01&createdSince={backfill_since}&InclZeroOnHand=true&skipQty={skipQty}"
            else:
                url = f"https://pharoh.co.za/api/InventorySync/get-inventory-for-erpnext?apikey={apikey}&lastDate={lastDate}&skipQty={skipQty}"
            payload = {"loginName": loginName, "loginPwd": loginPwd, "useOAuth": False, "sessionToken": None, "provider": None}

            try:
                response = frappe.make_post_request(url, json=payload)
            except Exception as http_err:
                status = None
                try:
                    status = http_err.response.status_code
                except Exception:
                    status = None
                if status == 503 or status == 429:
                    wait_secs = 5
                    try:
                        ra = http_err.response.headers.get("Retry-After")
                        if ra:
                            wait_secs = int(float(ra))
                    except Exception:
                        pass
                    try:
                        body = http_err.response.json()
                        if body and body.get("retryAfterSeconds"):
                            wait_secs = int(float(body.get("retryAfterSeconds")))
                    except Exception:
                        pass
                    block_until = frappe.utils.add_to_date(now, seconds=wait_secs)
                    frappe.db.set_value("Company Sage Integration", integration.name, "custom_sage_retry_after", block_until)
                    frappe.log_error(message=f"Pharoh asked us to wait {wait_secs}s (until {block_until})", title=f"Sage backoff {integration.company}"[:140])
                    throttled = True
                    break
                else:
                    raise

            items = response.get("items") or []
            total = response.get("totalResults", 0)
            returned = response.get("returnedResults", 0)

            if not items:
                break

            for item_data in items:
                try:
                    item_code = item_data.get("item_code")
                    if not item_code:
                        continue

                    uom = item_data.get("stock_uom")
                    if not uom:
                        uom = "each"

                    if not frappe.db.exists("UOM", uom):
                        uom_doc = frappe.new_doc("UOM")
                        uom_doc.uom_name = uom
                        uom_doc.enabled = 1
                        uom_doc.insert(ignore_permissions=True)

                    item_group = item_data.get("item_group") or "All Item Groups"
                    if not frappe.db.exists("Item Group", item_group):
                        if not frappe.db.exists("Item Group", "All Item Groups"):
                            item_group = "Products"
                        group_doc = frappe.new_doc("Item Group")
                        group_doc.item_group_name = item_group
                        group_doc.parent_item_group = "All Item Groups"
                        group_doc.is_group = 0
                        group_doc.insert(ignore_permissions=True)

                    if frappe.db.exists("Item", item_code):
                        item_doc = frappe.get_doc("Item", item_code)
                    else:
                        item_doc = frappe.new_doc("Item")
                        item_doc.item_code = item_code
                        # A new doc pre-fills the Category Select with its FIRST option (Ceramics),
                        # so a Home/Fashion item looked foreign to the company pulling it, the
                        # own-company rule skipped item_group, and the save failed with
                        # "item_group" mandatory (2026-10-20, the VSS scarves). A brand-new item
                        # belongs to the company that brings it in.
                        item_doc.custom_category = integration.company

                    # OWN-COMPANY RULE (2026-10-16): the same item exists in all three Sage
                    # companies, and this loop used to let each company overwrite the ONE
                    # ERPNext item's selection id, tax type, item group and retail price -
                    # last company to run won (Nozy's "random" price changes). Now only the
                    # item's own category company writes those item-level fields. The
                    # per-company Sage Item Selection rows below are still kept for every
                    # company, because posting needs them all.
                    if not item_doc.get("custom_category"):
                        item_doc.custom_category = integration.company
                    own = (item_doc.get("custom_category") == integration.company)
                    item_doc.item_name = item_data.get("item_name") or f"{item_code} - Item"
                    item_doc.description = item_data.get("description") or item_doc.item_name
                    if own:
                        item_doc.item_group = item_group
                    item_doc.is_stock_item = item_data.get("is_stock_item", 0)
                    if not frappe.db.exists("Item", item_code):
                        item_doc.stock_uom = uom

                    # NOTE: standard_rate is deliberately NOT set here.
                    # Assigning it makes ERPNext write an Item Price to the DEFAULT
                    # selling price list ("Standard Selling"), which is disabled on this
                    # site - every such item then failed with "The price list Standard
                    # Selling does not exist or is disabled" and never synced.
                    # Selling prices are owned by the dedicated price sync
                    # (get-additional-prices-for-erpnext), which writes each Sage price
                    # list to its correctly mapped ERPNext list via
                    # Price List.custom_sage_pricelist_id (e.g. "Ardmore Ceramics TEST -
                    # Retail"). Do not reintroduce standard_rate here.
                    sage_price_incl = sage_number(item_data.get("standard_rate_incl"))
                    sage_price_excl = sage_number(item_data.get("standard_rate"))
                    # Sold / inactive items (Russell, 2026-10-20): ex-VAT price only - no
                    # incl-VAT price and no till price row.
                    is_inactive = 1 if item_data.get("disabled", 0) else 0
                    if own:
                        if sage_price_excl > 0:
                            item_doc.custom_retail_price_excl_vat = sage_price_excl
                        if is_inactive:
                            item_doc.custom_retail_price_incl_vat = 0
                        else:
                            item_doc.custom_retail_price_incl_vat = sage_price_incl
                    # Valuation Rate is owned by Item_Cost, never by Sage. Sage returns a
                    # figure it calls valuation_rate that is sometimes the SELLING
                    # price, which valued stock at retail and made cost of sales
                    # equal revenue.
                    sheet_cost = sage_number(item_doc.get("custom_item_cost"))
                    if sheet_cost > 0:
                        item_doc.valuation_rate = sheet_cost
                    item_doc.is_sales_item = item_data.get("is_sales_item", 0)
                    item_doc.is_purchase_item = item_data.get("is_purchase_item", 0)
                    item_doc.disabled = item_data.get("disabled", 0)

                    sage_item_id = (item_data.get("SelectionID") or
                        item_data.get("selectionId") or
                        item_data.get("custom_sage_selection_id") or
                        item_data.get("id"))
                    if sage_item_id and own:
                        item_doc.custom_sage_selection_id = str(sage_item_id)

                    tax_type_id = item_data.get("tax_typeid_sales")
                    if tax_type_id and own:
                        item_doc.custom_sage_tax_type_id = tax_type_id

                    # Sage item user fields (Russell, 2026-10-20): 1 = Sculptor, 2 = Thrower,
                    # 3 = Painter; the numeric fields are the rates in the same order. Own
                    # company only; a blank in Sage never wipes what the kiln sheet set.
                    if own:
                        artists = [["text_user_field1", "custom_sculptor_c", "numeric_user_field1", "custom_sculptor_rate"], ["text_user_field2", "custom_thrower_c", "numeric_user_field2", "custom_thrower_rate"], ["text_user_field3", "custom_painter_c", "numeric_user_field3", "custom_painter_rate"]]
                        for a in artists:
                            nm = str(item_data.get(a[0]) or "").strip()
                            if nm and nm != "0":
                                if not frappe.db.exists("Manufacturer", nm):
                                    maker = frappe.new_doc("Manufacturer")
                                    maker.short_name = nm
                                    maker.full_name = nm
                                    maker.insert(ignore_permissions=True)
                                item_doc.set(a[1], nm)
                            rt = sage_number(item_data.get(a[2]))
                            if rt > 0:
                                item_doc.set(a[3], rt)

                    # NOTE: custom_size is deliberately LEFT ALONE.
                    # This used to be forced to None on every sync, which silently wiped
                    # the Size the kiln / Home-Fashion importers had mapped from the
                    # sheet - minutes after the import. It was almost certainly a
                    # workaround for Select-validation errors ("Size cannot be ..."),
                    # which are now fixed properly by having every real value in the
                    # custom_size options. Sage does not own Size, so the sync must not
                    # clear it. Do not reintroduce.

                    # Neutralise the bench hook that auto-adds a duplicate Item Default:
                    # keep one row per company, and seed the default company up front.
                    dedupe_item_defaults(item_doc)
                    if not (item_doc.item_defaults or []):
                        if default_company:
                            item_doc.append("item_defaults", {"company": default_company})

                    item_doc.save(ignore_permissions=True)

                    # Sage standard selling price -> the till price list (Russell, 2026-10-16:
                    # "if they change the Sage standard selling price, it updates the POS
                    # instances"). Own company only. Once an item is in Sage, Sage wins over
                    # the sheet: a sheet price cannot be pushed into an existing Sage item.
                    if own and not is_inactive and sage_price_incl > 0 and frappe.db.exists("Price List", TILL_PRICE_LIST):
                        ip_name = frappe.db.get_value("Item Price", {"item_code": item_code, "price_list": TILL_PRICE_LIST, "selling": 1}, "name")
                        if ip_name:
                            if float(frappe.db.get_value("Item Price", ip_name, "price_list_rate") or 0) != sage_price_incl:
                                frappe.db.set_value("Item Price", ip_name, "price_list_rate", sage_price_incl)
                        else:
                            ip = frappe.new_doc("Item Price")
                            ip.item_code = item_code
                            ip.price_list = TILL_PRICE_LIST
                            ip.price_list_rate = sage_price_incl
                            ip.selling = 1
                            ip.currency = "ZAR"
                            ip.insert(ignore_permissions=True)

                    if sage_item_id:
                        sel_name = item_code + "-" + integration.company
                        if frappe.db.exists("Sage Item Selection", sel_name):
                            frappe.db.set_value("Sage Item Selection", sel_name, "selection_id", str(sage_item_id))
                        else:
                            sel = frappe.new_doc("Sage Item Selection")
                            sel.item_code = item_code
                            sel.company = integration.company
                            sel.selection_id = str(sage_item_id)
                            sel.insert(ignore_permissions=True)

                except Exception as inner:
                    frappe.log_error(message=str(inner), title=f"Error processing Item {item_data.get('item_code')}")

            frappe.db.commit()

            skipQty = skipQty + returned
            has_more = skipQty < total
            if backfill:
                frappe.db.set_value("Company Sage Integration", integration.name, "custom_backfill_skip", skipQty)
                frappe.db.commit()
                pages_left = pages_left - 1
                if not has_more:
                    frappe.db.set_value("Company Sage Integration", integration.name, "custom_backfill_created_since", None)
                    frappe.db.set_value("Company Sage Integration", integration.name, "custom_backfill_skip", 0)
                    frappe.db.commit()
                    frappe.log_error(message=f"{integration.company}: backfill of items created since {backfill_since} finished at {skipQty} items.", title="Sage item backfill finished")
                elif pages_left <= 0:
                    break

        if not throttled and not backfill:
            if retry_after:
                frappe.db.set_value("Company Sage Integration", integration.name, "custom_sage_retry_after", None)
            frappe.db.set_value("Company Sage Integration", integration.name, "custom_last_inventory_sync", sync_start)

    except Exception as outer:
        frappe.log_error(message=str(outer), title=f"Sage Item Sync Fatal Error for {integration.company}"[:140])
