# SEND IMPORTED ITEMS TO SAGE, 25 AT A TIME (Russell, 6 Nov 2026: the system batches, not the users).
# Scheduler Event, cron */5 * * * *. Item.custom_sage_post_status says what an item still needs:
#   Create  new from an importer: created in Home, Fashion and Ceramics with qty 0; the opening qty follows in its own
#           company as a stock adjustment at the sheet's Item Cost (Sage costs stock on a create from the selling price)
#   Update  re-imported: category and the workbook's wholesale, in ERPNext's words, go to Sage
#   Repair  one-off for KSI-00018: created where Sage lacks it (Fashion), then category, wholesale and retail
#   Done / Failed   finished; Failed holds the reason in custom_sage_post_error after five tries
# Item.custom_sage_adjust_qty is stock still to add in the item's own Sage company: a new item's opening qty, or what a
# Home/Fashion import added to an existing item. It goes by item adjustment at the sheet's Item Cost (Russell, 8 Nov 2026).
# Each item is committed as it finishes, so nothing can be in Sage and rolled back here. A 503 from Pharoh stops
# the run; the item stays queued for the next one. Ceramics goes last: it is the item price the sync copies back.
PHAROH_READY = 1  # Pharoh's category, prices and update-item-in-sage deployed and proven on Sage TEST (Pharoh report, 8 Nov 2026)
BATCH = 25
TIME_LIMIT = 240  # seconds; a cron job on the default queue is killed at 300
MAX_ATTEMPTS = 5
VAT = 1.15
COMPANIES = ["Home", "Fashion", "Ceramics"]
RETAIL_LIST = {"Home": "Home - Retail Price", "Fashion": "Fashion - Retail - Local", "Ceramics": "Ceramics - Retail"}
WHOLESALE_LIST = {"Home": "Home - Wholesale Price", "Fashion": "Fashion - Wholesale - Local", "Ceramics": "Ceramics - Wholesale"}

started = frappe.utils.now_datetime()
wanted = ["Create", "Update", "Repair"] if PHAROH_READY else ["Create"]
queue = frappe.get_all("Item", filters={"custom_sage_post_status": ["in", wanted]}, pluck="name", order_by="creation asc", limit_page_length=BATCH)

ADJ_FIELDS = ["name", "custom_category", "custom_sage_adjust_qty", "custom_sage_adjust_attempts", "custom_item_cost", "valuation_rate", "custom_sage_selection_id", "custom_sage_post_status", "custom_sage_post_error"]


def owed_stock(fields, batch, max_attempts):
    # Items still owing Sage stock, oldest first. Those waiting to be created or given up on are left out here, not
    # in the loop, so they can never fill the batch and block the rest.
    rows = frappe.get_all("Item", filters={"custom_sage_adjust_qty": [">", 0]}, fields=fields, order_by="modified asc", limit_page_length=1000)
    return [r for r in rows if r.custom_sage_post_status != "Create" and int(r.custom_sage_adjust_attempts or 0) < max_attempts][:batch]


adjust = owed_stock(ADJ_FIELDS, BATCH, MAX_ATTEMPTS)

conn = {}
list_id = {}
if queue or adjust:
    for c in COMPANIES:
        sage = frappe.get_doc("Company Sage Integration", c)
        conn[c] = {
            "apikey": sage.get_password("api_key"),
            "tax_id": sage.tax_id,
            "credentials": {"loginName": sage.username, "loginPwd": sage.get_password("password"), "useOAuth": False, "sessionToken": None, "provider": None}
        }
        list_id[RETAIL_LIST[c]] = int(frappe.db.get_value("Price List", RETAIL_LIST[c], "custom_sage_pricelist_id"))
        list_id[WHOLESALE_LIST[c]] = int(frappe.db.get_value("Price List", WHOLESALE_LIST[c], "custom_sage_pricelist_id"))

throttled = False
for code in queue:
    if throttled or frappe.utils.time_diff_in_seconds(frappe.utils.now_datetime(), started) > TIME_LIMIT:
        break

    item = frappe.get_doc("Item", code)
    status = item.custom_sage_post_status
    own = (item.custom_category or "").strip()
    retail = float(item.custom_retail_price_incl_vat or 0)
    wholesale = float(item.custom_wholesale_price_incl_vat or 0)
    category = item.item_group if item.item_group and item.item_group != "All Item Groups" else None
    problems = []

    for c in COMPANIES:
        if status == "Create" and own not in COMPANIES:
            problems.append("Category '" + own + "' is not Home, Fashion or Ceramics, so the opening stock has no Sage company")
            break
        prices = []
        if wholesale > 0:
            prices.append({"priceListId": list_id[WHOLESALE_LIST[c]], "priceInclusive": wholesale, "priceExclusive": round(wholesale / VAT, 2)})
        if retail > 0 and status != "Update":
            prices.append({"priceListId": list_id[RETAIL_LIST[c]], "priceInclusive": retail, "priceExclusive": round(retail / VAT, 2)})

        extra = {}
        if PHAROH_READY:
            extra["prices"] = prices
            if category:
                extra["category"] = category

        if status in ["Create", "Repair"]:
            body_item = {
                "ID": 0,
                "Code": item.item_code,
                "Description": item.item_name or item.description,
                "Active": True if item.disabled == 0 else False,
                "Physical": True if item.is_stock_item else False,
                "Unit": item.stock_uom or "Each",
                "PriceExclusive": round(retail / VAT, 2),
                "PriceInclusive": retail,
                "TaxTypeIdSales": conn[c]["tax_id"],
                "TaxTypeIdPurchases": conn[c]["tax_id"],
                # the sheet's Item Cost (Russell, 8 Nov 2026): Sage takes the cost from LastCost
                "LastCost": float(item.custom_item_cost or item.last_purchase_rate or 0),
                "AverageCost": float(item.valuation_rate or 0),
                "QuantityOnHand": 0,  # the opening qty follows as a stock adjustment, below
                "Created": frappe.utils.format_datetime(item.creation, "yyyy-MM-dd'T'HH:mm:ss"),
                "Modified": frappe.utils.format_datetime(item.modified, "yyyy-MM-dd'T'HH:mm:ss")
            }
            body_item.update(extra)
            url = "https://pharoh.co.za/api/InventorySync/post-new-item-to-sage?apikey=" + conn[c]["apikey"]
        else:
            body_item = {"code": item.item_code}
            body_item.update(extra)
            url = "https://pharoh.co.za/api/InventorySync/update-item-in-sage?apikey=" + conn[c]["apikey"]

        existed = False
        try:
            resp = frappe.make_post_request(url, json={"credentials": conn[c]["credentials"], "item": body_item}, headers={"Content-Type": "application/json"}) or {}
            existed = resp.get("alreadyExisted") == True
            # Already in this Sage company: create wrote nothing, so bring its category and prices up to date.
            if status in ["Create", "Repair"] and PHAROH_READY and existed:
                resp = frappe.make_post_request("https://pharoh.co.za/api/InventorySync/update-item-in-sage?apikey=" + conn[c]["apikey"], json={"credentials": conn[c]["credentials"], "item": {"code": item.item_code, "category": category, "prices": prices}}, headers={"Content-Type": "application/json"}) or {}
        except Exception as e:
            http_status = None
            body = ""
            try:
                http_status = e.response.status_code
                body = str(e.response.text)[:200]
            except Exception:
                body = ""
            if http_status == 503 or http_status == 429:
                # Throttled part-way through a create: Sage may already hold the item, so its opening qty is owed.
                if status == "Create" and c == own and float(item.custom_opening_qty or 0) > 0:
                    try:
                        part = e.response.json() or {}
                        if part.get("id") and not part.get("alreadyExisted"):
                            owed = float(frappe.db.get_value("Item", code, "custom_sage_adjust_qty") or 0) + float(item.custom_opening_qty or 0)
                            frappe.db.set_value("Item", code, "custom_sage_adjust_qty", owed, update_modified=False)
                    except Exception:
                        pass
                throttled = True
                break
            if http_status == 404 and status == "Update":
                continue  # not in this Sage company, so nothing to update there
            problems.append(c + ": " + str(http_status or "") + " " + (body or str(e)[:200].replace(conn[c]["apikey"], "***")))
            continue

        # HTTP 200 can still be a partial failure.
        if resp.get("success") == False:
            problems.append(c + ": Sage did not accept it")
        cat_result = resp.get("categoryResult") or {}
        if cat_result.get("status") in ["failed", "notFound"]:
            problems.append(c + ": category " + str(cat_result.get("status")))
        for p in (resp.get("priceResults") or []):
            if p.get("status") == "failed":
                problems.append(c + ": price list " + str(p.get("priceListId")) + " " + str(p.get("message") or "failed"))

        sage_id = resp.get("SelectionID") or resp.get("selectionId") or resp.get("id") or resp.get("ID")
        if sage_id and status in ["Create", "Repair"]:
            # Once only: a create that found the item already in Sage adds no stock. Committed at once, because the
            # next create would answer alreadyExisted and the opening qty could never be owed again.
            if c == own and not existed and float(item.custom_opening_qty or 0) > 0:
                owed = float(frappe.db.get_value("Item", code, "custom_sage_adjust_qty") or 0) + float(item.custom_opening_qty or 0)
                frappe.db.set_value("Item", code, "custom_sage_adjust_qty", owed, update_modified=False)
                frappe.db.commit()
            try:
                sel_name = item.item_code + "-" + c
                if frappe.db.exists("Sage Item Selection", sel_name):
                    frappe.db.set_value("Sage Item Selection", sel_name, "selection_id", str(sage_id))
                else:
                    sel = frappe.new_doc("Sage Item Selection")
                    sel.item_code = item.item_code
                    sel.company = c
                    sel.selection_id = str(sage_id)
                    sel.insert(ignore_permissions=True)
                if c == own:
                    frappe.db.set_value("Item", code, "custom_sage_selection_id", str(sage_id), update_modified=False)
            except Exception as e:
                problems.append(c + ": Sage id " + str(sage_id) + " not saved: " + str(e)[:150])

    if throttled:
        frappe.db.commit()
        break

    if problems:
        attempts = int(item.custom_sage_post_attempts or 0) + 1
        frappe.db.set_value("Item", code, {
            "custom_sage_post_attempts": attempts,
            "custom_sage_post_error": "; ".join(problems)[:900],
            "custom_sage_post_status": "Failed" if attempts >= MAX_ATTEMPTS else status
        }, update_modified=False)
        if attempts >= MAX_ATTEMPTS:
            frappe.log_error(message=code + ": " + "; ".join(problems), title="Sage item post failed")
    else:
        frappe.db.set_value("Item", code, {"custom_sage_post_status": "Done", "custom_sage_post_attempts": 0, "custom_sage_post_error": ""}, update_modified=False)
    frappe.db.commit()

# items created above now owe their opening qty
if queue and not throttled:
    adjust = owed_stock(ADJ_FIELDS, BATCH, MAX_ATTEMPTS)

# STOCK ADJUSTMENTS. Sage takes the adjustment's cost as the item's new average cost, so the sheet's
# Item Cost is sent (Russell, 8 Nov 2026). Once Sage has the quantity, the Sage stock sync owns the item again.
for a in adjust:
    if throttled or frappe.utils.time_diff_in_seconds(frappe.utils.now_datetime(), started) > TIME_LIMIT:
        break
    code = a.name
    own = (a.custom_category or "").strip()
    qty = float(a.custom_sage_adjust_qty or 0)
    cost = float(a.custom_item_cost or 0) or float(a.valuation_rate or 0)
    sage_id = frappe.db.get_value("Sage Item Selection", {"item_code": code, "company": own}, "selection_id") or a.custom_sage_selection_id
    problem = ""
    if own not in conn:
        problem = "category " + own + " has no Sage company"
    elif not sage_id:
        problem = own + ": item is not linked to Sage"
    else:
        stamp = frappe.utils.format_datetime(frappe.utils.now_datetime(), "yyyy-MM-dd'T'HH:mm:ss")
        try:
            body_adj = {"id": 0, "date": stamp, "itemID": int(sage_id), "averageCost": cost, "quantity": qty, "reason": "Stock added by ERPNext import", "created": stamp}
            resp = frappe.make_post_request("https://pharoh.co.za/api/InventorySync/post-item-adjustment-to-sage?apikey=" + conn[own]["apikey"], json={"credentials": conn[own]["credentials"], "adjustment": body_adj}, headers={"Content-Type": "application/json"}) or {}
            if resp.get("success") != True:
                msg = str(resp.get("errorMessage") or "")
                # until Pharoh's next deploy a throttle here is HTTP 200 with success false (Pharoh report, 8 Nov 2026)
                if "rate-limit" in msg.lower() or "pacing limit" in msg.lower():
                    throttled = True
                    break
                problem = own + ": " + (msg or "Sage did not accept the adjustment")[:300]
        except Exception as e:
            http_status = None
            body = ""
            try:
                http_status = e.response.status_code
                body = str(e.response.text)[:200]
            except Exception:
                body = ""
            if http_status == 503 or http_status == 429:
                throttled = True
                break
            problem = own + ": " + str(http_status or "") + " " + (body or str(e)[:200].replace(conn[own]["apikey"], "***"))

    # stock adds keep their own try count, so they never push a create or update to Failed or reset its count
    if problem:
        attempts = int(a.custom_sage_adjust_attempts or 0) + 1
        frappe.db.set_value("Item", code, {"custom_sage_adjust_attempts": attempts, "custom_sage_post_error": ("Stock add of " + str(qty) + ": " + problem)[:900]}, update_modified=False)
        if attempts >= MAX_ATTEMPTS:
            frappe.log_error(message=code + ": stock add of " + str(qty) + " failed: " + problem, title="Sage stock add failed")
    else:
        done = {"custom_sage_adjust_attempts": 0}
        if str(a.custom_sage_post_error or "").startswith("Stock add"):
            done["custom_sage_post_error"] = ""
        # an import that landed while this ran keeps its own quantity owed
        left = float(frappe.db.get_value("Item", code, "custom_sage_adjust_qty") or 0) - qty
        if left > 0:
            done["custom_sage_adjust_qty"] = left
        else:
            done["custom_sage_adjust_qty"] = 0
            done["custom_qty_pending_sage"] = 0
        frappe.db.set_value("Item", code, done, update_modified=False)
    frappe.db.commit()
