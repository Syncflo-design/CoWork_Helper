// =============================================================
// Ardmore POS - New Customer (v4, 2026-11-03)
// Client Script on POS Invoice (Form) - evaluated inside the POS page.
// -------------------------------------------------------------
// * "+" next to the customer search opens a short dialog:
//   Customer Type, Name, VAT number (companies), Mobile, Email,
//   Add to Mailing List, and an optional Address.
// * Save creates the Customer (and its address) and puts it straight on
//   the cart. No full Customer form afterwards.
// * The search box's "Create a new Customer" path opens the same dialog.
// * Mailing list requires an email (checked against the dialog's own
//   email field, so the false "please add an email" error is gone).
// 2026-11-01 (Russell, go-live day): companies pay at the till and need a
// tax invoice in their name - Customer Type + VAT number (Customer.tax_id,
// printed on the receipt); customers who need goods shipped give an
// address, saved as their primary + shipping Address so it lands on the
// sale and prints on the receipt. Never a credit sale: that is Account Sale.
// 2026-11-02 (Russell): section relabelled "Ship to (optional)" -> "Address (optional)".
// 2026-11-02: new customers get Customer Group "Cash". The tills now only accept customers
// in Cash / Online Sales, and a group-less customer failed with "does not match" at the till.
// 2026-11-03 (Russell): "Paste full address" - a copied address goes into one box and fills the
// lines below it (street / address 2 / suburb or town / postal code / country), which stay
// editable to check before saving. Replaces v3; v3 stays disabled as the way back.
// =============================================================
(function () {
	'use strict';
	if (window.__ardmore_cust_ux_v4) return; // Client Scripts re-run per Form; install once
	window.__ardmore_cust_ux_v4 = true;

	const PLUS_ID = 'ardmore-cust-plus';
	const NEW_CUSTOMER_GROUP = 'Cash'; // Sage Home walk-in category; one of the tills' allowed customer groups
	const ADDRESS_FIELDS = ['address_line1', 'address_line2', 'city', 'state', 'pincode'];
	// what people type for a country; the commonest are here so they never wait on the Country
	// list, which loads in the background when the dialog opens and covers every other country
	const COUNTRY_ALIASES = {
		'south africa': 'South Africa', 'sa': 'South Africa', 'rsa': 'South Africa', 'za': 'South Africa',
		'united kingdom': 'United Kingdom', 'uk': 'United Kingdom', 'england': 'United Kingdom', 'great britain': 'United Kingdom',
		'united states': 'United States', 'us': 'United States', 'usa': 'United States', 'united states of america': 'United States'
	};
	const PROVINCES = {
		'gauteng': 'Gauteng', 'western cape': 'Western Cape', 'eastern cape': 'Eastern Cape',
		'northern cape': 'Northern Cape', 'kwazulu-natal': 'KwaZulu-Natal', 'kwazulu natal': 'KwaZulu-Natal',
		'kzn': 'KwaZulu-Natal', 'free state': 'Free State', 'limpopo': 'Limpopo',
		'mpumalanga': 'Mpumalanga', 'north west': 'North West'
	};

	let countries = null; // lower-case name -> Country record, loaded once per till session

	function on_pos() {
		return (frappe.get_route() || [])[0] === 'point-of-sale';
	}

	function set_customer_on_cart(name) {
		const pos = window.cur_pos;
		if (pos && pos.cart && pos.cart.customer_field) {
			pos.cart.customer_field.set_value(name);
		}
	}

	function clean(v) {
		return (v || '').toString().trim();
	}

	function load_countries() {
		if (countries) return;
		countries = {};
		frappe.db.get_list('Country', { fields: ['name'], limit: 500 }).then((rows) => {
			(rows || []).forEach((r) => { countries[r.name.toLowerCase()] = r.name; });
		});
	}

	function country_of(text) {
		const key = clean(text).toLowerCase().replace(/\./g, '');
		return COUNTRY_ALIASES[key] || (countries && countries[key]) || '';
	}

	// 2196, 90210, 10001-1234, SW1A 1AA - a digit, no word of four letters or more
	function is_postcode(text) {
		return /^(?=.*\d)[A-Za-z0-9][A-Za-z0-9 -]{2,9}$/.test(text) && !/[A-Za-z]{4,}/.test(text);
	}

	// One pasted address -> the address fields. Read from the end: country, postal code (its own
	// line, or the end of the town line), province, town; the rest is street and address 2.
	// Lines may also arrive comma-separated on a single line.
	function split_address(text) {
		let parts = clean(text).split(/\r?\n/).map((s) => clean(s).replace(/,+$/, '').trim()).filter(Boolean);
		if (parts.length === 1) parts = parts[0].split(',').map(clean).filter(Boolean);
		const out = { address_line1: '', address_line2: '', city: '', state: '', pincode: '', country: '' };
		const last = () => parts[parts.length - 1];
		if (parts.length > 1 && country_of(last())) out.country = country_of(parts.pop());
		if (parts.length > 1 && is_postcode(last())) {
			out.pincode = parts.pop();
		} else if (parts.length > 1) {
			const m = last().match(/^(.*\D)[\s,]+(\d{4,6}(?:-\d{4})?)$/);
			if (m) {
				parts[parts.length - 1] = clean(m[1]);
				out.pincode = m[2];
			}
		}
		if (parts.length > 1 && PROVINCES[last().toLowerCase()]) out.state = PROVINCES[parts.pop().toLowerCase()];
		if (parts.length > 1) out.city = parts.pop();
		out.address_line1 = parts.shift() || '';
		out.address_line2 = parts.join(', ');
		return out;
	}

	function fill_from_paste(d) {
		const text = d.get_value('paste_address');
		if (!clean(text)) return;
		const a = split_address(text);
		ADDRESS_FIELDS.forEach((f) => d.set_value(f, a[f]));
		if (a.country) d.set_value('country', a.country);
	}

	// The address goes on after the customer exists; a failure here keeps the customer.
	function save_address(customer, v, done) {
		frappe.call({
			method: 'frappe.client.insert',
			args: {
				doc: {
					doctype: 'Address',
					address_title: customer.customer_name || customer.name,
					address_type: 'Shipping',
					address_line1: clean(v.address_line1),
					address_line2: clean(v.address_line2),
					city: clean(v.city),
					state: clean(v.state),
					pincode: clean(v.pincode),
					country: v.country || 'South Africa',
					is_primary_address: 1,
					is_shipping_address: 1,
					links: [{ link_doctype: 'Customer', link_name: customer.name }]
				}
			},
			callback() { done(true); },
			error() { done(false); }
		});
	}

	function open_new_customer_dialog(prefill_name) {
		if (window.__ardmore_cust_dialog) return;
		load_countries();
		const d = new frappe.ui.Dialog({
			title: __('New Customer'),
			fields: [
				{ fieldname: 'customer_type', label: __('Customer Type'), fieldtype: 'Select',
					options: 'Individual\nCompany', default: 'Individual' },
				{ fieldname: 'customer_name', label: __('Customer Name'), fieldtype: 'Data', reqd: 1,
					default: prefill_name || '' },
				{ fieldname: 'tax_id', label: __('Company VAT Number'), fieldtype: 'Data',
					depends_on: "eval:doc.customer_type=='Company'" },
				{ fieldname: 'mobile_no', label: __('Mobile Number'), fieldtype: 'Data' },
				{ fieldname: 'email_id', label: __('Email'), fieldtype: 'Data', options: 'Email' },
				{ fieldname: 'add_to_mailing_list', label: __('Add to Mailing List'), fieldtype: 'Check', default: 0 },
				{ fieldname: 'ship_section', label: __('Address (optional)'), fieldtype: 'Section Break', collapsible: 1 },
				{ fieldname: 'paste_address', label: __('Paste full address'), fieldtype: 'Small Text',
					description: __('Paste the whole address here (street, address 2, suburb or town, postal code, country). It fills the lines below; check them before you save.'),
					onchange() { fill_from_paste(d); } },
				{ fieldname: 'address_line1', label: __('Address Line 1'), fieldtype: 'Data' },
				{ fieldname: 'address_line2', label: __('Address Line 2'), fieldtype: 'Data' },
				{ fieldname: 'city', label: __('Suburb / Town'), fieldtype: 'Data' },
				{ fieldname: 'state', label: __('Province'), fieldtype: 'Data' },
				{ fieldname: 'pincode', label: __('Postal Code'), fieldtype: 'Data' },
				{ fieldname: 'country', label: __('Country'), fieldtype: 'Link', options: 'Country', default: 'South Africa' }
			],
			primary_action_label: __('Save'),
			primary_action(v) {
				const name = clean(v.customer_name);
				const email = clean(v.email_id);
				const mobile = clean(v.mobile_no);
				const company = v.customer_type === 'Company';
				const vat = company ? clean(v.tax_id) : '';
				const mailing = v.add_to_mailing_list ? 1 : 0;
				const has_address = ADDRESS_FIELDS.some((f) => clean(v[f]));
				if (!name) return;
				if (mailing && !email) {
					frappe.msgprint({
						title: __('Email needed'),
						indicator: 'red',
						message: __('Please enter an email address before adding this customer to the mailing list.')
					});
					return;
				}
				if (has_address && (!clean(v.address_line1) || !clean(v.city))) {
					frappe.msgprint({
						title: __('Address incomplete'),
						indicator: 'red',
						message: __('To save an address, fill in at least Address Line 1 and Suburb / Town. Or clear the Address fields.')
					});
					return;
				}
				const doc = {
					doctype: 'Customer',
					customer_name: name,
					customer_type: company ? 'Company' : 'Individual',
					// the till's customer box only accepts its POS Profile's customer groups
					customer_group: NEW_CUSTOMER_GROUP,
					add_to_mailing_list: mailing
				};
				if (vat) doc.tax_id = vat;
				if (mobile) doc.mobile_no = mobile;
				if (email) {
					doc.email_id = email;
					doc.custom_email_address = email;
				}
				d.get_primary_btn().prop('disabled', true);
				frappe.call({
					method: 'frappe.client.insert',
					args: { doc: doc },
					callback(r) {
						const c = r.message;
						const finish = (address_ok) => {
							d.hide();
							set_customer_on_cart(c.name);
							const who = frappe.utils.escape_html(c.customer_name || c.name);
							frappe.show_alert({
								message: __('Customer {0} saved', [who])
									+ (mailing ? ' &middot; ' + __('added to mailing list') : '')
									+ (has_address && address_ok ? ' &middot; ' + __('address saved') : ''),
								indicator: 'green'
							}, 4);
							if (has_address && !address_ok) {
								frappe.msgprint({
									title: __('Address not saved'),
									indicator: 'orange',
									message: __('{0} was saved, but the address was not. Add it on the customer later.', [who])
								});
							}
						};
						if (has_address) save_address(c, v, finish);
						else finish(true);
					},
					always() {
						d.get_primary_btn().prop('disabled', false);
					}
				});
			}
		});
		d.onhide = () => { window.__ardmore_cust_dialog = null; };
		window.__ardmore_cust_dialog = d;
		// fill the lines as soon as an address is pasted, not only when the box loses focus
		let paste_timer = null;
		d.fields_dict.paste_address.$input.on('input', () => {
			clearTimeout(paste_timer);
			paste_timer = setTimeout(() => fill_from_paste(d), 250);
		});
		d.show();
		setTimeout(() => d.fields_dict.customer_name && d.fields_dict.customer_name.set_focus(), 200);
	}

	// Route the search box's "Create a new Customer" through the same dialog.
	// Frappe calls make_quick_entry from the Link control (frappe._from_link set)
	// and from frappe.new_doc; both come here. We set the cart ourselves, so the
	// link callback is dropped to avoid a double set.
	const orig_mqe = frappe.ui.form.make_quick_entry;
	frappe.ui.form.make_quick_entry = function (doctype) {
		if (doctype === 'Customer' && on_pos()) {
			const typed = (frappe.route_options && frappe.route_options.name_field) || '';
			frappe.route_options = null;
			frappe._from_link = null;
			open_new_customer_dialog(typed);
			return Promise.resolve();
		}
		return orig_mqe.apply(this, arguments);
	};

	// "+" button beside the customer search (only while no customer is selected)
	function find_customer_input() {
		const inputs = document.querySelectorAll('#page-point-of-sale .customer-field input, #page-point-of-sale input');
		for (const inp of inputs) {
			if ((inp.placeholder || '').toLowerCase().includes('search by customer')) return inp;
		}
		return null;
	}

	function inject_plus_btn() {
		if (!on_pos()) return;
		if (document.getElementById(PLUS_ID)) return;
		const inp = find_customer_input();
		if (!inp) return;
		const btn = document.createElement('button');
		btn.id = PLUS_ID;
		btn.type = 'button';
		btn.textContent = '+';
		btn.title = __('New Customer');
		btn.style.cssText =
			'width:34px;height:34px;border-radius:50%;border:none;flex-shrink:0;' +
			'background:#1a56db;color:#fff;font-size:22px;font-weight:700;cursor:pointer;' +
			'display:inline-flex;align-items:center;justify-content:center;' +
			'box-shadow:0 2px 6px rgba(26,86,219,.4);margin-left:6px;';
		btn.addEventListener('click', (e) => {
			e.preventDefault();
			e.stopPropagation();
			open_new_customer_dialog('');
		});
		const wrap = inp.closest('.control-input') || inp.parentElement;
		wrap.style.display = 'flex';
		wrap.style.alignItems = 'center';
		wrap.appendChild(btn);
	}

	let timer = null;
	const observer = new MutationObserver(() => {
		clearTimeout(timer);
		timer = setTimeout(inject_plus_btn, 300);
	});
	observer.observe(document.body, { childList: true, subtree: true });
	[800, 2000, 4000, 8000].forEach((ms) => setTimeout(inject_plus_btn, ms));
})();
