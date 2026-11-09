// =============================================================
// Ardmore POS - Select POS User (2026-10-27)
// Client Script on POS Invoice, run in the till by "POS Till Scripts Loader".
// -------------------------------------------------------------
// Several assistants share one till login, so the till header shows a
// dropdown of the Sales Person records linked to this till (API Server
// Script "pos-sales-people" - till logins cannot read Sales Person).
// The chosen name is saved on every sale in custom_sales_representative,
// and a sale cannot be completed until a name is chosen (Russell, 27 Oct).
// The name stays picked on this laptop until it is changed or a new till day
// (a new POS Opening Entry) starts, even after a page reload (Russell, 28 Oct).
// Replaces Paul's code in the Page doc "point-of-sale", wiped 20 Jul 2026.
// Recent Orders (Russell, 27 Oct): the order summary shows the sales person
// under "Sold by", and item quantities and amounts no longer wrap.
// =============================================================
(function () {
	'use strict';
	if (window.__ardmore_pos_sales_person_v1) return;
	window.__ardmore_pos_sales_person_v1 = true;

	const ID = 'ard-sales-person';
	const KEY = 'ard_pos_sales_person';
	let loading = false;

	// Kept per browser, so two laptops on the same till login each keep their own name.
	function opening() { return window.cur_pos && window.cur_pos.pos_opening; }
	function load_choice() {
		try {
			const saved = JSON.parse(localStorage.getItem(KEY) || 'null');
			return saved && opening() && saved.opening === opening() ? saved.name : '';
		} catch (e) { return ''; }
	}
	function save_choice(name) {
		try {
			if (opening()) localStorage.setItem(KEY, JSON.stringify({ opening: opening(), name: name }));
		} catch (e) { /* storage blocked: the name still stays until the page reloads */ }
	}
	function restore(sel) {
		sel.dataset.opening = opening() || '';
		const name = load_choice();
		sel.value = name && Array.from(sel.options).some(function (o) { return o.value === name; }) ? name : '';
	}

	document.head.insertAdjacentHTML('beforeend', '<style>'
		+ '.past-order-summary .item-row-data .item-name{flex:1 1 auto!important;min-width:0!important;white-space:normal!important;overflow:visible!important}'
		+ '.past-order-summary .item-row-data .item-qty,.past-order-summary .item-row-data .item-rate-disc,.past-order-summary .item-row-data .item-rate{flex:0 0 auto!important;white-space:nowrap!important}'
		+ '</style>');

	setInterval(function () {
		// The till rebuilds its components when the cashier comes back to it, so patch each new summary.
		const summary = window.cur_pos && window.cur_pos.order_summary;
		if (summary && !summary.__ard_sales_person) {
			summary.__ard_sales_person = true;
			const upper = summary.get_upper_section_html;
			summary.get_upper_section_html = function (doc) {
				const html = upper.apply(this, arguments);
				if (!doc.custom_sales_representative) return html;
				const $wrap = $('<div>').html(html);
				$wrap.find('.cashier').after('<div class="cashier">' + __('Sales person') + ': '
					+ frappe.utils.escape_html(doc.custom_sales_representative) + '</div>');
				return $wrap.html();
			};
		}

		const title = document.querySelector('#page-point-of-sale .page-title');
		const profile = window.cur_pos && window.cur_pos.pos_profile;
		const current = document.getElementById(ID);
		// A new till day without a page reload starts with no name picked.
		if (current && opening() && current.dataset.opening !== opening()) restore(current);
		if (!title || !profile || loading || current) return;
		loading = true;
		frappe.call({ method: 'ardmore_pos_sales_people', args: { pos_profile: profile } }).then(function (r) {
			loading = false;
			const options = (r.message || []).map(function (p) {
				return '<option value="' + frappe.utils.escape_html(p.name) + '">' + frappe.utils.escape_html(p.sales_person_name) + '</option>';
			}).join('');
			title.insertAdjacentHTML('beforeend', '<select id="' + ID + '" class="form-control input-xs" style="display:inline-block;width:auto;margin-left:12px">'
				+ '<option value="">' + __('Select POS User') + '</option>' + options + '</select>');
			const sel = document.getElementById(ID);
			restore(sel);
			sel.addEventListener('change', function () { save_choice(sel.value); });
		}, function () {
			loading = false;
		});
	}, 1000);

	function stamp(frm) {
		const page = document.getElementById('page-point-of-sale');
		const sel = document.getElementById(ID);
		if (!page || page.offsetParent === null || !sel || !frm.doc.is_pos || frm.doc.is_return) return;
		if (!sel.value) {
			frappe.msgprint({ title: __('Sales person missing'), indicator: 'red',
				message: __('Choose who is selling in Select POS User at the top of the till, then try again.') });
			frappe.validated = false;
			return;
		}
		frm.doc.custom_sales_representative = sel.value;
	}
	frappe.ui.form.on('Sales Invoice', { validate: stamp });
	frappe.ui.form.on('POS Invoice', { validate: stamp });
})();
