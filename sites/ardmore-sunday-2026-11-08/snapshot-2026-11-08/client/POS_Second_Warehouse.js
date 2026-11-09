// =============================================================
// Ardmore POS - sell one item group from a second warehouse (v1, 2026-11-02)
// Client Script on POS Invoice (Form) - evaluated inside the POS page
// (loaded by "POS Till Scripts Loader" in Sales Invoice mode).
// -------------------------------------------------------------
// Russell, 2026-11-02: Hyde Park sells fabric that is held at JHB Atrium Home
// (Atrium also sells it online, so the stock stays there). Set on the POS Profile:
//   Second Stock Warehouse / Item Group Sold From Second Warehouse / Tile Tag.
//
// * Search: when the cashier searches (or picks that item group in the filter),
//   the till's own results get the group's items that have stock in the second
//   warehouse, with THAT quantity - server script pos_second_warehouse_items.
//   They never appear in the plain grid. Their tiles carry the tag (e.g. Atrium).
// * Cart: the stock check for those lines uses the second warehouse, and the line
//   is moved there at once so the panel shows the right quantity.
// * Save: Server Script "Sales Invoice - POS Second Warehouse" books the lines out
//   of the second warehouse (and returns back into it), whatever the screen did.
// =============================================================
(function () {
	'use strict';
	if (window.__ardmore_pos_second_wh_v1) return;
	window.__ardmore_pos_second_wh_v1 = true;

	const second_codes = new Set(); // items listed from the second warehouse this session

	function cfg() {
		const s = window.cur_pos && window.cur_pos.settings;
		if (!s || !s.custom_second_warehouse || !s.custom_second_warehouse_item_group) return null;
		return {
			warehouse: s.custom_second_warehouse,
			group: s.custom_second_warehouse_item_group,
			tag: s.custom_second_warehouse_tag || ''
		};
	}

	function ensure_style() {
		if (document.getElementById('ard-second-wh-style')) return;
		const st = document.createElement('style');
		st.id = 'ard-second-wh-style';
		st.textContent = '.point-of-sale-app .ard-second-wh-tag { display: inline-block; margin-right: 4px; ' +
			'padding: 1px 6px; border-radius: 10px; background: #e0e7ff; color: #3730a3; ' +
			'font-size: 10px; font-weight: 600; line-height: 1.6; vertical-align: middle; }';
		document.head.appendChild(st);
	}

	async function is_second(row, c) {
		if (second_codes.has(row.item_code)) return true;
		let group = row.item_group;
		if (!group) {
			const r = await frappe.db.get_value('Item', row.item_code, 'item_group');
			group = r && r.message && r.message.item_group;
		}
		if (group === c.group) second_codes.add(row.item_code);
		return group === c.group;
	}

	function patch_selector() {
		const cls = window.erpnext && erpnext.PointOfSale && erpnext.PointOfSale.ItemSelector;
		if (!cls) return false;
		if (cls.prototype.__ardmore_second_wh) return true;

		const std_get_items = cls.prototype.get_items;
		cls.prototype.get_items = function (args) {
			const a = args || {};
			const c = cfg();
			const standard = std_get_items.apply(this, arguments);
			const term = (a.search_term || '').trim();
			const whole_group = !!(c && !term && this.item_group === c.group);
			if (!c || (!term && !whole_group) || cint(a.start) > 0) return standard;

			// callers chain .then().always(), so hand back a jQuery promise
			const d = $.Deferred();
			const doc = this.events.get_frm().doc;
			const price_list = (doc && doc.selling_price_list) || this.price_list;
			standard.then((r) => {
				frappe.call({
					method: 'pos_second_warehouse_items',
					args: { pos_profile: this.pos_profile, search_term: term, price_list: price_list, whole_group: whole_group ? 1 : 0 }
				}).then((r2) => {
					const extra = (r2 && r2.message && r2.message.items) || [];
					const msg = Object.assign({}, (r && r.message) || {});
					const extra_codes = new Set(extra.map((e) => e.item_code));
					extra_codes.forEach((code) => second_codes.add(code));
					// a till-warehouse copy of the same item gives way to the second-warehouse one
					msg.items = (msg.items || []).filter((it) => !extra_codes.has(it.item_code)).concat(extra);
					d.resolve(Object.assign({}, r, { message: msg }));
				}, () => d.resolve(r));
			}, (e) => d.reject(e));
			return d.promise();
		};

		const std_item_html = cls.prototype.get_item_html;
		cls.prototype.get_item_html = function (item) {
			let html = std_item_html.apply(this, arguments);
			const c = cfg();
			if (item && item.ard_second_wh && c && c.tag) {
				ensure_style();
				const tag = '<span class="ard-second-wh-tag">' + frappe.utils.escape_html(c.tag) + '</span>';
				html = html.replace('<div class="item-qty-pill">', '<div class="item-qty-pill">' + tag);
			}
			return html;
		};

		cls.prototype.__ardmore_second_wh = true;
		return true;
	}

	function patch_controller() {
		const cls = window.erpnext && erpnext.PointOfSale && erpnext.PointOfSale.Controller;
		if (!cls) return false;
		if (cls.prototype.__ardmore_second_wh) return true;

		const std_check = cls.prototype.check_stock_availability;
		cls.prototype.check_stock_availability = async function (item_row, qty_needed, warehouse) {
			const c = cfg();
			if (c && item_row && item_row.item_code && (await is_second(item_row, c))) {
				warehouse = c.warehouse;
				if (item_row.warehouse !== c.warehouse) {
					await frappe.model.set_value(item_row.doctype, item_row.name, 'warehouse', c.warehouse);
				}
			}
			return std_check.call(this, item_row, qty_needed, warehouse);
		};

		cls.prototype.__ardmore_second_wh = true;
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
