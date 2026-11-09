# "Send to Sage" button on a Sales Invoice / Credit Note.  (2026-09-29)
#
# Runs the same posting script the document runs on submit, on demand. Used for:
#   - a document that has used up its automatic retries, once the cause is fixed
#   - a "Check Sage" document, after someone has confirmed Sage does NOT have it
# The posting scripts carry the TEST-ONLY lock, so this cannot reach a live
# Sage company while the lock is on.
#
# Permission is checked on the document itself: frappe.has_permission is not
# available inside a Server Script, the document's own method is.
name = frappe.form_dict.get("name")
if not name:
    frappe.throw("No invoice given.")

inv = frappe.get_doc("Sales Invoice", name)
if not inv.has_permission("write"):
    frappe.throw("You do not have permission to send this document to Sage.")
if inv.docstatus != 1:
    frappe.throw("Only a submitted document can be sent to Sage.")
if inv.get("custom_sage_sync_status") == "Synced" and inv.get("custom_sage_order_id"):
    frappe.throw("This document is already in Sage.")
TRAINING_COMPANIES = ["Ardmore Ceramics TEST"]  # training company never talks to Sage (2026-10-16)
if inv.company in TRAINING_COMPANIES:
    frappe.throw("This is a training document. The training company is never sent to Sage.")
if inv.get("is_pos") and inv.get("is_consolidated"):
    frappe.throw("Day-end consolidated invoices are not sent to Sage.")

script_name = "post-customerreturn-to-sage" if inv.get("is_return") else "post-taxinvoice-to-sage"
script = frappe.get_doc("Server Script", script_name)
if script.disabled:
    frappe.throw("Sage posting is switched off (" + script_name + " is disabled).")

try:
    script.execute_doc(inv)
except Exception as e:
    pass  # status and reason are already written to the document

frappe.response["message"] = frappe.db.get_value(
    "Sales Invoice", name,
    ["custom_sage_sync_status", "custom_sage_document_number", "custom_sage_sync_error"],
    as_dict=True)
