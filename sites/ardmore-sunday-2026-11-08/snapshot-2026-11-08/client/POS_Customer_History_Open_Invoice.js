// =============================================================
// Ardmore POS - Customer history -> open invoice (2026-09-08)
// Client Script on POS Invoice (Form) - evaluated inside the POS page.
// -------------------------------------------------------------
// The customer panel lists the customer's recent transactions but they were
// display-only. Clicking one now opens it in the Recent Orders summary, where
// Print Receipt / Return live - no need to search for it again.
// =============================================================
(function () {
	'use strict';
	if (window.__ardmore_cust_history) return;
	window.__ardmore_cust_history = true;

	const SEL = '#page-point-of-sale .customer-transactions .invoice-wrapper[data-invoice-name]';

	function open_invoice(name) {
		const pos = window.cur_pos;
		if (!pos || !pos.order_summary || !pos.recent_order_list) return;
		const dt = pos.settings && pos.settings.frm_doctype === 'Sales Invoice' ? 'Sales Invoice' : 'POS Invoice';
		frappe.db.exists(dt, name).then((ok) => {
			const doctype = ok ? dt : (dt === 'POS Invoice' ? 'Sales Invoice' : 'POS Invoice');
			return frappe.db.get_doc(doctype, name);
		}).then((doc) => {
			if (pos.recent_order_list.$component.is(':hidden')) pos.toggle_recent_order();
			pos.order_summary.load_summary_of(doc);
		}).catch(() => {
			frappe.show_alert({ message: __('Could not open {0}', [name]), indicator: 'red' }, 4);
		});
	}

	// Capture phase: the POS binds its own click handler on the customer section
	// (it collapses the details panel), so a bubbling handler never sees the click.
	document.addEventListener('click', function (e) {
		const row = e.target.closest ? e.target.closest(SEL) : null;
		if (!row) return;
		e.preventDefault();
		e.stopPropagation();
		open_invoice(row.dataset.invoiceName);
	}, true);

	// make the rows look clickable
	const css = document.createElement('style');
	css.textContent = SEL + ' { cursor: pointer; } ' + SEL + ':hover { background: var(--bg-light-gray, #f4f5f6); border-radius: 6px; }';
	document.head.appendChild(css);
})();
