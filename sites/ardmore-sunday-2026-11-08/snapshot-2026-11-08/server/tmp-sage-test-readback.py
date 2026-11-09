# TEMPORARY (final testing, 27 Oct 2026): read documents back from the Sage TESTING
# company through Pharoh's history endpoint. Read only. DELETE after final testing.
if not frappe.db.exists("Has Role", {"parent": frappe.session.user, "role": "System Manager"}):
    frappe.throw("Not permitted")
company = "Ardmore Ceramics TEST"
wanted = str(frappe.form_dict.get("docs") or "")
dtype = frappe.form_dict.get("dtype") or "Invoice"
day = frappe.form_dict.get("date") or frappe.utils.nowdate()
sage = frappe.get_doc("Company Sage Integration", company)
apikey = sage.get_password("api_key")
creds = {"loginName": sage.username, "loginPwd": sage.get_password("password"), "useOAuth": False, "sessionToken": None, "provider": None}
nums = [x.strip() for x in wanted.split(",") if x.strip()]
out = []
skip = 0
while True:
    url = "https://pharoh.co.za/api/TaxInvoice/get-sales-history-for-erpnext?apikey=" + apikey + "&fromDate=" + day + "&toDate=" + day + "&documentType=" + dtype + "&skipQty=" + str(skip)
    resp = frappe.make_post_request(url, json=creds, headers={"Content-Type": "application/json"}) or {}
    page = resp.get("items") or []
    if not page:
        break
    for inv in page:
        if not nums or str(inv.get("documentNumber")) in nums:
            out.append(inv)
    skip = skip + len(page)
    if skip >= int(resp.get("totalResults") or 0):
        break
frappe.response["message"] = out
