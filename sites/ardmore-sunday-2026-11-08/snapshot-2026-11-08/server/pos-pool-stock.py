# Till stock check across several warehouses (Russell, 3 Nov 2026): for a till whose POS Profile lists
# "Also Sell From Warehouses", what one item has in the till's warehouse plus those, in the shape of
# erpnext...pos_invoice.get_stock_availability: [qty, is_stock_item, negative stock allowed]. The till
# script "POS Sell From Several Warehouses" uses it for the cart check and the item panel.
profile = str(frappe.form_dict.get("pos_profile") or "")
item_code = str(frappe.form_dict.get("item_code") or "")

cfg = frappe.db.get_value("POS Profile", profile, ["warehouse", "custom_also_sell_from"], as_dict=True) if profile else None
total = 0
if cfg and cfg.warehouse and item_code:
    whs = [cfg.warehouse]
    for line in str(cfg.custom_also_sell_from or "").split("\n"):
        wh = line.strip()
        if wh and wh not in whs:
            whs.append(wh)
    for b in frappe.get_all("Bin", filters={"item_code": item_code, "warehouse": ["in", whs]}, fields=["actual_qty"]):
        total = total + frappe.utils.flt(b.actual_qty)

is_stock_item = frappe.utils.cint(frappe.db.get_value("Item", item_code, "is_stock_item")) if item_code else 0
allow_negative = frappe.utils.cint(frappe.db.get_single_value("Stock Settings", "allow_negative_stock"))
frappe.response["message"] = [total, is_stock_item, allow_negative]
