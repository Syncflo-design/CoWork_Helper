// =============================================================
// Ardmore POS - Voucher and Credit Note reference (v6, 2026-11-01)
// Lives on POS Invoice; also loaded for Sales Invoice tills by the
// Client Script "POS Till Scripts Loader".
// -------------------------------------------------------------
// The voucher number is asked for ONCE, when the cashier clicks
// Complete Order and a Voucher amount is present. (v2 asked as soon as the
// amount changed, i.e. on the first digit typed - the popup then fought the
// amount box for the keyboard and corrupted the amount.)
// Stored on <invoice>.custom_voucher_ref (field exists on POS Invoice AND
// Sales Invoice); printed on the receipt.
// 2026-11-01 (Russell): Credit Note is a payment method too and works the same
// way - its number is asked for at Complete Order and stored on
// custom_credit_note_ref. Both are asked in turn when both are used.
// =============================================================
(function () {
	'use strict';
	if (window.__ardmore_voucher_ref_v6) return;
	window.__ardmore_voucher_ref_v6 = true;

	const REFS = [
		{ mode: 'Voucher', field: 'custom_voucher_ref',
			title: __('Voucher used - enter the voucher number'), label: __('Voucher Reference No.') },
		{ mode: 'Credit Note', field: 'custom_credit_note_ref',
			title: __('Credit note used - enter the credit note number'), label: __('Credit Note No.') }
	];

	// The till's page element, not frappe.get_route(): opened by its URL, the nest_home
	// redirect leaves the route on "nest-home" while the till is on screen (27 Oct 2026).
	function on_pos() {
		const page = document.getElementById('page-point-of-sale');
		return !!(page && page.offsetParent !== null);
	}

	function amount(doc, mode) {
		return (doc.payments || [])
			.filter((p) => p.mode_of_payment === mode)
			.reduce((s, p) => s + flt(p.amount), 0);
	}

	function has_ref(doc, field) {
		return !!(doc[field] || '').toString().trim();
	}

	// the first payment used without its number yet
	function missing(doc) {
		return REFS.find((r) => amount(doc, r.mode) > 0 && !has_ref(doc, r.field));
	}

	function ask(frm, ref, after) {
		if (window.__ardmore_voucher_prompt) return;
		// take the keyboard away from the payment amount box first
		if (document.activeElement && document.activeElement.blur) document.activeElement.blur();
		const d = new frappe.ui.Dialog({
			title: ref.title,
			fields: [
				{ fieldname: 'ref', fieldtype: 'Data', label: ref.label, reqd: 1,
					default: frm.doc[ref.field] || '' }
			],
			primary_action_label: __('Save'),
			primary_action(v) {
				const value = (v.ref || '').trim();
				if (!value) return;
				frappe.model.set_value(frm.doctype, frm.docname, ref.field, value);
				d.hide();
				if (after) setTimeout(after, 300);
			}
		});
		// keep typing inside the dialog - never let it reach the POS key handlers
		d.$wrapper.on('keydown keypress keyup', (e) => e.stopPropagation());
		d.onhide = () => { window.__ardmore_voucher_prompt = null; };
		window.__ardmore_voucher_prompt = d;
		d.show();
		setTimeout(() => d.fields_dict.ref && d.fields_dict.ref.set_focus(), 300);
	}

	function reclick_complete() {
		const pos = window.cur_pos;
		const btn = pos && pos.payment && pos.payment.$component
			? pos.payment.$component.find('.submit-order-btn') : null;
		if (btn && btn.length) btn.click();
	}

	// Ask BEFORE ERPNext's own "Permanently Submit?" confirm, so the cashier
	// gets one number box per payment and then one confirm - not two confirms.
	document.addEventListener('click', function (e) {
		if (!on_pos()) return;
		const btn = e.target.closest ? e.target.closest('.submit-order-btn') : null;
		if (!btn) return;
		const pos = window.cur_pos;
		const frm = pos && pos.frm;
		if (!frm || frm.doc.docstatus || frm.doc.is_return) return;
		const need = missing(frm.doc);
		if (need) {
			e.preventDefault();
			e.stopImmediatePropagation();
			ask(frm, need, reclick_complete);
		}
	}, true);

	function validate(frm) {
		if (!on_pos() || frm.doc.docstatus || frm.doc.is_return) return;
		const need = missing(frm.doc);
		if (need) {
			frappe.validated = false;
			ask(frm, need, reclick_complete); // safety net (e.g. Ctrl+Enter)
			return;
		}
		// a payment removed again - do not keep a stale number
		REFS.forEach((r) => {
			if (!(amount(frm.doc, r.mode) > 0) && has_ref(frm.doc, r.field)) frm.doc[r.field] = '';
		});
	}

	frappe.ui.form.on('Sales Invoice', { validate: validate });
	frappe.ui.form.on('POS Invoice', { validate: validate });
})();
