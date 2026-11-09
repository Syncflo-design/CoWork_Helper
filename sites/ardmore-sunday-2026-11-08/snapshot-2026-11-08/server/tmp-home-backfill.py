# One-off (Russell, 3 Nov 2026): items held in JHB Atrium Fashion / Main Distribution that have no Sage Home
# item. The item code is the only link between the Sage companies. For each code: look it up in Sage Home;
# if Home already has it, record Home's SelectionID; if not, create it in Home (quantity 0 - Home only owns
# what it buys) and record the SelectionID Home returns. Then read the code back from Home and correct the
# Home row if Sage holds a different ID. Only the Home row of Sage Item Selection is written; the item's own
# SelectionID (its category's company) is left alone.
#   list                    how many are left
#   run   after, count      the next `count` codes after `after` (alphabetical); call again with after = last
#   ids   fix (0/1)         items whose own SelectionID is not their category company's ID; fix=1 corrects it
if not frappe.db.exists("Has Role", {"parent": frappe.session.user, "role": "System Manager"}):
    frappe.throw("Not permitted")

HOME = "Home"
SOURCES = ("JHB Atrium Fashion - A", "Main Distribution - A")
mode = frappe.form_dict.get("mode") or "list"
out = {"mode": mode}


def candidates(after, limit):
    return frappe.db.sql("""
        select distinct b.item_code from `tabBin` b
        join `tabItem` i on i.name = b.item_code
        left join `tabSage Item Selection` s on s.item_code = b.item_code and s.company = 'Home'
        where b.actual_qty > 0 and s.name is null and i.disabled = 0
            and b.warehouse in %(wh)s and b.item_code > %(after)s
        order by b.item_code limit %(lim)s""", {"wh": SOURCES, "after": after, "lim": limit}, pluck=True)


def set_home(code, sid):
    name = frappe.db.get_value("Sage Item Selection", {"item_code": code, "company": HOME}, "name")
    if name:
        if str(frappe.db.get_value("Sage Item Selection", name, "selection_id") or "").strip() != sid:
            frappe.db.set_value("Sage Item Selection", name, "selection_id", sid)
            return "corrected"
        return "same"
    sel = frappe.new_doc("Sage Item Selection")
    sel.item_code = code
    sel.company = HOME
    sel.selection_id = sid
    sel.insert(ignore_permissions=True)
    return "added"


if mode == "list":
    left = candidates("", 100000)
    skipped = frappe.db.sql("""
        select count(distinct b.item_code) from `tabBin` b
        join `tabItem` i on i.name = b.item_code
        left join `tabSage Item Selection` s on s.item_code = b.item_code and s.company = 'Home'
        where b.actual_qty > 0 and s.name is null and i.disabled = 1 and b.warehouse in %(wh)s""", {"wh": SOURCES})[0][0]
    out.update({"left": len(left), "disabled_not_touched": skipped, "first": left[:10]})

elif mode == "run":
    sage = frappe.get_doc("Company Sage Integration", HOME)
    apikey = sage.get_password("api_key")
    cred = {"loginName": sage.username, "loginPwd": sage.get_password("password"), "useOAuth": False, "sessionToken": None, "provider": None}
    tax_id = int(sage.tax_id or 0)
    started = frappe.utils.now_datetime()

    def lookup(codes):
        # Pharoh returns nothing at all for 25+ codes, so 10 a call. A code missing from a COMPLETE answer is not
        # in Home; an incomplete answer proves nothing, so those codes are left for another run.
        found = {}
        absent = []
        unsure = []
        i = 0
        while i < len(codes):
            batch = codes[i:i + 10]
            i = i + 10
            try:
                resp = frappe.make_post_request(
                    "https://pharoh.co.za/api/InventorySync/get-item-selectionid-for-erpnext?apikey=" + apikey,
                    json={"credentials": cred, "itemCodes": batch}, headers={"Content-Type": "application/json"}) or {}
            except Exception as e:
                unsure = unsure + batch
                out["errors"].append("lookup " + batch[0] + ": " + str(e).replace(str(apikey), "***")[:300])
                continue
            items = resp.get("items") or []
            ids = {}
            for f in items:
                ids[str(f.get("item_code") or "").strip().upper()] = str(f.get("custom_sage_selection_id") or "").strip()
            complete = len(items) >= int(resp.get("returnedResults") or 0)
            for code in batch:
                sid = ids.get(code.upper()) or ""
                if sid and sid != "0":
                    found[code] = sid
                elif complete:
                    absent.append(code)
                else:
                    unsure.append(code)
        return [found, absent, unsure]

    out["errors"] = []
    after = str(frappe.form_dict.get("after") or "")
    count = int(frappe.form_dict.get("count") or 25)
    codes = candidates(after, count)
    res = {"already_in_home": [], "created": [], "create_failed": [], "not_checked": [], "corrected_after_create": [], "not_found_after_create": []}

    first = lookup(codes)
    for code in first[0]:
        set_home(code, first[0][code])
        res["already_in_home"].append(code)
    res["not_checked"] = first[2]
    frappe.db.commit()

    made = []
    for code in first[1]:
        it = frappe.db.get_value("Item", code, ["item_name", "description", "is_stock_item", "stock_uom",
            "custom_retail_price_incl_vat", "last_purchase_rate", "valuation_rate", "creation", "modified"], as_dict=True)
        incl = float(it.custom_retail_price_incl_vat or 0)
        payload = {
            "credentials": cred,
            "item": {
                "ID": 0,
                "Code": code,
                "Description": it.item_name or it.description or code,
                "Active": True,
                "Physical": True if it.is_stock_item else False,
                "Unit": it.stock_uom or "Each",
                "PriceExclusive": round(incl / 1.15, 2),
                "PriceInclusive": incl,
                "TaxTypeIdSales": tax_id,
                "TaxTypeIdPurchases": tax_id,
                "LastCost": float(it.last_purchase_rate or 0),
                "AverageCost": float(it.valuation_rate or 0),
                "QuantityOnHand": 0,
                "Created": frappe.utils.format_datetime(it.creation, "yyyy-MM-dd'T'HH:mm:ss"),
                "Modified": frappe.utils.format_datetime(it.modified, "yyyy-MM-dd'T'HH:mm:ss")
            }
        }
        try:
            resp = frappe.make_post_request("https://pharoh.co.za/api/InventorySync/post-new-item-to-sage?apikey=" + apikey,
                json=payload, headers={"Content-Type": "application/json"}) or {}
        except Exception as e:
            body = ""
            try:
                body = str(e.response.text)[:300]
            except Exception:
                body = ""
            res["create_failed"].append([code, (str(e).replace(str(apikey), "***")[:200] + " " + body).strip()])
            continue
        sid = str(resp.get("SelectionID") or resp.get("selectionId") or resp.get("id") or resp.get("ID") or "").strip()
        if not sid or sid == "0":
            res["create_failed"].append([code, str(resp)[:300]])
            continue
        set_home(code, sid)
        made.append(code)
        res["created"].append([code, sid])
        frappe.db.commit()

    # read every new code back from Home: the row must hold the ID Sage holds
    if made:
        back = lookup(made)
        for code in back[0]:
            if set_home(code, back[0][code]) == "corrected":
                res["corrected_after_create"].append([code, back[0][code]])
        res["not_found_after_create"] = back[1] + back[2]
        frappe.db.commit()

    out.update({"after": after, "asked": count, "processed": len(codes), "last": codes[len(codes) - 1] if codes else None,
        "seconds": frappe.utils.time_diff_in_seconds(frappe.utils.now_datetime(), started), "result": res})

elif mode == "ids":
    fix = str(frappe.form_dict.get("fix") or "") == "1"
    rows = frappe.db.sql("""
        select i.name, i.custom_category, i.custom_sage_selection_id as item_id, s.selection_id as own_id
        from `tabItem` i
        join `tabSage Item Selection` s on s.item_code = i.name and s.company = i.custom_category
        where ifnull(i.custom_sage_selection_id, '') != ifnull(s.selection_id, '')""", as_dict=True)
    by_cat = {}
    for r in rows:
        by_cat[str(r.custom_category)] = (by_cat.get(str(r.custom_category)) or 0) + 1
        if fix:
            frappe.db.set_value("Item", r.name, "custom_sage_selection_id", r.own_id, update_modified=False)
    no_own_row = frappe.db.sql("""
        select count(*) from `tabItem` i
        left join `tabSage Item Selection` s on s.item_code = i.name and s.company = i.custom_category
        where i.custom_category in ('Home', 'Fashion', 'Ceramics') and s.name is null""")[0][0]
    out.update({"fixed": fix, "mismatched": len(rows), "by_category": by_cat, "sample": rows[:8], "no_row_for_own_company": no_own_row})

else:
    frappe.throw("mode must be list, run or ids")

frappe.response["message"] = out
