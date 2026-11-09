# Till "Select POS User" list (rebuilt 27 Oct 2026, Client Script "POS Sales Person").
# Returns the Sales Person records linked to a till (Sales Person.pos_profile). Runs on the
# server because till logins have no read permission on Sales Person. Names only.
profile = frappe.form_dict.get("pos_profile") or ""
if not profile:
    frappe.response["message"] = []
else:
    frappe.response["message"] = frappe.get_all(
        "Sales Person",
        filters={"pos_profile": profile, "enabled": 1, "is_group": 0},
        fields=["name", "sales_person_name"],
        order_by="sales_person_name asc")
