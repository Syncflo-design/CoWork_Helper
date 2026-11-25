# A TILL THAT SELLS FROM SEVERAL WAREHOUSES (Russell, 3 Nov 2026). A till whose POS Profile lists
# "Also Sell From Warehouses" (Online: all Atrium + Main Distribution) shows their stock too (till script
# "POS Sell From Several Warehouses"), but every line still sells from the till's own warehouse, so each
# online movement runs through Online Store. Just before the sale is booked, whatever that warehouse is
# short of is moved into it: ONE Material Transfer per sale, each item taken from the warehouse whose
# Sage entity is the item's Category first, then the others in the profile's order. The transfer posts
# the intercompany pair itself on submit (post-intercompany-transfer-to-sage), so the sale still posts
# wholly to the till's Sage entity (post-taxinvoice-to-sage), as before. The transfer names the invoice
# (For Sale on the Stock Entry) and the invoice gets a comment naming the transfer. Returns go back into
# the till's warehouse, so there is nothing to do for them. Not enough stock anywhere: the sale stops.
if doc.get("is_pos") and doc.get("pos_profile") and doc.get("update_stock") and not doc.get("is_return"):
    cfg = frappe.db.get_value("POS Profile", doc.pos_profile, ["warehouse", "custom_also_sell_from"], as_dict=True)
    till = cfg.warehouse if cfg else None
    pool = []
    if till and cfg.custom_also_sell_from:
        for line in str(cfg.custom_also_sell_from).split("\n"):
            wh = line.strip()
            if wh and wh != till and wh not in pool and frappe.db.exists("Warehouse", wh):
                pool.append(wh)

    need = {}
    uom = {}
    if pool:
        for row in doc.items:
            if row.item_code and row.warehouse == till and frappe.db.get_value("Item", row.item_code, "is_stock_item"):
                qty = frappe.utils.flt(row.stock_qty) or frappe.utils.flt(row.qty) * frappe.utils.flt(row.conversion_factor or 1)
                need[row.item_code] = need.get(row.item_code, 0) + qty
                uom[row.item_code] = row.stock_uom

    moves = []
    missing = []
    if need:
        entity = {}
        for wh in pool:
            entity[wh] = frappe.db.get_value("Warehouse", wh, "custom_sage_entity") or ""
        for code in need:
            short = need[code] - frappe.utils.flt(frappe.db.get_value("Bin", {"item_code": code, "warehouse": till}, "actual_qty"))
            if short <= 0:
                continue
            category = frappe.db.get_value("Item", code, "custom_category") or ""
            first = [wh for wh in pool if category and entity[wh] == category]
            order = first + [wh for wh in pool if wh not in first]
            for wh in order:
                if short <= 0:
                    break
                there = frappe.utils.flt(frappe.db.get_value("Bin", {"item_code": code, "warehouse": wh}, "actual_qty"))
                take = min(there, short)
                if take > 0:
                    moves.append({"item_code": code, "s_warehouse": wh, "qty": take})
                    short = short - take
            if short > 0:
                missing.append(code + " (" + ("%g" % short) + " short)")

    if missing:
        frappe.throw("Not enough stock for this sale in " + till + " or the warehouses it also sells from: " + ", ".join(missing) + ".", title="Not enough stock")

    if moves:
        se = frappe.new_doc("Stock Entry")
        se.stock_entry_type = "Material Transfer"
        se.purpose = "Material Transfer"
        se.company = doc.company
        # same moment as the sale, so the stock is in the till's warehouse when the sale books it out
        se.set_posting_time = 1
        se.posting_date = doc.posting_date
        se.posting_time = doc.posting_time
        se.to_warehouse = till
        se.custom_sales_invoice = doc.name
        se.remarks = "Moved into " + till + " for till sale " + doc.name
        for m in moves:
            se.append("items", {
                "item_code": m["item_code"],
                "s_warehouse": m["s_warehouse"],
                "t_warehouse": till,
                "qty": m["qty"],
                "uom": uom.get(m["item_code"]),
                "conversion_factor": 1
            })
        # a sale submitted in one step is not written yet, so its link cannot be checked
        se.flags.ignore_links = True
        se.insert(ignore_permissions=True)
        se.flags.ignore_permissions = True
        se.submit()
        if frappe.db.exists("Sales Invoice", doc.name):
            doc.add_comment("Comment", "Stock moved into " + till + " for this sale: " + se.name)
