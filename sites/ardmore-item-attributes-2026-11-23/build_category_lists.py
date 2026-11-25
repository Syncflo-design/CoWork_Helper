"""ERPNext Category fix for Ardmore (ticket 0165, plan approved 23 Nov 2026).

Input: category_groups.json, the check of every Item's ERPNext Category against which Sage
companies hold it (Sage Item Selection rows + stock on hand) and the item's own Sage category.
  A  the category names a Sage company that does not hold the item, and the company that
     does hold it matches what the item is                      -> we change it
  B  a ceramic piece under Home that Sage Ceramics also holds   -> Ceramics (Russell's rule)
  C  the evidence points two ways                               -> Cheri confirms

Output:
  category_changes.json                          what we change (code, from, to, group)
  S:/Ardmore/Ardmore Item Categories to Confirm.xlsx   Cheri's short list

Usage: python -I build_category_lists.py <category_groups.json>
"""

import json
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

HERE = Path(__file__).parent
CHERI_SHEET = Path("//SYNCFLO-DESKTOP/S_Drive_Claude/Ardmore/Ardmore Item Categories to Confirm.xlsx")

KEY_A = "A only one Sage company holds it and the product type matches"
KEY_B = "B ceramic piece under Home, Ceramics Sage has it"
KEY_C = "C needs Cheri"

# Held back: none. CHACK, SCRCDJ and WPBOOK1 were held on 23 Nov for fear of locking their R0.01
# till price, but the Hyde Park and Online tills allow price changes on every item (allow_rate_change),
# so the category does not decide price editing there.
# Will not save (negative Quantity On Hand from Sage), change once Sage stock is corrected:
# CUSHMBAV50, CUSHMBN60, PVTEA.
HOLD = ()

# Group C items checked by name on 23 Nov: the category names a company that does not hold the
# item, and a holding company matches the product. Moved to A.
C_TO_HOME = (
    "CUSHCCAOD", "CUSHFCJ60", "CUSHFRGJ60", "CUSHFSRJ60", "CUSHLLA50", "CUSHLLAV",
    "CUSHLLC50", "CUSHLLCS", "CUSHLLCV", "CUSHLLDV", "CUSHMBDEOD", "CUSHSFPOD",
    "FURPOUFTNMV", "FURPOUFTTSV",
)
C_TO_FASHION = ("SWSKF135", "SWSKFL135", "SWSKJ135")

VALUES_TO_CONFIRM = (
    ("Design", "Sampe Critters", "LAMPCCDBCKCL", "Lampshade CCDelta Barrel, CKCoral Lining, No Piping",
     "Camp Critters? Then Sampe Critters can be removed."),
    ("Colour", "Silver Rippler", "FABHANGRCSRL", "Fabric Hanger - Riverchase Silver Ripple, Linen",
     "Silver Ripple? Then Silver Rippler can be removed."),
    ("Colour", "Silver Rippler", "FABHANGRCSRV", "Fabric Hanger - Riverchase Silver Ripple, Velvet",
     "Silver Ripple? Then Silver Rippler can be removed."),
    ("Colour", "Rippler", "FABHANGFSRV", "Fabric Hanger- Feather Silver Ripple, Velvet",
     "Silver Ripple? Then Rippler can be removed."),
)


def suggestion(r):
    """Our suggestion for an item Cheri confirms, in her words."""
    cat, sage, code = r["category"], r["sage"], r["code"]
    group = (r.get("item_group") or "").lower()
    held = " and ".join("Sage " + s for s in sage) + (" do" if len(sage) > 1 else " does")
    if (r.get("name") or "").strip().lower() == "q":
        return "The item name is just 'q'. What is this item?"
    if code.startswith("zzz_"):
        return "Adjustment item, held only by Sage Fashion. Fashion?"
    if cat == "Fashion":
        return "Fashion product, but Sage Fashion does not hold it (" + held + "). Keep as Fashion?"
    if cat == "Home":
        return "Home product, but Sage Home does not hold it (" + held + "). Keep as Home?"
    if "ceramic" in group or group in ("coin dishes", "jugs medium", "riders medium", "small gift items"):
        return "Ceramic piece, but Sage Ceramics does not hold it (" + held + "). Keep as Ceramics?"
    if "scar" in group or "wrap" in group:
        return "Fashion product, held only by " + held[:-5] + ". Fashion or Home?"
    if sage == ["Home"]:
        return "Held only by Sage Home. Home?"
    return "Sage Ceramics does not hold it (" + held + "). Which category?"


def main(groups_path):
    groups = json.loads(Path(groups_path).read_text(encoding="utf-8"))
    a, b, c = groups[KEY_A], groups[KEY_B], groups[KEY_C]

    changes, held, cheri = [], [], []
    for r in a:
        (held if r["code"] in HOLD else changes).append(
            {"code": r["code"], "from": r["category"], "to": r["sage"][0], "group": "A"}
        )
    for r in b:
        changes.append({"code": r["code"], "from": r["category"], "to": "Ceramics", "group": "B"})
    for r in c:
        if r["code"] in C_TO_HOME:
            changes.append({"code": r["code"], "from": r["category"], "to": "Home", "group": "A"})
        elif r["code"] in C_TO_FASHION:
            changes.append({"code": r["code"], "from": r["category"], "to": "Fashion", "group": "A"})
        else:
            cheri.append(r)

    missing = set(C_TO_HOME + C_TO_FASHION) - {r["code"] for r in c}
    assert not missing, f"not in group C: {missing}"
    assert len(held) == len(HOLD), held

    (HERE / "category_changes.json").write_text(json.dumps(changes, indent=1), encoding="utf-8")

    wb = Workbook()
    ws = wb.active
    ws.title = "Please confirm"
    ws.append(["Item code", "Item name", "ERPNext Category now", "Held in Sage by", "Our suggestion", "Your answer"])
    for r in sorted(cheri, key=lambda x: (x["category"], x["code"])):
        ws.append([r["code"], r["name"], r["category"], ", ".join(r["sage"]), suggestion(r), None])
    head = Font(bold=True, color="FFFFFF")
    fill = PatternFill("solid", fgColor="4A5D4F")
    for cell in ws[1]:
        cell.font, cell.fill = head, fill
    for col, width in zip("ABCDEF", (24, 48, 20, 24, 70, 24)):
        ws.column_dimensions[col].width = width
    for row in ws.iter_rows(min_row=2):
        row[4].alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "A2"

    # List values we could not be sure of (checked on Live 23 Nov). The certain doubles
    # (Camp Criters, Bushbandits, Limelight, Butterdust, Refelctions) are merged by us.
    vs = wb.create_sheet("Values to confirm")
    vs.append(["List", "Value", "Item code", "Item name", "Our suggestion", "Your answer"])
    for row in VALUES_TO_CONFIRM:
        vs.append(list(row) + [None])
    for cell in vs[1]:
        cell.font, cell.fill = head, fill
    for col, width in zip("ABCDEF", (12, 18, 18, 52, 48, 24)):
        vs.column_dimensions[col].width = width
    vs.freeze_panes = "A2"
    wb.save(CHERI_SHEET)

    by = {}
    for ch in changes:
        k = (ch["group"], ch["to"])
        by[k] = by.get(k, 0) + 1
    print("changes:", len(changes), dict(sorted(by.items())))
    print("held:", [h["code"] for h in held])
    print("cheri:", len(cheri), "->", CHERI_SHEET)


if __name__ == "__main__":
    main(sys.argv[1])
