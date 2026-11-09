# SALES OTHER (Russell, 6 Nov 2026, ticket 0129): a till line with no item code is a Sales Other line, typed by
# the cashier with the till's "Sales Other" button: a description and a price including VAT, for an income
# account, not stock. No Item record exists for it. These rules hold whatever the screen did:
#   qty is always 1 (-1 on a credit note) and it never has a line discount;
#   a sale carrying one takes no discount on the whole sale (ERPNext would spread it over this line too);
#   the description is at most 100 characters (Sage refuses more);
#   the Sage company must have its one Sales Other account chosen (Company Sage Integration).
# A credit note for it stands alone: ERPNext cannot submit a stock-updating return that holds a no-item line,
# so such a return switches stock updating off and cannot also carry stock lines.
if doc.get("is_pos"):
    others = [row for row in doc.items if not row.item_code]
    if others:
        if frappe.utils.flt(doc.get("additional_discount_percentage")) or frappe.utils.flt(doc.get("discount_amount")):
            frappe.throw("This sale has a Sales Other line, so it cannot take a discount on the whole sale. Remove the discount, or ring the Sales Other line as a separate sale.", title="Sales Other")
        for row in others:
            words = frappe.utils.strip_html(str(row.item_name or "")).strip()
            if not words:
                frappe.throw("A Sales Other line needs a description.", title="Sales Other")
            if len(words) > 100:
                frappe.throw("A Sales Other description can be at most 100 characters.", title="Sales Other")
            if abs(frappe.utils.flt(row.qty)) != 1:
                frappe.throw("A Sales Other line is always quantity 1.", title="Sales Other")
            if frappe.utils.flt(row.rate) <= 0:
                frappe.throw("A Sales Other line needs a price.", title="Sales Other")
            if frappe.utils.flt(row.discount_percentage) or frappe.utils.flt(row.discount_amount):
                frappe.throw("A Sales Other line cannot have a discount.", title="Sales Other")
            row.item_name = words
            row.description = words
            row.price_list_rate = row.rate

        if doc.company != "Ardmore Ceramics TEST":
            entity = frappe.db.get_value("POS Profile", doc.pos_profile, "custom_sage_entity") if doc.get("pos_profile") else None
            if not entity and doc.get("set_warehouse"):
                entity = frappe.db.get_value("Warehouse", doc.set_warehouse, "custom_sage_entity")
            if not entity or not frappe.db.get_value("Company Sage Integration", entity, "custom_sage_sales_other_account_id"):
                frappe.throw("No Sales Other account is chosen for " + str(entity or doc.get("pos_profile") or doc.company) + ". Ask head office to choose it on Company Sage Integration.", title="Sales Other")
            income = "Sales - Other - " + str(frappe.db.get_value("Company", doc.company, "abbr"))
            if not frappe.db.exists("Account", income):
                frappe.throw("Account " + income + " does not exist.", title="Sales Other")
            for row in others:
                row.income_account = income

        if doc.get("is_return"):
            if len(others) != len(doc.items):
                frappe.throw("Return the Sales Other line on its own credit note, separately from the stock items.", title="Sales Other")
            doc.update_stock = 0
