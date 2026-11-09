# POS QUOTES (ticket 0128, Russell, 6 Nov 2026). A till saves a quote from its cart - anything can go on
# it, in stock or not - and finds it under Recent Orders > Quotes. "Invoice this quote" builds a draft till
# sale at the quoted prices, and the till opens that draft as it opens any draft: stock, payment, the VAT
# selector and Sage all work as on any sale. Nothing reaches Sage until that sale is completed.
# Called by the Client Script "POS Quote". Till logins have no Selling roles, so the documents are written here.
# action = price | save | list | invoice
VALID_DAYS = 30
form = frappe.form_dict
action = form.get("action")


def till_of(profile):
    if not profile or not frappe.db.exists("POS Profile", profile):
        frappe.throw("This quote has no till.")
    user = frappe.session.user
    if not frappe.db.exists("POS Profile User", {"parent": profile, "user": user}) and not frappe.db.exists("Has Role", {"parent": user, "parenttype": "User", "role": "System Manager"}):
        frappe.throw("You are not on the " + profile + " till.")
    return frappe.db.get_value("POS Profile", profile, ["company", "currency", "customer", "selling_price_list", "taxes_and_charges", "warehouse", "letter_head"], as_dict=True)


def list_price(item_code, price_list):
    return float(frappe.db.get_value("Item Price", {"item_code": item_code, "price_list": price_list, "selling": 1}, "price_list_rate") or 0)


def tax_rows(template):
    return frappe.get_all("Sales Taxes and Charges", filters={"parent": template, "parenttype": "Sales Taxes and Charges Template"}, fields=["charge_type", "account_head", "description", "rate", "included_in_print_rate", "cost_center"], order_by="idx asc")


if action == "price":
    t = till_of(form.get("pos_profile"))
    frappe.response["message"] = {"rate": list_price(form.get("item_code"), t.selling_price_list)}

elif action == "save":
    profile = form.get("pos_profile")
    t = till_of(profile)
    customer = form.get("customer")
    if not customer or not frappe.db.exists("Customer", customer) or customer == t.customer:
        frappe.throw("A quote needs a customer: choose or add them on the cart first.")
    rows = json.loads(form.get("items") or "[]")
    if not rows:
        frappe.throw("Add at least one item.")
    q = frappe.new_doc("Quotation")
    q.quotation_to = "Customer"
    q.party_name = customer
    q.company = t.company
    q.order_type = "Sales"
    q.transaction_date = frappe.utils.nowdate()
    q.valid_till = form.get("valid_till") or frappe.utils.add_days(frappe.utils.nowdate(), VALID_DAYS)
    q.currency = t.currency
    q.conversion_rate = 1
    q.selling_price_list = t.selling_price_list
    q.price_list_currency = t.currency
    q.plc_conversion_rate = 1
    q.ignore_pricing_rule = 1
    q.letter_head = t.letter_head
    q.taxes_and_charges = t.taxes_and_charges
    q.custom_pos_profile = profile
    q.custom_sales_representative = form.get("sales_person") or None
    for row in rows:
        code = row.get("item_code")
        item = frappe.db.get_value("Item", code, ["item_name", "description", "stock_uom", "disabled"], as_dict=True)
        if not item or item.disabled:
            frappe.throw(str(code) + " is not an item that can be quoted.")
        qty = float(row.get("qty") or 0)
        rate = float(row.get("rate") or 0)
        if qty <= 0 or rate <= 0:
            frappe.throw("Enter a quantity and a price for " + str(code) + ".")
        q.append("items", {"item_code": code, "item_name": item.item_name, "description": item.description or item.item_name, "qty": qty, "uom": item.stock_uom, "stock_uom": item.stock_uom, "conversion_factor": 1, "rate": rate, "price_list_rate": list_price(code, t.selling_price_list) or rate})
    for tax in tax_rows(t.taxes_and_charges):
        q.append("taxes", tax)
    q.flags.ignore_permissions = True
    q.insert()
    q.submit()
    frappe.response["message"] = {"name": q.name, "grand_total": q.grand_total, "currency": q.currency, "letter_head": q.letter_head}

elif action == "list":
    profile = form.get("pos_profile")
    till_of(profile)
    values = {"profile": profile}
    search = ""
    term = (form.get("term") or "").strip()
    if term:
        values["like"] = "%" + term + "%"
        search = " and (q.name like %(like)s or q.party_name like %(like)s or q.customer_name like %(like)s)"
    # a quote leaves the list once its sale is completed; a draft sale keeps it here to carry on
    found = frappe.db.sql("select q.name, q.customer_name, q.party_name as customer, q.grand_total, q.currency, q.transaction_date as posting_date, q.creation, q.status from `tabQuotation` q left join `tabSales Invoice` si on si.name = q.custom_sales_invoice where q.docstatus = 1 and q.custom_pos_profile = %(profile)s and ifnull(si.docstatus, 0) != 1" + search + " order by q.creation desc limit 50", values, as_dict=True)
    out = []
    for r in found:
        out.append({"doctype": "Quotation", "name": r.name, "customer_name": r.customer_name or r.customer, "customer": r.customer, "grand_total": r.grand_total, "currency": r.currency, "status": r.status, "posting_date": str(r.posting_date), "posting_time": str(r.creation).split(" ")[1][:8]})
    frappe.response["message"] = out

elif action == "invoice":
    q = frappe.get_doc("Quotation", form.get("quotation"))
    profile = q.get("custom_pos_profile")
    t = till_of(profile)
    if q.docstatus != 1:
        frappe.throw(q.name + " is not an open quote.")
    existing = q.get("custom_sales_invoice")
    state = frappe.db.get_value("Sales Invoice", existing, "docstatus") if existing else None
    if state == 1:
        frappe.throw(q.name + " has already been invoiced on " + existing + ".")
    if state == 0:
        # started earlier and not finished: carry on with the same sale, never a second one
        frappe.response["message"] = {"name": existing}
    else:
        si = frappe.new_doc("Sales Invoice")
        si.customer = q.party_name
        si.company = q.company
        si.is_pos = 1
        si.is_created_using_pos = 1
        si.pos_profile = profile
        si.update_stock = 1
        si.set_warehouse = t.warehouse
        si.currency = q.currency
        si.conversion_rate = 1
        si.selling_price_list = q.selling_price_list
        si.price_list_currency = q.currency
        si.plc_conversion_rate = 1
        si.ignore_pricing_rule = 1
        si.letter_head = q.letter_head
        si.taxes_and_charges = t.taxes_and_charges
        si.custom_sales_representative = q.get("custom_sales_representative")
        for i in q.items:
            si.append("items", {"item_code": i.item_code, "item_name": i.item_name, "description": i.description, "qty": i.qty, "uom": i.uom, "stock_uom": i.stock_uom, "conversion_factor": i.conversion_factor or 1, "rate": i.rate, "price_list_rate": i.price_list_rate, "warehouse": t.warehouse})
        for tax in tax_rows(t.taxes_and_charges):
            si.append("taxes", tax)
        si.flags.ignore_permissions = True
        si.insert()
        frappe.db.set_value("Quotation", q.name, "custom_sales_invoice", si.name, update_modified=False)
        frappe.response["message"] = {"name": si.name}

else:
    frappe.throw("Unknown action.")
