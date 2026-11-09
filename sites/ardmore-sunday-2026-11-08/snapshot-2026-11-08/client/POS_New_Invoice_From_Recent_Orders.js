// =============================================================
// Ardmore POS - "New Invoice" from Recent Orders and after a sale
// Client Script on POS Invoice (Form) - evaluated inside the POS page.
// -------------------------------------------------------------
// Standard ERPNext: the New Invoice button only acts when the cart has
// unsaved items or the payment screen is showing. So it does nothing with
// Recent Orders open (v1, 2026-09-21) and nothing on the receipt screen
// after Complete Order, where the current invoice is already submitted
// (v2, 2026-10-01, Brittany 24 Sept). Both now start a clean invoice.
// An unsaved cart is still left to ERPNext's own confirm.
// v3 (2026-10-28): after Complete Order, ERPNext opened Recent Orders with
// the order summary hidden, so a sale could not be opened or returned until
// the page was reloaded. The summary now always shows with Recent Orders.
// =============================================================
(function () {
	'use strict';
	if (window.__ardmore_new_invoice_fix_v3) return;
	window.__ardmore_new_invoice_fix_v3 = true;

	document.addEventListener('click', function (e) {
		const pos = window.cur_pos;
		if (!pos || !pos.page || !pos.page.btn_primary) return;
		if ((frappe.get_route() || [])[0] !== 'point-of-sale') return;
		const btn = pos.page.btn_primary.get(0);
		if (!btn || !(e.target === btn || btn.contains(e.target))) return;

		const frm = pos.frm;
		const recent_open = pos.recent_order_list && pos.recent_order_list.$component.is(':visible');
		const submitted = frm && frm.doc && frm.doc.docstatus === 1; // receipt screen after Complete Order
		if (!recent_open && !submitted) return; // normal flow: ERPNext handles it

		const unsaved_cart = frm && frm.doc && frm.doc.docstatus === 0 &&
			(frm.doc.items || []).length !== 0 && (frm.is_new() || frm.is_dirty());
		if (unsaved_cart) return; // let ERPNext ask about the unsaved cart

		e.preventDefault();
		e.stopImmediatePropagation();
		pos.load_new_invoice_on_pos();
		if (pos.page.btn_secondary && pos.page.btn_secondary.get(0)) {
			pos.page.btn_secondary.get(0).innerText = __('Recent Orders');
		}
	}, true);

	setInterval(function () {
		const pos = window.cur_pos;
		if (!pos || !pos.toggle_recent_order_list || pos.__ard_summary_fix) return;
		pos.__ard_summary_fix = true;
		const toggle = pos.toggle_recent_order_list;
		pos.toggle_recent_order_list = function (show) {
			toggle.apply(this, arguments);
			if (show && this.order_summary) this.order_summary.toggle_component(true);
		};
	}, 1000);
})();
