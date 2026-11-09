# Till search, second warehouse (Russell, 2 Nov 2026): items of the POS Profile's second-warehouse
# group that have stock THERE, in the row shape of erpnext...point_of_sale.get_items, priced from
# the till's price list. The till script "POS Second Warehouse" adds these to its search results.
# A search term (name, code or barcode) is required, or the group itself picked in the till's filter.
profile = str(frappe.form_dict.get("pos_profile") or "")
term = str(frappe.form_dict.get("search_term") or "").strip()
price_list = str(frappe.form_dict.get("price_list") or "")

cfg = frappe.db.get_value("POS Profile", profile,
    ["custom_second_warehouse", "custom_second_warehouse_item_group", "custom_second_warehouse_tag",
     "selling_price_list"], as_dict=True) if profile else None

out = []
wh = ""
group = ""
tag = ""
if cfg and cfg.custom_second_warehouse and cfg.custom_second_warehouse_item_group:
    wh = cfg.custom_second_warehouse
    group = cfg.custom_second_warehouse_item_group
    tag = cfg.custom_second_warehouse_tag or ""
    price_list = price_list or cfg.selling_price_list
    base = {"item_group": group, "disabled": 0, "is_sales_item": 1, "has_variants": 0}

    codes = []
    if term:
        scanned = frappe.db.get_value("Item Barcode", {"barcode": term}, "parent")
        if scanned:
            if frappe.db.get_value("Item", scanned, "item_group") == group:
                codes = [scanned]
        else:
            like = "%" + term + "%"
            codes = frappe.get_all("Item", filters=base,
                or_filters=[["name", "like", like], ["item_name", "like", like]],
                pluck="name", limit_page_length=200)
    elif str(frappe.form_dict.get("whole_group") or "") == "1":
        codes = frappe.get_all("Item", filters=base, pluck="name", limit_page_length=1000)

    qty = {}
    if codes:
        for b in frappe.get_all("Bin", filters={"warehouse": wh, "item_code": ["in", codes], "actual_qty": [">", 0]},
                                fields=["item_code", "actual_qty"]):
            qty[b.item_code] = b.actual_qty

    if qty:
        today = frappe.utils.nowdate()
        items = frappe.get_all("Item", filters={"name": ["in", list(qty.keys())]},
            fields=["name", "item_name", "description", "stock_uom", "image", "is_stock_item"],
            order_by="name asc")
        for it in items:
            rate = None
            currency = None
            prices = frappe.get_all("Item Price",
                filters={"price_list": price_list, "item_code": it.name, "selling": 1},
                fields=["price_list_rate", "currency", "uom", "valid_from", "valid_upto"])
            best = None
            for p in prices:
                if p.valid_from and str(p.valid_from) > today:
                    continue
                if p.valid_upto and str(p.valid_upto) < today:
                    continue
                if best is None or (p.uom == it.stock_uom and best.uom != it.stock_uom):
                    best = p
            if best:
                rate = best.price_list_rate
                currency = best.currency
            out.append({
                "item_code": it.name,
                "item_name": it.item_name,
                "description": it.description,
                "stock_uom": it.stock_uom,
                "item_image": it.image,
                "is_stock_item": it.is_stock_item,
                "actual_qty": qty[it.name],
                "price_list_rate": rate,
                "currency": currency,
                "uom": it.stock_uom,
                "batch_no": None,
                "ard_second_wh": 1
            })

frappe.response["message"] = {"items": out, "warehouse": wh, "item_group": group, "tag": tag}
