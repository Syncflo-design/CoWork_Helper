// =============================================================
// Ardmore POS Closing - cashier UX (2026-09-07)
// Client Script on POS Closing Entry (Form)
// -------------------------------------------------------------
// * Taxes & Charges table hidden (cashiers don't need it).
// * Closing amounts pre-filled with the expected amounts once the
//   day's invoices load, so the cashier only corrects a difference.
// * One click: Save submits the closing straight away (no Submit,
//   no "Permanently submit?" confirmation).
// 2026-09-29: intro text no longer mentions EFT (removed from every till).
// =============================================================
frappe.ui.form.on('POS Closing Entry', {
	refresh(frm) {
		frm.set_df_property('taxes', 'hidden', 1);
		frm.set_df_property('total_taxes_and_charges', 'hidden', 1);
		frm.set_df_property('net_total', 'hidden', 1);
		if (frm.doc.docstatus === 0) {
			ardmore_prefill_closing(frm);
			frm.set_intro(__('Check the closing amounts against your card machine and voucher totals, then click Save to close the till.'), 'blue');
		}
	},
	pos_opening_entry(frm) {
		if (frm.doc.docstatus === 0) ardmore_prefill_closing(frm);
	},
	after_save(frm) {
		if (frm.doc.docstatus === 0 && !frm.is_new()) {
			setTimeout(() => frm.save('Submit'), 150);
		}
	}
});

function ardmore_prefill_closing(frm) {
	if (frm.__ardmore_prefill_timer) clearInterval(frm.__ardmore_prefill_timer);
	let n = 0;
	frm.__ardmore_prefill_timer = setInterval(() => {
		n += 1;
		if (frm.doc.docstatus !== 0 || n > 60) {
			clearInterval(frm.__ardmore_prefill_timer);
			frm.__ardmore_prefill_timer = null;
			return;
		}
		let changed = false;
		(frm.doc.payment_reconciliation || []).forEach((r) => {
			if (!r.__ardmore_prefilled && flt(r.expected_amount) && !flt(r.closing_amount)) {
				r.closing_amount = flt(r.expected_amount);
				r.difference = 0;
				r.__ardmore_prefilled = 1;
				changed = true;
			}
		});
		if (changed) frm.refresh_field('payment_reconciliation');
	}, 500);
}
