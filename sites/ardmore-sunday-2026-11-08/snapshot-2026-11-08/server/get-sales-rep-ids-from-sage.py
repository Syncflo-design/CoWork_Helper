# Sage rep id for the till sales people (Russell, 27 Oct 2026): the name picked in the till's
# "Select POS User" goes to Sage as the sales rep, so Ardmore can report who sold what.
# The id comes from the person's rep record in the Sage company that owns their till (POS
# Profile "Sage entity"), matched by name. Read only - nothing is written to Sage.
reps = {}
for sp in frappe.get_all("Sales Person", filters={"enabled": 1, "is_group": 0, "pos_profile": ["is", "set"]}, fields=["name", "sales_person_name", "pos_profile", "custom_sage_rep_id"]):
    company = frappe.db.get_value("POS Profile", sp.pos_profile, "custom_sage_entity")
    if not company or not frappe.db.exists("Company Sage Integration", company):
        continue
    if company not in reps:
        reps[company] = {}
        sage = frappe.get_doc("Company Sage Integration", company)
        apikey = sage.get_password("api_key")
        try:
            body = {"loginName": sage.username, "loginPwd": sage.get_password("password"), "useOAuth": False, "sessionToken": None, "provider": None}
            for r in frappe.make_post_request("https://pharoh.co.za/api/SalesReps/get-salesperson-for-erpnext?apikey=" + apikey, json=body) or []:
                reps[company][" ".join(str(r.get("sales_person_name") or "").split()).lower()] = int(r.get("id") or 0)
        except Exception as e:
            frappe.log_error(message=str(e).replace(str(apikey), "***"), title="Sage sales rep ids " + company)
    # names compared with spaces collapsed: Sage holds "Kelly  Blakemore" with two (31 Oct 2026)
    rep_id = reps[company].get(" ".join(str(sp.sales_person_name or sp.name).split()).lower(), 0)
    if rep_id and rep_id != int(sp.custom_sage_rep_id or 0):
        frappe.db.set_value("Sales Person", sp.name, "custom_sage_rep_id", rep_id)
frappe.db.commit()
