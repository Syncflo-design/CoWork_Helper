// =============================================================
// Ardmore POS - Split payment auto-balance (v2, 2026-09-21)
// Lives on POS Invoice; also loaded for Sales Invoice tills by the
// Client Script "POS Till Scripts Loader" (POS Settings > Invoice Type =
// Sales Invoice on Ardmore).
// -------------------------------------------------------------
// When the cashier enters an amount on a non-default mode (e.g. Voucher),
// the default mode (Credit Card) is set to what is left to pay, so a
// R6555 sale with a R1000 voucher shows R5555 on card automatically.
// Editing the default mode directly is left alone. Returns are skipped.
// =============================================================
(function () {
	'use strict';
	if (window.__ardmore_pos_autobalance_v2) return;
	window.__ardmore_pos_autobalance_v2 = true;

	// The till's page element, not frappe.get_route(): opened by its URL, the nest_home
	// redirect leaves the route on "nest-home" while the till is on screen (27 Oct 2026).
	function on_pos() {
		const page = document.getElementById('page-point-of-sale');
		return !!(page && page.offsetParent !== null);
	}

	frappe.ui.form.on('Sales Invoice Payment', {
		amount(frm, cdt, cdn) {
			if (!on_pos()) return;
			if (frm.doctype !== 'Sales Invoice' && frm.doctype !== 'POS Invoice') return;
			if (frm.doc.is_return || frm.doc.docstatus) return;
			const row = locals[cdt] && locals[cdt][cdn];
			if (!row || row.default) return;
			const payments = frm.doc.payments || [];
			const def = payments.find((p) => p.default);
			if (!def) return;

			const total = cint(frappe.sys_defaults.disable_rounded_total)
				? flt(frm.doc.grand_total) : flt(frm.doc.rounded_total);
			const others = payments
				.filter((p) => p.name !== def.name)
				.reduce((s, p) => s + flt(p.amount), 0);
			const want = flt(Math.max(total - others, 0), precision('amount', def));
			if (Math.abs(flt(def.amount) - want) < 0.005) return;

			const pos = window.cur_pos;
			const pay = pos && pos.payment;
			const key = pay && pay.sanitize_mode_of_payment
				? pay.sanitize_mode_of_payment(def.mode_of_payment) + '_control' : null;
			const ctl = key && pay[key];
			if (ctl && ctl.$input) {
				// goes through the POS control so the on-screen amount updates too
				ctl.set_value(want);
			} else {
				frappe.model.set_value(def.doctype, def.name, 'amount', want);
			}
		}
	});
})();
