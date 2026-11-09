# One-off (Russell, 2026-10-21): remove the customers Paul's 2025 sync inserted every night.
# 28,224 Customers were 1,802 names; none of the copies carries a transaction.
#
# KEEPS a customer when ANY of these is true:
#   - it has a Sage Customer Selection row (mapped by the hourly customer sync)
#   - the old Sage Customer ID field is filled
#   - it appears on a Sales Invoice, Sales Order, Delivery Note, Quotation or Payment Entry
#   - it is the default customer on a POS Profile
#   - it was created today (the hourly sync may be mid-way through it)
#   - ERPNext refuses the delete because something else links to it (e.g. a Contact on an
#     old POS Invoice, or "you can disable this Customer instead") - such a customer is
#     marked KEEP-LINKED in the old Sage ID field so the next batch skips it. Any other
#     failure (a busy queue, a lock) is simply retried.
# Runs every 2 minutes, BATCH at a time, logs a summary, and disables itself when nothing is left.
BATCH = 200

rows = frappe.db.sql("""
    select c.name from `tabCustomer` c
    where (c.custom_sage_customer_id is null or c.custom_sage_customer_id = '')
      and date(c.creation) < curdate()
      and not exists (select 1 from `tabSage Customer Selection` s where s.customer = c.name)
      and not exists (select 1 from `tabSales Invoice` t where t.customer = c.name)
      and not exists (select 1 from `tabSales Order` t where t.customer = c.name)
      and not exists (select 1 from `tabDelivery Note` t where t.customer = c.name)
      and not exists (select 1 from `tabQuotation` t where t.quotation_to = 'Customer' and t.party_name = c.name)
      and not exists (select 1 from `tabPayment Entry` t where t.party_type = 'Customer' and t.party = c.name)
      and not exists (select 1 from `tabPOS Profile` t where t.customer = c.name)
    order by c.creation desc
    limit %s
""", (BATCH,), as_dict=1)

if not rows:
    frappe.db.set_value("Server Script", "cleanup-duplicate-customers-once", "disabled", 1)
    frappe.db.commit()
    frappe.log_error(message="No unused duplicate customers left. Job disabled itself. Customers now: " + str(frappe.db.count("Customer")) + "; kept because something links to them: " + str(frappe.db.count("Customer", {"custom_sage_customer_id": "KEEP-LINKED"})), title="Customer cleanup finished")
else:
    deleted = 0
    kept = 0
    retry = 0
    first_err = ""
    for r in rows:
        try:
            frappe.delete_doc("Customer", r.name, ignore_permissions=True)
            deleted = deleted + 1
        except Exception as e:
            msg = str(e)
            if "linked with" in msg or "Cannot delete" in msg or "disable this" in msg:
                kept = kept + 1
                frappe.db.set_value("Customer", r.name, "custom_sage_customer_id", "KEEP-LINKED", update_modified=False)
            else:
                retry = retry + 1
            if not first_err:
                first_err = r.name + ": " + msg[:300]
        if (deleted + kept + retry) % 50 == 0:
            frappe.db.commit()
    frappe.db.commit()
    frappe.log_error(message="Deleted " + str(deleted) + ", kept (linked) " + str(kept) + ", to retry " + str(retry) + ". Remaining customers: " + str(frappe.db.count("Customer")) + (" First error: " + first_err if first_err else ""), title="Customer cleanup batch")
