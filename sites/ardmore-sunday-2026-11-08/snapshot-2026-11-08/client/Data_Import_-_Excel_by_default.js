// Ardmore (Russell, 3 Nov 2026): Download Template opens on Excel, not CSV, so the workbook that
// comes back can be uploaded again as it is. CSV is still one click away in the dialog.
// The v16 import wizard calls frm.events.download_template, which is the LAST handler registered,
// so this must not register its own download_template handler (that hid Frappe's and the button
// did nothing). Instead it wraps Frappe's handler once the form has loaded.
frappe.ui.form.on('Data Import', {
	onload(frm) {
		const standard = frm.events.download_template;
		if (!standard || standard._ardmore_excel) return;
		const wrapped = function (frm) {
			standard(frm);
			let tries = 0;
			const timer = setInterval(() => {
				const dialog = frm.data_exporter && frm.data_exporter.dialog;
				if (dialog && dialog.display) {
					clearInterval(timer);
					dialog.set_value('file_type', 'Excel');
				} else if (++tries > 40) {
					clearInterval(timer);
				}
			}, 250);
		};
		wrapped._ardmore_excel = true;
		frm.events.download_template = wrapped;
	}
});
