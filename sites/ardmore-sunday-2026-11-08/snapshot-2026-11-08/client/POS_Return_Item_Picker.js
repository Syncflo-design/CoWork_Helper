// =============================================================
// Ardmore POS - Return item picker (2026-09-07)
// Client Script on POS Invoice (Form) - evaluated inside the POS page.
// -------------------------------------------------------------
// Standard ERPNext loads EVERY line of the original sale into the return
// cart and the cashier removes what the customer keeps. Cashiers read that
// backwards. This wraps the POS controller's make_return_invoice so that,
// right after the return is built, a dialog asks WHICH items (and how many)
// are coming back. Only ticked lines stay in the cart, so the refund total
// is the value of the returned goods. Cancel drops the return.
// Refund is then placed on the payment mode that carried the original sale.
// =============================================================
(function () {
	'use strict';
	if (window.__ardmore_return_picker) return;
	window.__ardmore_return_picker = true;

	let tries = 0;
	const t = setInterval(() => {
		tries += 1;
		const pos = window.cur_pos;
		if (pos && typeof pos.make_return_invoice === 'function') {
			clearInterval(t);
			if (!pos.__ardmore_return_wrapped) install(pos);
		} else if (tries > 240) {
			clearInterval(t);
		}
	}, 250);

	function install(pos) {
		pos.__ardmore_return_wrapped = true;
		const orig = pos.make_return_invoice.bind(pos);

		pos.make_return_invoice = async function (source) {
			await orig(source);
			const frm = this.frm;
			const items = (frm.doc.items || []).slice();
			if (!items.length) return;

			// The POS chain has frappe.dom.freeze() active here; the overlay would sit
			// above the dialog and block clicks. Lift it while the cashier chooses,
			// then restore it so the chain's later unfreeze() stays balanced.
			frappe.dom.unfreeze();
			let choice = null;
			try {
				choice = await pick_items(items, frm.doc.currency, source);
			} finally {
				frappe.dom.freeze();
			}
			if (!choice) {
				// cashier cancelled - drop the return and start a clean invoice
				await this.make_new_invoice();
				return;
			}

			// Keep only ticked lines, at the chosen quantities. Rates are untouched.
			for (const row of items) {
				const qty = flt(choice[row.name]);
				if (qty <= 0) {
					frappe.model.clear_doc(row.doctype, row.name);
				} else {
					row.qty = -qty;
					row.stock_qty = -qty * flt(row.conversion_factor || 1);
				}
			}
			frm.cscript.calculate_taxes_and_totals();

			// Refund goes on the mode that carried the most of the original sale.
			const refund = cint(frappe.sys_defaults.disable_rounded_total)
				? flt(frm.doc.grand_total) : flt(frm.doc.rounded_total);
			const pays = frm.doc.payments || [];
			if (pays.length) {
				let target = pays.reduce((a, b) => (Math.abs(flt(b.amount)) > Math.abs(flt(a.amount)) ? b : a), pays[0]);
				if (!flt(target.amount)) target = pays.find((p) => p.default) || pays[0];
				pays.forEach((p) => { p.amount = 0; p.base_amount = 0; });
				target.amount = refund;
				target.base_amount = flt(refund * flt(frm.doc.conversion_rate || 1));
				frm.cscript.calculate_taxes_and_totals();
			}
		};
	}

	function pick_items(items, currency, source) {
		return new Promise((resolve) => {
			let done = false;
			const finish = (v) => { if (!done) { done = true; resolve(v); } };

			const rows = items.map((r) => {
				const sold = Math.abs(flt(r.qty));
				return `
				<tr data-row="${r.name}">
					<td style="text-align:center;width:40px">
						<input type="checkbox" class="ard-ret-chk" style="width:18px;height:18px;cursor:pointer">
					</td>
					<td>${frappe.utils.escape_html(r.item_name || r.item_code)}
						<div class="text-muted small">${format_currency(Math.abs(flt(r.rate)), currency)} ${__('each')}</div>
					</td>
					<td style="text-align:center;width:70px">${sold}</td>
					<td style="width:110px">
						<input type="number" class="ard-ret-qty form-control" min="0" max="${sold}" step="1"
							value="${sold}" disabled style="text-align:center">
					</td>
				</tr>`;
			}).join('');

			const d = new frappe.ui.Dialog({
				title: __('Return from {0}', [frappe.utils.escape_html(source.name)]),
				size: 'large',
				fields: [{ fieldname: 'html', fieldtype: 'HTML' }],
				primary_action_label: __('Return ticked items'),
				primary_action() {
					const out = {};
					let any = false;
					d.$wrapper.find('tr[data-row]').each(function () {
						const $tr = $(this);
						if ($tr.find('.ard-ret-chk').prop('checked')) {
							const q = flt($tr.find('.ard-ret-qty').val());
							if (q > 0) { out[$tr.attr('data-row')] = q; any = true; }
						}
					});
					if (!any) {
						frappe.show_alert({ message: __('Tick at least one item to return.'), indicator: 'orange' }, 4);
						return;
					}
					finish(out);
					d.hide();
				},
				secondary_action_label: __('Cancel'),
				secondary_action() { d.hide(); }
			});

			d.fields_dict.html.$wrapper.html(`
				<p class="text-muted" style="margin:0 0 8px">${__('Tick the items the customer is bringing back and adjust the quantity if only some are returned.')}</p>
				<div style="max-height:55vh;overflow:auto">
				<table class="table table-bordered" style="margin:0">
					<thead><tr>
						<th></th><th>${__('Item')}</th>
						<th style="text-align:center">${__('Sold')}</th>
						<th style="text-align:center">${__('Return qty')}</th>
					</tr></thead>
					<tbody>${rows}</tbody>
				</table></div>`);

			d.$wrapper.on('change', '.ard-ret-chk', function () {
				const $q = $(this).closest('tr').find('.ard-ret-qty');
				$q.prop('disabled', !this.checked);
				if (this.checked) $q.focus().select();
			});
			d.$wrapper.on('input', '.ard-ret-qty', function () {
				const max = flt(this.max);
				if (flt(this.value) > max) this.value = max;
			});

			d.onhide = () => finish(null);
			d.show();
		});
	}
})();
