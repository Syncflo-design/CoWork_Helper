frappe.ui.form.on('Stock Transfer', {
    refresh(frm) {
        ast_inject_css();
        ast_density_css();
        ast_tighten_css();
        ast_contrast_css();
        frm.$wrapper.addClass('ast-pretty');
        ast_label_sections(frm);
        ast_hide_empty_sections(frm);
        ast_render_banner(frm);
        ast_fix_item_search(frm);
        ast_mark_required(frm);
    },
    company(frm) { ast_mark_required(frm); },
    source_warehouse(frm) { ast_render_banner(frm); ast_fix_item_search(frm); ast_mark_required(frm); },
    target_warehouse(frm) { ast_render_banner(frm); ast_mark_required(frm); },
    workflow_state(frm) { ast_render_banner(frm); ast_mark_required(frm); },
});

function ast_label_sections(frm) {
    const map = [
        ['company', 'Transfer Details'],
        ['source_warehouse', 'Transfer Route'],
        ['items', 'Items to Move'],
    ];
    map.forEach(function (pair) {
        const ctrl = frm.$wrapper.find('[data-fieldname="' + pair[0] + '"]').first();
        if (!ctrl.length) return;
        const section = ctrl.closest('.form-section');
        section.find('.section-head.ast-injected').remove();
        if (section.find('.section-head').length === 0) {
            section.prepend('<div class="section-head ast-injected">' + pair[1] + '</div>');
        }
    });
}

function ast_hide_empty_sections(frm) {
    frm.$wrapper.find('.form-section').each(function () {
        const $s = $(this);
        const visible = $s.find('.frappe-control').filter(function () {
            return $(this).css('display') !== 'none' && !$(this).hasClass('hide-control');
        });
        $s.toggleClass('ast-empty', visible.length === 0);
    });
}

function ast_render_banner(frm) {
    const layout = $(frm.layout.wrapper);
    layout.find('.ast-banner').remove();

    let status = 'Draft', cls = 'draft';
    if (frm.doc.workflow_state) { status = frm.doc.workflow_state; cls = 'submitted'; }
    else if (frm.doc.docstatus === 1) { status = 'Submitted'; cls = 'submitted'; }
    else if (frm.doc.docstatus === 2) { status = 'Cancelled'; cls = 'cancelled'; }

    const clean = function (w) { return w ? frappe.utils.escape_html(w.replace(/ - [^-]+$/, '')) : '—'; };
    const src = frm.doc.source_warehouse;
    const tgt = frm.doc.target_warehouse;
    let sub = 'Move stock between warehouses';
    if (src || tgt) { sub = clean(src) + ' &nbsp;→&nbsp; ' + clean(tgt); }

    const banner = ''
        + '<div class="ast-banner">'
        + '  <div class="ast-banner-left">'
        + '    <div class="ast-mark">'
        + '      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        + '        <path d="M3 8h13M13 4l4 4-4 4"/><path d="M21 16H8M11 20l-4-4 4-4"/>'
        + '      </svg>'
        + '    </div>'
        + '    <div>'
        + '      <p class="ast-title">Stock Transfer</p>'
        + '      <div class="ast-sub">' + sub + '</div>'
        + '    </div>'
        + '  </div>'
        + '  <span class="ast-badge ' + cls + '">' + frappe.utils.escape_html(status) + '</span>'
        + '</div>';
    layout.prepend(banner);
}

function ast_inject_css() {
    if (document.getElementById('ast-stock-transfer-css')) return;
    const css = ''
        + '.ast-pretty .form-page{background:#FBF9F5;padding-top:6px;}'
        + '.ast-banner{display:flex;align-items:center;justify-content:space-between;gap:16px;background:linear-gradient(135deg,#23201C 0%,#332D26 100%);color:#fff;border-radius:14px;padding:18px 22px;margin:6px 0 18px;box-shadow:0 8px 24px rgba(35,32,28,.14);}'
        + '.ast-banner-left{display:flex;align-items:center;gap:14px;min-width:0;}'
        + '.ast-mark{width:38px;height:38px;border-radius:10px;background:#1E6A52;display:flex;align-items:center;justify-content:center;flex:none;}'
        + '.ast-title{font-size:19px;font-weight:600;letter-spacing:.3px;margin:0;line-height:1.2;}'
        + '.ast-sub{font-size:12px;letter-spacing:.5px;text-transform:uppercase;opacity:.72;margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}'
        + '.ast-badge{flex:none;font-size:11px;font-weight:600;letter-spacing:.7px;text-transform:uppercase;padding:6px 13px;border-radius:999px;}'
        + '.ast-badge.draft{background:#F1EADB;color:#8A6D3B;}'
        + '.ast-badge.submitted{background:#E3EFE9;color:#1E6A52;}'
        + '.ast-badge.cancelled{background:#F6E2DF;color:#A23A2E;}'
        + '.ast-pretty .form-section{background:#fff;border:1px solid #ECE6DC;border-radius:12px;padding:8px 20px 14px;margin-bottom:16px;box-shadow:0 1px 2px rgba(35,32,28,.04);}'
        + '.ast-pretty .form-section.ast-empty{display:none !important;}'
        + '.ast-pretty .section-head{color:#23201C;font-weight:600;font-size:12.5px;letter-spacing:.7px;text-transform:uppercase;border-left:3px solid #1E6A52;padding:2px 0 2px 11px;margin:6px 0 12px;}'
        + '.ast-pretty .control-label{color:#6B6256;font-weight:500;font-size:12px;letter-spacing:.2px;}'
        + '.ast-pretty .form-control{border-radius:8px;border-color:#E2DACE;background:#FCFBF8;transition:border-color .15s,box-shadow .15s;}'
        + '.ast-pretty .form-control:focus{border-color:#1E6A52;box-shadow:0 0 0 3px rgba(30,106,82,.13);}'
        + '.ast-pretty [data-fieldname="source_warehouse"],.ast-pretty [data-fieldname="target_warehouse"]{background:#FCFBF8;border:1px solid #ECE6DC;border-radius:12px;padding:14px 16px;}'
        + '.ast-pretty [data-fieldname="source_warehouse"]{border-left:4px solid #B4A88E;}'
        + '.ast-pretty [data-fieldname="target_warehouse"]{border-left:4px solid #1E6A52;}'
        + '.ast-pretty [data-fieldname="html_hria"]{display:flex;align-items:center;justify-content:center;height:100%;}'
        + '.ast-pretty [data-fieldname="html_hria"] svg line{stroke:#1E6A52 !important;}'
        + '.ast-pretty [data-fieldname="html_hria"] svg path{fill:#1E6A52 !important;}'
        + '.ast-pretty .grid-heading-row{background:#F4EFE7 !important;border-radius:8px 8px 0 0;}'
        + '.ast-pretty .grid-heading-row .col{color:#6B6256 !important;font-weight:600;text-transform:uppercase;font-size:11px;letter-spacing:.4px;}'
        + '.ast-pretty .grid-body .grid-row:nth-child(even){background:#FCFBF8;}'
        + '.ast-pretty .grid-body .grid-row:hover{background:#F4EFE7;}'
        + '.ast-pretty .grid-footer .grid-add-row,.ast-pretty .grid-footer .grid-add-multiple-rows{color:#1E6A52 !important;font-weight:500;}'
        + '.ast-pretty .grid-buttons .btn-success{background:#1E6A52;border-color:#1E6A52;}';
    $('<style id="ast-stock-transfer-css">' + css + '</style>').appendTo('head');
}


// ---------------------------------------------------------------------
// Item search fix (Ardmore, 2026-08-12).
//
// The server_scripts app points the Item field at its own query,
// stock_transfer.in_stock_items. That query IGNORES the text the user
// types and returns all ~2,200 in-stock items, so the dropdown only ever
// shows the first few - all ceramics - and typing changes nothing.
// Fabrics were in the list all along, roughly 850 rows down.
//
// We cannot fix the app, so we re-register the query after its script has
// run, using ERPNext's standard item search, which does honour the typed
// text. Trade-off: standard search knows nothing about warehouse stock, so
// an item not held in the source warehouse can be picked. That fails
// safely - the transfer refuses to submit on negative stock - it just
// fails at submit rather than at selection.
//
// Remove this once in_stock_items honours its txt argument.
// ---------------------------------------------------------------------
function ast_fix_item_search(frm) {
    // Deferred: the app registers its own query in its source_warehouse
    // handler. Running on the next tick means ours is always the last one
    // registered, regardless of handler order.
    setTimeout(function () { ast_apply_item_query(frm); }, 0);
}

// Items offered are restricted to what is actually in the source
// warehouse. The app's own query already does that, but it ignores the
// typed text, so we take its list once per warehouse and let ERPNext's
// standard search - which does honour typing - work inside that set.
var ast_stock_cache = { warehouse: null, codes: [], loaded: false };

function ast_apply_item_query(frm) {
    var wh = frm.doc.source_warehouse;

    frm.set_query('item', 'items', function () {
        var filters = { is_stock_item: 1, disabled: 0, has_variants: 0 };
        if (ast_stock_cache.loaded && ast_stock_cache.warehouse === wh) {
            // An empty warehouse must offer nothing, not everything.
            filters.name = ['in', ast_stock_cache.codes.length ? ast_stock_cache.codes : ['__none__']];
        }
        return { query: 'erpnext.controllers.queries.item_query', filters: filters };
    });

    if (!wh || (ast_stock_cache.loaded && ast_stock_cache.warehouse === wh)) return;
    ast_load_stock_codes(wh);
}

function ast_load_stock_codes(wh) {
    // Read the warehouse stock straight from Bin rather than calling the
    // app's in_stock_items: that function does filters.get(...), and
    // frappe.call sends nested objects as a JSON string, so it blows up
    // with "'str' object has no attribute 'get'". Bin is the same source
    // it reads anyway.
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Bin',
            filters: { warehouse: wh, actual_qty: ['>', 0] },
            fields: ['item_code'],
            limit_page_length: 0
        },
        callback: function (r) {
            var rows = (r && r.message) || [];
            var codes = [];
            rows.forEach(function (row) {
                if (row && row.item_code) codes.push(row.item_code);
            });
            ast_stock_cache = { warehouse: wh, codes: codes, loaded: true };
        },
        error: function () {
            // Leave the search unrestricted rather than block the user - the
            // app still refuses an item with no stock when it is picked.
            ast_stock_cache = { warehouse: null, codes: [], loaded: false };
        }
    });
}


// ---------------------------------------------------------------------
// Density and contrast pass.
//
// The form was airy to the point of being hard to scan, and gave no
// signal about what still needed filling in. This tightens the vertical
// rhythm and makes an empty required field obvious - amber, with a bar
// down its left edge - which settles to a quiet green once answered.
//
// Loaded after the base stylesheet so it wins on equal specificity.
// ---------------------------------------------------------------------
function ast_density_css() {
    if (document.getElementById('ast-stock-transfer-density')) return;
    var css = ''
        + '.ast-pretty .form-page{padding-top:2px;}'
        + '.ast-banner{padding:12px 18px;margin:2px 0 12px;border-radius:12px;}'
        + '.ast-banner .ast-title{font-size:17px;}'
        + '.ast-pretty .form-section{padding:4px 16px 8px;margin-bottom:10px;border-radius:10px;}'
        + '.ast-pretty .section-head{margin:6px 0 8px;font-size:11.5px;}'
        + '.ast-pretty .form-column{padding-left:10px;padding-right:10px;}'
        + '.ast-pretty .frappe-control{margin-bottom:8px !important;}'
        + '.ast-pretty .control-label{margin-bottom:2px;font-size:11.5px;letter-spacing:.3px;}'
        + '.ast-pretty .help-box,.ast-pretty .control-description{margin-top:2px;font-size:11px;}'
        + '.ast-pretty .form-control{padding:5px 10px;min-height:30px;height:auto;font-size:13px;}'
        + '.ast-pretty .form-control[readonly],.ast-pretty .like-disabled-input{background:#F4F1EA !important;border-color:#E8E1D5 !important;color:#5C544A;}'
        + '.ast-pretty [data-fieldname="source_warehouse"],.ast-pretty [data-fieldname="target_warehouse"]{padding:10px 12px;border-radius:10px;margin-bottom:0 !important;}'
        + '.ast-pretty [data-fieldname="html_hria"] svg{max-width:200px;}'
        + '.ast-pretty [data-fieldname="html_hria"]{padding:0 !important;}'
        + '.ast-pretty .ast-need .form-control{background:#FFFAF0;border-color:#D9A441;box-shadow:inset 3px 0 0 0 #D9A441;}'
        + '.ast-pretty .ast-need .control-label{color:#8A6D3B;font-weight:600;}'
        + '.ast-pretty .ast-done .form-control{background:#FFFFFF;border-color:#BED8CB;box-shadow:inset 3px 0 0 0 #1E6A52;}'
        + '.ast-pretty .ast-done .control-label{color:#1E6A52;}'
        + '.ast-pretty .grid-heading-row .col{font-size:10.5px;}'
        + '.ast-pretty .grid-body .grid-row{padding-top:2px;padding-bottom:2px;}'
        + '.ast-pretty .grid-empty{padding:10px;font-size:12px;}';
    $('<style id="ast-stock-transfer-density">' + css + '</style>').appendTo('head');
}

function ast_mark_required(frm) {
    ['company', 'source_warehouse', 'target_warehouse'].forEach(function (fn) {
        var f = frm.fields_dict[fn];
        if (!f || !f.$wrapper) return;
        var filled = !!frm.doc[fn];
        f.$wrapper.toggleClass('ast-need', !filled);
        f.$wrapper.toggleClass('ast-done', filled);
    });
}


// A second, tighter pass. Loaded last so it wins.
// The timezone hint under each date is noise on a form this small.
function ast_tighten_css() {
    if (document.getElementById('ast-stock-transfer-tight')) return;
    var css = ''
        + '.ast-pretty .form-section{padding:2px 14px 4px !important;margin-bottom:6px !important;}'
        + '.ast-pretty .section-head{margin:4px 0 6px !important;}'
        + '.ast-pretty .frappe-control{margin-bottom:2px !important;}'
        + '.ast-pretty .form-control{min-height:26px !important;padding:3px 9px !important;}'
        + '.ast-pretty .control-label{margin-bottom:1px !important;}'
        + '.ast-pretty .control-value{padding-top:2px !important;}'
        + '.ast-pretty .help-box,.ast-pretty .control-description{display:none !important;}'
        + '.ast-pretty .form-column{padding-top:0 !important;padding-bottom:0 !important;}'
        + '.ast-pretty .row.form-section-body{margin-bottom:0 !important;}'
        + '.ast-banner{padding:9px 16px !important;margin:0 0 8px !important;}'
        + '.ast-pretty [data-fieldname="source_warehouse"],.ast-pretty [data-fieldname="target_warehouse"]{padding:8px 10px !important;}'
        + '.ast-pretty [data-fieldname="html_hria"] svg{max-width:160px;}';
    $('<style id="ast-stock-transfer-tight">' + css + '</style>').appendTo('head');
}


// Contrast pass. The page was near-white on near-white, so the cards had
// nothing to sit against. Drop the page a few shades, keep the cards
// white, and let the shadow and border do the separating.
function ast_contrast_css() {
    if (document.getElementById('ast-stock-transfer-contrast')) return;
    var css = ''
        + '.ast-pretty .form-page{background:#EDE7DC !important;}'
        + '.ast-pretty .form-section{background:#FFFFFF !important;border:1px solid #DCD3C4 !important;box-shadow:0 1px 3px rgba(35,32,28,.08) !important;}'
        + '.ast-pretty .section-head{color:#23201C !important;border-left-width:4px !important;}'
        + '.ast-pretty .control-label{color:#4A443B !important;}'
        + '.ast-pretty .form-control{border-color:#C9BFAE !important;background:#FFFFFF !important;color:#23201C !important;}'
        + '.ast-pretty .form-control[readonly],.ast-pretty .like-disabled-input{background:#EFEADF !important;border-color:#D5CCBC !important;color:#4A443B !important;}'
        + '.ast-pretty [data-fieldname="source_warehouse"],.ast-pretty [data-fieldname="target_warehouse"]{background:#FBF8F2 !important;border:1px solid #D5CCBC !important;}'
        + '.ast-pretty .grid-heading-row{background:#E4DCCC !important;}'
        + '.ast-pretty .grid-heading-row .col{color:#4A443B !important;}'
        + '.ast-pretty .grid-body .grid-row:nth-child(even){background:#FAF7F1 !important;}'
        + '.ast-pretty .grid-body .grid-row{border-bottom:1px solid #E7E0D3 !important;}'
        // required / answered still need to read loudly against white
        + '.ast-pretty .ast-need .form-control{background:#FFF4DA !important;border-color:#C08A2E !important;box-shadow:inset 3px 0 0 0 #C08A2E !important;}'
        + '.ast-pretty .ast-done .form-control{background:#FFFFFF !important;border-color:#9CC4B0 !important;box-shadow:inset 3px 0 0 0 #1E6A52 !important;}';
    $('<style id="ast-stock-transfer-contrast">' + css + '</style>').appendTo('head');
}
