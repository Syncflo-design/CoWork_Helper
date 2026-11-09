# ZERO-RATED SALE (Russell, 28 Oct 2026): a sale rung up at VAT 0% with the till's VAT selector
# (tax category "Zero Rated" + the till's zero-rated tax template). The customer still pays the
# full price, so it all becomes the exclusive amount. Items carry the standard 15% Item Tax
# Template, which would put the VAT back, so it is cleared on every line before the totals are
# worked out. A return copies the tax category, so it is zero-rated too.
if doc.get("tax_category") == "Zero Rated":
    for row in doc.items:
        row.item_tax_template = None
        row.item_tax_rate = "{}"

    # EXPORT PROOF (Russell, 28 Oct 2026): the till takes the flight number or a comment; the
    # courier waybill is added at dispatch ("Export Waybill No.", editable after submit).
    flight = (doc.get("custom_export_flight_no") or "").strip()
    comment = (doc.get("custom_export_comment") or "").strip()
    if doc.docstatus == 1 and not doc.get("is_return") and not flight and not comment:
        frappe.throw("This sale is at VAT 0%. Click Edit Cart and enter the flight number or a comment under VAT 0%, then complete the sale.", title="Export details missing")
