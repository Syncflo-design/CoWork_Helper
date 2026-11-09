// Warn the moment Update Only is ticked, so nobody discovers after the fact
// that their new items were never created.
frappe.ui.form.on('Kiln Sheet Importer', {
    update_only(frm) {
        if (!frm.doc.update_only) return;
        frappe.msgprint({
            title: __('Update Only - please read'),
            indicator: 'orange',
            message: __(
                'This import will <b>only change items that are already in the system</b>.'
                + '<br><br>'
                + 'Anything in your sheet that does not exist yet will <b>not</b> be created, '
                + 'and <b>no stock will be added</b>.'
                + '<br><br>'
                + 'Use this to correct details such as the category or a price. '
                + 'Anything that could not be updated is listed when the import finishes.'
            )
        });
    }
});
