// Sales Invoice - "Send to Sage" button (2026-09-29)
// Shown on a submitted sale or credit note that has NOT reached Sage.
//   Failed      resend is safe
//   Check Sage  the connection dropped after sending; Sage may already have it,
//               so the user must confirm they have looked in Sage first
// The automatic retry runs every 15 minutes; this is for the ones it cannot do.
//
// Desk form only. The till uses a Sales Invoice form of its own and this script
// is loaded there too, so it steps aside on the till.
frappe.ui.form.on('Sales Invoice', {
	refresh: function (frm) {
		if ((frappe.get_route() || [])[0] === 'point-of-sale') return;
		if (window.cur_pos && window.cur_pos.frm === frm) return;
		if (frm.doc.docstatus !== 1) return;
		if (frm.doc.is_pos && frm.doc.is_consolidated) return;
		const status = frm.doc.custom_sage_sync_status || '';
		if (status === 'Synced' && frm.doc.custom_sage_order_id) return;
		if (status !== 'Failed' && status !== 'Check Sage') return;

		if (frm.doc.custom_sage_sync_error && frm.dashboard && frm.dashboard.set_headline_alert) {
			frm.dashboard.set_headline_alert(
				__('Not in Sage: {0}', [frappe.utils.escape_html(frm.doc.custom_sage_sync_error)]),
				status === 'Check Sage' ? 'orange' : 'red'
			);
		}

		frm.add_custom_button(__('Send to Sage'), function () {
			const send = function () {
				frappe.call({
					method: 'ardmore_send_invoice_to_sage',
					args: { name: frm.doc.name },
					freeze: true,
					freeze_message: __('Sending to Sage...'),
					callback: function (r) {
						const m = r.message || {};
						if (m.custom_sage_sync_status === 'Synced') {
							frappe.show_alert({ message: __('In Sage as {0}', [m.custom_sage_document_number || '']), indicator: 'green' });
						} else {
							frappe.msgprint({
								title: __('Still not in Sage'),
								indicator: 'red',
								message: frappe.utils.escape_html(m.custom_sage_sync_error || __('No reason was returned.'))
							});
						}
						frm.reload_doc();
					}
				});
			};
			if (status === 'Check Sage') {
				frappe.confirm(
					__('The connection dropped while this was being sent, so Sage may already have it. Have you checked Sage for reference {0}? Sending again could create a duplicate.', [frm.doc.name]),
					send
				);
			} else {
				send();
			}
		});
	}
});
