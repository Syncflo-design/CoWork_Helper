// =============================================================
// Ardmore POS - price editable on Ceramics items (v2, 2026-11-02)
// Client Script on POS Invoice (Form) - evaluated inside the POS page
// (loaded by "POS Till Scripts Loader" in Sales Invoice mode).
// -------------------------------------------------------------
// Russell, 2026-11-02: cashiers may change the price of any item whose Sage
// Category (Item.custom_category) is "Ceramics"; every other item keeps the
// price-list price. v1 keyed on ticked Item Groups - replaced the same day.
//
// The till's item panel locks the Rate box from POS Profile > Allow Rate Change
// every time an item is opened (ItemDetails.bind_custom_control_change_event).
// This wraps that one method: for a Ceramics item it behaves as if Allow Rate
// Change were on, otherwise it keeps the POS Profile setting. The category is
// read once per item and remembered for the session.
// Sage gets the price as rung up, with no line discount (post-taxinvoice-to-sage).
// =============================================================
(function () {
	'use strict';
	if (window.__ardmore_pos_ceramic_price_v2) return;
	window.__ardmore_pos_ceramic_price_v2 = true;

	const CATEGORY = 'Ceramics';
	const category_of = {}; // item_code -> custom_category

	function item_category(code) {
		if (category_of[code] !== undefined) return Promise.resolve(category_of[code]);
		return frappe.db.get_value('Item', code, 'custom_category').then((r) => {
			category_of[code] = (r && r.message && r.message.custom_category) || '';
			return category_of[code];
		});
	}

	// First time this item is opened: unlock once its category is known.
	function unlock_when_known(details, row) {
		item_category(row.item_code).then((cat) => {
			if (details.current_item !== row || !details.rate_control) return; // cashier moved on
			if (cat === CATEGORY) {
				details.rate_control.df.read_only = 0;
				details.rate_control.refresh();
			}
		});
	}

	function patch() {
		const cls = window.erpnext && erpnext.PointOfSale && erpnext.PointOfSale.ItemDetails;
		if (!cls) return false;
		if (cls.prototype.__ardmore_ceramic_price_v2) return true;
		const standard = cls.prototype.bind_custom_control_change_event;
		cls.prototype.bind_custom_control_change_event = function () {
			if (this.__ardmore_profile_allow === undefined) this.__ardmore_profile_allow = !!this.allow_rate_change;
			const row = this.current_item || {};
			const cat = row.item_code ? category_of[row.item_code] : '';
			this.allow_rate_change = this.__ardmore_profile_allow || cat === CATEGORY;
			const result = standard.apply(this, arguments);
			if (!this.__ardmore_profile_allow && cat === undefined) unlock_when_known(this, row);
			return result;
		};
		cls.prototype.__ardmore_ceramic_price_v2 = true;
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
