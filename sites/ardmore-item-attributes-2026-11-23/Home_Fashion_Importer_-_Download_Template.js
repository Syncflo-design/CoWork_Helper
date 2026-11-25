// Download Template + Download Current Items (tickets 0165/0166, 23 Nov 2026).
// Both workbooks are built on the server (nest_help.api.download_import_sheet) from
// ERPNext's dropdown lists as they are now, so a list corrected in Customize Form shows
// up in the next download. The old button opened a fixed file whose Allowed values
// sheet was a copy from 29 Sep 2026.
frappe.ui.form.on('Home Fashion Importer', {
    refresh: function(frm) {
        frm.add_custom_button('Download Template', function() {
            window.open('/api/method/nest_help.api.download_import_sheet');
        }, 'fa fa-download');

        // The active items of the chosen Category (all, or only those with stock), with their
        // current attributes, in the template layout. Rows that look wrong are yellow with the
        // reason in the last column. Correct the cells, tick Update Only, attach it and Save.
        frm.add_custom_button('Download Current Items', function() {
            if (['Home', 'Fashion'].indexOf(frm.doc.category) === -1) {
                frappe.msgprint(__('Choose the Category (Home or Fashion) first.'));
                return;
            }
            frappe.prompt({
                fieldname: 'which', fieldtype: 'Select', label: __('Which items'), reqd: 1,
                options: ['Only items with stock', 'All items'], default: 'Only items with stock'
            }, function(values) {
                window.open('/api/method/nest_help.api.download_import_sheet?category='
                    + encodeURIComponent(frm.doc.category)
                    + (values.which === 'All items' ? '' : '&in_stock=1'));
            }, __('Download Current Items'), __('Download'));
        }, 'fa fa-download');
    }
});
