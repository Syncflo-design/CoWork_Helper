# SAGE HOME BACKFILL, background (Russell, 3 Nov 2026). Temporary: disable or delete once the
# "Sage Home backfill finished" Error Log appears.
#
# Items held in JHB Atrium Fashion / Main Distribution that have no Sage Home item cannot be moved into a
# Home store or sold online (the intercompany needs the item in Home). The item code is the only link
# between the Sage companies. Every 5 minutes, 20 codes, one Sage call at a time:
#   1. look the codes up in Sage Home (10 a call); one Home already has -> record Home's SelectionID
#   2. a code Home does not have -> create it in Home with quantity 0 (Home only owns what it buys) and
#      record the SelectionID Home returns
#   3. read every new code back from Home and correct the Home row if Sage holds a different ID
# Only the Home row of Sage Item Selection is written; the item's own SelectionID is left alone.
# Sage asking us to slow down (429/503) sets Home's "retry after" and the run stops; later runs wait for it.
# A code that fails to create gets an Error Log titled "Sage Home backfill: <code>" and is not tried again.
HOME = "Home"
SOURCES = ("JHB Atrium Fashion - A", "Main Distribution - A")
PER_RUN = 20
TAG = "Sage Home backfill: "
state = {"stop": 0}


def throttled(e):
    status = None
    try:
        status = e.response.status_code
    except Exception:
        status = None
    if status != 429 and status != 503:
        return False
    wait = 120
    try:
        h = e.response.headers.get("Retry-After")
        if h:
            wait = int(float(h))
    except Exception:
        wait = 120
    frappe.db.set_value("Company Sage Integration", HOME, "custom_sage_retry_after",
        frappe.utils.add_to_date(frappe.utils.now_datetime(), seconds=wait))
    frappe.db.commit()
    state["stop"] = 1
    return True


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


def lookup(codes, apikey, cred):
    # Pharoh returns nothing at all for 25+ codes, so 10 a call. A code missing from a COMPLETE answer is not
    # in Home; an incomplete answer proves nothing, so those codes wait for the next run.
    found = {}
    absent = []
    i = 0
    while i < len(codes) and not state["stop"]:
        batch = codes[i:i + 10]
        i = i + 10
        try:
            resp = frappe.make_post_request(
                "https://pharoh.co.za/api/InventorySync/get-item-selectionid-for-erpnext?apikey=" + apikey,
                json={"credentials": cred, "itemCodes": batch}, headers={"Content-Type": "application/json"}) or {}
        except Exception as e:
            if not throttled(e):
                frappe.log_error(title="Sage Home backfill: lookup failed", message=str(e).replace(str(apikey), "***")[:600])
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
    return [found, absent]


sage = frappe.get_doc("Company Sage Integration", HOME)
ra = sage.get("custom_sage_retry_after")
if not (ra and frappe.utils.get_datetime(ra) > frappe.utils.now_datetime()):
    codes = frappe.db.sql("""
        select distinct b.item_code from `tabBin` b
        join `tabItem` i on i.name = b.item_code
        left join `tabSage Item Selection` s on s.item_code = b.item_code and s.company = 'Home'
        where b.actual_qty > 0 and s.name is null and i.disabled = 0 and b.warehouse in %(wh)s
            and not exists (select 1 from `tabError Log` e where e.method = concat(%(tag)s, b.item_code))
        order by b.item_code limit %(lim)s""", {"wh": SOURCES, "tag": TAG, "lim": PER_RUN}, pluck=True)

    if not codes:
        if not frappe.db.exists("Error Log", {"method": "Sage Home backfill finished"}):
            failed = frappe.db.count("Error Log", {"method": ["like", TAG + "%"]})
            frappe.log_error(title="Sage Home backfill finished",
                message="Every active item held in JHB Atrium Fashion / Main Distribution has a Sage Home item, apart from any listed in Error Logs titled '" + TAG + "...' (" + str(failed) + " logs, lookups included). Disable the server script sage-home-backfill.")
    else:
        apikey = sage.get_password("api_key")
        cred = {"loginName": sage.username, "loginPwd": sage.get_password("password"), "useOAuth": False, "sessionToken": None, "provider": None}
        tax_id = int(sage.tax_id or 0)

        first = lookup(codes, apikey, cred)
        for code in first[0]:
            set_home(code, first[0][code])
        frappe.db.commit()

        made = []
        for code in first[1]:
            if state["stop"]:
                break
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
                if throttled(e):
                    break
                body = ""
                try:
                    body = str(e.response.text)[:400]
                except Exception:
                    body = ""
                frappe.log_error(title=TAG + code, message=(str(e).replace(str(apikey), "***")[:300] + " " + body).strip())
                continue
            sid = str(resp.get("SelectionID") or resp.get("selectionId") or resp.get("id") or resp.get("ID") or "").strip()
            if not sid or sid == "0":
                frappe.log_error(title=TAG + code, message="Sage did not return a SelectionID: " + str(resp)[:500])
                continue
            set_home(code, sid)
            made.append(code)
            frappe.db.commit()

        # read every new code back from Home: the row must hold the ID Sage holds
        if made and not state["stop"]:
            back = lookup(made, apikey, cred)
            for code in back[0]:
                if set_home(code, back[0][code]) == "corrected":
                    frappe.log_error(title="Sage Home backfill check: " + code, message="Home row corrected to the SelectionID Sage holds: " + back[0][code])
            for code in back[1]:
                frappe.log_error(title="Sage Home backfill check: " + code, message="Created, but Sage Home did not return it on the read-back. Check it in Sage.")
            frappe.db.commit()
