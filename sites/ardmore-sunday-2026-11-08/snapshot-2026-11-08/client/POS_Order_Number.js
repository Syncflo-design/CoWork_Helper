// =============================================================
// Ardmore POS - Order Number on the payment screen (v1, 2026-11-03)
// Client Script on POS Invoice (Form) - evaluated inside the POS page
// (loaded by "POS Till Scripts Loader" in Sales Invoice mode).
// -------------------------------------------------------------
// Russell, 2026-11-03: the Online till types the Shopify order number for EACH sale. On the
// payment screen an "Order Number" card sits on the customer card's line (right-hand side) and
// the Payment Method card moves down so its top lines up with the Item Cart. Only on a till
// whose POS Profile is an online store (Online Store box ticked).
// The number is kept on the invoice's Customer's Purchase Order (po_no), so one customer can
// have a different number on every order and a new invoice starts empty. post-taxinvoice-to-sage
// sends it to Sage's Customer Ref as "Customer name: order number" (returns likewise).
// =============================================================
(function () {
	'use strict';
	if (window.__ardmore_pos_order_no_v1) return;
	window.__ardmore_pos_order_no_v1 = true;

	function is_online() {
		const s = window.cur_pos && window.cur_pos.settings;
		return !!(s && cint(s.custom_online_store));
	}

	function ensure_style() {
		if (document.getElementById('ard-order-no-style')) return;
		const st = document.createElement('style');
		st.id = 'ard-order-no-style';
		st.textContent = [
			'.point-of-sale-app > .payment-container.ard-has-order { position: relative; overflow: visible; }',
			'.point-of-sale-app > .payment-container > .ard-order-card { position: absolute; left: 0; right: 0; box-sizing: border-box;',
			'  display: flex; flex-direction: column; justify-content: center; padding: var(--padding-md) var(--padding-lg);',
			'  background-color: var(--fg-color); box-shadow: var(--shadow-base); border-radius: var(--border-radius-md); }',
			'.point-of-sale-app > .payment-container > .ard-order-card .section-label { margin-bottom: var(--margin-sm); }',
			'.point-of-sale-app > .payment-container > .ard-order-card .ard-order-input { max-width: 24rem; }'
		].join('\n');
		document.head.appendChild(st);
	}

	// The card takes the customer card's place and height on the right; the Payment Method card
	// starts where the Item Cart starts. Side by side only: a narrow screen stacks them instead.
	function layout($pay) {
		const $card = $pay.children('.ard-order-card');
		const $cust = $('.point-of-sale-app > .customer-cart-container > .customer-section');
		const $cart = $('.point-of-sale-app > .customer-cart-container > .cart-container');
		if (!$card.length || !$cust.length || !$cart.length) return;
		const beside = $pay.offset().left >= $cust.offset().left + $cust.outerWidth() - 1;
		const offset = Math.max(Math.round($cart.offset().top - $cust.offset().top), 0);
		if (!beside || !offset) {
			$card.css({ position: 'static', top: '', height: '', 'margin-bottom': 'var(--margin-md)' });
			$pay.css({ 'margin-top': '', height: '', 'max-height': '', 'min-height': '' });
			$pay.find('.payment-modes').css('height', '');
			return;
		}
		const fit = 'calc(100vh - 5rem - ' + offset + 'px)';
		$pay.css({ 'margin-top': offset + 'px', height: fit, 'max-height': fit, 'min-height': 0 });
		$card.css({ position: '', top: -offset + 'px', height: $cust.outerHeight() + 'px', 'margin-bottom': '' });
		$pay.find('.payment-modes').css('height', 'calc(100vh - ' + (350 + offset) + 'px)');
	}

	function reset($pay) {
		$pay.removeClass('ard-has-order').css({ 'margin-top': '', height: '', 'max-height': '', 'min-height': '' });
		$pay.children('.ard-order-card').remove();
		$pay.find('.payment-modes').css('height', '');
	}

	function render(payment) {
		const $pay = payment.$component;
		if (!$pay || !$pay.length) return;
		if (!is_online()) { reset($pay); return; }
		ensure_style();
		const frm = payment.events.get_frm();
		let $card = $pay.children('.ard-order-card');
		if (!$card.length) {
			$card = $([
				'<div class="ard-order-card">',
				'  <div class="section-label">' + __('Order Number') + '</div>',
				'  <input type="text" class="form-control ard-order-input" autocomplete="off" spellcheck="false"',
				'         placeholder="' + __('Shopify order number') + '">',
				'</div>'
			].join('\n')).prependTo($pay);
			const $input = $card.find('input');
			// typing here must never reach the till's own key handlers (amounts, shortcuts)
			$input.on('keydown keypress keyup', (e) => e.stopPropagation());
			$input.on('input', function () {
				const f = payment.events.get_frm();
				if (f && !f.doc.docstatus) f.doc.po_no = ($(this).val() || '').trim();
			});
			$input.on('change', function () {
				const f = payment.events.get_frm();
				if (f && !f.doc.docstatus) frappe.model.set_value(f.doctype, f.docname, 'po_no', ($(this).val() || '').trim());
			});
		}
		$pay.addClass('ard-has-order');
		$card.find('input').val((frm && frm.doc.po_no) || '');
		layout($pay);
	}

	function patch() {
		const cls = window.erpnext && erpnext.PointOfSale && erpnext.PointOfSale.Payment;
		if (!cls) return false;
		if (cls.prototype.__ardmore_order_no) return true;

		const std_checkout = cls.prototype.checkout;
		cls.prototype.checkout = function () {
			const out = std_checkout.apply(this, arguments);
			try { render(this); } catch (e) { console.warn('Ardmore POS order number:', e); }
			return out;
		};

		const std_toggle = cls.prototype.toggle_component;
		cls.prototype.toggle_component = function (show) {
			const out = std_toggle.apply(this, arguments);
			if (!show && this.$component) {
				try { reset(this.$component); } catch (e) { console.warn('Ardmore POS order number:', e); }
			}
			return out;
		};

		cls.prototype.__ardmore_order_no = true;
		return true;
	}

	$(window).on('resize.ard_order_no', frappe.utils.debounce(() => {
		const $pay = $('.point-of-sale-app > .payment-container.ard-has-order');
		if ($pay.length && $pay.is(':visible')) layout($pay);
	}, 150));

	if (!patch()) {
		let tries = 0;
		const timer = setInterval(() => {
			tries = tries + 1;
			if (patch() || tries > 30) clearInterval(timer);
		}, 1000);
	}
})();
