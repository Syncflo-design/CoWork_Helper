# VAT 0% SALES AWAITING EXPORT PROOF (Russell, 28 Oct 2026): the badge on the "Export Proof" tile
# (Nest Home). A paid VAT 0% sale (so not a draft, a return or a returned sale) with no flight
# number from the till and no courier waybill yet. Same filters as the tile's list.
frappe.response["message"] = frappe.db.count("Sales Invoice", {
    "status": "Paid",
    "tax_category": "Zero Rated",
    "custom_export_flight_no": ["is", "not set"],
    "custom_export_waybill": ["is", "not set"],
})
