# TEMPORARY (1 Nov 2026 switch-over): compare one Sage company's on-hand, pulled fresh, with ERPNext
# stock in the Ardmore warehouses that company owns. Read only. Delete at close-out.
if not frappe.db.exists("Has Role", {"parent": frappe.session.user, "role": "System Manager"}):
    frappe.throw("Not permitted")


def safe_float(val):
    if val is None:
        return 0.0
    s = str(val).strip().replace(' ', '').replace(u'\xa0', '')
    if not s:
        return 0.0
    if (',' in s) and ('.' in s):
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


company = frappe.form_dict.get("company")
sage = frappe.get_doc("Company Sage Integration", company)
apikey = sage.get_password("api_key")
payload = {"loginName": sage.username, "loginPwd": sage.get_password("password"), "useOAuth": False, "sessionToken": None, "provider": None}
whs = frappe.get_all("Warehouse", filters={"company": "Ardmore", "is_group": 0, "custom_sage_entity": company}, pluck="name")
whole_uoms = frappe.get_all("UOM", filters={"must_be_whole_number": 1}, pluck="name")

sage_qty = {}
skip = 0
total = 1
calls = 0
while skip < total:
    url = "https://pharoh.co.za/api/InventorySync/get-inventory-qtyonhand-for-erpnext?apikey=" + apikey + "&lastDate=1970-01-01&skipQty=" + str(skip) + "&InclZeroOnHand=false"
    r = frappe.make_post_request(url, json=payload)
    calls = calls + 1
    items = r.get("items") or []
    total = r.get("totalResults", 0)
    returned = r.get("returnedResults", 0)
    if not items or not returned:
        break
    for it in items:
        code = str(it.get("code") or "").strip()
        if code:
            sage_qty[code] = sage_qty.get(code, 0) + safe_float(it.get("quantityOnHand"))
    skip = skip + returned

erp = {}
for b in frappe.get_all("Bin", filters={"warehouse": ["in", whs], "actual_qty": ["!=", 0]}, fields=["item_code", "actual_qty"]):
    erp[b.item_code] = erp.get(b.item_code, 0) + b.actual_qty

match = 0
rounded = 0
diff = []
not_in_erp = []
disabled = []
negative = []
for code in sage_qty:
    s = sage_qty[code]
    if s != int(s) and frappe.db.get_value("Item", code, "stock_uom") in whole_uoms:
        s = float(int(s))
        rounded = rounded + 1
    e = erp.get(code, 0)
    if (s - e) < 0.0001 and (e - s) < 0.0001:
        match = match + 1
    elif s < 0 and e == 0:
        negative.append([code, s])
    elif not frappe.db.exists("Item", code):
        not_in_erp.append([code, s])
    elif frappe.db.get_value("Item", code, "disabled"):
        disabled.append([code, s])
    else:
        diff.append([code, s, e])
extra = []
for c in erp:
    if c not in sage_qty:
        extra.append([c, erp[c]])

frappe.response["message"] = {
    "company": company,
    "warehouses": whs,
    "pharoh_calls": calls,
    "sage_lines": len(sage_qty),
    "erpnext_units": sum([erp[c] for c in erp]),
    "match": match,
    "half_units_rounded_down": rounded,
    "different": len(diff), "different_list": diff[:60],
    "negative_in_sage": len(negative),
    "not_in_erpnext": len(not_in_erp), "not_in_erpnext_list": not_in_erp[:30],
    "disabled_in_erpnext": len(disabled), "disabled_list": disabled[:30],
    "in_erpnext_not_sage": len(extra), "in_erpnext_not_sage_list": extra[:30],
}
