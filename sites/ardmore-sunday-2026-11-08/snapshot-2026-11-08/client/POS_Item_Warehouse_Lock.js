// =============================================================
// Ardmore POS - Item Details panel: Warehouse and UOM Conversion Factor hidden (v2, 2026-11-02)
// Client Script on POS Invoice (Form) - evaluated inside the POS page
// (loaded by "POS Till Scripts Loader" in Sales Invoice mode).
// -------------------------------------------------------------
// Russell, 2026-11-02: a cashier must not pick another warehouse for a line, and
// has no use for the conversion factor. Every line sells from the till's own
// warehouse (POS Profile), which the invoice fills in on save.
// v1 locked the Warehouse box; v2 hides both boxes (same day).
//
// Wraps ItemDetails.bind_custom_control_change_event (it builds the panel's
// controls each time an item is opened).
// =============================================================
(function () {
	'use strict';
	if (window.__ardmore_pos_wh_lock_v2) return;
	window.__ardmore_pos_wh_lock_v2 = true;

	const HIDE = ['warehouse', 'conversion_factor'];

	function hide(details) {
		const wc = details.warehouse_control;
		if (wc) {
			wc.df.read_only = 1;
			wc.df.reqd = 0;
		}
		if (details.$form_container) {
			HIDE.forEach((f) => details.$form_container.find('.' + f + '-control').hide());
		}
	}

	function patch() {
		const cls = window.erpnext && erpnext.PointOfSale && erpnext.PointOfSale.ItemDetails;
		if (!cls) return false;
		if (cls.prototype.__ardmore_wh_lock_v2) return true;
		const standard = cls.prototype.bind_custom_control_change_event;
		cls.prototype.bind_custom_control_change_event = function () {
			const result = standard.apply(this, arguments);
			try { hide(this); } catch (e) { console.warn('Ardmore POS item panel:', e); }
			return result;
		};
		cls.prototype.__ardmore_wh_lock_v2 = true;
		return true;
	}

	if (!patch()) {
		let tries = 0;
		const timer = setInterval(() => {
			tries = tries + 1;
			if (patch() || tries > 30) clearInterval(timer);
		}, 1000);
	}
})();
