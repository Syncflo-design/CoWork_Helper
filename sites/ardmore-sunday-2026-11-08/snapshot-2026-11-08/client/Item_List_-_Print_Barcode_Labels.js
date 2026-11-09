// Ardmore - "Print Barcode Labels" action on the Item list.
//
// Select items -> Actions -> Print Barcode Labels -> set a quantity per item ->
// the labels go straight to the store's USB Zebra via Zebra Browser Print.
//
// The site is on Frappe Cloud and the printer is on the shop counter, so the
// server cannot reach it. Everything below runs in the browser: ERPNext builds
// the ZPL, this script hands it to the Browser Print service on localhost.
// If that service is not installed, the ZPL can still be downloaded.

frappe.listview_settings['Item'] = frappe.listview_settings['Item'] || {};

frappe.provide('ardmore.labels');

ardmore.labels = (function () {
	// Browser Print listens on 9101 (https) and 9100 (http). Browsers treat
	// 127.0.0.1 as a secure origin, so an https page may call it.
	const ORIGINS = ['https://127.0.0.1:9101', 'http://127.0.0.1:9100'];

	function find_printer() {
		let chain = Promise.resolve(null);
		ORIGINS.forEach(function (origin) {
			chain = chain.then(function (found) {
				if (found) {
					return found;
				}
				return fetch(origin + '/default?type=printer')
					.then(function (res) {
						return res.ok ? res.text() : null;
					})
					.then(function (txt) {
						if (!txt) {
							return null;
						}
						try {
							return { origin: origin, device: JSON.parse(txt) };
						} catch (e) {
							return null;
						}
					})
					.catch(function () {
						return null;
					});
			});
		});
		return chain;
	}

	function send_to_printer(target, zpl) {
		return fetch(target.origin + '/write', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ device: target.device, data: zpl })
		}).then(function (res) {
			if (!res.ok) {
				throw new Error('Browser Print returned ' + res.status);
			}
			return true;
		});
	}

	function download(zpl) {
		const blob = new Blob([zpl], { type: 'application/octet-stream' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = 'ardmore-labels.zpl';
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);
		URL.revokeObjectURL(url);
	}

	function rows_html(items) {
		let h = '<div style="max-height:300px;overflow:auto;border:1px solid var(--border-color);border-radius:var(--border-radius)">';
		h += '<table class="table table-sm" style="margin-bottom:0">';
		h += '<thead><tr><th>' + __('Item') + '</th><th style="width:130px">' + __('How many?') + '</th></tr></thead><tbody>';
		items.forEach(function (it, i) {
			h += '<tr><td><div><b>' + frappe.utils.escape_html(it.name) + '</b></div>';
			if (it.item_name && it.item_name !== it.name) {
				h += '<div class="text-muted small">' + frappe.utils.escape_html(it.item_name) + '</div>';
			}
			h += '</td><td><input type="number" min="0" step="1" value="1" class="form-control ard-qty" data-idx="' + i + '"></td></tr>';
		});
		h += '</tbody></table></div>';
		return h;
	}

	function collect(dialog, items) {
		const out = [];
		dialog.$wrapper.find('.ard-qty').each(function () {
			const idx = parseInt($(this).attr('data-idx'), 10);
			const qty = parseInt($(this).val(), 10) || 0;
			if (qty > 0 && items[idx]) {
				out.push({ item: items[idx].name, qty: qty });
			}
		});
		return out;
	}

	function build_zpl(dialog, items) {
		const rows = collect(dialog, items);
		if (!rows.length) {
			frappe.msgprint(__('Put a number next to at least one item first.'));
			return Promise.resolve(null);
		}
		return frappe
			.call({
				method: 'ardmore_barcode_label_zpl',
				args: {
					items: JSON.stringify(rows),
					label_w: dialog.get_value('label_w') || 40,
					label_h: dialog.get_value('label_h') || 20
				}
			})
			.then(function (r) {
				const msg = r && r.message;
				if (!msg || !msg.labels) {
					frappe.msgprint(__('Nothing to print.'));
					return null;
				}
				if (msg.warnings && msg.warnings.length) {
					frappe.msgprint({
						title: __('Some stickers could not be made'),
						indicator: 'orange',
						message: msg.warnings.join('<br>')
					});
				}
				return msg;
			});
	}

	function open(listview) {
		const items = listview.get_checked_items() || [];
		if (!items.length) {
			frappe.msgprint(__('Tick the boxes next to the items you want stickers for, then try again.'));
			return;
		}

		const dialog = new frappe.ui.Dialog({
			title: __('Print barcode stickers'),
			size: 'large',
			fields: [
				{ fieldtype: 'HTML', fieldname: 'rows' },
				{ fieldtype: 'Section Break' },
				{
					fieldtype: 'Int',
					fieldname: 'set_all',
					label: __('Same number for every item'),
					description: __('Type one number here and every item in the list gets that many labels. You can still change any single item afterwards. Put 0 next to an item to skip it.')
				},
				{ fieldtype: 'Column Break' },
				{ fieldtype: 'Float', fieldname: 'label_w', label: __('Sticker width (mm)'), default: 40, description: __('How wide one sticker is. Only change this if you buy a different sticker.') },
				{ fieldtype: 'Column Break' },
				{ fieldtype: 'Float', fieldname: 'label_h', label: __('Sticker height (mm)'), default: 20, description: __('How tall one sticker is.') }
			],
			primary_action_label: __('Print now'),
			primary_action: function () {
				build_zpl(dialog, items).then(function (msg) {
					if (!msg) {
						return;
					}
					find_printer().then(function (target) {
						if (!target) {
							frappe.msgprint({
								title: __('No printer found on this computer'),
								indicator: 'orange',
								message: __(
									'Zebra Browser Print is not running on this computer, so the labels could not be sent to the printer. Use "Download .zpl" instead, or install Zebra Browser Print on the till PC.'
								)
							});
							return;
						}
						send_to_printer(target, msg.zpl)
							.then(function () {
								dialog.hide();
								frappe.show_alert({
									message: __('Sent {0} label(s) to the printer.', [msg.labels]),
									indicator: 'green'
								});
							})
							.catch(function (e) {
								frappe.msgprint({
									title: __('Printing failed'),
									indicator: 'red',
									message: frappe.utils.escape_html(String(e.message || e))
								});
							});
					});
				});
			},
			secondary_action_label: __('Save to a file instead'),
			secondary_action: function () {
				build_zpl(dialog, items).then(function (msg) {
					if (msg) {
						download(msg.zpl);
					}
				});
			}
		});

		dialog.fields_dict.rows.$wrapper.html(rows_html(items));

		dialog.fields_dict.set_all.$input.on('change', function () {
			const v = parseInt($(this).val(), 10);
			if (!isNaN(v) && v >= 0) {
				dialog.$wrapper.find('.ard-qty').val(v);
			}
		});

		dialog.show();
	}

	return { open: open };
})();

frappe.listview_settings['Item'].onload = function (listview) {
	const label = __('Print Barcode Labels');
	const handler = function () {
		ardmore.labels.open(listview);
	};
	if (listview.page.add_actions_menu_item) {
		listview.page.add_actions_menu_item(label, handler, false);
	} else {
		listview.page.add_menu_item(label, handler);
	}
};
