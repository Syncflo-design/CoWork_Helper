// =============================================================
// Ardmore POS - Recent Orders: this till's Sales / Returns only (v3, 2026-11-02)
// Client Script on POS Invoice (Form) - evaluated inside the POS page.
// -------------------------------------------------------------
// Standard filter offers Draft / Paid / Consolidated / Return / Partly Paid
// and defaults to Draft. Once a day is closed its sales AND returns move to
// Consolidated, so cashiers could not find yesterday's sale under Paid.
// Now: two choices - "Sales" and "Returns" - defaulting to Sales.
//
// v2: the POS REBUILDS its components every time the cashier leaves the till
// and comes back (page refresh -> check_opening_entry), which creates a new
// Recent Orders list. v1 patched only the first one, so the old five options
// came back. This version keeps watching and patches every new instance.
// v3 (Russell, go-live 2 Nov 2026): the standard list shows every till's
// invoices, so the September test sales (old POS Invoices, test tills) filled
// Hyde Park's list. It now shows only submitted Sales Invoices of THIS till's
// POS Profile (Ardmore runs Invoice Type = Sales Invoice; POS Invoices are
// test-era only). Nothing is deleted - other tills' and test records just
// do not appear here.
// =============================================================
(function () {
	'use strict';
	if (window.__ardmore_recent_orders_v3) return;
	window.__ardmore_recent_orders_v3 = true;

	const FIELDS = ['name', 'grand_total', 'currency', 'customer', 'customer_name', 'posting_date', 'posting_time'];

	setInterval(() => {
		const pos = window.cur_pos;
		const list = pos && pos.recent_order_list;
		if (list && list.status_field && list.search_field && !list.__ardmore_v3) install(list);
	}, 1000);

	function till_profile() {
		const pos = window.cur_pos;
		return (pos && pos.pos_profile) || (pos && pos.frm && pos.frm.doc && pos.frm.doc.pos_profile) || '';
	}

	function fetch_orders(term, want_returns) {
		const profile = till_profile();
		if (!profile) return Promise.resolve([]);
		const args = {
			filters: { pos_profile: profile, docstatus: 1, is_pos: 1, is_return: want_returns ? 1 : 0 },
			fields: FIELDS,
			order_by: 'posting_date desc, posting_time desc',
			limit: 50
		};
		if (term) {
			const like = '%' + term + '%';
			args.or_filters = [['name', 'like', like], ['customer', 'like', like], ['customer_name', 'like', like]];
		}
		return frappe.db.get_list('Sales Invoice', args).then((rows) => {
			(rows || []).forEach((r) => { r.doctype = 'Sales Invoice'; });
			return rows || [];
		});
	}

	function install(list) {
		list.__ardmore_v3 = true;

		list.refresh_list = function () {
			frappe.dom.freeze();
			this.events.reset_summary();
			const term = this.search_field.get_value();
			const want_returns = this.status_field.get_value() === 'Returns';
			this.$invoices_container.html('');
			return fetch_orders(term, want_returns)
				.then((rows) => rows.forEach((r) => this.$invoices_container.append(this.get_invoice_html(r))))
				.finally(() => frappe.dom.unfreeze());
		};

		const sf = list.status_field;
		sf.df.options = ['Sales', 'Returns'].join('\n');
		sf.df.placeholder = __('Sales or Returns');
		sf.refresh();
		sf.set_value('Sales');
		if (list.$component.is(':visible')) list.refresh_list();
	}
})();
