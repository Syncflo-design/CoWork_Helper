# INVOICE TO (Russell, 1 Nov 2026 - go-live day): the tax invoice always prints the "Invoice To"
# block - one format for every sale. On each sale it is filled from the customer: name, VAT number
# and primary address. A walk-in sale on the till's cash customer leaves it empty (the receipt
# shows no customer, as before). After the sale the three fields stay editable (allow on submit),
# so a customer who comes back for an invoice in a company's name gets it by editing Invoice To
# and printing again; the customer, the ledger and Sage are unchanged.
# A return copies Invoice To from the sale it returns, so it keeps whatever the sale carried.
if not (doc.get("is_return") and doc.get("custom_invoice_to_name")):
    walk_in = frappe.db.get_value("POS Profile", doc.pos_profile, "customer") if doc.get("pos_profile") else None
    if doc.customer and doc.customer != walk_in:
        doc.custom_invoice_to_name = doc.customer_name or doc.customer
        doc.custom_invoice_to_vat = doc.get("tax_id") or frappe.db.get_value("Customer", doc.customer, "tax_id") or ""
        # the sale's address; on a brand-new invoice ERPNext sets it only after this runs, so fall
        # back to the customer's primary address (else any address linked to the customer)
        addr = doc.get("customer_address")
        if not addr:
            linked = frappe.get_all("Dynamic Link", filters={"link_doctype": "Customer", "link_name": doc.customer, "parenttype": "Address"}, pluck="parent")
            for n in linked:
                if frappe.db.get_value("Address", n, "is_primary_address"):
                    addr = n
                    break
            if not addr and linked:
                addr = linked[0]
        lines = []
        if addr:
            a = frappe.db.get_value("Address", addr, ["address_line1", "address_line2", "city", "state", "pincode", "country"], as_dict=True)
            if a:
                town = []
                for v in [a.city, a.state, a.pincode]:
                    if v:
                        town.append(str(v))
                for v in [a.address_line1, a.address_line2, " ".join(town), a.country]:
                    if v:
                        lines.append(str(v))
        doc.custom_invoice_to_address = "\n".join(lines)
    else:
        doc.custom_invoice_to_name = ""
        doc.custom_invoice_to_vat = ""
        doc.custom_invoice_to_address = ""
