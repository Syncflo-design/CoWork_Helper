// =============================================================
// Ardmore POS - item tiles: full name + SKU / item ID row, price at foot (v4, 2026-11-02)
// Client Script on POS Invoice (Form) - evaluated inside the POS page
// (loaded by "POS Till Scripts Loader" in Sales Invoice mode).
// -------------------------------------------------------------
// Standard tiles cut the item name at 18 characters in the POS code itself
// (frappe.ellipsis), so "Fabric - Cherry Brown Mustard Yellow" and its
// sister colours all read "Fabric - Cherry Br...". Cheri, 24 Sept 2026:
// staff cannot tell items apart and should not rely on the image.
//
// Each tile now shows:
//   1. the FULL item name, wrapped over up to three lines
//   2. one small row: SKU (item code) on the left, 8-digit item ID on the right
//   3. the price, pinned to the bottom edge of the tile so prices line up
//      across a row whatever the length of the names above them
// The full name stays on hover (standard title attribute).
//
// The 8-digit item ID is printed by nest_help (.nh-pos-code) a moment after
// the tile renders; this script moves it up into the SKU row when it arrives.
//
// Grid view only. The list view (Hide Images) already shows the full name.
// The POS re-renders its tiles on every search, so this keeps watching.
// v2: SKU and item ID share one row, smaller text (Russell, 2026-09-29).
// v3: price pinned to the foot of the tile (Russell, 2026-09-29).
// v4: available-qty pill pale green whenever there is stock (Russell, 2026-11-02). The
//     POS paints 1-10 units orange, which on one-off Ardmore pieces read as "no stock".
//     Zero stays red.
// =============================================================
(function () {
	'use strict';
	if (window.__ardmore_pos_tile_names_v4) return;
	window.__ardmore_pos_tile_names_v4 = true;

	const TILE = '.point-of-sale-app > .items-selector > .items-container.show-item-image > .item-wrapper';
	const GRID = '.point-of-sale-app .items-container.show-item-image > .item-wrapper[data-item-code]';
	const QTY_PILL = '.point-of-sale-app .items-container .item-qty-pill > .indicator-pill';

	function ensure_style() {
		if (document.getElementById('ard-pos-tile-style')) return;
		const st = document.createElement('style');
		st.id = 'ard-pos-tile-style';
		st.textContent = [
			TILE + ' { display: flex; flex-direction: column; }',
			TILE + ' > .item-detail { flex: 1 1 auto; height: auto; min-height: 3.5rem; justify-content: flex-start; padding-top: 6px; padding-bottom: 8px; }',
			TILE + ' > .item-detail > .item-name { display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 3; white-space: normal; overflow: hidden; line-height: 1.25; overflow-wrap: anywhere; }',
			TILE + ' > .item-detail > .ard-pos-idrow { display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; column-gap: 8px; margin-top: 3px; font-size: 11px; line-height: 1.3; }',
			TILE + ' > .item-detail > .ard-pos-idrow > .ard-pos-sku { font-weight: 600; letter-spacing: 0.02em; overflow-wrap: anywhere; }',
			TILE + ' > .item-detail > .ard-pos-idrow > .nh-pos-code { font-size: 11px; margin-top: 0; }',
			TILE + ' > .item-detail > .item-rate { margin-top: auto; padding-top: 4px; }',
			QTY_PILL + '.orange, ' + QTY_PILL + '.green { background: #dcfce7; color: #166534; }',
			QTY_PILL + '.orange::before, ' + QTY_PILL + '.green::before { background: #16a34a; }'
		].join('\n');
		document.head.appendChild(st);
	}

	function paint() {
		const tiles = document.querySelectorAll(GRID);
		if (!tiles.length) return;
		ensure_style();

		for (let i = 0; i < tiles.length; i++) {
			const w = tiles[i];
			const detail = w.querySelector('.item-detail');
			if (!detail) continue;

			let row = detail.querySelector('.ard-pos-idrow');

			if (!w.hasAttribute('data-ard-named')) {
				w.setAttribute('data-ard-named', '1');

				const name_el = detail.querySelector('.item-name');
				if (!name_el) continue;

				const full = (w.getAttribute('title') || '').trim();
				if (full) name_el.textContent = full;

				let code = (w.getAttribute('data-item-code') || '').trim();
				if (/%[0-9A-Fa-f]{2}/.test(code)) {
					try { code = decodeURIComponent(code); } catch (e) { /* keep as is */ }
				}

				row = document.createElement('div');
				row.className = 'ard-pos-idrow';
				// Many Ardmore codes ARE the description - do not print it twice.
				if (code && code.toLowerCase() !== full.toLowerCase()) {
					const sku = document.createElement('span');
					sku.className = 'ard-pos-sku';
					sku.textContent = code;
					row.appendChild(sku);
				}
				name_el.insertAdjacentElement('afterend', row);
			}

			// nest_help appends the item ID at the bottom of the tile, sometimes
			// after this script has run. Lift it into the SKU row.
			if (row) {
				const id_el = detail.querySelector(':scope > .nh-pos-code');
				if (id_el) row.appendChild(id_el);
			}
		}
	}

	let timer = null;
	function schedule() {
		if (timer) return;
		timer = setTimeout(function () {
			timer = null;
			try { paint(); } catch (e) { console.warn('Ardmore POS tile names:', e); }
		}, 120);
	}

	schedule();
	new MutationObserver(schedule).observe(document.body, { childList: true, subtree: true });
})();
