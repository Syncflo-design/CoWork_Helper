# Nightly self-refreshing item-price sync. Per-page commit, resumable within the night,
# and re-pulls fresh once per day (custom_sage_sync_date). Idles once done for the day.
test_companies = []        # [] = all companies
max_pages = 500            # pages per run (100 rows each)

base_url = "https://pharoh.co.za/api/AdditionalItemPricesSync/get-additional-prices-for-erpnext"
today = frappe.utils.nowdate()

created = 0
updated = 0
unchanged = 0
skipped_items = 0
errors = []
pages_done = 0
stop = False

company_rows = frappe.get_all("Company Sage Integration", fields=["name"])

for ci in range(len(company_rows)):
    if stop:
        break
    integ_name = company_rows[ci]["name"]
    try:
        sage = frappe.get_doc("Company Sage Integration", integ_name)
    except Exception as e:
        errors.append("Load " + str(integ_name) + ": " + str(e))
        continue

    company = sage.company
    if test_companies and (company not in test_companies):
        continue

    apikey = sage.get_password("api_key")
    login_name = sage.username
    login_pwd = sage.get_password("password")
    payload = {"loginName": login_name, "loginPwd": login_pwd,
               "useOAuth": False, "sessionToken": None, "provider": None}

    lists = frappe.get_all("Price List",
        filters={"custom_sage_company": company,
                 "custom_sage_pricelist_id": ["is", "set"]},
        fields=["name", "custom_sage_pricelist_id", "custom_sage_sync_done",
                "custom_sage_sync_date", "custom_sage_sync_offset"])

    for li in range(len(lists)):
        if stop:
            break
        pl_name = lists[li]["name"]
        sage_pl_id = str(lists[li]["custom_sage_pricelist_id"] or "").strip()
        if not sage_pl_id:
            continue

        sync_date = str(lists[li].get("custom_sage_sync_date") or "")
        done = lists[li].get("custom_sage_sync_done")

        # already fully refreshed today -> skip
        if sync_date == str(today) and done:
            continue

        # new day -> restart this list from the top
        if sync_date != str(today):
            skip = 0
            frappe.db.set_value("Price List", pl_name, "custom_sage_sync_offset", 0)
            frappe.db.set_value("Price List", pl_name, "custom_sage_sync_done", 0)
            frappe.db.set_value("Price List", pl_name, "custom_sage_sync_date", today)
            frappe.db.commit()
        else:
            skip = int(lists[li].get("custom_sage_sync_offset") or 0)

        while True:
            if pages_done >= max_pages:
                stop = True
                break

            url = (base_url + "?apikey=" + str(apikey) +
                   "&pricelistID=" + sage_pl_id + "&skipQty=" + str(skip))
            try:
                resp = frappe.make_post_request(url, json=payload)
            except Exception as e:
                errors.append("Fetch " + pl_name + " @" + str(skip) + ": " + str(e))
                break

            pages_done = pages_done + 1
            if not resp:
                break
            items = resp.get("items") or []
            total = resp.get("totalResults") or 0
            returned = resp.get("returnedResults") or len(items)

            for ii in range(len(items)):
                row = items[ii]
                raw = str(row.get("itemCode") or "")
                rate = row.get("priceListRate")
                if rate is None:
                    rate = 0
                # Sage prices EXCLUDE VAT. Ardmore price INCLUDING VAT in
                # round numbers and the till rings the price list rate as
                # it stands, so bring Sage onto the same basis.
                rate = round(float(rate) * 1.15, 2)
                sel_id = raw
                if sel_id[:5] == "ITEM-":
                    sel_id = sel_id[5:]
                sel_id = sel_id.strip()
                if not sel_id:
                    skipped_items = skipped_items + 1
                    continue
                # Per-company lookup (2026-10-16): the item-level selection id belongs to the
                # item's own company only; every company's id lives in Sage Item Selection.
                erp_item = frappe.db.get_value("Sage Item Selection",
                    {"selection_id": sel_id, "company": company}, "item_code")
                if not erp_item:
                    skipped_items = skipped_items + 1
                    continue
                existing_ip = frappe.db.get_value("Item Price",
                    {"item_code": erp_item, "price_list": pl_name, "selling": 1}, "name")
                try:
                    if existing_ip and frappe.db.get_value("Item Price", existing_ip, "custom_from_sheet"):
                        # The import sheet owns this price - leave it alone.
                        continue
                    if existing_ip:
                        cur = frappe.db.get_value("Item Price", existing_ip, "price_list_rate")
                        if float(cur or 0) != float(rate):
                            frappe.db.set_value("Item Price", existing_ip, "price_list_rate", rate)
                            updated = updated + 1
                        else:
                            unchanged = unchanged + 1
                    else:
                        ip = frappe.new_doc("Item Price")
                        ip.item_code = erp_item
                        ip.price_list = pl_name
                        ip.price_list_rate = rate
                        ip.selling = 1
                        ip.currency = "ZAR"
                        ip.insert(ignore_permissions=True)
                        created = created + 1
                except Exception as e:
                    errors.append(str(erp_item) + " @ " + pl_name + ": " + str(e))

            skip = skip + returned
            frappe.db.set_value("Price List", pl_name, "custom_sage_sync_offset", skip)
            frappe.db.commit()

            if returned == 0 or (total and skip >= total):
                frappe.db.set_value("Price List", pl_name, "custom_sage_sync_done", 1)
                frappe.db.commit()
                break

frappe.response["message"] = {"created": created, "updated": updated,
    "unchanged": unchanged, "skipped_items": skipped_items,
    "pages": pages_done, "errors": errors[0:20]}