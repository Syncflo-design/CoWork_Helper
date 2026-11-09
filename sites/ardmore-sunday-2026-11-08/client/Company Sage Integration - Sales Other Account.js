// =============================================================
// Ardmore - the Sage account for Sales Other lines (Russell, 6 Nov 2026, ticket 0129)
// Client Script on Company Sage Integration (Form).
// -------------------------------------------------------------
// One account per company: this screen holds one record per company and each
// record holds one account, so choosing another replaces the one that was there.
// The list comes live from that company's Sage (Server Script
// sage-accounts-for-company), income accounts only.
// =============================================================
frappe.ui.form.on('Company Sage Integration', {
	custom_sage_sales_other_select(frm) {
		if (frm.is_new()) {
			frappe.msgprint(__('Save this company first.'));
			return;
		}
		frappe.call({
			method: 'sage_accounts_for_company',
			args: { company: frm.doc.name },
			freeze: true,
			freeze_message: __('Reading the accounts from Sage...')
		}).then((r) => {
			const accounts = r.message || [];
			if (!accounts.length) {
				frappe.msgprint(__('Sage returned no income accounts for {0}.', [frm.doc.name]));
				return;
			}
			const d = new frappe.ui.Dialog({
				title: __('Sales Other account for {0}', [frm.doc.name]),
				fields: [{
					fieldname: 'account',
					fieldtype: 'Autocomplete',
					label: __('Sage account'),
					reqd: 1,
					options: accounts.map((a) => ({ label: a.name + ' (' + a.type + ')', value: String(a.id) })),
					description: frm.doc.custom_sage_sales_other_account
						? __('This replaces {0}.', [frappe.utils.escape_html(frm.doc.custom_sage_sales_other_account)])
						: __('Every Sales Other line on this company\'s tills posts to this one account.')
				}],
				primary_action_label: __('Use this account'),
				primary_action(values) {
					const chosen = accounts.find((a) => String(a.id) === String(values.account));
					if (!chosen) {
						frappe.show_alert({ message: __('Pick an account from the list.'), indicator: 'orange' });
						return;
					}
					d.hide();
					frm.set_value({
						custom_sage_sales_other_account: chosen.name,
						custom_sage_sales_other_account_id: chosen.id
					}).then(() => frm.save());
				}
			});
			d.show();
		});
	}
});
