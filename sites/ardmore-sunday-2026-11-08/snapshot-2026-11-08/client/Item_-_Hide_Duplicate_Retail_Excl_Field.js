// Two fields on this form carry the label "Retail Price Excl Vat":
//
//   custom_retail_price_excl_vat  - ours, populated (incl / 1.15). Keep.
//   standard_rate                 - ERPNext's Standard Selling Rate, relabelled.
//                                   Always R0.00, and it must stay empty: filling
//                                   it writes an Item Price to the DISABLED
//                                   Standard Selling list and the item then
//                                   refuses to save.
//
// It is already hidden via Customize Form, but the form keeps rendering it, so
// hide it at render time as well. Belt and braces - this cannot be cached around.
frappe.ui.form.on('Item', {
    refresh(frm) {
        frm.set_df_property('standard_rate', 'hidden', 1);
        frm.set_df_property('standard_rate', 'read_only', 1);
        frm.refresh_field('standard_rate');
    }
});
