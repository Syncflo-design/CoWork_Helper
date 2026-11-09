# Till items from several warehouses (Russell, 3 Nov 2026): a till whose POS Profile lists "Also Sell
# From Warehouses" (Online: all Atrium + Main Distribution) shows what is in stock in its own warehouse
# AND those, quantities added up, in the row shape of erpnext...point_of_sale.get_items, priced from the
# till's price list. The till script "POS Sell From Several Warehouses" uses this instead of the standard
# list for such a till; the sale then moves in what the till is short of (Server Script
# "Sales Invoice - Online Auto Transfer"). Stock items only: Ardmore sells no non-stock items.
profile = str(frappe.form_dict.get("pos_profile") or "")
term = str(frappe.form_dict.get("search_term") or "").strip()
price_list = str(frappe.form_dict.get("price_list") or "")
group = str(frappe.form_dict.get("item_group") or "")
start = frappe.utils.cint(frappe.form_dict.get("start"))
page_length = frappe.utils.cint(frappe.form_dict.get("page_length")) or 40

cfg = frappe.db.get_value("POS Profile", profile, ["warehouse", "custom_also_sell_from", "selling_price_list"], as_dict=True) if profile else None

out = []
if cfg and cfg.warehouse:
    whs = [cfg.warehouse]
    for line in str(cfg.custom_also_sell_from or "").split("\n"):
        wh = line.strip()
        if wh and wh not in whs and frappe.db.exists("Warehouse", wh):
            whs.append(wh)
    price_list = price_list or cfg.selling_price_list

    qty = {}
    for b in frappe.get_all("Bin", filters={"warehouse": ["in", whs], "actual_qty": [">", 0]}, fields=["item_code", "actual_qty"]):
        qty[b.item_code] = qty.get(b.item_code, 0) + b.actual_qty

    base = {"disabled": 0, "has_variants": 0, "is_sales_item": 1, "is_fixed_asset": 0}
    if group and frappe.db.exists("Item Group", group):
        bounds = frappe.db.get_value("Item Group", group, ["lft", "rgt"], as_dict=True)
        base["item_group"] = ["in", frappe.get_all("Item Group", filters={"lft": [">=", bounds.lft], "rgt": ["<=", bounds.rgt]}, pluck="name")]
    fields = ["name", "item_name", "description", "stock_uom", "image", "is_stock_item", "item_group"]

    rows = []
    scanned = frappe.db.get_value("Item Barcode", {"barcode": term}, "parent") if term else None
    if scanned:
        # a scanned barcode shows its item even when none is in stock, as the standard till does
        rows = frappe.get_all("Item", filters={"name": scanned, "disabled": 0}, fields=fields)
    elif qty:
        filters = dict(base)
        filters["name"] = ["in", list(qty.keys())]
        or_filters = None
        if term:
            like = "%" + term + "%"
            or_filters = [["name", "like", like], ["item_name", "like", like]]
            for f in frappe.get_all("POS Search Fields", pluck="fieldname"):
                if f:
                    or_filters.append([f, "like", like])
        rows = frappe.get_all("Item", filters=filters, or_filters=or_filters, fields=fields,
            order_by="name asc", limit_start=start, limit_page_length=page_length)

    prices = {}
    if rows:
        today = frappe.utils.nowdate()
        for p in frappe.get_all("Item Price",
                filters={"price_list": price_list, "item_code": ["in", [r.name for r in rows]], "selling": 1},
                fields=["item_code", "price_list_rate", "currency", "uom", "valid_from", "valid_upto"]):
            if p.valid_from and str(p.valid_from) > today:
                continue
            if p.valid_upto and str(p.valid_upto) < today:
                continue
            prices.setdefault(p.item_code, []).append(p)

    for r in rows:
        best = None
        for p in prices.get(r.name, []):
            if best is None or (p.uom == r.stock_uom and best.uom != r.stock_uom):
                best = p
        out.append({
            "item_code": r.name,
            "item_name": r.item_name,
            "description": r.description,
            "stock_uom": r.stock_uom,
            "item_image": r.image,
            "is_stock_item": r.is_stock_item,
            "item_group": r.item_group,
            "actual_qty": qty.get(r.name, 0),
            "price_list_rate": best.price_list_rate if best else None,
            "currency": best.currency if best else None,
            "uom": r.stock_uom,
            "batch_no": None
        })

frappe.response["message"] = {"items": out}
