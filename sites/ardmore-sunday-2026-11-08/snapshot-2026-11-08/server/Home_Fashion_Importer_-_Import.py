if doc.imported:
    frappe.throw('This file has already been imported. Create a new Home Fashion Importer to import again.')

if not doc.attach_excel_file:
    frappe.throw('Please attach the import sheet (.xlsx or .txt).')

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

if not rows or len(rows) < 2:
    frappe.throw('The sheet is empty or has no data rows (headers on row 1, data from row 2).')

headers = []
for h in rows[0]:
    headers.append(str(h or '').strip())
data_rows = rows[1:]

required = ['item_code', 'item_name']
for r in required:
    if r not in headers:
        frappe.throw('Missing required column: ' + r)

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

# Home sheets import into JHB Atrium Home, Fashion sheets into JHB Atrium Fashion, nowhere
# else (Russell, 1 Nov 2026). Stores only ever receive stock by Stock Transfer.
import_wh = {'Home': 'JHB Atrium Home - A', 'Fashion': 'JHB Atrium Fashion - A'}.get(doc.category)
wh_company = frappe.db.get_value('Warehouse', doc.default_warehouse, 'company')
if not import_wh or wh_company != doc.company or doc.default_warehouse != import_wh:
    frappe.throw('Home sheets import into JHB Atrium Home and Fashion sheets into JHB Atrium Fashion. Set Default Warehouse to it.')


def get_options(fieldname):
    opts = frappe.db.get_value('Custom Field', {'dt': 'Item', 'fieldname': fieldname}, 'options') or ''
    allowed = []
    for o in opts.split('\n'):
        oo = o.strip()
        if oo:
            allowed.append(oo)
    return allowed


opt_sub = get_options('custom_sub_category')
opt_col = get_options('custom_collection')
opt_des = get_options('custom_design')
opt_clr = get_options('custom_colour')
opt_bcl = get_options('custom_base_cloth')
opt_sz = get_options('custom_size')


def hval(headers, row, name):
    if name in headers:
        idx = headers.index(name)
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
    heights, prices and sizes that were perfectly good."""
    # NOTE: the emptiness test is inlined on purpose. A function defined in a
    # Server Script cannot call another function defined alongside it - it only
    # sees globals, and those defs live in locals. Calling is_blank() here fails
    # at runtime with "name 'is_blank' is not defined".
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


def set_select(item, fieldname, value, allowed, label, missing, row_num, code):
    """Match a sheet value to one of the field's allowed options.

    A blank cell is always left alone, so this needs no separate Update Only
    handling. An unmatched value is reported against its row and item code
    rather than as a bare list, so the row can be found and fixed."""
    if value is None:
        return
    v = str(value).strip()
    if v == '':
        return
    nv = ''.join(v.split()).lower()
    matched = None
    for i in range(len(allowed)):
        if ''.join(allowed[i].split()).lower() == nv:
            matched = allowed[i]
            break
    if matched:
        item.set(fieldname, matched)
    else:
        missing.append({'row': row_num, 'code': code, 'reason': label + " value '" + v + "' is not on the allowed list"})


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
missing_values = []
seen_codes = {}
not_found = []
sage_category_moves = []
local_qty_rows = []
qty_skipped = []
uom_rejected = []
values_rejected = []
# Spellings people actually type, mapped to the unit as ERPNext names it.
uom_alias = {
    'm': 'Meter', 'mt': 'Meter', 'mtr': 'Meter', 'mtrs': 'Meter',
    'metre': 'Meter', 'metres': 'Meter', 'meters': 'Meter',
    'ea': 'Each',
}

for ridx in range(len(data_rows)):
    row = data_rows[ridx]
    row_num = ridx + 2
    code = ''
    try:
        raw_code = hval(headers, row, 'item_code')
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

        raw_name = hval(headers, row, 'item_name')
        desc = str(raw_name or code).strip()

        r_excl_raw = hval(headers, row, 'retail_price_excl_vat')
        r_incl_raw = hval(headers, row, 'retail_price_incl_vat')
        w_excl_raw = hval(headers, row, 'wholesale_price_excl_vat')
        w_incl_raw = hval(headers, row, 'wholesale_price_incl_vat')

        r_excl_in = clean_num(r_excl_raw)
        r_incl_in = clean_num(r_incl_raw)
        w_excl_in = clean_num(w_excl_raw)
        w_incl_in = clean_num(w_incl_raw)

        retail_excl = r_excl_in if r_excl_in else (round(r_incl_in / vat_divisor, 2) if r_incl_in else 0)
        retail_incl = r_incl_in if r_incl_in else (round(r_excl_in * vat_divisor, 2) if r_excl_in else 0)
        whole_excl = w_excl_in if w_excl_in else (round(w_incl_in / vat_divisor, 2) if w_incl_in else 0)
        whole_incl = w_incl_in if w_incl_in else (round(w_excl_in * vat_divisor, 2) if w_excl_in else 0)

        retail_blank = is_blank(r_excl_raw) and is_blank(r_incl_raw)
        whole_blank = is_blank(w_excl_raw) and is_blank(w_incl_raw)

        exists = frappe.db.exists('Item', code)
        is_new = not exists

        if is_new and update_only:
            not_found.append(code)
            issues.append({'row': row_num, 'code': code, 'reason': 'NOT UPDATED - this item does not exist yet'})
            skipped = skipped + 1
            continue

        # ---- Unit of measure ------------------------------------------
        # The unit can only be set when an item is CREATED. ERPNext refuses
        # to change it once the item has stock movements, and a new item
        # gets stock within minutes (its opening qty goes to Sage and comes
        # back). So a unit we do not recognise STOPS the row: creating the
        # item as Each would lock the wrong unit in for good.
        sheet_uom = str(hval(headers, row, 'uom') or '').strip()
        uom_name = ''
        if sheet_uom:
            uom_key = ''.join(sheet_uom.split()).lower()
            uom_name = frappe.db.get_value('UOM', uom_alias.get(uom_key) or sheet_uom, 'name') or ''
            if not uom_name:
                if is_new:
                    uom_rejected.append(code + " (unit '" + sheet_uom + "')")
                    issues.append({
                        'row': row_num,
                        'code': code,
                        'reason': "NOT CREATED - unit '" + sheet_uom + "' is not a recognised unit of measure. Use Each or Meter, then import this row again",
                    })
                    skipped = skipped + 1
                    continue
                issues.append({
                    'row': row_num,
                    'code': code,
                    'reason': "Unit '" + sheet_uom + "' is not a recognised unit of measure - ignored",
                })
        if (not is_new) and uom_name:
            cur_uom = str(frappe.db.get_value('Item', code, 'stock_uom') or '')
            if cur_uom.lower() != uom_name.lower():
                issues.append({
                    'row': row_num,
                    'code': code,
                    'reason': "Unit NOT changed - this item already exists as '" + cur_uom + "'. The unit of an existing item cannot be changed by import",
                })

        if is_new:
            item = frappe.new_doc('Item')
            item.item_code = code
            ig = str(hval(headers, row, 'item_group') or '').strip()
            item.item_group = ig if ig else 'All Item Groups'
            item.stock_uom = uom_name if uom_name else 'Each'
            item.is_stock_item = 1
        else:
            item = frappe.get_doc('Item', code)

        # Every value must be on its allowed list. A row with one that is not is NOT
        # imported at all (Russell, 2026-10-01): a half-filled item carrying a wrong
        # default is worse than a row to correct and import again.
        bad = []
        set_select(item, 'custom_sub_category', hval(headers, row, 'sub_category'), opt_sub, 'Sub Category', bad, row_num, code)
        set_select(item, 'custom_collection', hval(headers, row, 'collection'), opt_col, 'Collection', bad, row_num, code)
        set_select(item, 'custom_design', hval(headers, row, 'design'), opt_des, 'Design', bad, row_num, code)
        set_select(item, 'custom_colour', hval(headers, row, 'colour'), opt_clr, 'Colour', bad, row_num, code)
        set_select(item, 'custom_base_cloth', hval(headers, row, 'base_cloth'), opt_bcl, 'Base Cloth', bad, row_num, code)
        set_select(item, 'custom_size', hval(headers, row, 'size'), opt_sz, 'Size', bad, row_num, code)
        if bad:
            for b in bad:
                issues.append({'row': b['row'], 'code': b['code'], 'reason': 'NOT IMPORTED - ' + b['reason']})
            values_rejected.append(code + ' (row ' + str(row_num) + ')')
            skipped = skipped + 1
            continue

        raw_qty = hval(headers, row, 'qty')
        qty_val = clean_num(raw_qty)
        raw_cost = hval(headers, row, 'item_cost')
        item_cost = clean_num(raw_cost)

        # Stock is never touched on a corrections run.
        if not update_only:
            if (not is_new) and qty_val > 0:
                if item.is_stock_item and not item.disabled:
                    local_qty_rows.append({'code': code, 'qty': qty_val, 'rate': item_cost})
                else:
                    reason = 'disabled' if item.disabled else 'not a stock item'
                    qty_skipped.append(code + ' (qty ' + str(qty_val) + ') - ' + reason)
                    issues.append({'row': row_num, 'code': code, 'reason': 'Quantity not added - item is ' + reason})
            elif (not is_new) and qty_val < 0:
                qty_skipped.append(code + ' (qty ' + str(qty_val) + ') - negative quantity ignored')
                issues.append({'row': row_num, 'code': code, 'reason': 'Negative quantity ignored'})

        # Moving an item between categories moves which Sage company its sales
        # post to. If Sage already knows this item we cannot silently re-point it.
        if (not is_new) and item.get('custom_category') and item.get('custom_category') != doc.category:
            if item.get('custom_sage_selection_id'):
                move_note = code + ': ' + str(item.get('custom_category')) + ' -> ' + str(doc.category)
                if move_note not in sage_category_moves:
                    sage_category_moves.append(move_note)

        setv(item, 'item_name', raw_name, desc, update_only)
        item.custom_category = doc.category
        item.custom_from_import = 1
        setv(item, 'custom_opening_qty', raw_qty, qty_val, update_only)

        if is_new:
            item.custom_retail_price_excl_vat = retail_excl
            item.custom_retail_price_incl_vat = retail_incl
            item.custom_wholesesale_price_ex_vat = whole_excl
            item.custom_wholesale_price_incl_vat = whole_incl
        elif (retail_incl and round(float(item.get('custom_retail_price_incl_vat') or 0), 2) != round(retail_incl, 2)) or (whole_incl and round(float(item.get('custom_wholesale_price_incl_vat') or 0), 2) != round(whole_incl, 2)):
            issues.append({'row': row_num, 'code': code, 'reason': 'Price NOT changed - this item already exists, and Sage owns its price. Change the price in Sage; it reaches the tills within minutes'})

        setv(item, 'custom_item_cost', raw_cost, item_cost, update_only)
        if item_cost > 0:
            item.valuation_rate = item_cost

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

if sage_category_moves:
    log.append('')
    log.append('*** CATEGORY CHANGED ON ITEMS SAGE ALREADY KNOWS (' + str(len(sage_category_moves)) + ') ***')
    log.append('The category decides which Sage company a sale is posted to. These items')
    log.append('have been moved, and their next sale will look for a Sage record under the')
    log.append('NEW company. Check them in Sage before selling them.')
    for m in sage_category_moves:
        log.append('  - ' + m)

if uom_rejected:
    log.append('')
    log.append('NOT CREATED - UNIT OF MEASURE NOT RECOGNISED (' + str(len(uom_rejected)) + '):')
    log.append('Correct the uom column (Each or Meter) and import these rows again.')
    for c in uom_rejected:
        log.append('  - ' + c)

if values_rejected:
    log.append('')
    log.append('NOT IMPORTED - VALUE NOT ON THE ALLOWED LIST (' + str(len(values_rejected)) + '):')
    log.append('Correct the sheet to a value from the Allowed values sheet and import these rows again.')
    for c in values_rejected:
        log.append('  - ' + c)

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

msg = 'Home/Fashion import complete.<br>' + summary
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
if uom_rejected:
    msg = msg + ('<br><br><b style="color:#b3261e">' + str(len(uom_rejected))
                 + ' item(s) were NOT created: unit of measure not recognised.</b>'
                 + '<br>Use Each or Meter in the uom column and import those rows again.')
if values_rejected:
    msg = msg + ('<br><br><b style="color:#b3261e">' + str(len(values_rejected))
                 + ' item(s) were NOT imported: a value is not on the allowed list.</b>'
                 + '<br>Correct the sheet and import those rows again.')
if issues:
    msg = msg + '<br><br><b>' + str(len(issues)) + ' row(s) had a problem.</b> Use <b>Download Issues</b> for the list.'
frappe.msgprint(msg)
