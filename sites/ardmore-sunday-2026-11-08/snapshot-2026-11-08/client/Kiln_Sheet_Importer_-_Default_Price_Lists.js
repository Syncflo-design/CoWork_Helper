frappe.ui.form.on('Kiln Sheet Importer', {
    company(frm) { ardmore_set_kiln_pricelists(frm, true); },
    refresh(frm) { ardmore_set_kiln_pricelists(frm, false); }
});

function ardmore_set_kiln_pricelists(frm, force) {
    if (frm.doc.imported) return;
    const c = frm.doc.company;
    if (!c) return;
    if (force || !frm.doc.custom_retail_price_list) {
        frm.set_value('custom_retail_price_list', c + ' - Retail');
    }
    if (force || !frm.doc.custom_wholesale_price_list) {
        frm.set_value('custom_wholesale_price_list', c + ' - Wholesale');
    }
}