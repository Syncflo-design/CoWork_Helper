# BLOCK A SALE THAT HAS NO INTERCOMPANY PRICE (Russell, 27 Oct 2026): "if there is no price
# available it needs to inform the user and prevent the sale being processed."
# A line sold out of another entity's stock (the Online till selling a Ceramics bowl from Main
# Distribution, an Account Sale of another entity's goods) is invoiced between the entities at
# the pair's wholesale list (Sage Intercompany Account, Jon 26 Oct). Without a price on that
# list the intercompany post fails after the sale, so the sale is stopped here instead.
# Who sold / who owned = the same rules as post-intercompany-sale-to-sage.
# Runs on Before Save and acts only while the invoice is being submitted (docstatus 1):
# the Before Submit event did not fire for Sales Invoice on this site (tested 27 Oct).
if doc.docstatus == 1 and doc.company != "Ardmore Ceramics TEST" and not doc.get("is_return") and not (doc.get("is_pos") and doc.get("is_consolidated")):
    seller = None
    if doc.get("is_pos"):
        if doc.get("pos_profile"):
            seller = frappe.db.get_value("POS Profile", doc.pos_profile, "custom_sage_entity")
        if not seller and doc.get("set_warehouse"):
            seller = frappe.db.get_value("Warehouse", doc.set_warehouse, "custom_sage_entity")
    else:
        mapped = frappe.get_all("Sage Customer Selection", filters={"customer": doc.customer}, pluck="company")
        if len(mapped) == 1:
            seller = mapped[0]
        elif len(mapped) > 1:
            cats = []
            for item in doc.items:
                c = frappe.db.get_value("Item", item.item_code, "custom_category")
                if c and c not in cats:
                    cats.append(c)
            seller = cats[0] if (len(cats) == 1 and cats[0] in mapped) else sorted(mapped)[0]

    missing = []
    if seller:
        for row in doc.items:
            owner = frappe.db.get_value("Warehouse", row.warehouse, "custom_sage_entity") if row.warehouse else None
            owner = owner or frappe.db.get_value("Item", row.item_code, "custom_category")
            if not owner or owner == seller:
                continue
            cfg = frappe.db.get_value("Sage Intercompany Account", owner + "-" + seller, ["price_basis", "price_list"], as_dict=True)
            if not cfg or cfg.price_basis != "Price List":
                continue
            if not frappe.db.get_value("Item Price", {"item_code": row.item_code, "price_list": cfg.price_list, "price_list_rate": [">", 0]}, "name"):
                line = frappe.utils.escape_html(row.item_name or row.item_code) + " (" + row.item_code + ") - no price on " + frappe.utils.escape_html(cfg.price_list)
                if line not in missing:
                    missing.append(line)

    if missing:
        frappe.throw(
            "This sale cannot go through. These items have no wholesale price for the intercompany invoice:<br><br>"
            + "<br>".join(missing)
            + "<br><br>Ask head office to add the wholesale price, then try again.",
            title="Wholesale price missing")
