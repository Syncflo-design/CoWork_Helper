# Credit notes are numbered CRN-#####, tax invoices stay ACC-SINV (Russell, 2026-10-16;
# prefix ACC-CRN -> CRN on 2026-11-02, old ACC-CRN numbers stay valid).
# Before Insert runs before Frappe names the document, so setting the series here is enough;
# the till sends the sales series for a return as well, and this overrides it.
# Home till sales are numbered JSSA-##### (Russell, 2026-11-02): a till whose POS Profile
# Sage entity is Home. No year in either (Russell, 3 Nov 2026: it only used up characters in the
# Sage reference); JSSA- carries on from JSSA-2026-00011.
if doc.get("is_return"):
    doc.naming_series = "CRN-"
elif doc.get("is_pos") and doc.get("pos_profile"):
    if frappe.db.get_value("POS Profile", doc.pos_profile, "custom_sage_entity") == "Home":
        doc.naming_series = "JSSA-"
