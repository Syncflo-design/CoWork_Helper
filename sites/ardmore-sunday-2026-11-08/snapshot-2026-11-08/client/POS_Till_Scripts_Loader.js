// =============================================================
// Ardmore POS - till scripts loader (2026-09-21)
// Client Script on Sales Invoice (Form).
// -------------------------------------------------------------
// Ardmore runs POS Settings > Invoice Type = "Sales Invoice" (each till sale
// is a real tax invoice, so stock and Sage stay aligned). The till therefore
// builds a hidden *Sales Invoice* form, and Client Scripts attached to
// POS Invoice would never run.
//
// A Client Script's DocType cannot be changed after creation, so instead of
// keeping two copies of every till script, this loader runs the POS Invoice
// Client Scripts whenever the till opens. ONE copy of each script, kept under
// POS Invoice:
//   POS Customer UX, POS Split Payment Autobalance, POS Voucher Ref,
//   POS Return Item Picker, POS Customer History Open Invoice,
//   POS Recent Orders Sales Returns, POS New Invoice From Recent Orders
// Each of those guards itself with a window.__ardmore_* flag, so running
// them twice is harmless.
//
// Guard: only inside the till. Do NOT test frappe.get_route() here - while
// the till is starting, nest_home's landing redirect can still report
// "nest-home". The POS page element is the reliable signal.
//
// 2026-10-28: the scripts are fetched fresh from the server every time. The
// browser's cached POS Invoice meta kept an old copy, so a new till script
// (the VAT selector) did not run until the cache was cleared.
// =============================================================
(function () {
	'use strict';
	if (window.__ardmore_till_loader) return;
	const in_till = !!document.getElementById('page-point-of-sale') ||
		(frappe.get_route() || [])[0] === 'point-of-sale';
	if (!in_till) return;
	window.__ardmore_till_loader = true;

	frappe.call({ method: 'frappe.desk.form.load.getdoctype', args: { doctype: 'POS Invoice' } }).then(function (r) {
		const meta = (r.docs || []).find(function (d) { return d.name === 'POS Invoice'; });
		const js = meta && meta.__custom_js;
		if (!js) return;
		try {
			new Function(js)();
		} catch (e) {
			console.error('Ardmore till scripts failed to load', e);
		}
	});
})();
