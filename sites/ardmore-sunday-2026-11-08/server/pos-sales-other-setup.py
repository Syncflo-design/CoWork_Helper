# SALES OTHER (Russell, 6 Nov 2026, ticket 0129): what the till's Sales Other button needs to add a line, and a
# refusal up front when the till's Sage company has no Sales Other account chosen yet.
pos_profile = frappe.form_dict.get("pos_profile")
user = frappe.session.user
if not frappe.db.exists("POS Profile User", {"parent": pos_profile, "parenttype": "POS Profile", "user": user}) and not frappe.db.exists("Has Role", {"parent": user, "parenttype": "User", "role": "System Manager"}):
    frappe.throw("You are not set up on the till " + str(pos_profile) + ".")

till = frappe.db.get_value("POS Profile", pos_profile, ["company", "warehouse", "custom_sage_entity", "cost_center"], as_dict=True)
entity = till.custom_sage_entity or frappe.db.get_value("Warehouse", till.warehouse, "custom_sage_entity")
if not entity or not frappe.db.get_value("Company Sage Integration", entity, "custom_sage_sales_other_account_id"):
    frappe.throw("No Sales Other account is chosen for " + str(entity or pos_profile) + ". Ask head office to choose it on Company Sage Integration.", title="Sales Other")

income = "Sales - Other - " + str(frappe.db.get_value("Company", till.company, "abbr"))
if not frappe.db.exists("Account", income):
    frappe.throw("Account " + income + " does not exist.", title="Sales Other")

frappe.response["message"] = {
    "income_account": income,
    "cost_center": till.cost_center or frappe.db.get_value("Company", till.company, "cost_center"),
    "uom": "each"
}
