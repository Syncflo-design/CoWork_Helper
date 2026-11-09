# Sage -> ERPNext account customers (hourly).  Rewritten 2026-10-21 for Russell.
#
# WHAT: pulls every Sage customer whose category is NOT listed in "Sage customer
# categories NOT synced" on Company Sage Integration (default: the till and web
# walk-in categories). The Sage category becomes the Customer Group. The customer's
# Sage ID in THAT Sage company goes to Sage Customer Selection - one row per customer
# per company, like Sage Item Selection - and Account Sales (non-till invoices) post
# against it. See post-taxinvoice-to-sage.
#
# HOW: one Sage company at a time, 100 customers a page, at most PAGES_PER_RUN pages a
# run, resuming from "Customer sync position". When Sage runs out the position resets
# to 0 and Last Customer Sync moves on, so the next pass asks Sage only for customers
# changed since then. Sage inactive customers are mapped if we already have them,
# never created. The training company never talks to Sage.
#
# NEVER run two copies at once (e.g. by hand while the hour's run is going): both
# insert the same new customers and trip over each other's saves. To run it now, enqueue
# the Scheduled Job Type (execute_event) - do not call execute_scheduled_method from an
# API script, the request times out while the work carries on.
#
# WHY REWRITTEN: the old version matched on a Customer "company" field that does not
# exist, so it never found what it had made and inserted the whole Sage customer list
# again every night (Sept/Oct 2025: 28,224 customers from 1,802 names). It also stored
# Sage's raw text in the validated Email / Phone fields of the Customer AND its primary
# Contact (Customer.email_id / mobile_no are fetched back from that Contact on every
# save), so those records cannot be saved until both are cleaned - done below on first touch.
PAGES_PER_RUN = 5
TRAINING_COMPANIES = ["Ardmore Ceramics TEST"]
# Jon's address is the Sage email on staff/cash accounts such as Store Sales (Credit Card)
# (2 Nov 2026) - never copied onto an ERPNext customer, so it never prints on an invoice
IGNORED_EMAILS = ["jon@ardmore-design.com", "jon@ardmoreceramics.co.za"]


def clean(v):
    if v is None:
        return ""
    return str(v).strip()


def parse_groups(raw):
    out = []
    for p in str(raw or "").split(","):
        g = p.strip().lower()
        if g:
            out.append(g)
    return out


def norm_phone(ph):
    # ERPNext's Phone field insists on a country code (+27...). Sage holds free text.
    digits = ""
    for ch in ph:
        if ch in "0123456789":
            digits = digits + ch
    cand = ""
    if ph.startswith("+") and len(digits) >= 10:
        cand = "+" + digits
    elif len(digits) == 10 and digits.startswith("0"):
        cand = "+27" + digits[1:]
    elif len(digits) == 11 and digits.startswith("27"):
        cand = "+" + digits
    if not cand:
        return ""
    # the same check the Phone field runs on save - anything it refuses is dropped, not fatal
    try:
        frappe.utils.validate_phone_number_with_country_code(cand, "phone")
    except Exception:
        return ""
    return cand


def first_email(em):
    # Sage often holds "a@x.com;b@y.com" - ERPNext takes one valid address
    em = em.replace(";", " ").replace(",", " ")
    for p in em.split():
        if "@" in p and "." in p and p.lower() not in IGNORED_EMAILS:
            return p.lower()
    return ""


def fix_contact(cname):
    # The primary Contact feeds Customer.email_id / mobile_no on every save (fetch_from), so
    # raw Sage text there blocks the customer too. Clean it once; drop rows left empty.
    c = frappe.get_doc("Contact", cname)
    changed = 0
    em = first_email(clean(c.get("email_id")))
    if clean(c.get("email_id")) != em:
        c.email_id = em
        changed = 1
    keep_emails = []
    for row in (c.get("email_ids") or []):
        fixed = first_email(clean(row.email_id))
        if clean(row.email_id) != fixed:
            changed = 1
        if fixed:
            row.email_id = fixed
            keep_emails.append(row)
    if changed:
        c.email_ids = keep_emails
    for fld in ["mobile_no", "phone"]:
        fixed = norm_phone(clean(c.get(fld)))
        if clean(c.get(fld)) != fixed:
            c.set(fld, fixed)
            changed = 1
    keep_phones = []
    phones_changed = 0
    for row in (c.get("phone_nos") or []):
        fixed = norm_phone(clean(row.phone))
        if clean(row.phone) != fixed:
            phones_changed = 1
        if fixed:
            row.phone = fixed
            keep_phones.append(row)
    if phones_changed:
        c.phone_nos = keep_phones
        changed = 1
    if changed:
        c.save(ignore_permissions=True)


def ensure_group(g):
    if g and not frappe.db.exists("Customer Group", g):
        cg = frappe.new_doc("Customer Group")
        cg.customer_group_name = g
        cg.parent_customer_group = "All Customer Groups"
        cg.is_group = 0
        cg.insert(ignore_permissions=True)


def find_customer(company, sid, cname):
    # 1. already mapped for this company
    cust = frappe.db.get_value("Sage Customer Selection", {"company": company, "sage_customer_id": sid}, "customer")
    if cust and frappe.db.exists("Customer", cust):
        return cust
    # 2. the old single Sage ID field on Customer
    cust = frappe.db.get_value("Customer", {"custom_sage_customer_id": sid}, "name")
    if cust:
        return cust
    # 3. same name: prefer one already mapped for another Sage company, else the oldest
    cands = frappe.get_all("Customer", filters={"customer_name": cname}, fields=["name"], order_by="creation asc", limit_page_length=100)
    for c in cands:
        if frappe.db.exists("Sage Customer Selection", {"customer": c.name}):
            return c.name
    if cands:
        return cands[0].name
    # 4. a record whose ID is the name (Customer is named by customer name)
    if frappe.db.exists("Customer", cname):
        return cname
    return None


def upsert_selection(cust, company, sid, group):
    sel = frappe.db.get_value("Sage Customer Selection", {"customer": cust, "company": company}, "name")
    if sel:
        frappe.db.set_value("Sage Customer Selection", sel, {"sage_customer_id": sid, "sage_category": group})
    else:
        s = frappe.new_doc("Sage Customer Selection")
        s.customer = cust
        s.company = company
        s.sage_customer_id = sid
        s.sage_category = group
        s.insert(ignore_permissions=True)


def apply_customer(c, company, group):
    sid = clean(c.get("name"))
    cname = clean(c.get("customer_name"))
    inactive = 1 if c.get("disabled") else 0
    em = first_email(clean(c.get("email_id")))
    ph = norm_phone(clean(c.get("telephone")))
    cust = find_customer(company, sid, cname)
    if not cust:
        if inactive:
            return "skipped"
        d = frappe.new_doc("Customer")
        d.customer_name = cname
        d.customer_type = "Company"
        if group:
            d.customer_group = group
        if em:
            d.email_id = em
            d.custom_email_address = em
        if ph:
            d.custom_phone = ph
        d.custom_sage_customer_id = sid
        d.insert(ignore_permissions=True)
        upsert_selection(d.name, company, sid, group)
        return "created"
    d = frappe.get_doc("Customer", cust)
    changed = 0
    # the old sync wrote the Sage category into Customer Type (a Select) - repair or the save fails
    if d.get("customer_type") not in ["Company", "Individual", "Partnership"]:
        d.customer_type = "Company"
        changed = 1
    # ...and raw Sage text into the validated Email / Phone fields - clean or the save fails
    old_em = clean(d.get("email_id"))
    if old_em and old_em != first_email(old_em):
        d.email_id = first_email(old_em)
        changed = 1
    old_mob = clean(d.get("mobile_no"))
    if old_mob and old_mob != norm_phone(old_mob):
        d.mobile_no = norm_phone(old_mob)
        changed = 1
    old_ph = clean(d.get("custom_phone"))
    if old_ph and old_ph != norm_phone(old_ph):
        d.custom_phone = norm_phone(old_ph)
        changed = 1
    if group and d.get("customer_group") != group:
        d.customer_group = group
        changed = 1
    if em and d.get("custom_email_address") != em:
        d.custom_email_address = em
        changed = 1
    if ph and d.get("custom_phone") != ph:
        d.custom_phone = ph
        changed = 1
    if not d.get("custom_sage_customer_id"):
        d.custom_sage_customer_id = sid
        changed = 1
    if changed:
        if d.get("customer_primary_contact") and frappe.db.exists("Contact", d.get("customer_primary_contact")):
            fix_contact(d.get("customer_primary_contact"))
        d.save(ignore_permissions=True)
    upsert_selection(cust, company, sid, group)
    return "updated" if changed else "same"


integrations = frappe.get_all("Company Sage Integration", fields=["name", "company"])
for integration in integrations:
    if integration.company in TRAINING_COMPANIES:
        continue
    sage = frappe.get_doc("Company Sage Integration", integration.name)
    ra = sage.get("custom_sage_retry_after")
    if ra and str(ra) > frappe.utils.now():
        continue  # Sage asked us to back off (set by the item sync)
    apikey = sage.get_password("api_key")
    loginName = sage.username
    loginPwd = sage.get_password("password")
    if not apikey or not loginName or not loginPwd:
        continue
    excluded = parse_groups(sage.get("custom_customer_sync_exclude_groups"))
    lastDate = str(sage.get("custom_last_customer_sync") or "1970-01-01")
    skip = int(sage.get("custom_customer_sync_skip") or 0)
    payload = {"loginName": loginName, "loginPwd": loginPwd, "useOAuth": False, "sessionToken": None, "provider": None}
    counts = {"created": 0, "updated": 0, "same": 0, "skipped": 0, "errors": 0}
    pages = 0
    finished = 0
    while pages < PAGES_PER_RUN:
        url = f"https://pharoh.co.za/api/CustomersSync/get-customers-for-erpnext?apikey={apikey}&lastDate={lastDate}&skipQty={skip}"
        try:
            r = frappe.make_post_request(url, json=payload, headers={"Content-Type": "application/json"})
        except Exception as http_err:
            # the URL carries the API key - keep it out of the log
            frappe.log_error(message=integration.company + ": " + str(http_err)[:600].replace(str(apikey), "***"), title="Sage customer sync: Pharoh call failed")
            break
        items = r.get("items") or []
        total = int(r.get("totalResults") or 0)
        for c in items:
            group = clean(c.get("customer_group"))
            if group == "All Customer Groups":
                group = ""  # Pharoh's stand-in for "no category in Sage"
            if group.lower() in excluded or not clean(c.get("customer_name")):
                counts["skipped"] = counts["skipped"] + 1
                continue
            try:
                ensure_group(group)
                res = apply_customer(c, integration.company, group)
                counts[res] = counts[res] + 1
            except Exception as e:
                counts["errors"] = counts["errors"] + 1
                if counts["errors"] <= 5:
                    frappe.log_error(message=integration.company + " / Sage " + clean(c.get("name")) + " " + clean(c.get("customer_name")) + ": " + str(e)[:800], title="Sage customer sync: customer failed")
        skip = skip + len(items)
        pages = pages + 1
        if not items or skip >= total:
            finished = 1
            skip = 0
        frappe.db.set_value("Company Sage Integration", integration.name, "custom_customer_sync_skip", skip)
        if finished:
            # a day of overlap on purpose: a pass can span several hours, and re-reading a customer is harmless
            frappe.db.set_value("Company Sage Integration", integration.name, "custom_last_customer_sync", frappe.utils.add_days(frappe.utils.nowdate(), -1))
        frappe.db.commit()
        if finished:
            break
    if counts["created"] or counts["updated"] or counts["errors"]:
        tail = "pass complete" if finished else "more to come next hour"
        frappe.log_error(message=integration.company + ": created " + str(counts["created"]) + ", updated " + str(counts["updated"]) + ", unchanged " + str(counts["same"]) + ", skipped (excluded category, inactive or no name) " + str(counts["skipped"]) + ", errors " + str(counts["errors"]) + ". Position " + str(skip) + ", " + tail + ".", title="Sage customer sync")
