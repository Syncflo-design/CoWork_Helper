// =============================================================
// Ardmore POS - VAT selector (2026-10-28)
// Client Script on POS Invoice, run in the till by "POS Till Scripts Loader".
// -------------------------------------------------------------
// Online and Airport sometimes sell at VAT 0% (Russell, 28 Oct). On a till
// whose POS Profile names a "Zero-rated VAT Template", the VAT line in the
// cart totals is a selector: VAT 15% / VAT 0%. The customer pays the same
// price either way; at 0% it is all exclusive. 0% puts the sale on tax
// category "Zero Rated" with the zero-rated template and clears the 15% item
// VAT (Server Script "zero-rated-sale-vat" repeats that on save, and the Sage
// scripts send the zero-rated tax type). Every new sale starts at 15%; a
// return keeps the VAT of the sale it returns.
// Export proof (Russell, 28 Oct): at 0% the till also takes a flight number
// and a comment - one of them is required (checked again on the server). The
// courier waybill is added on the invoice at dispatch.
// =============================================================
(function () {
	'use strict';
	if (window.__ardmore_pos_vat_selector_v1) return;
	window.__ardmore_pos_vat_selector_v1 = true;

	const ZERO = 'Zero Rated';

	function set_vat(cart, frm, template, zero) {
		frm.doc.tax_category = zero ? ZERO : '';
		frm.doc.taxes_and_charges = template;
		if (!zero) {
			frm.doc.custom_export_flight_no = '';
			frm.doc.custom_export_comment = '';
		}
		(frm.doc.items || []).forEach(function (row) {
			row.item_tax_template = '';
			row.item_tax_rate = '{}';
		});
		frappe.call({
			method: 'erpnext.controllers.accounts_controller.get_taxes_and_charges',
			args: { master_doctype: 'Sales Taxes and Charges Template', master_name: template }
		}).then(function (r) {
			frm.clear_table('taxes');
			(r.message || []).forEach(function (t) { frm.add_child('taxes', t); });
			frm.cscript.calculate_taxes_and_totals();
			cart.update_totals_section(frm);
		});
	}

	setInterval(function () {
		// The till rebuilds its cart when the cashier comes back to it, so patch each new cart.
		const pos = window.cur_pos;
		const cart = pos && pos.cart;
		if (!cart || cart.__ard_vat || !pos.pos_profile) return;
		cart.__ard_vat = true;
		frappe.db.get_value('POS Profile', pos.pos_profile, ['custom_zero_vat_template', 'taxes_and_charges']).then(function (r) {
			const profile = r.message || {};
			if (!profile.custom_zero_vat_template || !profile.taxes_and_charges) return;
			const render = cart.render_taxes;
			cart.render_taxes = function () {
				render.apply(this, arguments);
				const me = this;
				const frm = this.events.get_frm();
				const zero = frm.doc.tax_category === ZERO;
				const vat = (frm.doc.taxes || []).reduce(function (s, t) { return s + flt(t.tax_amount_after_discount_amount); }, 0);
				let html = '<div class="tax-row"><div class="tax-label"><select class="ard-vat form-control input-xs" style="width:auto">'
					+ '<option value="15">' + __('VAT 15%') + '</option><option value="0">' + __('VAT 0%') + '</option></select></div>'
					+ '<div class="tax-value">' + format_currency(vat, frm.doc.currency) + '</div></div>';
				if (zero) {
					html += '<div style="display:flex;gap:8px;width:100%;margin-top:6px">'
						+ '<input class="ard-flight form-control input-xs" style="flex:0 0 35%" placeholder="' + __('Flight no.') + '">'
						+ '<input class="ard-comment form-control input-xs" style="flex:1" placeholder="' + __('Comment') + '">'
						+ '</div>';
				}
				const $box = this.$totals_section.find('.taxes-container').css('display', 'flex').html(html);
				$box.find('.ard-vat').val(zero ? '0' : '15').prop('disabled', !!frm.doc.is_return).on('change', function () {
					const to_zero = this.value === '0';
					set_vat(me, frm, to_zero ? profile.custom_zero_vat_template : profile.taxes_and_charges, to_zero);
				});
				$box.find('.ard-flight').val(frm.doc.custom_export_flight_no || '').prop('readonly', !!frm.doc.is_return).on('input', function () {
					frm.doc.custom_export_flight_no = this.value;
				});
				$box.find('.ard-comment').val(frm.doc.custom_export_comment || '').prop('readonly', !!frm.doc.is_return).on('input', function () {
					frm.doc.custom_export_comment = this.value;
				});
				// keep the till's barcode-scanner listener from also typing into the item search
				$box.find('input').on('keydown keypress keyup', function (e) { e.stopPropagation(); });
			};
			const frm = cart.events.get_frm();
			if (frm && frm.doc) cart.update_totals_section(frm);
		});
	}, 1000);
})();
