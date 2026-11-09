frappe.ui.form.on('Home Fashion Importer', {
    company(frm) { ardmore_hf_pricelists(frm, true); },
    refresh(frm) { ardmore_hf_pricelists(frm, false); }
});

function ardmore_hf_pricelists(frm, force) {
    if (frm.doc.imported) return;
    const c = frm.doc.company;
    if (!c) return;
    ardmore_hf_pick(frm, 'custom_retail_price_list', c, 'Retail', force);
    ardmore_hf_pick(frm, 'custom_wholesale_price_list', c, 'Wholesale', force);
}

function ardmore_hf_pick(frm, field, company, term, force) {
    if (!force && frm.doc[field]) return;
    frappe.db.get_list('Price List', {
        filters: { custom_sage_company: company, enabled: 1, price_list_name: ['like', '%' + term + '%'] },
        fields: ['name'],
        order_by: 'name asc',
        limit: 1
    }).then(r => {
        if (r && r.length) { frm.set_value(field, r[0].name); }
    });
}