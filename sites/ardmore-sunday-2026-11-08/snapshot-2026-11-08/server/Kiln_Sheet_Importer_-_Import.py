if doc.imported:
    frappe.throw('This kiln sheet has already been imported. Create a new Kiln Sheet Importer to import again.')

if not doc.attach_excel_file:
    frappe.throw('Please attach the kiln sheet (.xlsx or .txt).')

if doc.sheet_data:
        rows = json.loads(doc.sheet_data)
else:
    fl = (doc.attach_excel_file or '').lower()
    if fl.endswith('.xlsx') or fl.endswith('.xlsm'):
        frappe.throw('The file is still being read - wait a second after attaching, then Save again.')
    fname = frappe.db.get_value('File', {'file_url': doc.attach_excel_file}, 'name')
    if not fname:
        frappe.throw('Could not find the uploaded file.')
    content = frappe.get_doc('File', fname).get_content()
    try:
        content = content.decode('utf-8', 'ignore')
    except Exception:
        content = content
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    rows = [ln.split('\t') for ln in content.split('\n')]

# Two-row header: row 1 = group labels, row 2 = column names, DATA FROM ROW 3.
if not rows or len(rows) < 3:
    frappe.throw('No data rows found. Expected headers on rows 1-2 and data from row 3.')

data_rows = rows[2:]

# Corrections run: update what already exists, create nothing, move no stock,
# and treat a blank cell as "leave this alone" rather than "clear it".
update_only = 1 if doc.get('update_only') else 0

tmpl = frappe.db.get_value('Sales Taxes and Charges Template', {'company': doc.company, 'is_default': 1}, 'name')
if not tmpl:
    frappe.throw('No default Sales Taxes and Charges Template set for ' + doc.company + '. Set one before importing.')
vat_rate = frappe.db.get_value('Sales Taxes and Charges', {'parent': tmpl, 'parenttype': 'Sales Taxes and Charges Template'}, 'rate')
if not vat_rate:
    frappe.throw('The default tax template (' + tmpl + ') has no tax rate.')
vat_divisor = 1 + (float(vat_rate) / 100.0)

retail_list = doc.custom_retail_price_list
whole_list = doc.custom_wholesale_price_list
if not retail_list or not whole_list:
    frappe.throw('Select both the Retail and Wholesale price lists to update.')

if not doc.default_warehouse:
    frappe.throw('Select a Default Warehouse before importing.')

# Kiln sheets import into Main Distribution only (Russell, 1 Nov 2026).
# Stores only ever receive stock by Stock Transfer.
wh_company = frappe.db.get_value('Warehouse', doc.default_warehouse, 'company')
if wh_company != doc.company or doc.default_warehouse != 'Main Distribution - A':
    frappe.throw('Kiln sheets import into Main Distribution only. Set Default Warehouse to Main Distribution.')

type_opts = frappe.db.get_value('Custom Field', {'dt': 'Item', 'fieldname': 'custom_type'}, 'options') or ''
allowed_types = []
for t in type_opts.split('\n'):
    tt = t.strip()
    if tt:
        allowed_types.append(tt)

size_opts = frappe.db.get_value('Custom Field', {'dt': 'Item', 'fieldname': 'custom_size'}, 'options') or ''
size_map = {}
for s in size_opts.split('\n'):
    ss = s.strip()
    if ss:
        size_map[''.join(ss.split()).lower()] = ss


def norm_size(v):
    return ''.join(str(v or '').split()).lower()


C_CODE = 0
C_DESC = 1
C_TYPE = 2
C_WHOLE_INCL = 6
C_RETAIL_INCL = 8
C_SCULPTOR = 10
C_THROWER = 11
C_PAINTER = 12
C_HEIGHT = 13
C_LENGTH = 14
C_WIDTH = 15
C_SIZE = 16
C_MANUF_DATE = 17
C_THROWER_AMT = 33
C_SCULPTOR_AMT = 35
C_PAINTER_AMT = 37
C_OVERHEAD = 39
C_ITEM_COST = 40
C_QTY = 26


def cell(row, idx):
    if idx < len(row):
        return row[idx]
    return None


def is_blank(v):
    if v is None:
        return True
    return str(v).strip() == ''


def setv(item, fieldname, raw, value, skip_blank):
    """Write a field unless this is a corrections run and the cell was empty.

    A blank cell in an Update Only sheet means "I am not touching this", never
    "set it to nothing" - otherwise a cut-down correction sheet silently wipes
    dimensions, rates and sizes that were perfectly good.

    NOTE: the emptiness test is inlined on purpose. A function defined in a
    Server Script cannot call another function defined alongside it - it only
    sees globals, and those defs live in locals."""
    if skip_blank and (raw is None or str(raw).strip() == ''):
        return
    item.set(fieldname, value)


def clean_num(v):
    if v is None:
        return 0.0
    s = str(v).strip()
    if s == '' or s == '-':
        return 0.0
    s = s.replace('R', '').replace('r', '').replace(' ', '').replace(u'\xa0', '').replace(',', '.')
    try:
        return float(s)
    except Exception:
        return 0.0


def parse_date(v):
    if not v:
        return None
    s = str(v).strip()
    if not s:
        return None
    if len(s) >= 10 and s[4] == '-' and s[7] == '-':
        return s[:10]
    s = s.replace('-', '/').replace('.', '/')
    parts = s.split('/')
    if len(parts) == 3 and len(parts[0]) <= 2:
        yy = parts[2]
        if len(yy) == 2:
            yy = '20' + yy
        return yy + '-' + parts[1].zfill(2) + '-' + parts[0].zfill(2)
    return None


def link_artist(nm):
    if nm is None:
        return [None, None]
    s = str(nm).strip()
    if s == '':
        return [None, None]
    m = frappe.db.get_value('Manufacturer', {'full_name': s}, 'name')
    if not m:
        m = frappe.db.get_value('Manufacturer', {'short_name': s}, 'name')
    if m:
        return [m, None]
    return [None, s]


def upsert_price(code, plist, rate):
    if not rate or rate <= 0:
        return
    ex = frappe.db.get_value('Item Price', {'item_code': code, 'price_list': plist}, 'name')
    if ex:
        frappe.db.set_value('Item Price', ex, 'price_list_rate', rate)
        # Stamp it so the nightly Sage price sync will not overwrite it.
        frappe.db.set_value('Item Price', ex, 'custom_from_sheet', 1)
    else:
        ip = frappe.new_doc('Item Price')
        ip.item_code = code
        ip.price_list = plist
        ip.price_list_rate = rate
        ip.selling = 1
        ip.custom_from_sheet = 1
        ip.insert(ignore_permissions=True)


log = []
created = 0
updated = 0
skipped = 0
errors = 0
issues = []
seen_codes = {}
not_found = []
sage_category_moves = []
missing_artists = []
local_qty_rows = []
qty_skipped = []

for ridx in range(len(data_rows)):
    row = data_rows[ridx]
    row_num = ridx + 3
    code = ''
    try:
        raw_code = cell(row, C_CODE)
        code = str(raw_code or '').strip()

        # A stray or truncated code is a data fault, not a silent skip.
        if len(code) < 2:
            skipped = skipped + 1
            if not is_blank(raw_code):
                issues.append({'row': row_num, 'code': code, 'reason': 'Item code is too short to be valid'})
            continue

        if code in seen_codes:
            issues.append({
                'row': row_num,
                'code': code,
                'reason': 'Duplicate of row ' + str(seen_codes[code]) + ' in this sheet - the later row wins',
            })
        seen_codes[code] = row_num

        raw_desc = cell(row, C_DESC)
        desc = str(raw_desc or code).strip()

        raw_retail = cell(row, C_RETAIL_INCL)
        raw_whole = cell(row, C_WHOLE_INCL)
        retail_incl = clean_num(raw_retail)
        whole_incl = clean_num(raw_whole)
        retail_excl = round(retail_incl / vat_divisor, 2) if retail_incl else 0
        whole_excl = round(whole_incl / vat_divisor, 2) if whole_incl else 0
        retail_blank = is_blank(raw_retail)
        whole_blank = is_blank(raw_whole)

        sc = link_artist(cell(row, C_SCULPTOR))
        th = link_artist(cell(row, C_THROWER))
        pa = link_artist(cell(row, C_PAINTER))
        for miss in [sc[1], th[1], pa[1]]:
            if miss:
                if miss not in missing_artists:
                    missing_artists.append(miss)
                issues.append({'row': row_num, 'code': code, 'reason': "Artist '" + miss + "' is not set up as a Manufacturer"})

        exists = frappe.db.exists('Item', code)
        is_new = not exists

        if is_new and update_only:
            not_found.append(code)
            issues.append({'row': row_num, 'code': code, 'reason': 'NOT UPDATED - this item does not exist yet'})
            skipped = skipped + 1
            continue

        if is_new:
            item = frappe.new_doc('Item')
            item.item_code = code
            item.item_group = 'All Item Groups'
            item.stock_uom = 'Each'
            item.is_stock_item = 1
        else:
            item = frappe.get_doc('Item', code)

        raw_qty = cell(row, C_QTY)
        qty_val = clean_num(raw_qty)
        raw_cost = cell(row, C_ITEM_COST)
        item_cost = clean_num(raw_cost)

        # Ceramics: there is only ever ONE piece of an item (Russell, 2026-10-16). A
        # re-import updates the details but NEVER adds quantity; stock is corrected by
        # a transfer or an adjustment. (Home/Fashion sheets still add on re-import.)
        if (not is_new) and qty_val != 0:
            qty_skipped.append(code + ' (qty ' + str(qty_val) + ') - ceramics: one piece only, quantity is never added on a re-import')
            issues.append({'row': row_num, 'code': code, 'reason': 'Quantity NOT added - a ceramics piece exists once. Fix stock by transfer or adjustment'})

        # Moving an item between categories moves which Sage company its sales
        # post to. If Sage already knows this item we cannot silently re-point it.
        if (not is_new) and item.get('custom_category') and item.get('custom_category') != doc.category:
            if item.get('custom_sage_selection_id'):
                move_note = code + ': ' + str(item.get('custom_category')) + ' -> ' + str(doc.category)
                if move_note not in sage_category_moves:
                    sage_category_moves.append(move_note)

        setv(item, 'item_name', raw_desc, desc, update_only)
        item.custom_category = doc.category
        item.custom_from_import = 1
        setv(item, 'custom_opening_qty', raw_qty, qty_val, update_only)

        raw_type = cell(row, C_TYPE)
        tval = str(raw_type or '').strip()
        if tval:
            if tval in allowed_types:
                item.custom_type = tval
            else:
                issues.append({'row': row_num, 'code': code, 'reason': "Type '" + tval + "' is not on the allowed list"})

        raw_size = cell(row, C_SIZE)
        if not is_blank(raw_size):
            msize = size_map.get(norm_size(raw_size))
            if msize:
                item.custom_size = msize
            else:
                issues.append({'row': row_num, 'code': code, 'reason': "Size '" + str(raw_size).strip() + "' is not on the allowed list"})

        setv(item, 'custom_item_height', cell(row, C_HEIGHT), int(clean_num(cell(row, C_HEIGHT))), update_only)
        setv(item, 'custom_item_length', cell(row, C_LENGTH), int(clean_num(cell(row, C_LENGTH))), update_only)
        setv(item, 'custom_item_width', cell(row, C_WIDTH), int(clean_num(cell(row, C_WIDTH))), update_only)

        if is_new:
            item.custom_retail_price_incl_vat = retail_incl
            item.custom_retail_price_excl_vat = retail_excl
            item.custom_wholesale_price_incl_vat = whole_incl
            item.custom_wholesesale_price_ex_vat = whole_excl
        elif (retail_incl and round(float(item.get('custom_retail_price_incl_vat') or 0), 2) != round(retail_incl, 2)) or (whole_incl and round(float(item.get('custom_wholesale_price_incl_vat') or 0), 2) != round(whole_incl, 2)):
            issues.append({'row': row_num, 'code': code, 'reason': 'Price NOT changed - this item already exists, and Sage owns its price. Change the price in Sage; it reaches the tills within minutes'})

        setv(item, 'custom_item_cost', raw_cost, item_cost, update_only)
        if item_cost > 0:
            item.valuation_rate = item_cost
        setv(item, 'custom_overhead', cell(row, C_OVERHEAD), clean_num(cell(row, C_OVERHEAD)), update_only)
        setv(item, 'custom_sculptor_rate', cell(row, C_SCULPTOR_AMT), clean_num(cell(row, C_SCULPTOR_AMT)), update_only)
        setv(item, 'custom_thrower_rate', cell(row, C_THROWER_AMT), clean_num(cell(row, C_THROWER_AMT)), update_only)
        setv(item, 'custom_painter_rate', cell(row, C_PAINTER_AMT), clean_num(cell(row, C_PAINTER_AMT)), update_only)

        md = parse_date(cell(row, C_MANUF_DATE))
        if md:
            item.custom_created_date = md

        # Artists: only overwrite when the sheet actually names one, otherwise a
        # corrections sheet would strip the sculptor/thrower/painter off an item.
        if sc[0] or not update_only:
            item.custom_sculptor_c = sc[0]
        if th[0] or not update_only:
            item.custom_thrower_c = th[0]
        if pa[0] or not update_only:
            item.custom_painter_c = pa[0]

        found_def = False
        for d in (item.get('item_defaults') or []):
            if d.company == doc.company:
                d.default_warehouse = doc.default_warehouse
                found_def = True
        if not found_def:
            item.append('item_defaults', {'company': doc.company, 'default_warehouse': doc.default_warehouse})

        item.save(ignore_permissions=True)

        # A corrections run is exactly when a wrong price needs fixing, so prices
        # are written on update too - not only for brand-new items.
        # Sage owns the price once the item exists there (Russell, 2026-10-16): the sheet
        # prices an item only when it CREATES it. For an existing item the sheet cannot
        # reach Sage, and the item sync would copy Sage's price straight back.
        if is_new:
            upsert_price(code, retail_list, retail_incl)
            upsert_price(code, whole_list, whole_incl)

        if is_new:
            created = created + 1
            log.append('Row ' + str(row_num) + ': ' + code + ' created.')
        else:
            updated = updated + 1
            log.append('Row ' + str(row_num) + ': ' + code + ' updated.')

    except Exception as e:
        errors = errors + 1
        log.append('Row ' + str(row_num) + ': ERROR - ' + str(e))
        issues.append({'row': row_num, 'code': code, 'reason': str(e)[:250]})

stock_added = 0
stock_entry_name = None
stock_failed = []


# company/warehouse are passed in: a function defined inside a Server Script cannot
# see script-level names like 'doc' (they live in locals, not globals).
def make_receipt(lines, se_company, se_warehouse):
    se = frappe.new_doc('Stock Entry')
    se.company = se_company
    se.stock_entry_type = 'Material Receipt'
    se.purpose = 'Material Receipt'
    for r in lines:
        line = {'item_code': r['code'], 'qty': r['qty'], 't_warehouse': se_warehouse}
        if r['rate'] and r['rate'] > 0:
            line['basic_rate'] = r['rate']
        else:
            line['allow_zero_valuation_rate'] = 1
        se.append('items', line)
    se.insert(ignore_permissions=True)
    se.submit()
    return se.name


# No frappe.db.commit() / rollback() below - the Server Script sandbox does not expose
# them (AttributeError: module has no attribute 'rollback'). The request commits at the end.
if local_qty_rows:
    try:
        stock_entry_name = make_receipt(local_qty_rows, doc.company, doc.default_warehouse)
        stock_added = len(local_qty_rows)
        for r in local_qty_rows:
            frappe.db.set_value('Item', r['code'], 'custom_qty_pending_sage', 1)
    except Exception as e_se:
        log.append('')
        log.append('Batch stock receipt failed (' + str(e_se)[:150] + ') - retrying one item at a time.')
        for r in local_qty_rows:
            try:
                nm = make_receipt([r], doc.company, doc.default_warehouse)
                if not stock_entry_name:
                    stock_entry_name = nm
                stock_added = stock_added + 1
                frappe.db.set_value('Item', r['code'], 'custom_qty_pending_sage', 1)
            except Exception as e_one:
                stock_failed.append(r['code'] + ' (qty ' + str(r['qty']) + ') - ' + str(e_one)[:120])
                issues.append({'row': '', 'code': r['code'], 'reason': 'Stock could not be added: ' + str(e_one)[:150]})

mode = 'UPDATE ONLY' if update_only else 'FULL IMPORT'
summary = mode + ' | Created: ' + str(created) + ' | Updated: ' + str(updated) + ' | Skipped: ' + str(skipped) + ' | Errors: ' + str(errors)

if update_only:
    log.append('')
    log.append('UPDATE ONLY was ticked: no items were created and no stock was added.')
    log.append('Blank cells in the sheet were left as they were.')

if not_found:
    log.append('')
    log.append('NOT UPDATED - these are not in the system yet (' + str(len(not_found)) + '):')
    for c in not_found:
        log.append('  - ' + c)

if missing_artists:
    log.append('')
    log.append('ARTISTS TO ADD (Manufacturers tile, then re-import):')
    for a in missing_artists:
        log.append("  - '" + a + "' not found")

if sage_category_moves:
    log.append('')
    log.append('*** CATEGORY CHANGED ON ITEMS SAGE ALREADY KNOWS (' + str(len(sage_category_moves)) + ') ***')
    log.append('The category decides which Sage company a sale is posted to. These items')
    log.append('have been moved, and their next sale will look for a Sage record under the')
    log.append('NEW company. Check them in Sage before selling them.')
    for m in sage_category_moves:
        log.append('  - ' + m)

if issues:
    log.append('')
    log.append('ROWS WITH PROBLEMS (' + str(len(issues)) + ') - use Download Issues for the full list:')
    for p in issues[:40]:
        log.append('  - Row ' + str(p['row']) + ' ' + str(p['code']) + ': ' + p['reason'])

if stock_added:
    log.append('')
    log.append('STOCK ADDED IN ERPNEXT (' + str(stock_added) + ' item(s), Stock Entry ' + str(stock_entry_name) + ')')
    log.append('These items already existed, so their quantity could not be sent to Sage.')
    log.append('It was ADDED to ' + str(doc.default_warehouse) + ' here instead, and each item is')
    log.append('flagged so the Sage stock sync will not overwrite it. Once Sage holds the')
    log.append('correct quantity, untick "Qty Added Locally" on the item.')
    log.append('IMPORTANT: do not import this sheet again - the quantity would be added twice.')
    for r in local_qty_rows:
        log.append('  - ' + r['code'] + ' + ' + str(r['qty']))

if qty_skipped:
    log.append('')
    log.append('QUANTITY SKIPPED (nothing was added for these):')
    for q in qty_skipped:
        log.append('  - ' + q)

if stock_failed:
    log.append('')
    log.append('STOCK COULD NOT BE ADDED for these - set them in Sage instead:')
    for q in stock_failed:
        log.append('  - ' + q)


def csv_cell(v):
    s = str(v if v is not None else '')
    return '"' + s.replace('"', '""') + '"'


if issues:
    csv_lines = ['"Row","Item Code","Problem"']
    for p in issues:
        csv_lines.append(csv_cell(p['row']) + ',' + csv_cell(p['code']) + ',' + csv_cell(p['reason']))
    doc.issues_csv = '\n'.join(csv_lines)
else:
    doc.issues_csv = ''

doc.imported = 1
doc.import_log = summary + '\n\n' + '\n'.join(log)

msg = 'Kiln sheet import complete.<br>' + summary
if update_only:
    msg = msg + '<br><br><b>Update Only:</b> nothing was created and no stock was added.'
if not_found:
    msg = msg + '<br><br><b>' + str(len(not_found)) + ' item(s) in your sheet are not in the system yet</b> and were not created.'
if sage_category_moves:
    msg = msg + ('<br><br><b style="color:#b3261e">WARNING: ' + str(len(sage_category_moves))
                 + ' item(s) that Sage already knows have been moved to a different category.</b>'
                 + '<br>Their next sale will post to a different Sage company. Check them in Sage.')
if stock_added:
    msg = msg + '<br><br><b>' + str(stock_added) + ' existing item(s) had their sheet quantity ADDED into ERPNext</b> (Stock Entry ' + str(stock_entry_name) + ').<br>Do not import this sheet again or the stock will be added twice.'
if issues:
    msg = msg + '<br><br><b>' + str(len(issues)) + ' row(s) had a problem.</b> Use <b>Download Issues</b> for the list.'
frappe.msgprint(msg)
