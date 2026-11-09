// =============================================================
// Ardmore POS - Quotes (ticket 0128, Russell, 6 Nov 2026)
// Client Script on POS Invoice, run in the till by "POS Till Scripts Loader".
// -------------------------------------------------------------
// * A "Quote" button beside Recent Orders saves the cart as a Quotation for the customer on the
//   cart. The dialog can also add items the till cannot sell (it hides zero stock), such as
//   wallpaper ordered in for a customer.
// * Recent Orders gets a third choice, Quotes: search, open, print, or "Invoice this quote".
// * Invoicing builds a draft till sale at the quoted prices (API Server Script "pos-quote") and the
//   till opens it the way it opens any draft, so stock, payment, VAT and Sage are a normal sale.
// =============================================================
(function () {
	'use strict';
	if (window.__ardmore_pos_quote_v1) return;
	window.__ardmore_pos_quote_v1 = true;

	const API = 'ardmore_pos_quote';
	const BTN = 'ard-pos-quote';
	const PRINT_FORMAT = 'Ardmore Quote';
	const QUOTES = 'Quotes';
	const VALID_DAYS = 30;

	function esc(v) {
		return frappe.utils.escape_html(v == null ? '' : String(v));
	}

	function print_quote(name, letter_head) {
		frappe.utils.print('Quotation', name, PRINT_FORMAT, letter_head, frappe.boot.lang);
	}

	// ---- the Quote button: cart -> Quotation ------------------------------------------

	function start_quote() {
		const pos = window.cur_pos;
		const frm = pos && pos.frm;
		if (!frm || !frm.doc) return;
		if (frm.doc.docstatus === 1 || frm.doc.is_return) {
			frappe.msgprint({ title: __('Start a new invoice'), indicator: 'orange',
				message: __('Tap New Invoice first: a quote starts from an open cart.') });
			return;
		}
		const who = document.getElementById('ard-sales-person');
		if (who && !who.value) {
			frappe.msgprint({ title: __('Sales person missing'), indicator: 'red',
				message: __('Choose who is selling in Select POS User at the top of the till, then try again.') });
			return;
		}
		frappe.db.get_value('POS Profile', pos.pos_profile, 'customer').then(function (r) {
			const walk_in = r.message && r.message.customer;
			if (!frm.doc.customer || frm.doc.customer === walk_in) {
				frappe.msgprint({ title: __('Choose the customer'), indicator: 'orange',
					message: __('A quote needs a customer: choose or add them on the cart, then tap Quote.') });
				return;
			}
			quote_dialog(pos, frm, who ? who.value : '');
		});
	}

	function quote_dialog(pos, frm, sales_person) {
		const rows = (frm.doc.items || []).filter(function (i) { return i.item_code; }).map(function (i) {
			return { item_code: i.item_code, qty: i.qty, rate: i.rate };
		});
		const d = new frappe.ui.Dialog({
			title: __('New quote for {0}', [frm.doc.customer_name || frm.doc.customer]),
			size: 'large',
			fields: [
				{ fieldname: 'valid_till', fieldtype: 'Date', label: __('Valid until'), reqd: 1,
					default: frappe.datetime.add_days(frappe.datetime.get_today(), VALID_DAYS) },
				{ fieldname: 'note', fieldtype: 'HTML',
					options: '<div class="text-muted small">' + __('Prices include VAT. Add any item here, in stock or not.') + '</div>' },
				{ fieldname: 'items', fieldtype: 'Table', label: __('Items'), cannot_add_rows: false, in_place_edit: true, data: rows,
					fields: [
						{ fieldname: 'item_code', fieldtype: 'Link', options: 'Item', label: __('Item'), in_list_view: 1, reqd: 1, columns: 5,
							get_query: function () { return { filters: { disabled: 0, has_variants: 0, is_sales_item: 1 } }; },
							onchange: function () {
								const row = this.doc;
								if (!row || !row.item_code) return;
								if (!row.qty) row.qty = 1;
								frappe.call({ method: API, args: { action: 'price', pos_profile: pos.pos_profile, item_code: row.item_code } }).then(function (r) {
									row.rate = (r.message && r.message.rate) || 0;
									d.fields_dict.items.grid.refresh();
								});
							} },
						{ fieldname: 'qty', fieldtype: 'Float', label: __('Qty'), in_list_view: 1, reqd: 1, columns: 2 },
						{ fieldname: 'rate', fieldtype: 'Currency', label: __('Price incl. VAT'), in_list_view: 1, reqd: 1, columns: 3 }
					] }
			],
			primary_action_label: __('Save quote'),
			primary_action: function (values) {
				const items = (values.items || []).filter(function (r) { return r.item_code; }).map(function (r) {
					return { item_code: r.item_code, qty: flt(r.qty), rate: flt(r.rate) };
				});
				if (!items.length) {
					frappe.msgprint({ title: __('Nothing to quote'), indicator: 'orange', message: __('Add at least one item.') });
					return;
				}
				frappe.call({
					method: API,
					freeze: true,
					freeze_message: __('Saving the quote...'),
					args: { action: 'save', pos_profile: pos.pos_profile, customer: frm.doc.customer,
						valid_till: values.valid_till, sales_person: sales_person, items: JSON.stringify(items) }
				}).then(function (r) {
					const q = r.message;
					d.hide();
					pos.load_new_invoice_on_pos();
					frappe.msgprint({
						title: __('Quote saved'),
						indicator: 'green',
						message: __('{0} for {1}. Find it under Recent Orders, Quotes.', [esc(q.name), format_currency(q.grand_total, q.currency)]),
						primary_action: { label: __('Print quote'), action: function () { print_quote(q.name, q.letter_head); } }
					});
				});
			}
		});
		// keep the till's barcode-scanner listener from also typing into the item search
		d.$wrapper.on('keydown keypress keyup', 'input', function (e) { e.stopPropagation(); });
		d.show();
	}

	// ---- Recent Orders: find a quote, print it or invoice it --------------------------

	function show_quote(doc) {
		const s = window.cur_pos.order_summary;
		s.doc = doc;
		s.toggle_summary_placeholder(false);
		s.$component.css('grid-column', 'span 6 / span 6');
		s.$upper_section.html('<div class="left-section"><div class="customer-section"><div class="customer-name">' + esc(doc.customer_name) + '</div></div>'
			+ '<div class="cashier">' + __('Prepared by') + ': ' + esc(doc.custom_sales_representative || doc.owner) + '</div>'
			+ '<div class="cashier">' + __('Valid until') + ': ' + esc(frappe.datetime.str_to_user(doc.valid_till)) + '</div></div>'
			+ '<div class="right-section"><div class="paid-amount">' + format_currency(doc.grand_total, doc.currency) + '</div>'
			+ '<div class="invoice-name">' + esc(doc.name) + '</div>'
			+ '<span class="indicator-pill whitespace-nowrap ' + (doc.status === 'Expired' ? 'red' : 'blue') + '"><span>' + esc(__(doc.status === 'Expired' ? 'Expired' : 'Quote')) + '</span></span></div>');
		s.$items_container.html((doc.items || []).map(function (i) {
			return '<div class="item-row-wrapper"><div class="item-row-data">'
				+ '<div class="item-name">' + esc(i.item_name) + '</div>'
				+ '<div class="item-qty">' + esc(i.qty) + ' ' + esc(i.uom) + '</div>'
				+ '<div class="item-rate-disc"><div class="item-rate">' + format_currency(i.rate, doc.currency) + '</div></div>'
				+ '</div></div>';
		}).join(''));
		s.attach_totals_info(doc);
		s.$payment_container.html('').prev('.label').hide();
		s.$summary_btns.html('<div class="summary-btn btn btn-default ard-quote-invoice">' + __('Invoice this quote') + '</div>'
			+ '<div class="summary-btn btn btn-default ard-quote-print">' + __('Print quote') + '</div>');
	}

	function invoice_quote(doc) {
		frappe.call({
			method: API,
			freeze: true,
			freeze_message: __('Starting the sale...'),
			args: { action: 'invoice', quotation: doc.name }
		}).then(function (r) {
			// what the till's own Edit Order button does with a draft
			const s = window.cur_pos.order_summary;
			s.events.edit_order('Sales Invoice', r.message.name);
			s.toggle_component(false);
			s.$component.find('.no-summary-placeholder').css('display', 'flex');
			s.$summary_wrapper.css('display', 'none');
		});
	}

	function patch_list(list) {
		// after "POS Recent Orders Sales Returns" has made it this till's Sales / Returns
		if (!list.__ardmore_v3 || list.__ard_quotes) return;
		list.__ard_quotes = true;

		const refresh = list.refresh_list;
		list.refresh_list = function () {
			if (this.status_field.get_value() !== QUOTES) return refresh.apply(this, arguments);
			const me = this;
			frappe.dom.freeze();
			this.events.reset_summary();
			this.$invoices_container.html('');
			return Promise.resolve(frappe.call({
				method: API,
				args: { action: 'list', pos_profile: window.cur_pos.pos_profile, term: this.search_field.get_value() || '' }
			})).then(function (r) {
				(r.message || []).forEach(function (q) { me.$invoices_container.append(me.get_invoice_html(q)); });
			}).finally(function () { frappe.dom.unfreeze(); });
		};

		const open = list.events.open_invoice_data;
		list.events.open_invoice_data = function (doctype, name) {
			if (doctype !== 'Quotation') return open.apply(this, arguments);
			frappe.db.get_doc('Quotation', name).then(show_quote);
		};

		const sf = list.status_field;
		sf.df.options = ['Sales', 'Returns', QUOTES].join('\n');
		sf.df.placeholder = __('Sales, Returns or Quotes');
		sf.refresh();
	}

	function patch_summary(s) {
		if (s.__ard_quotes) return;
		s.__ard_quotes = true;
		const load = s.load_summary_of;
		s.load_summary_of = function () {
			this.$payment_container.prev('.label').show();
			return load.apply(this, arguments);
		};
		s.$summary_container.on('click', '.ard-quote-invoice', function () { invoice_quote(s.doc); });
		s.$summary_container.on('click', '.ard-quote-print', function () { print_quote(s.doc.name, s.doc.letter_head); });
	}

	// The till rebuilds its components when the cashier comes back to it, so keep watching.
	setInterval(function () {
		const pos = window.cur_pos;
		if (!pos) return;
		if (pos.page && pos.page.btn_secondary && pos.page.btn_secondary.length && !document.getElementById(BTN)) {
			$('<button id="' + BTN + '" class="btn btn-default btn-sm ellipsis">' + __('Quote') + '</button>')
				.insertBefore(pos.page.btn_secondary)
				.on('click', start_quote);
		}
		if (pos.recent_order_list) patch_list(pos.recent_order_list);
		if (pos.order_summary) patch_summary(pos.order_summary);
	}, 1000);
})();
