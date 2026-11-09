# SALES OTHER ACCOUNT (Russell, 6 Nov 2026, ticket 0129): the accounts in one company's Sage that a Sales
# Other line can post to, for the picker on Company Sage Integration. Income accounts only: Sage reports
# them as "Sales" or "Other Income". Read-only. System Manager, the only role that can edit that screen.
if not frappe.db.exists("Has Role", {"parent": frappe.session.user, "parenttype": "User", "role": "System Manager"}):
    frappe.throw("Only a System Manager can read the Sage accounts.")

company = frappe.form_dict.get("company")
sage = frappe.get_doc("Company Sage Integration", company)
apikey = sage.get_password("api_key")
creds = {"loginName": sage.username, "loginPwd": sage.get_password("password"), "useOAuth": False, "sessionToken": None, "provider": None}
accounts = []
skip = 0
total = 1
try:
    while skip < total:
        r = frappe.make_post_request("https://pharoh.co.za/api/AccountsSync/get-accounts-for-erpnext?apikey=" + apikey + "&lastDate=1970-01-01&skipQty=" + str(skip), json=creds) or {}
        items = r.get("items") or []
        total = int(r.get("totalResults") or 0)
        if not items:
            break
        for a in items:
            account_id = int(a.get("sageacct_idx") or 0)
            if account_id > 0 and not a.get("disabled") and a.get("account_type") in ["Sales", "Other Income"]:
                accounts.append({"id": account_id, "name": a.get("account_name"), "type": a.get("account_type")})
        skip = skip + len(items)
except Exception as e:
    frappe.throw("Could not read the accounts from Sage for " + str(company) + ": " + str(e)[:200].replace(str(apikey), "***"))

frappe.response["message"] = sorted(accounts, key=lambda a: str(a["name"]).lower())
