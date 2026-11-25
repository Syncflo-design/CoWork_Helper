# Server Script: DocType Event, Sales Invoice, After Submit.
# SHOPIFY ORDERS (Russell, 20 Nov 2026): once the Online till completes a Shopify order, its Sales Order is
# closed, so it stops reserving stock and stays out of the open-order lists (the till's Shopify Orders list
# already drops it, because the sale carries the Shopify order id). Never stops the sale.
if doc.get("is_pos") and not doc.get("is_return") and doc.get("shopify_order_id"):
    so_name = frappe.db.get_value("Sales Order", {"shopify_order_id": doc.shopify_order_id, "docstatus": 1}, "name")
    if so_name:
        try:
            so = frappe.get_doc("Sales Order", so_name)
            if so.status != "Closed":
                so.update_status("Closed")
        except Exception as e:
            frappe.log_error(message="Sales Invoice " + doc.name + ", Sales Order " + so_name + ": " + str(e)[:500],
                title="Shopify order not closed")
