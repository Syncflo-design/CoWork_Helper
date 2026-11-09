frappe.ui.form.on('Home Fashion Importer', {
    attach_excel_file: function(frm) {
        if (!frm.doc.attach_excel_file) {
            frm.set_value('sheet_data', '');
            return;
        }
        frappe.call({
            method: 'nest_sheets.api.read_sheet',
            args: { file_url: frm.doc.attach_excel_file },
            freeze: true,
            freeze_message: 'Reading spreadsheet...',
            callback: function(r) {
                if (r && r.message) {
                    frm.set_value('sheet_data', JSON.stringify(r.message));
                }
            },
            error: function() {
                frappe.msgprint('Could not read the file. Make sure the Nest Sheets app is installed.');
            }
        });
    },
    refresh: function(frm) {
        if (frm.doc.issues_csv) {
            frm.add_custom_button('Download Issues', function() {
                var blob = new Blob([frm.doc.issues_csv], {type: 'text/csv;charset=utf-8'});
                var url = window.URL.createObjectURL(blob);
                var a = document.createElement('a');
                a.href = url;
                a.download = 'home-fashion-import-issues-' + frm.doc.name + '.csv';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            });
        } else if (frm.doc.import_log) {
            // Older imports have no CSV - fall back to the text log.
            frm.add_custom_button('Download Error Log', function() {
                var lines = (frm.doc.import_log || '').split('\n');
                var keep = [];
                for (var i = 0; i < lines.length; i++) {
                    var l = lines[i];
                    var isSuccessRow = (l.indexOf('Row ') === 0 && (l.indexOf(' created.') !== -1 || l.indexOf(' updated.') !== -1));
                    if (!isSuccessRow) keep.push(l);
                }
                var text = 'Home/Fashion Import - Error Log\nDocument: ' + frm.doc.name + '\n\n' + keep.join('\n') + '\n';
                var blob = new Blob([text], {type: 'text/plain;charset=utf-8'});
                var url = window.URL.createObjectURL(blob);
                var a = document.createElement('a');
                a.href = url;
                a.download = 'home-fashion-import-error-log-' + frm.doc.name + '.txt';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            });
        }
    }
});