// =============================================================
// Ardmore POS - Sales Other line (Russell, 6 Nov 2026, ticket 0129)
// Client Script on POS Invoice (Form), run in the till by "POS Till Scripts Loader".
// -------------------------------------------------------------
// A Sales Other button beside the item search: the cashier types a description
// (100 characters at most, Sage refuses more) and a price including VAT. The
// line goes in the cart with no item code and quantity 1. There is no Item
// record, and the cashier never sees or picks a Sage account.
// The line cannot be edited: clicking it only offers to remove it. A discount on
// the whole sale is refused while one is in the cart, and adding one is refused
// while the sale has a discount. Server Script "Sales Invoice - Sales Other"
// holds the same rules on save, whatever the screen did.
// =============================================================
(function () {
	'use strict';
	if (window.__ardmore_pos_sales_other_v1) return;
	window.__ardmore_pos_sales_other_v1 = true;

	const MAX_WORDS = 100;

	function pos() {
		return window.cur_pos && window.cur_pos.frm && window.cur_pos.cart ? window.cur_pos : null;
	}

	function has_other(frm) {
		return (frm.doc.items || []).some((row) => !row.item_code);
	}

	function warn(message) {
		frappe.show_alert({ message: message, indicator: 'orange' });
		frappe.utils.play_sound('error');
	}

	function add_line(p, words, price, setup) {
		const frm = p.frm;
		const row = frm.add_child('items', {
			item_name: words,
			description: words,
			qty: 1,
			stock_qty: 1,
			uom: setup.uom,
			stock_uom: setup.uom,
			conversion_factor: 1,
			rate: price,
			price_list_rate: price,
			income_account: setup.income_account,
			cost_center: setup.cost_center
		});
		frm.cscript.calculate_taxes_and_totals();
		frm.dirty();
		p.update_cart_html(row);
	}

	function ask_for_line(p, setup) {
		const d = new frappe.ui.Dialog({
			title: __('Sales Other'),
			fields: [
				{ fieldname: 'description', fieldtype: 'Data', label: __('Description'), reqd: 1 },
				{ fieldname: 'price', fieldtype: 'Currency', label: __('Price (incl. VAT)'), reqd: 1 }
			],
			primary_action_label: __('Add to cart'),
			primary_action(values) {
				const words = String(values.description || '').replace(/[<>]/g, '').trim();
				const price = flt(values.price);
				if (!words) {
					warn(__('Type a description.'));
					return;
				}
				if (words.length > MAX_WORDS) {
					warn(__('The description can be at most {0} characters.', [MAX_WORDS]));
					return;
				}
				if (price <= 0) {
					warn(__('Type a price.'));
					return;
				}
				d.hide();
				add_line(p, words, price, setup);
			}
		});
		d.fields_dict.description.$input.attr('maxlength', MAX_WORDS);
		// keep the till's barcode-scanner listener from also typing into the item search
		d.$wrapper.find('input').on('keydown keypress keyup', (e) => e.stopPropagation());
		d.show();
	}

	function open_button() {
		const p = pos();
		if (!p) return;
		const doc = p.frm.doc;
		if (doc.docstatus !== 0 || doc.is_return) {
			warn(__('Sales Other can only be added to a new sale.'));
			return;
		}
		if (!doc.customer) {
			p.raise_customer_selection_alert();
			return;
		}
		if (flt(doc.additional_discount_percentage) || flt(doc.discount_amount)) {
			warn(__('Remove the discount first: a sale with a Sales Other line cannot take a discount.'));
			return;
		}
		frappe.call({
			method: 'pos_sales_other_setup',
			args: { pos_profile: p.pos_profile }
		}).then((r) => {
			if (r && r.message) ask_for_line(p, r.message);
		});
	}

	function offer_to_remove(p, row) {
		frappe.confirm(__('Remove {0} from the cart?', [frappe.utils.escape_html(row.item_name)]), () => {
			frappe.model.clear_doc(row.doctype, row.name);
			p.frm.cscript.calculate_taxes_and_totals();
			p.frm.dirty();
			p.update_cart_html(row, true);
		});
	}

	function patch() {
		const P = window.erpnext && erpnext.PointOfSale;
		if (!P || !P.ItemDetails || !P.ItemCart) return false;

		if (!P.ItemDetails.prototype.__ardmore_sales_other) {
			const std_toggle = P.ItemDetails.prototype.toggle_item_details_section;
			P.ItemDetails.prototype.toggle_item_details_section = function (row) {
				if (row && row.name && !row.item_code) {
					const p = pos();
					return Promise.resolve(std_toggle.call(this, null)).then(() => {
						if (!p) return;
						p.cart.toggle_item_highlight();
						offer_to_remove(p, row);
					});
				}
				return std_toggle.apply(this, arguments);
			};
			P.ItemDetails.prototype.__ardmore_sales_other = true;
		}

		if (!P.ItemCart.prototype.__ardmore_sales_other) {
			const std_discount = P.ItemCart.prototype.show_discount_control;
			P.ItemCart.prototype.show_discount_control = function () {
				if (has_other(this.events.get_frm())) {
					warn(__('A sale with a Sales Other line cannot take a discount.'));
					return;
				}
				return std_discount.apply(this, arguments);
			};
			P.ItemCart.prototype.__ardmore_sales_other = true;
		}
		return true;
	}

	function paint_button() {
		const label = document.querySelector('.point-of-sale-app .items-selector .filter-section .label');
		if (!label || label.querySelector('.ard-sales-other-btn')) return;
		const button = document.createElement('button');
		button.type = 'button';
		button.className = 'btn btn-xs btn-default ard-sales-other-btn';
		button.style.marginLeft = '12px';
		button.textContent = __('Sales Other');
		button.addEventListener('click', open_button);
		label.appendChild(button);
	}

	if (!patch()) {
		let tries = 0;
		const timer = setInterval(() => {
			tries = tries + 1;
			if (patch() || tries > 30) clearInterval(timer);
		}, 1000);
	}
	// The till rebuilds its screens when the cashier comes back to it, so keep the button there.
	setInterval(paint_button, 1000);
})();
