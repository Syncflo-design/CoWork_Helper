# Server Script: API, method ardmore_pos_shopify_orders.
# SHOPIFY ORDERS ON THE ONLINE TILL (Russell, 20 Nov 2026). The till script "POS Shopify Orders" lists the
# paid Shopify orders still waiting (their Sales Orders, made by the Shopify connector) and opens one as a
# ready sale: the customer, the items at the prices and VAT Shopify charged, the Shopify number in Order
# Number, paid by "Shopify". The till opens it like any draft (as it does a quote), so stock, receipt,
# End of Day and Sage are a normal till sale. The sale carries the Shopify order id, which is how the list
# knows an order is done. Only for users of a till ticked "Online Store".
form = frappe.form_dict
action = str(form.get("action") or "")
profile = str(form.get("pos_profile") or "")
PAYMENT = "Shopify"
OPEN_STATUSES = ["Closed", "Completed", "On Hold"]


def till_of(name):
    t = frappe.db.get_value("POS Profile", name, ["company", "currency", "warehouse", "selling_price_list", "taxes_and_charges",
        "custom_zero_vat_template", "letter_head", "custom_online_store", "disabled"], as_dict=True) if name else None
    if not t or t.disabled or not t.custom_online_store:
        frappe.throw("Shopify orders open only on the Online till.")
    if frappe.session.user != "Administrator" and not frappe.db.exists("POS Profile User", {"parent": name, "user": frappe.session.user}):
        frappe.throw("You are not a user of the " + name + " till.")
    return t


def sales_for(order_ids):
    # every live till sale (draft or completed, not a return) carrying one of these Shopify order ids
    if not order_ids:
        return []
    return frappe.get_all("Sales Invoice", filters={"shopify_order_id": ["in", order_ids], "docstatus": ["<", 2], "is_return": 0},
        fields=["name", "docstatus", "shopify_order_id"])


def tax_rows(template):
    return frappe.get_all("Sales Taxes and Charges", filters={"parent": template, "parenttype": "Sales Taxes and Charges Template"},
        fields=["charge_type", "account_head", "description", "rate", "included_in_print_rate", "cost_center"], order_by="idx asc")


if action == "list":
    t = till_of(profile)
    orders = frappe.get_all("Sales Order",
        filters={"docstatus": 1, "company": t.company, "status": ["not in", OPEN_STATUSES], "shopify_order_id": ["is", "set"]},
        fields=["name", "shopify_order_id", "shopify_order_number", "customer_name", "transaction_date", "grand_total", "currency"],
        order_by="transaction_date asc, creation asc", limit_page_length=200)
    done = []
    started = {}
    for s in sales_for([o.shopify_order_id for o in orders]):
        if s.docstatus == 1:
            done.append(s.shopify_order_id)
        else:
            started[s.shopify_order_id] = s.name
    out = []
    for o in orders:
        if o.shopify_order_id in done:
            continue
        out.append({"name": o.name, "order_no": o.shopify_order_number or "", "customer": o.customer_name or "",
            "date": str(o.transaction_date or ""), "total": o.grand_total, "currency": o.currency,
            "started": started.get(o.shopify_order_id) or ""})
    frappe.response["message"] = out

elif action == "open":
    t = till_of(profile)
    so_name = str(form.get("sales_order") or "")
    if not frappe.db.exists("Sales Order", so_name):
        frappe.throw("Sales Order " + so_name + " was not found.")
    so = frappe.get_doc("Sales Order", so_name)
    if so.docstatus != 1 or not so.get("shopify_order_id") or so.company != t.company or so.status in OPEN_STATUSES:
        frappe.throw(so.name + " is not a Shopify order waiting on this till.")

    existing = sales_for([so.shopify_order_id])
    for s in existing:
        if s.docstatus == 1:
            frappe.throw("Shopify order " + str(so.shopify_order_number or "") + " was already completed on " + s.name + ".")
    if existing:
        # opened earlier and not finished: carry on with the same sale, never a second one
        frappe.response["message"] = {"name": existing[0].name}
    else:
        # Shopify's VAT: the Sales Order holds Shopify's own tax per line. None at all = Shopify charged no VAT
        # (an international order), so the sale is rung up at VAT 0% with the export comment filled in.
        # (a fully discounted order has no VAT because it has no value: that is not an export)
        zero = frappe.utils.flt(so.total_taxes_and_charges) == 0 and frappe.utils.flt(so.net_total) > 0
        if zero and not t.custom_zero_vat_template:
            frappe.throw("This Shopify order has no VAT, but the till has no Zero-rated VAT Template.")
        tax_of = {}
        for d in (so.get("item_wise_tax_details") or []):
            tax_of[d.item_row] = frappe.utils.flt(tax_of.get(d.item_row)) + frappe.utils.flt(d.amount)

        si = frappe.new_doc("Sales Invoice")
        si.customer = so.customer
        si.company = so.company
        si.is_pos = 1
        si.is_created_using_pos = 1
        si.pos_profile = profile
        si.update_stock = 1
        si.set_warehouse = t.warehouse
        si.currency = so.currency
        si.conversion_rate = 1
        si.selling_price_list = t.selling_price_list
        si.price_list_currency = so.currency
        si.plc_conversion_rate = 1
        si.ignore_pricing_rule = 1
        si.disable_rounded_total = 1  # exactly what Shopify charged, to the cent (no rounding to the rand)
        si.letter_head = t.letter_head
        si.po_no = so.shopify_order_number or ""
        si.shopify_order_id = so.shopify_order_id
        si.shopify_order_number = so.shopify_order_number
        if zero:
            si.tax_category = "Zero Rated"
            si.taxes_and_charges = t.custom_zero_vat_template
            country = frappe.db.get_value("Address", so.shipping_address_name, "country") if so.get("shipping_address_name") else ""
            si.custom_export_comment = "Shopify order " + str(so.shopify_order_number or "") + (", shipped to " + country if country else "")
        else:
            si.taxes_and_charges = t.taxes_and_charges
        for i in so.items:
            qty = frappe.utils.flt(i.qty)
            line = frappe.utils.flt(i.net_amount or i.amount)
            if not zero:
                line_tax = tax_of.get(i.name)
                if line_tax is None and frappe.utils.flt(so.net_total):
                    line_tax = frappe.utils.flt(so.total_taxes_and_charges) * line / frappe.utils.flt(so.net_total)
                line = line + frappe.utils.flt(line_tax)
            # the till's prices include VAT: Shopify's line total (after any discount code) per unit
            rate = frappe.utils.flt(line / qty, 2) if qty else 0
            free = rate <= 0
            si.append("items", {"item_code": i.item_code, "item_name": i.item_name, "description": i.description, "qty": qty,
                "uom": i.uom, "stock_uom": i.stock_uom, "conversion_factor": i.conversion_factor or 1,
                "rate": 0 if free else rate, "price_list_rate": 0 if free else rate, "discount_percentage": 100 if free else 0,
                "warehouse": t.warehouse})
        for tax in tax_rows(si.taxes_and_charges):
            si.append("taxes", tax)
        si.insert()  # as the till user, who rings up sales anyway

        # paid in Shopify: the till's payment methods (ERPNext's own reset, as a new till sale gets them),
        # with the whole amount on "Shopify"
        si.reset_mode_of_payments()
        if not [p for p in si.payments if p.mode_of_payment == PAYMENT]:
            frappe.throw("Add the payment method " + PAYMENT + " to the " + profile + " POS Profile first.")
        total = frappe.utils.flt(si.grand_total)
        for p in si.payments:
            p.amount = total if p.mode_of_payment == PAYMENT else 0
            p.default = 1 if p.mode_of_payment == PAYMENT else 0
        si.save()
        frappe.response["message"] = {"name": si.name}

else:
    frappe.throw("Unknown action.")
