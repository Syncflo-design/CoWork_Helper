# Server Script: DocType Event, Sales Order, Before Validate.
# SHOPIFY ORDERS (Russell, 20 Nov 2026): an online sale posts each item to the Sage company of its ERPNext
# Category, so a Shopify order with an item that has no Category is held. The Shopify connector catches
# this message, writes it on the order's Ecommerce Integration Log (status Error) and the "Shopify order
# held" alert goes to the Shopify Orders role. Staff set the Category, then click Retry on that log.
if doc.get("shopify_order_id") and doc.docstatus == 0:
    missing = []
    for row in doc.items:
        if row.item_code and not frappe.db.get_value("Item", row.item_code, "custom_category"):
            missing.append(row.item_code + " - " + (row.item_name or ""))
    if missing:
        frappe.throw(
            "Shopify order " + str(doc.get("shopify_order_number") or "") + ": no ERPNext Category on "
            + ", ".join(missing) + ". Set it on the item, then click Retry on this log."
        )
