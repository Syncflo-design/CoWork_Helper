# TEMPORARY (2 Nov 2026): read-only lookup of a Sage GL account by name in ONE Sage company.
# Returns every field Pharoh sends for the matching accounts, so the Sage account id can be read.
if not frappe.db.exists("Has Role", {"parent": frappe.session.user, "role": "System Manager"}):
    frappe.throw("Not permitted")

wanted = str(frappe.form_dict.get("name") or "Sales - Other").strip().lower()
company = str(frappe.form_dict.get("company") or "Home")
sage = frappe.get_doc("Company Sage Integration", company)
apikey = sage.get_password("api_key")
payload = {"loginName": sage.username, "loginPwd": sage.get_password("password"),
           "useOAuth": False, "sessionToken": None, "provider": None}
hits = []
seen = 0
skip = int(frappe.form_dict.get("skip") or 0)
total = skip + 1
fields = []
err = ""
pages = 0
while skip < total and pages < 3:
    try:
        r = frappe.make_post_request(
            "https://pharoh.co.za/api/AccountsSync/get-accounts-for-erpnext?apikey=" + apikey + "&lastDate=1970-01-01&skipQty=" + str(skip),
            json=payload) or {}
    except Exception as e:
        err = str(e)[:200].replace(str(apikey), "***")
        break
    pages = pages + 1
    items = r.get("items") or []
    total = int(r.get("totalResults") or 0)
    returned = int(r.get("returnedResults") or len(items))
    if not items:
        break
    if not fields:
        fields = list(items[0].keys())
    for a in items:
        seen = seen + 1
        if str(a.get("account_name") or "").strip().lower() == wanted:
            hits.append(a)
    skip = skip + returned

frappe.response["message"] = {"company": company, "accounts_read": seen, "next_skip": skip, "total": total, "matches": hits, "fields": fields, "error": err}
