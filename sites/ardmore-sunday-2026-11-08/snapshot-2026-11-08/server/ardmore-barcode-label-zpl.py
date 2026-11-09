# Ardmore barcode label ZPL generator - Zebra ZD230, 203 dpi, 2-up.
#
# Encodes Item.custom_pos_barcode (an 8-digit internal number), NOT the item code.
# Item codes are too long and too dirty to print as a scannable barcode; the
# generated number always fits, even on the existing 40x20mm label stock.
#
# Geometry is in millimetres and converted to dots, so the label stock can be
# changed from one place if ADE supply a different size.
#
# Input:  items = [{"item": "FABFCJ", "qty": 3}, ...]
#         (or {"code": "10000001"} to encode a literal value)

DPMM = 8.0

label_w = float(frappe.form_dict.get("label_w") or 40.0)
label_h = float(frappe.form_dict.get("label_h") or 20.0)
edge_gap = float(frappe.form_dict.get("edge_gap") or 1.5)
centre_gap = float(frappe.form_dict.get("centre_gap") or 4.0)
darkness = int(frappe.form_dict.get("darkness") or 15)

raw = frappe.form_dict.get("items")
if not raw:
    frappe.throw("No items supplied.")

try:
    wanted = json.loads(raw)
except Exception:
    wanted = raw


def mm(v):
    return int(round(v * DPMM))


label_dots = mm(label_w)
web_dots = mm(edge_gap + label_w + centre_gap + label_w + edge_gap)
left_x = mm(edge_gap)
right_x = mm(edge_gap + label_w + centre_gap)

# Code128 subset B worst case: start + data + checksum at 11 modules each, stop is 13.
# All-numeric data is narrower still, because the printer switches to subset C.
QUIET_MODULES = 10


def bar_metrics(value):
    modules = 11 * (len(value) + 2) + 13
    for module_dots in [3, 2, 1]:
        width = modules * module_dots
        quiet = QUIET_MODULES * module_dots
        if width + (2 * quiet) <= label_dots:
            return {"module": module_dots, "width": width, "fits": True}
    return {"module": 1, "width": modules, "fits": False}


queue = []
warnings = []

for row in wanted:
    qty = int(row.get("qty") or 0)
    if qty <= 0:
        continue

    item_code = str(row.get("item") or "").strip()
    value = str(row.get("code") or "").strip()
    caption = item_code

    if item_code and not value:
        rec = frappe.db.get_value("Item", item_code, ["custom_pos_barcode", "item_name"], as_dict=True)
        if not rec:
            warnings.append(item_code + " - no such item, skipped")
            continue
        if not rec.custom_pos_barcode:
            warnings.append(item_code + " - has no POS barcode yet, skipped")
            continue
        value = str(rec.custom_pos_barcode)

    if not value:
        continue
    if not caption:
        caption = value

    m = bar_metrics(value)
    if not m["fits"]:
        warnings.append(value + " will not fit a " + str(label_w) + "mm label - skipped")
        continue

    i = 0
    while i < qty:
        queue.append({"value": value, "caption": caption, "metrics": m})
        i = i + 1


def one_label(origin_x, entry):
    m = entry["metrics"]
    bx = origin_x + int((label_dots - m["width"]) / 2)
    cap = entry["caption"]
    if len(cap) > 26:
        cap = cap[:25] + "."
    out = []
    out.append("^BY" + str(m["module"]) + ",2.5," + str(mm(9.0)))
    out.append("^FO" + str(bx) + "," + str(mm(1.5)) + "^BCN," + str(mm(9.0)) + ",N,N,N^FD" + entry["value"] + "^FS")
    out.append("^FO" + str(origin_x) + "," + str(mm(11.2)) + "^FB" + str(label_dots) + ",1,0,C,0^A0N,18,18^FD" + cap + "^FS")
    out.append("^FO" + str(origin_x) + "," + str(mm(14.6)) + "^FB" + str(label_dots) + ",1,0,C,0^A0N,22,22^FD" + entry["value"] + "^FS")
    return "".join(out)


blocks = []
idx = 0
while idx < len(queue):
    left = queue[idx]
    right = queue[idx + 1] if (idx + 1) < len(queue) else None
    body = []
    body.append("^XA")
    body.append("^CI28")
    body.append("^PW" + str(web_dots))
    body.append("^LL" + str(mm(label_h)))
    body.append("^LH0,0")
    body.append("^MTD")
    body.append("^MNY")
    body.append("~SD" + str(darkness))
    body.append(one_label(left_x, left))
    if right:
        body.append(one_label(right_x, right))
    body.append("^XZ")
    blocks.append("".join(body))
    idx = idx + 2

frappe.response["message"] = {
    "zpl": "\n".join(blocks),
    "labels": len(queue),
    "print_rows": len(blocks),
    "blank_half_at_end": (len(queue) % 2) == 1,
    "label_mm": str(label_w) + " x " + str(label_h),
    "web_width_mm": round(web_dots / DPMM, 1),
    "warnings": warnings,
}
