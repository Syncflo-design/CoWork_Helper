# Server Script: DocType Event, Sales Invoice, Before Validate.
# ONLINE SPLIT (Russell + client, 20 Nov 2026): on a till ticked "Post Each Item to Its Own Company" every
# stock line sells from a warehouse its own company holds: the till's warehouse or one of its "Also Sell
# From Warehouses" whose Sage entity is the item's ERPNext Category, in the profile's order, the first one
# with enough stock. The item then posts to that company in Sage (post-taxinvoice-to-sage) and no stock
# moves between companies. If its own company holds too little, completing the sale stops and says where
# the stock is. A return goes back to the warehouse the item was sold from.
if doc.get("is_pos") and doc.get("pos_profile") and doc.get("update_stock"):
    cfg = frappe.db.get_value("POS Profile", doc.pos_profile, ["warehouse", "custom_also_sell_from", "custom_split_by_item_company"], as_dict=True)
    if cfg and cfg.custom_split_by_item_company and cfg.warehouse:
        whs = [cfg.warehouse]
        for line in str(cfg.custom_also_sell_from or "").split("\n"):
            wh = line.strip()
            if wh and wh not in whs and frappe.db.exists("Warehouse", wh):
                whs.append(wh)
        entity = {}
        for wh in whs:
            entity[wh] = frappe.db.get_value("Warehouse", wh, "custom_sage_entity") or ""

        if doc.get("is_return"):
            for row in doc.items:
                if not row.item_code:
                    continue
                sold_from = frappe.db.get_value("Sales Invoice Item", row.sales_invoice_item, "warehouse") if row.get("sales_invoice_item") else None
                if not sold_from:
                    # no link to the sold line: back into the item's own company's first warehouse
                    category = frappe.db.get_value("Item", row.item_code, "custom_category") or ""
                    for wh in whs:
                        if category and entity[wh] == category:
                            sold_from = wh
                            break
                if sold_from:
                    row.warehouse = sold_from
        else:
            taken = {}  # "item|warehouse" -> qty already given to earlier lines of this sale
            short = []
            for row in doc.items:
                if not row.item_code or not frappe.db.get_value("Item", row.item_code, "is_stock_item"):
                    continue
                category = frappe.db.get_value("Item", row.item_code, "custom_category") or ""
                own = []
                for wh in whs:
                    if category and entity[wh] == category:
                        own.append(wh)
                qty = frappe.utils.flt(row.stock_qty) or frappe.utils.flt(row.qty) * frappe.utils.flt(row.conversion_factor or 1)
                chosen = None
                for wh in own:
                    key = row.item_code + "|" + wh
                    have = frappe.utils.flt(frappe.db.get_value("Bin", {"item_code": row.item_code, "warehouse": wh}, "actual_qty")) - frappe.utils.flt(taken.get(key))
                    if have >= qty:
                        chosen = wh
                        break
                if chosen:
                    row.warehouse = chosen
                    key = row.item_code + "|" + chosen
                    taken[key] = frappe.utils.flt(taken.get(key)) + qty
                    continue

                row.warehouse = own[0] if own else cfg.warehouse
                if doc.docstatus == 1:
                    elsewhere = []
                    for wh in whs:
                        there = frappe.utils.flt(frappe.db.get_value("Bin", {"item_code": row.item_code, "warehouse": wh}, "actual_qty"))
                        if there > 0:
                            elsewhere.append(wh + " (" + ("%g" % there) + ")")
                    short.append(
                        row.item_code + " - " + (row.item_name or "") + " (" + (category or "no ERPNext Category") + "): "
                        + ("stock is in " + ", ".join(elsewhere) if elsewhere else "none in stock")
                    )
            if short:
                frappe.throw(
                    "These items are not in their own company's stock, so this sale cannot take them:<br><br>"
                    + "<br>".join(short)
                    + "<br><br>Move the stock with a stock request or transfer first, or take the item off the sale.",
                    title="Not in its own company's stock",
                )
