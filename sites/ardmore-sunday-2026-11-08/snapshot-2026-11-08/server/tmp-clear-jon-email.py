# ONE-OFF (2 Nov 2026, Russell): Jon's address is the email Sage holds for the till cash account
# "Store Sales (Credit Card)" (Sage Home 4150404, every till's default customer), so it landed on
# every walk-in invoice. Remove it from that account's Customer + Contacts, and teach the hourly
# customer sync to ignore Jon's address so it does not come back. Other customers are untouched.
if not frappe.db.exists("Has Role", {"parent": frappe.session.user, "role": "System Manager"}):
    frappe.throw("Not permitted")

JON = ["jon@ardmore-design.com", "jon@ardmoreceramics.co.za"]
TARGETS = ["Store Sales (Credit Card)"]
out = {"contacts": 0, "contact_rows": 0, "customer_fields": 0, "errors": [], "sync_patch": ""}

for cust in TARGETS:
    contacts = frappe.get_all("Dynamic Link",
        filters={"link_doctype": "Customer", "link_name": cust, "parenttype": "Contact"}, pluck="parent")
    for cname in contacts:
        try:
            c = frappe.get_doc("Contact", cname)
            keep = []
            for row in (c.get("email_ids") or []):
                if str(row.email_id or "").strip().lower() in JON:
                    out["contact_rows"] = out["contact_rows"] + 1
                else:
                    keep.append(row)
            changed = len(keep) != len(c.get("email_ids") or [])
            if str(c.email_id or "").strip().lower() in JON:
                c.email_id = keep[0].email_id if keep else ""
                changed = True
            if changed:
                c.email_ids = keep
                if keep and not [r for r in keep if r.is_primary]:
                    keep[0].is_primary = 1
                c.save(ignore_permissions=True)
                out["contacts"] = out["contacts"] + 1
        except Exception as e:
            out["errors"].append("Contact " + cname + ": " + str(e)[:200])
    for fld in ["email_id", "custom_email_address"]:
        if str(frappe.db.get_value("Customer", cust, fld) or "").strip().lower() in JON:
            frappe.db.set_value("Customer", cust, fld, "", update_modified=False)
            out["customer_fields"] = out["customer_fields"] + 1
frappe.db.commit()

# Hourly sync: never take Jon's address from Sage again (existing values elsewhere are left as they are)
ss = frappe.get_doc("Server Script", "get-customers-for-erpnext-new")
old = ("        if \"@\" in p and \".\" in p:\n"
       "            return p.lower()\n")
new = ("        if \"@\" in p and \".\" in p and p.lower() not in IGNORED_EMAILS:\n"
       "            return p.lower()\n")
anchor = "TRAINING_COMPANIES = [\"Ardmore Ceramics TEST\"]\n"
const = (anchor + "# Jon's address is the Sage email on staff/cash accounts such as Store Sales (Credit Card)\n"
         "# (2 Nov 2026) - never copied onto an ERPNext customer, so it never prints on an invoice\n"
         "IGNORED_EMAILS = [\"jon@ardmore-design.com\", \"jon@ardmoreceramics.co.za\"]\n")
if "IGNORED_EMAILS" in ss.script:
    out["sync_patch"] = "already patched"
elif ss.script.count(old) == 1 and ss.script.count(anchor) == 1:
    ss.script = ss.script.replace(old, new).replace(anchor, const)
    ss.save()
    out["sync_patch"] = "patched"
else:
    out["sync_patch"] = "skipped - anchors not found exactly once"

frappe.response["message"] = out
