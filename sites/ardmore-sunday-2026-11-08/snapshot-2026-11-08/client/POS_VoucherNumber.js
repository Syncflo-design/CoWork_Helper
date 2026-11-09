// =============================================================
// Ardmore Ceramics — POS Voucher Reference Field
// Version: 1.2 | Frappe v16
// -------------------------------------------------------------
// Injects a "Voucher Reference No." input field into the POS
// payment screen directly below the Voucher payment row.
// The value is saved to the POS Invoice custom field
// `voucher_reference_no` when the order is completed.
// =============================================================

(function () {
    'use strict';

    const FIELD_ID     = 'ardmore-voucher-ref-input';
    const WRAPPER_ID   = 'ardmore-voucher-ref-wrapper';
    const FIELD_NAME   = 'voucher_reference_no';
    const VOUCHER_LABEL = 'Voucher';

    // ---------------------------------------------------------
    // Inject the input field after the Voucher payment row
    // ---------------------------------------------------------
    function injectField() {
        // Don't inject twice
        if (document.getElementById(WRAPPER_ID)) return;

        // Walk all text nodes looking for exactly "Voucher"
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            null
        );

        let targetEl = null;
        let node;
        while ((node = walker.nextNode())) {
            if (node.textContent.trim() === VOUCHER_LABEL) {
                targetEl = node.parentElement;
                break;
            }
        }

        if (!targetEl) return;

        // Walk up to find the payment row container
        let row = targetEl;
        for (let i = 0; i < 5; i++) {
            if (!row.parentElement) break;
            row = row.parentElement;
            // Stop when we find something that looks like a full row
            if (row.offsetWidth > 200) break;
        }

        // Build the input wrapper
        const wrapper = document.createElement('div');
        wrapper.id = WRAPPER_ID;
        wrapper.style.cssText = [
            'padding: 10px 14px 14px',
            'background: #eff6ff',
            'border: 1.5px solid #93c5fd',
            'border-radius: 8px',
            'margin: 6px 0',
        ].join(';');

        wrapper.innerHTML = `
            <label for="${FIELD_ID}" style="
                display: block;
                font-size: 11px;
                font-weight: 700;
                color: #1e40af;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 6px;
            ">🏷️ Voucher Reference No.</label>
            <input
                id="${FIELD_ID}"
                type="text"
                placeholder="Enter voucher number (e.g. VCH-0042)"
                autocomplete="off"
                style="
                    width: 100%;
                    padding: 9px 12px;
                    border: 1.5px solid #3b82f6;
                    border-radius: 6px;
                    font-size: 14px;
                    color: #1f2937;
                    background: #fff;
                    outline: none;
                    box-sizing: border-box;
                "
            >
        `;

        // Hide by default — only show when Voucher has an amount
        wrapper.style.display = 'none';

        // Insert after the Voucher row
        row.insertAdjacentElement('afterend', wrapper);

        // Watch the Voucher amount input for changes
        watchVoucherAmount(row);
    }

    // ---------------------------------------------------------
    // Show/hide the reference field based on Voucher amount
    // ---------------------------------------------------------
    function watchVoucherAmount(voucherRow) {
        // The amount input is inside the Voucher row
        const amountInput = voucherRow.querySelector('input[type="number"], input[type="text"]');

        function checkAmount() {
            const wrapper = document.getElementById(WRAPPER_ID);
            if (!wrapper) return;
            const val = parseFloat(amountInput?.value || 0);
            wrapper.style.display = val > 0 ? 'block' : 'none';
            // Clear ref field if voucher amount is removed
            if (val === 0) {
                const refInput = document.getElementById(FIELD_ID);
                if (refInput) refInput.value = '';
            }
        }

        if (amountInput) {
            amountInput.addEventListener('input', checkAmount);
            amountInput.addEventListener('change', checkAmount);
        }

        // Mark ref input as required visually when shown
        const refInput = document.getElementById(FIELD_ID);
        if (refInput) {
            refInput.setAttribute('required', 'required');
        }

        // Also watch DOM for amount changes via MutationObserver on the row
        const amountObserver = new MutationObserver(checkAmount);
        amountObserver.observe(voucherRow, { childList: true, subtree: true, characterData: true, attributes: true });
    }

    // ---------------------------------------------------------
    // Save the voucher ref to the POS Invoice custom field
    // when the order is submitted
    // ---------------------------------------------------------
    function saveFieldValue() {
        const input = document.getElementById(FIELD_ID);
        if (!input || !input.value.trim()) return;

        const ref = input.value.trim();

        // Try cur_frm (standard Frappe form reference)
        if (window.cur_frm && cur_frm.doc) {
            cur_frm.set_value(FIELD_NAME, ref);
            return;
        }

        // Fallback: store in frappe.flags for pickup by server script
        if (window.frappe) {
            frappe.flags.voucher_reference_no = ref;
        }
    }

    // ---------------------------------------------------------
    // Reset when a new invoice starts
    // ---------------------------------------------------------
    function resetField() {
        const wrapper = document.getElementById(WRAPPER_ID);
        if (wrapper) wrapper.remove();
    }

    // ---------------------------------------------------------
    // Validate — voucher ref is mandatory if voucher amount > 0
    // ---------------------------------------------------------
    function validateVoucherRef() {
        const wrapper = document.getElementById(WRAPPER_ID);
        if (!wrapper || wrapper.style.display === 'none') return true; // not shown = not required

        const refInput = document.getElementById(FIELD_ID);
        const val = refInput ? refInput.value.trim() : '';

        if (!val) {
            // Highlight the field in red
            if (refInput) {
                refInput.style.borderColor = '#dc2626';
                refInput.style.background = '#fee2e2';
                refInput.focus();
            }
            // Show error message
            let errEl = document.getElementById('ardmore-voucher-ref-error');
            if (!errEl) {
                errEl = document.createElement('div');
                errEl.id = 'ardmore-voucher-ref-error';
                errEl.style.cssText = 'color:#dc2626;font-size:12px;font-weight:600;margin-top:6px;';
                errEl.textContent = '⚠️ Voucher Reference No. is required';
                wrapper.appendChild(errEl);
            }
            frappe.show_alert({ message: 'Please enter the Voucher Reference No. before completing the order.', indicator: 'red' }, 5);
            return false;
        }

        // Clear any error state
        if (refInput) {
            refInput.style.borderColor = '#3b82f6';
            refInput.style.background = '#fff';
        }
        const errEl = document.getElementById('ardmore-voucher-ref-error');
        if (errEl) errEl.remove();
        return true;
    }

    // ---------------------------------------------------------
    // Hook into Complete Order button
    // ---------------------------------------------------------
    document.addEventListener('click', function (e) {
        const btn = e.target.closest && e.target.closest('button, .btn, [class*="complete"], [class*="submit-order"]');
        if (!btn) return;
        const txt = btn.textContent || '';
        if (txt.includes('Complete Order') || txt.includes('Submit')) {
            if (!validateVoucherRef()) {
                e.stopImmediatePropagation();
                e.preventDefault();
                return;
            }
            saveFieldValue();
        }
    }, true);

    // ---------------------------------------------------------
    // Watch for route/page changes to reset
    // ---------------------------------------------------------
    if (window.frappe && frappe.router) {
        frappe.router.on('change', resetField);
    }

    // ---------------------------------------------------------
    // MutationObserver — re-inject when POS redraws
    // ---------------------------------------------------------
    const observer = new MutationObserver(function () {
        // If wrapper was removed (new invoice), try to re-inject
        if (!document.getElementById(WRAPPER_ID)) {
            injectField();
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });

    // Initial attempt
    injectField();

})();