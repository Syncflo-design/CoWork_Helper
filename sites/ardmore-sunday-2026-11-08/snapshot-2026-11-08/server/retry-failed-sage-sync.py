# Retry sales and returns that did not reach Sage.  (2026-09-29)
#
# A till sale or return is never blocked when Sage cannot be reached: the
# document stands and is flagged "Failed". Until now nothing ever tried again,
# so Sage stayed short of that sale and its stock drifted from ERPNext.
#
# Every 15 minutes this job picks up documents flagged "Failed" and runs the
# SAME Server Script that posts them on submit, so there is one posting routine,
# one TEST-ONLY lock, one set of rules:
#     sales    -> post-taxinvoice-to-sage
#     returns  -> post-customerreturn-to-sage
# Sales go first, so a return whose sale has just got through can follow in the
# same run.
#
# NOT retried here:
#   "Check Sage"   the connection dropped after sending; a resend could create a
#                  duplicate in Sage. A person checks, then uses "Send to Sage".
#   MAX_ATTEMPTS   reached. The reason is on the document (Sage Sync Error).
#                  Fix the cause, then use "Send to Sage" on the invoice.
#   anything dated before START_DATE (older documents were never meant to post).
MAX_ATTEMPTS = 8
BATCH = 15
# Go-live (review 31 Oct 2026): nothing from the test period is ever resent once the lock is off.
START_DATE = "2026-11-01"

SALE_SCRIPT = "post-taxinvoice-to-sage"
RETURN_SCRIPT = "post-customerreturn-to-sage"

rows = frappe.get_all(
    "Sales Invoice",
    filters={
        "docstatus": 1,
        "custom_sage_sync_status": "Failed",
        "posting_date": [">=", START_DATE],
        "custom_sage_sync_attempts": ["<", MAX_ATTEMPTS],
    },
    fields=["name", "is_return"],
    order_by="is_return asc, creation asc",
    limit_page_length=BATCH)

if rows:
    sale_script = frappe.get_doc("Server Script", SALE_SCRIPT)
    return_script = frappe.get_doc("Server Script", RETURN_SCRIPT)

    sent = 0
    still_failed = 0
    for r in rows:
        try:
            inv = frappe.get_doc("Sales Invoice", r.name)
            script = return_script if inv.get("is_return") else sale_script
            if script.disabled:
                continue
            script.execute_doc(inv)
            if frappe.db.get_value("Sales Invoice", r.name, "custom_sage_sync_status") == "Synced":
                sent = sent + 1
            else:
                still_failed = still_failed + 1
        except Exception as e:
            # back-office documents throw on failure - the status and reason are
            # already on the document, so just carry on with the next one
            still_failed = still_failed + 1
        frappe.db.commit()

    if still_failed:
        frappe.log_error(
            message=f"Retried {len(rows)} document(s): {sent} reached Sage, {still_failed} still failing. Open Sales Invoice list, filter Sage Sync Status = Failed, and read Sage Sync Error on each.",
            title="Sage retry: documents still failing")
