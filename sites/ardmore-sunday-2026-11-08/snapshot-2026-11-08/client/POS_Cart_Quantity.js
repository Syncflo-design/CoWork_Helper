// =============================================================
// Ardmore POS - type the quantity in the cart (v2, 2026-09-29)
// Client Script on POS Invoice (Form) - evaluated inside the POS page
// (loaded by "POS Till Scripts Loader" in Sales Invoice mode).
// -------------------------------------------------------------
// Standard POS shows the quantity in the cart as plain text. To change it the
// cashier has to open the item, or keep clicking the item tile. Cheri,
// 24 Sept 2026: "can't edit in cart".
//
// The quantity on each cart line is now a box the cashier can type into:
//   type a qty  then press Enter or click away
//   type 0      removes the line
//   Esc         puts the old figure back
// Typing only, no step buttons (Russell, 2026-09-29).
//
// v2 - WHOLE NUMBERS unless the unit is sold by length (Russell, 2026-09-29):
//   each (and every other unit)  whole numbers only, 2.5 is refused
//   Meter                        decimals allowed, e.g. 2.5
// The units that may take decimals are listed in DECIMAL_UNITS below. The same
// rule is enforced by ERPNext itself on save through UOM > "Must be Whole
// Number" (ticked on "each"), which also covers the item panel and every other
// document. Keep the two in step: a unit added to DECIMAL_UNITS must have that
// box unticked on its UOM record.
// Stock is checked exactly as the standard till does it. Clicking anywhere
// else on the line still opens the item as before.
//
// Not shown on returns (the return picker sets those quantities) and locked
// while the payment screen is open (use Edit Cart first, as standard).
//
// ERPNext only applies a quantity from outside the item panel when it is a
// "+1" from a tile click (Controller.on_cart_update), so this script sets the
// row itself, using the same calls in the same order as the standard code.
// The POS rebuilds a cart line every time it changes, so this keeps watching.
// =============================================================
(function () {
	'use strict';
	if (window.__ardmore_pos_cart_qty_v2) return;
	window.__ardmore_pos_cart_qty_v2 = true;

	const ROW = '.point-of-sale-app .cart-items-section .cart-item-wrapper';

	// Units that may be sold in part quantities. Lower case. Everything else is whole.
	const DECIMAL_UNITS = ['meter', 'metre'];

	function whole_only(row) {
		const u = String((row && row.uom) || '').trim().toLowerCase();
		return DECIMAL_UNITS.indexOf(u) === -1;
	}

	function ensure_style() {
		if (document.getElementById('ard-pos-cartqty-style')) return;
		const st = document.createElement('style');
		st.id = 'ard-pos-cartqty-style';
		st.textContent = [
			ROW + ' .item-qty .ard-qty { display: inline-flex; align-items: center; gap: 6px; white-space: nowrap; }',
			ROW + ' .item-qty .ard-qty-input { width: 58px; height: 28px; padding: 0 4px; border: 1px solid var(--border-color, #d1d8dd); border-radius: 6px; background: var(--fg-color, #fff); color: var(--text-color, #1f272e); font-weight: 600; text-align: center; }',
			ROW + ' .item-qty .ard-qty-input:focus { outline: none; border-color: var(--primary, #2490ef); }',
			ROW + ' .item-qty .ard-qty-uom { color: var(--text-muted, #8d99a6); }',
			ROW + ' .item-qty .ard-qty-plain { display: none; }',
			// payment screen open: show the plain figure, hide the box
			'.point-of-sale-app.ard-cart-locked .cart-item-wrapper .item-qty .ard-qty { display: none; }',
			'.point-of-sale-app.ard-cart-locked .cart-item-wrapper .item-qty .ard-qty-plain { display: inline; }'
		].join('\n');
		document.head.appendChild(st);
	}

	function pos() {
		return window.cur_pos && window.cur_pos.frm && window.cur_pos.cart ? window.cur_pos : null;
	}

	function get_row(name) {
		const p = pos();
		if (!p) return null;
		return (p.frm.doc.items || []).find(function (r) { return r.name === name; }) || null;
	}

	function fmt(q) {
		return String(flt(q, 3));
	}

	let busy = false;

	async function apply_qty(name, wanted) {
		const p = pos();
		const row = get_row(name);
		if (!p || !row || busy) return;
		if (p.frm.doc.is_return || p.frm.doc.docstatus !== 0) return;

		const qty = flt(wanted, 3);
		if (isNaN(qty) || qty < 0) { p.update_cart_html(row); return; }
		if (qty === flt(row.qty, 3)) { p.update_cart_html(row); return; }

		busy = true;
		frappe.dom.freeze();
		try {
			if (qty === 0) {
				const editing = p.item_details && p.item_details.current_item && p.item_details.current_item.name === row.name;
				await frappe.model.set_value(row.doctype, row.name, 'qty', 0);
				frappe.model.clear_doc(row.doctype, row.name);
				p.update_cart_html(row, true);
				if (editing) p.item_details.toggle_item_details_section(null);
			} else {
				if (!p.allow_negative_stock) {
					await p.check_stock_availability(row, qty * flt(row.conversion_factor || 1), p.frm.doc.set_warehouse);
				}
				await frappe.model.set_value(row.doctype, row.name, 'qty', qty);
				p.update_cart_html(row);
			}
		} catch (e) {
			// Not enough stock (the till has already told the cashier) - put the old figure back.
			const still = get_row(name);
			if (still) p.update_cart_html(still);
		} finally {
			busy = false;
			frappe.dom.unfreeze();
		}
	}

	function stop(e) { e.stopPropagation(); }

	function build(name, row) {
		const wrap = document.createElement('span');
		wrap.className = 'ard-qty';

		const input = document.createElement('input');
		input.type = 'text';
		input.inputMode = whole_only(row) ? 'numeric' : 'decimal';
		input.autocomplete = 'off';
		input.className = 'ard-qty-input';
		input.value = fmt(row.qty);
		input.title = whole_only(row)
			? __('Type a whole number, then press Enter. 0 removes the line.')
			: __('Type the quantity, then press Enter. 0 removes the line.');

		const uom = document.createElement('span');
		uom.className = 'ard-qty-uom';
		uom.textContent = row.uom || '';

		// Keep clicks and keystrokes away from the till's own listeners
		// (row click opens the item; keys feed the numpad and the scanner).
		['keydown', 'keypress', 'keyup', 'click', 'mousedown'].forEach(function (ev) {
			input.addEventListener(ev, stop);
		});
		input.addEventListener('focus', function () { input.select(); });
		input.addEventListener('keydown', function (e) {
			if (e.key === 'Enter') { e.preventDefault(); input.blur(); }
			if (e.key === 'Escape') { const r = get_row(name); input.value = r ? fmt(r.qty) : input.value; input.blur(); }
		});
		input.addEventListener('change', function () {
			const raw = String(input.value || '').replace(',', '.').trim();
			const r = get_row(name);
			if (raw === '' || isNaN(Number(raw)) || Number(raw) < 0) {
				if (r) input.value = fmt(r.qty);
				return;
			}
			if (r && whole_only(r) && Number(raw) !== Math.floor(Number(raw))) {
				input.value = fmt(r.qty);
				frappe.show_alert({
					message: __('{0} is sold in whole numbers only.', [frappe.utils.escape_html(r.item_name || r.item_code)]),
					indicator: 'orange'
				});
				frappe.utils.play_sound('error');
				return;
			}
			apply_qty(name, Number(raw));
		});

		wrap.appendChild(input);
		wrap.appendChild(uom);
		return wrap;
	}

	function paint() {
		const p = pos();
		if (!p) return;

		const app = document.querySelector('.point-of-sale-app');
		if (app) {
			const btn = app.querySelector('.edit-cart-btn');
			const locked = !!(btn && btn.offsetParent !== null);
			if (app.classList.contains('ard-cart-locked') !== locked) app.classList.toggle('ard-cart-locked', locked);
		}

		if (p.frm.doc.is_return || p.frm.doc.docstatus !== 0) return;

		const rows = document.querySelectorAll(ROW + '[data-row-name]');
		if (!rows.length) return;
		ensure_style();

		for (let i = 0; i < rows.length; i++) {
			const el = rows[i];
			const holder = el.querySelector('.item-qty');
			if (!holder || holder.querySelector('.ard-qty')) continue;
			const name = el.getAttribute('data-row-name');
			const row = get_row(name);
			if (!row) continue;

			const plain = holder.querySelector('span');
			if (plain) plain.classList.add('ard-qty-plain');
			holder.appendChild(build(name, row));
		}
	}

	let timer = null;
	function schedule() {
		if (timer) return;
		timer = setTimeout(function () {
			timer = null;
			try { paint(); } catch (e) { console.warn('Ardmore POS cart qty:', e); }
		}, 80);
	}

	schedule();
	new MutationObserver(schedule).observe(document.body, {
		childList: true, subtree: true, attributes: true, attributeFilter: ['style', 'class']
	});
})();
