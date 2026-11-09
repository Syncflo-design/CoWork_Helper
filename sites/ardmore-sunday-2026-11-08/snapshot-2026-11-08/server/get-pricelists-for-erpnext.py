# Per-company, ID-mapped price-list sync.
# Matches ERPNext Price List to Sage by custom_sage_pricelist_id (rename-safe),
# names every list "<Company> - <Sage name>", stores the Sage id + company.

# --- TEST SCOPING: only these companies run. Set to [] to process ALL. ---
test_companies = []

base_url = "https://pharoh.co.za/api/AdditionalPriceListSync/get-pricelists-for-erpnext"

created = []
updated = []
skipped = []
errors = []

def as_int(v):
    return 1 if v else 0

company_rows = frappe.get_all("Company Sage Integration", fields=["name"])

for ci in range(len(company_rows)):
    integ_name = company_rows[ci]["name"]
    try:
        sage = frappe.get_doc("Company Sage Integration", integ_name)
    except Exception as e:
        errors.append("Load integration " + str(integ_name) + ": " + str(e))
        continue

    company = sage.company
    if test_companies and (company not in test_companies):
        continue

    apikey = sage.get_password("api_key")
    login_name = sage.username
    login_pwd = sage.get_password("password")

    payload = {"loginName": login_name, "loginPwd": login_pwd,
               "useOAuth": False, "sessionToken": None, "provider": None}
    url = base_url + "?apikey=" + str(apikey)

    try:
        pricelists = frappe.make_post_request(url, json=payload)
    except Exception as e:
        errors.append("Fetch for " + str(company) + ": " + str(e))
        continue

    if not pricelists:
        continue

    for pi in range(len(pricelists)):
        pl = pricelists[pi]
        sage_id = str(pl.get("id") or "").strip()
        sage_name = str(pl.get("name") or "").strip()
        if (not sage_id) or (not sage_name):
            skipped.append("Blank id/name for " + str(company))
            continue

        desired_name = str(company) + " - " + sage_name
        pl_desc = pl.get("description")
        pl_default = as_int(pl.get("isDefault"))
        pl_enabled = as_int(pl.get("enabled"))

        # 1) already mapped by Sage id (+ company) -> update in place
        existing = frappe.db.get_value(
            "Price List",
            {"custom_sage_pricelist_id": sage_id, "custom_sage_company": company},
            "name")

        if existing:
            try:
                doc = frappe.get_doc("Price List", existing)
                doc.custom_description = pl_desc
                doc.custom_is_default = pl_default
                doc.enabled = pl_enabled
                doc.custom_sage_company = company
                doc.save(ignore_permissions=True)
                updated.append(desired_name)
            except Exception as e:
                errors.append("Update " + desired_name + ": " + str(e))
            continue

        # 2) a list with the target name exists but isn't mapped -> adopt it
        if frappe.db.exists("Price List", desired_name):
            try:
                doc = frappe.get_doc("Price List", desired_name)
                doc.custom_sage_pricelist_id = sage_id
                doc.custom_sage_company = company
                doc.custom_description = pl_desc
                doc.custom_is_default = pl_default
                doc.enabled = pl_enabled
                doc.save(ignore_permissions=True)
                updated.append(desired_name + " (adopted)")
            except Exception as e:
                errors.append("Adopt " + desired_name + ": " + str(e))
            continue

        # 3) new -> create
        try:
            new_doc = frappe.get_doc({
                "doctype": "Price List",
                "price_list_name": desired_name,
                "custom_sage_pricelist_id": sage_id,
                "custom_sage_company": company,
                "custom_description": pl_desc,
                "custom_is_default": pl_default,
                "enabled": pl_enabled,
                "selling": 1,
                "buying": 1,
                "currency": "ZAR"
            })
            new_doc.insert(ignore_permissions=True)
            created.append(desired_name)
        except Exception as e:
            errors.append("Create " + desired_name + ": " + str(e))

summary = ("Price lists — Created: " + str(len(created)) +
           " | Updated: " + str(len(updated)) +
           " | Skipped: " + str(len(skipped)) +
           " | Errors: " + str(len(errors)))
msg = summary
if created:
    msg = msg + "<br>Created: " + ", ".join(created)
if updated:
    msg = msg + "<br>Updated: " + ", ".join(updated)
if errors:
    msg = msg + "<br>Errors:<br>" + "<br>".join(errors)
frappe.msgprint(msg)
frappe.response["message"] = {"created": created, "updated": updated,
                              "skipped": skipped, "errors": errors}