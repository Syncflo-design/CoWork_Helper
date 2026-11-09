# GO-LIVE COUNT LOAD (Russell, 31 Oct 2026). Loads the Hyde Park / JHB Holding count sheets and lines up
# every COUNTED item's SelectionID in ERPNext with the Sage company that owns the warehouse (Home for both
# stores) - the ID a till sale in that store sends. The item code is the only link: each Sage company has
# its own SelectionID for the code. Only items on the sheet are touched; zero lines and unknown codes are
# skipped. Nothing is created in Sage.
#   check   report only. args: warehouse, rows = [[item_code, qty], ...]
#   align   look the counted codes up in the owner's Sage (Pharoh get-item-selectionid-for-erpnext, 10 codes
#           per call, one call at a time) and set the owner's Sage Item Selection row to the SelectionID Sage
#           returns (adds missing, corrects wrong). Codes Sage does not return are listed. Read-only on Sage,
#           so safe under the TEST lock. args: warehouse, rows, company (optional: TEST to try it there),
#           start (default 0), count (default 200 codes per call - call again with start = next_start until
#           next_start is empty)
#   load    "Stock already owned" transfers into the store from the warehouse its owner's Sage stock syncs
#           into (Home -> JHB Atrium Home, 1 Nov 2026), nothing posts to Sage.
#           args: warehouse, rows
if not frappe.db.exists("Has Role", {"parent": frappe.session.user, "role": "System Manager"}):
    frappe.throw("Not permitted")

LIVE = ["Home", "Ceramics", "Fashion"]
TEST = "Ardmore Ceramics TEST"
mode = frappe.form_dict.get("mode") or "check"


def creds(company):
    sage = frappe.get_doc("Company Sage Integration", company)
    return [sage, sage.get_password("api_key"), {"loginName": sage.username, "loginPwd": sage.get_password("password"), "useOAuth": False, "sessionToken": None, "provider": None}]


def has_row(code, company):
    return frappe.db.exists("Sage Item Selection", {"item_code": code, "company": company})


def sheet():
    # sum duplicate lines; keep only positive quantities
    raw = frappe.form_dict.get("rows") or []
    if isinstance(raw, str):
        raw = json.loads(raw)
    qty = {}
    order = []
    skipped = 0
    for r in raw:
        code = str(r[0] or "").strip()
        q = float(r[1] or 0)
        if not code or q <= 0:
            skipped = skipped + 1
            continue
        if code not in qty:
            qty[code] = 0.0
            order.append(code)
        qty[code] = qty[code] + q
    return [order, qty, skipped]


def target():
    wh = frappe.form_dict.get("warehouse")
    if not wh or not frappe.db.exists("Warehouse", wh):
        frappe.throw("Give the store warehouse, e.g. HDSQ - A.")
    return wh


def source_of(wh):
    # Everything in a store belongs to the store's owner, so its counted stock comes out of the
    # warehouse that owner's Sage stock syncs into (Home -> JHB Atrium Home; 1 Nov 2026).
    owner = frappe.db.get_value("Warehouse", wh, "custom_sage_entity")
    if not owner:
        frappe.throw("Warehouse " + wh + " has no Sage entity (owner) set.")
    src = frappe.db.get_value("Company Sage Integration", owner, "custom_default_warehouse")
    if not src:
        frappe.throw(owner + "'s stock sync has no warehouse yet - switch on " + owner + "'s stock sync first.")
    if src == wh:
        frappe.throw(wh + " is where " + owner + "'s Sage stock syncs into. Load counts into the stores.")
    return src


out = {"mode": mode}

if mode == "check":
    wh = target()
    s = sheet()
    owner = frappe.db.get_value("Warehouse", wh, "custom_sage_entity")
    src = frappe.db.get_value("Company Sage Integration", owner, "custom_default_warehouse") if owner else None
    unknown = []
    disabled = []
    # only the warehouse owner's ID matters for a store's sales (Russell, 31 Oct 2026)
    owners = [owner] if owner in LIVE else LIVE
    missing = {}
    for company in owners:
        missing[company] = []
    short_md = []
    short_owner = []
    for code in s[0]:
        q = s[1][code]
        if not frappe.db.exists("Item", code):
            unknown.append(code)
            continue
        if frappe.db.get_value("Item", code, "disabled"):
            disabled.append(code)
            continue
        for company in owners:
            if not has_row(code, company):
                missing[company].append(code)
        md = float(frappe.db.get_value("Bin", {"item_code": code, "warehouse": src}, "actual_qty") or 0)
        if src and md < q:
            short_md.append([code, q, md])
        raw = frappe.db.get_value("Item", code, "custom_sage_qoh_by_company")
        if owner and raw:
            try:
                held = float(json.loads(raw).get(owner) or 0)
            except Exception:
                held = 0.0
            if held < q:
                short_owner.append([code, q, held])
    out.update({
        "warehouse": wh, "owner": owner, "items": len(s[0]), "zero_lines_skipped": s[2],
        "unknown_codes": unknown, "disabled_items": disabled,
        "no_id_in_erpnext": {k: {"count": len(missing[k]), "first": missing[k][:40]} for k in missing},
        "source": src or "not set yet - switch on the owner's stock sync first", "more_than_source": short_md[:200], "more_than_owner_holds_in_sage": short_owner[:200]})

elif mode == "align":
    wh = target()
    s = sheet()
    owner = frappe.db.get_value("Warehouse", wh, "custom_sage_entity")
    if frappe.form_dict.get("company") == TEST:
        owner = TEST
    if owner not in LIVE and owner != TEST:
        frappe.throw("Warehouse " + wh + " has no Sage entity (Home, Ceramics or Fashion) set.")
    codes = []
    for code in s[0]:
        if frappe.db.exists("Item", code) and not frappe.db.get_value("Item", code, "disabled"):
            codes.append(code)
    start = int(frappe.form_dict.get("start") or 0)
    count = int(frappe.form_dict.get("count") or 200)
    part = codes[start:start + count]
    c = creds(owner)
    r = {"added": 0, "corrected": [], "unchanged": 0, "not_in_sage": [], "not_checked": [], "id_also_on_other_item": []}
    errors = []
    calls = 0
    i = 0
    while i < len(part):
        # 10 codes per call: Pharoh returns nothing at all for 25 or more (1 Nov 2026)
        batch = part[i:i + 10]
        i = i + 10
        calls = calls + 1
        try:
            resp = frappe.make_post_request(
                "https://pharoh.co.za/api/InventorySync/get-item-selectionid-for-erpnext?apikey=" + c[1],
                json={"credentials": c[2], "itemCodes": batch},
                headers={"Content-Type": "application/json"}) or {}
        except Exception as e:
            errors.append([batch[0] + " .. " + batch[-1], str(e).replace(str(c[1]), "***")[:300]])
            r["not_checked"] = r["not_checked"] + batch
            continue
        found = resp.get("items") or []
        ids = {}
        for f in found:
            ids[str(f.get("item_code") or "").strip().upper()] = str(f.get("custom_sage_selection_id") or "").strip()
        # Pharoh: totalResults = codes sent, returnedResults = codes found. A code not returned is not in this
        # Sage company - unless the list is shorter than returnedResults (cut short), then nothing is assumed.
        complete = len(found) >= int(resp.get("returnedResults") or 0)
        if not complete:
            errors.append([batch[0] + " .. " + batch[-1], "Pharoh returned " + str(len(found)) + " of " + str(resp.get("returnedResults")) + " found: " + str(resp)[:400]])
        for code in batch:
            sid = ids.get(code.upper()) or ""
            if not sid or sid == "0":
                if complete:
                    r["not_in_sage"].append(code)
                else:
                    r["not_checked"].append(code)
                continue
            rows = frappe.get_all("Sage Item Selection", filters={"item_code": code, "company": owner}, fields=["name", "selection_id"])
            if not rows:
                sel = frappe.new_doc("Sage Item Selection")
                sel.item_code = code
                sel.company = owner
                sel.selection_id = sid
                sel.insert(ignore_permissions=True)
                r["added"] = r["added"] + 1
            else:
                changed = False
                for row in rows:
                    if str(row.selection_id or "").strip() != sid:
                        frappe.db.set_value("Sage Item Selection", row.name, "selection_id", sid)
                        r["corrected"].append([code, row.selection_id, sid])
                        changed = True
                if not changed:
                    r["unchanged"] = r["unchanged"] + 1
            # a SelectionID is never shared in Sage, so another item holding it in ERPNext is wrong - report it
            other = frappe.get_all("Sage Item Selection", filters={"company": owner, "selection_id": sid, "item_code": ["!=", code]}, pluck="item_code")
            if other:
                r["id_also_on_other_item"].append([code, sid, other])
        frappe.db.commit()
    nxt = start + count
    out.update({"warehouse": wh, "company": owner, "codes_on_sheet": len(codes), "start": start,
                "checked": len(part), "pharoh_calls": calls, "next_start": nxt if nxt < len(codes) else None,
                "result": r, "errors": errors})

elif mode == "load":
    wh = target()
    s = sheet()
    src = source_of(wh)
    lines = []
    exceptions = []
    for code in s[0]:
        q = s[1][code]
        if not frappe.db.exists("Item", code):
            exceptions.append([code, q, "not in ERPNext"])
            continue
        if frappe.db.get_value("Item", code, "disabled"):
            exceptions.append([code, q, "item disabled"])
            continue
        md = float(frappe.db.get_value("Bin", {"item_code": code, "warehouse": src}, "actual_qty") or 0)
        if md < q:
            exceptions.append([code, q, src + " holds " + str(md)])
            continue
        lines.append([code, q])
    entries = []
    i = 0
    while i < len(lines):
        batch = lines[i:i + 100]
        se = frappe.new_doc("Stock Entry")
        se.company = frappe.db.get_value("Warehouse", wh, "company")
        se.stock_entry_type = "Material Transfer"
        se.purpose = "Material Transfer"
        se.custom_stock_already_owned = 1
        se.remarks = "Go-live count load into " + wh + " (stock already owned by the store's Sage entity)"
        for b in batch:
            se.append("items", {"item_code": b[0], "qty": b[1], "s_warehouse": src, "t_warehouse": wh})
        se.insert(ignore_permissions=True)
        se.submit()
        frappe.db.commit()
        entries.append(se.name)
        i = i + 100
    out.update({"warehouse": wh, "entries": entries, "lines_loaded": len(lines), "exceptions": exceptions})

else:
    frappe.throw("mode must be check, align or load")

frappe.response["message"] = out
