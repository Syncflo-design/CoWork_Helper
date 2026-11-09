# BLOCK A TRANSFER THAT HAS NO INTERCOMPANY PRICE (Russell, 27 Oct 2026): a stock move into
# another entity's store is invoiced between the entities at the pair's wholesale list
# (post-intercompany-transfer-to-sage, Sage Intercompany Account). Without a price on that list
# the intercompany post fails after the stock has moved, so the transfer is stopped instead.
# 3 Nov 2026 (Russell): WARN ONLY - the stock must still move. Sage is invoiced at the sending
# entity's cost for those lines (post-intercompany-transfer-to-sage); the price is caught when
# the item is sold (block-sale-without-wholesale-price).
# Runs on every save, so a stock request is stopped when it is issued (draft), not only when the
# store receives it. Same owner rules as post-intercompany-transfer-to-sage; "Stock already owned
# by the receiving entity" (count loads) posts nothing and is never blocked.
if doc.purpose == "Material Transfer" and doc.company != "Ardmore Ceramics TEST" and not doc.get("custom_stock_already_owned"):
    missing = []
    for row in doc.items:
        if not row.s_warehouse or not row.t_warehouse:
            continue
        frm = frappe.db.get_value("Warehouse", row.s_warehouse, "custom_sage_entity") or frappe.db.get_value("Item", row.item_code, "custom_category")
        to = frappe.db.get_value("Warehouse", row.t_warehouse, "custom_sage_entity") or frappe.db.get_value("Item", row.item_code, "custom_category")
        if not frm or not to or frm == to:
            continue
        cfg = frappe.db.get_value("Sage Intercompany Account", frm + "-" + to, ["price_basis", "price_list"], as_dict=True)
        if not cfg or cfg.price_basis != "Price List":
            continue
        if not frappe.db.get_value("Item Price", {"item_code": row.item_code, "price_list": cfg.price_list, "price_list_rate": [">", 0]}, "name"):
            line = frappe.utils.escape_html(row.item_name or row.item_code) + " (" + row.item_code + ") - no price on " + frappe.utils.escape_html(cfg.price_list)
            if line not in missing:
                missing.append(line)

    if missing:
        frappe.msgprint(
            "These items have no wholesale price for the intercompany invoice:<br><br>"
            + "<br>".join(missing)
            + "<br><br>The stock will still move. Sage will be invoiced at the sending company's cost for these items. "
            + "Add the wholesale price when you can (or ask head office to).",
            title="Wholesale price missing", indicator="orange")
