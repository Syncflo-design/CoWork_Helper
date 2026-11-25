// =============================================================
// Ardmore POS - Shopify Orders (Russell, 20 Nov 2026)
// Client Script on POS Invoice, run in the till by "POS Till Scripts Loader".
// -------------------------------------------------------------
// On a till ticked "Online Store" a "Shopify Orders" button sits beside Quote. It lists the paid
// Shopify orders waiting to be completed (oldest first). Open builds the ready sale on the server
// (API Server Script "pos-shopify-orders": customer, items at Shopify's prices and VAT, the Shopify
// number in Order Number, paid by Shopify) and the till opens it the way it opens any draft, so
// the staff member checks it and completes it. Nothing is typed.
// =============================================================
(function () {
	'use strict';
	if (window.__ardmore_pos_shopify_orders_v1) return;
	window.__ardmore_pos_shopify_orders_v1 = true;

	const API = 'ardmore_pos_shopify_orders';
	const BTN = 'ard-pos-shopify-orders';
	const online = {};  // POS Profile -> is it an Online Store till

	function esc(v) {
		return frappe.utils.escape_html(v == null ? '' : String(v));
	}

	function open_order(d, name) {
		frappe.call({
			method: API,
			freeze: true,
			freeze_message: __('Opening the Shopify order...'),
			args: { action: 'open', pos_profile: window.cur_pos.pos_profile, sales_order: name }
		}).then(function (r) {
			d.hide();
			// what the till's own Edit Order button does with a draft (as for a quote)
			const s = window.cur_pos.order_summary;
			s.events.edit_order('Sales Invoice', r.message.name);
			s.toggle_component(false);
			s.$component.find('.no-summary-placeholder').css('display', 'flex');
			s.$summary_wrapper.css('display', 'none');
		});
	}

	function show_orders() {
		const pos = window.cur_pos;
		const frm = pos && pos.frm;
		if (!frm || !frm.doc) return;
		frappe.call({ method: API, args: { action: 'list', pos_profile: pos.pos_profile } }).then(function (r) {
			const rows = r.message || [];
			const d = new frappe.ui.Dialog({
				title: __('Shopify orders waiting ({0})', [rows.length]),
				size: 'large',
				fields: [{ fieldname: 'list', fieldtype: 'HTML' }]
			});
			const body = rows.length
				? '<table class="table table-condensed"><thead><tr><th>' + __('Order') + '</th><th>' + __('Date') + '</th><th>'
					+ __('Customer') + '</th><th class="text-right">' + __('Total') + '</th><th></th></tr></thead><tbody>'
					+ rows.map(function (o) {
						return '<tr><td>' + esc(o.order_no) + (o.started ? ' <span class="indicator-pill orange"><span>' + __('Started') + '</span></span>' : '')
							+ '</td><td>' + esc(frappe.datetime.str_to_user(o.date)) + '</td><td>' + esc(o.customer)
							+ '</td><td class="text-right">' + format_currency(o.total, o.currency)
							+ '</td><td class="text-right"><button class="btn btn-primary btn-xs ard-shopify-open" data-name="' + esc(o.name) + '">'
							+ (o.started ? __('Continue') : __('Open')) + '</button></td></tr>';
					}).join('') + '</tbody></table>'
				: '<div class="text-muted">' + __('No Shopify orders are waiting.') + '</div>';
			d.fields_dict.list.$wrapper.html(body);
			d.fields_dict.list.$wrapper.on('click', '.ard-shopify-open', function () {
				const name = $(this).attr('data-name');
				const busy = (frm.doc.items || []).length && !frm.doc.docstatus;
				if (!busy) return open_order(d, name);
				frappe.confirm(__('Open the Shopify order? The items in the cart now will be cleared.'),
					function () { open_order(d, name); });
			});
			d.show();
		});
	}

	// The till rebuilds its components when the cashier comes back to it, so keep watching.
	setInterval(function () {
		const pos = window.cur_pos;
		if (!pos || !pos.pos_profile) return;
		if (online[pos.pos_profile] === undefined) {
			online[pos.pos_profile] = null;  // asking
			const asked = pos.pos_profile;
			frappe.db.get_value('POS Profile', asked, 'custom_online_store').then(function (r) {
				online[asked] = !!(r.message && r.message.custom_online_store);
			}, function () {
				delete online[asked];  // failed: ask again on the next tick
			});
			return;
		}
		if (!online[pos.pos_profile]) return;
		if (pos.page && pos.page.btn_secondary && pos.page.btn_secondary.length && !document.getElementById(BTN)) {
			$('<button id="' + BTN + '" class="btn btn-default btn-sm ellipsis">' + __('Shopify Orders') + '</button>')
				.insertBefore(pos.page.btn_secondary)
				.on('click', show_orders);
		}
	}, 1000);
})();
