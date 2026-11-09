// =============================================================
// Ardmore POS - a till that sells from several warehouses (v1, 2026-11-03)
// Client Script on POS Invoice (Form) - evaluated inside the POS page
// (loaded by "POS Till Scripts Loader" in Sales Invoice mode).
// -------------------------------------------------------------
// Russell, 2026-11-03: the Online till shows and sells what is in the Online Store AND in the
// warehouses on its POS Profile's "Also Sell From Warehouses" (all Atrium + Main Distribution).
// * Item list and search: server script pos_pool_items, quantities added up across them.
// * Cart stock check and the item panel's quantity: server script pos_pool_stock (same total).
// * Sale: lines still sell from the till's warehouse; Server Script "Sales Invoice - Online Auto
//   Transfer" first moves in whatever it is short of, and that transfer posts the intercompany pair.
// Tills without that field filled in behave exactly as before.
// =============================================================
(function () {
	'use strict';
	if (window.__ardmore_pos_pool_v1) return;
	window.__ardmore_pos_pool_v1 = true;

	// the till's POS Profile name when it sells from other warehouses too, else null
	function pool_profile() {
		const s = window.cur_pos && window.cur_pos.settings;
		return s && (s.custom_also_sell_from || '').trim() ? s.name : null;
	}

	function patch_selector() {
		const cls = window.erpnext && erpnext.PointOfSale && erpnext.PointOfSale.ItemSelector;
		if (!cls) return false;
		if (cls.prototype.__ardmore_pool) return true;

		const std_get_items = cls.prototype.get_items;
		cls.prototype.get_items = function (args) {
			const profile = pool_profile();
			if (!profile) return std_get_items.apply(this, arguments);
			const a = args || {};
			const doc = this.events.get_frm().doc;
			// same arguments and reply shape as the standard call; callers chain .then().always()
			return frappe.call({
				method: 'pos_pool_items',
				freeze: true,
				args: {
					pos_profile: this.pos_profile || profile,
					start: a.start || 0,
					page_length: a.page_length || 40,
					price_list: (doc && doc.selling_price_list) || this.price_list,
					item_group: this.item_group,
					search_term: a.search_term || ''
				}
			});
		};

		cls.prototype.__ardmore_pool = true;
		return true;
	}

	function patch_controller() {
		const cls = window.erpnext && erpnext.PointOfSale && erpnext.PointOfSale.Controller;
		if (!cls) return false;
		if (cls.prototype.__ardmore_pool) return true;

		// check_stock_availability and the item panel both ask this for [qty, is_stock_item, negative allowed]
		const std_stock = cls.prototype.get_available_stock;
		cls.prototype.get_available_stock = function (item_code, warehouse) {
			const profile = pool_profile();
			if (!profile) return std_stock.apply(this, arguments);
			const me = this;
			return frappe.call({
				method: 'pos_pool_stock',
				args: { pos_profile: profile, item_code: item_code },
				callback(res) {
					if (!me.item_stock_map[item_code]) me.item_stock_map[item_code] = {};
					me.item_stock_map[item_code][warehouse] = res.message;
				}
			});
		};

		cls.prototype.__ardmore_pool = true;
		return true;
	}

	function patch_all() {
		const a = patch_selector();
		const b = patch_controller();
		return a && b;
	}

	if (!patch_all()) {
		let tries = 0;
		const timer = setInterval(() => {
			tries = tries + 1;
			if (patch_all() || tries > 30) clearInterval(timer);
		}, 1000);
	}
})();
