// =============================================================
// Ardmore POS - no "Permanently Submit?" pop-up on the till (v1, 2026-09-29)
// Client Script on POS Invoice (Form) - evaluated inside the POS page
// (loaded by "POS Till Scripts Loader" in Sales Invoice mode).
// -------------------------------------------------------------
// Finishing a sale took three clicks: Checkout, Complete Order, then Yes on
// "Permanently Submit ACC-SINV-...?". Cheri, 24 Sept 2026: too many.
// Russell, 2026-09-29: remove the last one only.
//
// The pop-up is Frappe's standard confirmation inside frm.savesubmit(), which
// the till calls from Complete Order. This script wraps savesubmit ON THE
// TILL'S OWN FORM ONLY and answers that one confirmation with Yes. Everything
// else in savesubmit still runs as standard (validation, before_submit, save,
// on_submit), so the voucher prompt, the Sage post and the receipt are
// unchanged. Sales Invoices opened in the normal desk form keep the pop-up.
//
// NOTE: once Complete Order is clicked the sale is final. It posts to Sage
// within seconds and can only be undone with a return.
//
// The till rebuilds its form when the cashier leaves and comes back, so this
// keeps watching and wraps each new form once.
// =============================================================
(function () {
	'use strict';
	if (window.__ardmore_pos_no_submit_confirm_v1) return;
	window.__ardmore_pos_no_submit_confirm_v1 = true;

	function till_visible() {
		const page = document.getElementById('page-point-of-sale');
		return !!(page && page.offsetParent !== null);
	}

	function wrap(frm) {
		if (!frm || frm.__ardmore_no_submit_confirm || typeof frm.savesubmit !== 'function') return;
		const standard = frm.savesubmit;

		frm.savesubmit = function (btn, callback, on_error) {
			if (!till_visible()) return standard.call(this, btn, callback, on_error);

			// savesubmit calls frappe.confirm synchronously, exactly once.
			// Swap it for that one call, then put the real one straight back.
			const real_confirm = frappe.confirm;
			frappe.confirm = function (message, if_yes) {
				frappe.confirm = real_confirm;
				if (if_yes) if_yes();
			};
			let result;
			try {
				result = standard.call(this, btn, callback, on_error);
			} finally {
				frappe.confirm = real_confirm;
			}
			// A sale the server refused (e.g. "Wholesale price missing") is still a draft, but
			// savesubmit resolves anyway and the till would show "created successfully" and the
			// receipt. Hold the promise instead so the cashier stays on the payment screen (27 Oct 2026).
			const me = this;
			return Promise.resolve(result).then(function (r) {
				return me.doc.docstatus === 1 ? r : new Promise(function () {});
			});
		};
		frm.__ardmore_no_submit_confirm = true;
	}

	setInterval(function () {
		const pos = window.cur_pos;
		if (pos && pos.frm) wrap(pos.frm);
	}, 1000);
})();
