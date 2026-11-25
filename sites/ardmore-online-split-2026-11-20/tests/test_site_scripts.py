"""Break tests for the Ardmore online-split site scripts, run on the real script text with fake_frappe.

    python -I tests/test_site_scripts.py      (from the ardmore-online-split folder)

Each test prints PASS/FAIL. The key ones run the 8 Nov Live text (base/) and the new text (patched/) on the
same shop sale and require identical Sage traffic: the shop tills must not change."""

import copy
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from fake_frappe import DB, Doc, Frappe, FrappeThrow, Row, run  # noqa: E402

BASE = os.path.join(ROOT, "base")
NEW = os.path.join(ROOT, "patched")
SRV = os.path.join(ROOT, "server")


def tables(split=1):
    t = {
        "POS Profile": {
            "Hyde Park": {"company": "Ardmore", "warehouse": "HDSQ - A", "custom_sage_entity": "Home",
                "custom_sage_cash_customer_id": "4150404", "custom_sage_cash_customer_name": "Store Sales (Credit Card)",
                "custom_sage_sales_rep_id": 555, "custom_split_by_item_company": 0, "custom_online_store": 0},
            "Online": {"company": "Ardmore", "warehouse": "Online Store - A", "custom_sage_entity": "Home",
                "custom_sage_cash_customer_id": "4171600", "custom_sage_cash_customer_name": "Online Sales",
                "custom_sage_sales_rep_id": 622508, "custom_split_by_item_company": split, "custom_online_store": 1,
                "custom_also_sell_from": "JHB Atrium Home - A\nJHB Atrium Fashion - A\nJHB Atrium Ceramics - A\nMain Distribution - A",
                "selling_price_list": "Home - Retail Price", "taxes_and_charges": "South Africa Tax - A",
                "custom_zero_vat_template": "South Africa Zero Rated - A", "currency": "ZAR", "disabled": 0, "letter_head": "LH"},
        },
        "POS Profile User": {"u1": {"parent": "Online", "user": "online@ardmore-design.com"}},
        "POS Payment Method": {
            "p1": {"parent": "Online", "mode_of_payment": "Credit Card", "default": 1},
            "p2": {"parent": "Online", "mode_of_payment": "Shopify", "default": 0},
        },
        "Warehouse": {
            "HDSQ - A": {"custom_sage_entity": "Home"}, "Online Store - A": {"custom_sage_entity": "Home"},
            "JHB Atrium Home - A": {"custom_sage_entity": "Home"}, "JHB Atrium Fashion - A": {"custom_sage_entity": "Fashion"},
            "JHB Atrium Ceramics - A": {"custom_sage_entity": "Ceramics"}, "Main Distribution - A": {"custom_sage_entity": "Ceramics"},
        },
        "Item": {
            "HOM1": {"custom_category": "Home", "is_stock_item": 1, "item_name": "Cushion"},
            "FAS1": {"custom_category": "Fashion", "is_stock_item": 1, "item_name": "Scarf"},
            "CER1": {"custom_category": "Ceramics", "is_stock_item": 1, "item_name": "Bowl"},
            "NOCAT": {"custom_category": "", "is_stock_item": 1, "item_name": "Mystery"},
        },
        "Sage Item Selection": {},
        "Company Sage Integration": {
            "Home": {"company": "Home", "username": "u", "tax_id": 2704020, "custom_sage_zero_tax_id": 690655,
                "sage_pos_customer_id": "4150404", "sage_pos_customer_name": "Store Sales (Credit Card)",
                "custom_sage_pos_sales_rep_id": 622508, "custom_sage_online_customer_id": "4171600",
                "custom_sage_online_customer_name": "Online Sales", "custom_sage_online_sales_rep_id": 622508},
            "Ceramics": {"company": "Ceramics", "username": "u", "tax_id": 4849096, "custom_sage_zero_tax_id": 4849099,
                "sage_pos_customer_id": "23915171", "custom_sage_pos_sales_rep_id": 0,
                "custom_sage_online_customer_id": "414595", "custom_sage_online_customer_name": "Website Sales",
                "custom_sage_online_sales_rep_id": 7001},
            "Fashion": {"company": "Fashion", "username": "u", "tax_id": 5698238, "custom_sage_zero_tax_id": 5698241,
                "custom_sage_pos_sales_rep_id": 0, "custom_sage_online_customer_id": "498720",
                "custom_sage_online_customer_name": "ONLINE SALES", "custom_sage_online_sales_rep_id": 7002},
        },
        "Bin": {},
        "Sales Invoice": {},
        "Sales Invoice Item": {},
        "Sales Order": {},
        "Address": {},
    }
    n = 0
    for item, sel in (("HOM1", 11), ("FAS1", 22), ("CER1", 33)):
        for co in ("Home", "Fashion", "Ceramics"):
            n += 1
            t["Sage Item Selection"]["s%d" % n] = {"item_code": item, "company": co, "selection_id": str(sel * 100 + n)}
    return t


def line(code, qty, incl, wh, row="r"):
    net = round(incl / 1.15, 2)
    return {"name": row, "item_code": code, "item_name": code, "description": code, "qty": qty, "rate": incl,
        "net_rate": net, "net_amount": round(net * qty, 2), "amount": incl * qty, "uom": "Nos",
        "valuation_rate": 10, "warehouse": wh}


def invoice(name, profile, lines, **extra):
    d = {"name": name, "company": "Ardmore", "is_pos": 1, "is_return": 0, "pos_profile": profile,
        "set_warehouse": "Online Store - A" if profile == "Online" else "HDSQ - A", "posting_date": "2026-11-21",
        "due_date": "2026-11-21", "additional_discount_percentage": 0, "remarks": "", "customer": "C1",
        "customer_name": "Jane Buyer", "custom_invoice_to_name": "Jane Buyer", "owner": "online@ardmore-design.com",
        "taxes": [{"charge_type": "On Net Total", "rate": 15}], "items": lines, "docstatus": 1}
    d.update(extra)
    return d


def post(script_dir, t, inv_name, **fk):
    db = DB(t)
    f = Frappe(db, **fk)
    doc = f.get_doc("Sales Invoice", inv_name)
    run(os.path.join(script_dir, "post-taxinvoice-to-sage.py"), f, doc)
    return f, db, doc


def post_return(script_dir, t, ret_name, **fk):
    db = DB(t)
    f = Frappe(db, **fk)
    doc = f.get_doc("Sales Invoice", ret_name)
    run(os.path.join(script_dir, "post-customerreturn-to-sage.py"), f, doc)
    return f, db, doc


def payloads(f):
    return [(u.split("?")[0], p) for u, p in f.posts]


def sent(f):
    out = []
    for _u, p in f.posts:
        body = p.get("invoice") or p.get("customerReturn")
        cust = body.get("customerId") or body["customer"]["id"]
        out.append((cust, (body.get("salesRepresentative") or {}).get("id"), sorted(l["selectionId"] for l in body["lines"]),
            [l["taxTypeId"] for l in body["lines"]], body.get("fromDocumentId")))
    return out


RESULTS = []


def test(fn):
    try:
        fn()
        RESULTS.append(("PASS", fn.__name__, ""))
    except Exception as e:
        RESULTS.append(("FAIL", fn.__name__, "".join(traceback.format_exception_only(type(e), e)).strip()))
    return fn


def sel(code, company):
    t = tables()
    for r in t["Sage Item Selection"].values():
        if r["item_code"] == code and r["company"] == company:
            return int(r["selection_id"])


# ---------------------------------------------------------------- shops unchanged (base vs new, same input)

@test
def shop_sale_identical_to_today():
    for lines in ([line("HOM1", 1, 115, "HDSQ - A")], [line("HOM1", 2, 115, "HDSQ - A", "a"), line("CER1", 1, 230, "HDSQ - A", "b")]):
        t1, t2 = tables(), tables()
        t1["Sales Invoice"]["S1"] = invoice("S1", "Hyde Park", copy.deepcopy(lines))
        t2["Sales Invoice"]["S1"] = invoice("S1", "Hyde Park", copy.deepcopy(lines))
        fa, dba, da = post(BASE, t1, "S1")
        fb, dbb, db_ = post(NEW, t2, "S1")
        assert payloads(fa) == payloads(fb), "Sage payload differs for a Hyde Park sale"
        assert dba.db_sets == dbb.db_sets, (dba.db_sets, dbb.db_sets)
        assert len(fb.posts) == 1 and sent(fb)[0][0] == 4150404


@test
def shop_return_identical_to_today():
    for t in (tables(), tables()):
        t["Sales Invoice"]["S1"] = invoice("S1", "Hyde Park", [line("HOM1", 2, 115, "HDSQ - A")],
            custom_sage_order_id="777", custom_sage_document_number="JSSA1", custom_sage_sync_status="Synced")
        t["Sales Invoice"]["R1"] = invoice("R1", "Hyde Park", [line("HOM1", -1, 115, "HDSQ - A")], is_return=1, return_against="S1")
    ta, tb = tables(), tables()
    for t in (ta, tb):
        t["Sales Invoice"]["S1"] = invoice("S1", "Hyde Park", [line("HOM1", 2, 115, "HDSQ - A")],
            custom_sage_order_id="777", custom_sage_document_number="JSSA1", custom_sage_sync_status="Synced")
        t["Sales Invoice"]["R1"] = invoice("R1", "Hyde Park", [line("HOM1", -1, 115, "HDSQ - A")], is_return=1, return_against="S1")
    fa, dba, _ = post_return(BASE, ta, "R1")
    fb, dbb, _ = post_return(NEW, tb, "R1")
    assert payloads(fa) == payloads(fb), "credit note payload differs for a Hyde Park return"
    assert dba.db_sets == dbb.db_sets
    assert sent(fb)[0][4] == 777


@test
def online_unticked_identical_to_today():
    lines = [line("HOM1", 1, 115, "Online Store - A", "a"), line("CER1", 1, 230, "Online Store - A", "b")]
    ta, tb = tables(split=0), tables(split=0)
    ta["Sales Invoice"]["S1"] = invoice("S1", "Online", copy.deepcopy(lines), po_no="#12001")
    tb["Sales Invoice"]["S1"] = invoice("S1", "Online", copy.deepcopy(lines), po_no="#12001")
    fa, dba, _ = post(BASE, ta, "S1")
    fb, dbb, _ = post(NEW, tb, "S1")
    assert payloads(fa) == payloads(fb) and dba.db_sets == dbb.db_sets


# ---------------------------------------------------------------- Online split

@test
def combined_order_one_invoice_per_company():
    t = tables()
    t["Sales Invoice"]["S1"] = invoice("S1", "Online", [line("HOM1", 1, 115, "JHB Atrium Home - A", "a"),
        line("FAS1", 2, 230, "JHB Atrium Fashion - A", "b"), line("CER1", 1, 1150, "Main Distribution - A", "c")], po_no="#12002")
    f, db, doc = post(NEW, t, "S1")
    s = sent(f)
    assert [x[0] for x in s] == [4171600, 498720, 414595], s
    assert [x[1] for x in s] == [622508, 7002, 7001], s
    assert s[0][2] == [sel("HOM1", "Home")] and s[1][2] == [sel("FAS1", "Fashion")] and s[2][2] == [sel("CER1", "Ceramics")]
    rec = t["Sales Invoice"]["S1"]
    assert rec["custom_sage_companies"] == "Home, Fashion, Ceramics"
    assert len(rec["custom_sage_document_number"].split(",")) == 3 and rec["custom_sage_sync_status"] == "Synced"
    for _u, p in f.posts:
        assert p["invoice"]["reference"].endswith("#12002"), p["invoice"]["reference"]


@test
def single_company_order_goes_to_that_company_only():
    t = tables()
    t["Sales Invoice"]["S1"] = invoice("S1", "Online", [line("CER1", 1, 1150, "Main Distribution - A")])
    f, db, doc = post(NEW, t, "S1")
    assert [x[0] for x in sent(f)] == [414595]
    assert t["Sales Invoice"]["S1"]["custom_sage_companies"] == "Ceramics"


@test
def international_zero_rated_uses_each_companys_zero_tax():
    t = tables()
    t["Sales Invoice"]["S1"] = invoice("S1", "Online", [line("HOM1", 1, 100, "JHB Atrium Home - A", "a"),
        line("CER1", 1, 200, "Main Distribution - A", "b")], tax_category="Zero Rated", taxes=[{"charge_type": "On Net Total", "rate": 0}])
    f, db, doc = post(NEW, t, "S1")
    assert [x[3] for x in sent(f)] == [[690655], [4849099]], sent(f)
    for _u, p in f.posts:
        assert p["invoice"]["tax"] == 0


@test
def failed_company_is_retried_alone_never_twice():
    t = tables()
    t["Sales Invoice"]["S1"] = invoice("S1", "Online", [line("HOM1", 1, 115, "JHB Atrium Home - A", "a"),
        line("FAS1", 1, 230, "JHB Atrium Fashion - A", "b"), line("CER1", 1, 1150, "Main Distribution - A", "c")])
    f1, db1, _ = post(NEW, t, "S1", sage_fail_for={"498720"})
    rec = t["Sales Invoice"]["S1"]
    assert rec["custom_sage_sync_status"] == "Failed" and rec["custom_sage_companies"] == "Home", rec
    f2, db2, _ = post(NEW, t, "S1")  # the 15-minute retry
    assert [x[0] for x in sent(f2)] == [498720, 414595], sent(f2)
    assert rec["custom_sage_companies"] == "Home, Fashion, Ceramics" and rec["custom_sage_sync_status"] == "Synced"
    assert len(rec["custom_sage_order_id"].split(",")) == 3


@test
def timeout_marks_check_sage_and_keeps_posted_companies():
    t = tables()
    t["Sales Invoice"]["S1"] = invoice("S1", "Online", [line("HOM1", 1, 115, "JHB Atrium Home - A", "a"),
        line("CER1", 1, 1150, "Main Distribution - A", "c")])
    post(NEW, t, "S1", sage_timeout_for={"414595"})
    rec = t["Sales Invoice"]["S1"]
    assert rec["custom_sage_sync_status"] == "Check Sage" and rec["custom_sage_companies"] == "Home", rec


@test
def routing_change_after_partial_post_is_refused():
    t = tables()
    t["Sales Invoice"]["S1"] = invoice("S1", "Online", [line("HOM1", 1, 115, "JHB Atrium Home - A", "a"),
        line("CER1", 1, 1150, "Main Distribution - A", "c")])
    post(NEW, t, "S1", sage_fail_for={"414595"})
    rec = t["Sales Invoice"]["S1"]
    assert rec["custom_sage_companies"] == "Home"
    t["POS Profile"]["Online"]["custom_split_by_item_company"] = 0  # rollback between attempts
    f, db, _ = post(NEW, t, "S1")
    # everything now routes to Home, which is done; Ceramics' sale must NOT be called synced
    assert rec["custom_sage_sync_status"] == "Failed", rec["custom_sage_sync_status"]
    assert "routes elsewhere" in rec["custom_sage_sync_error"] and not f.posts


@test
def missing_online_customer_fails_clearly():
    t = tables()
    t["Company Sage Integration"]["Fashion"]["custom_sage_online_customer_id"] = ""
    t["Sales Invoice"]["S1"] = invoice("S1", "Online", [line("FAS1", 1, 230, "JHB Atrium Fashion - A")])
    f, db, _ = post(NEW, t, "S1")
    rec = t["Sales Invoice"]["S1"]
    assert not f.posts and rec["custom_sage_sync_status"] == "Failed"
    assert "Online customer not set on Company Sage Integration Fashion" in rec["custom_sage_sync_error"]


@test
def item_without_category_fails_clearly():
    t = tables()
    t["Sales Invoice"]["S1"] = invoice("S1", "Online", [line("NOCAT", 1, 100, "Online Store - A")])
    f, db, _ = post(NEW, t, "S1")
    assert not f.posts and "Set ERPNext Category on NOCAT" in t["Sales Invoice"]["S1"]["custom_sage_sync_error"]


# ---------------------------------------------------------------- returns

def split_sale(t):
    t["Sales Invoice"]["S1"] = invoice("S1", "Online", [line("HOM1", 1, 115, "JHB Atrium Home - A", "a"),
        line("CER1", 2, 1150, "Main Distribution - A", "c")], po_no="#12010")
    post(NEW, t, "S1")
    return t["Sales Invoice"]["S1"]


@test
def partial_return_of_split_sale_goes_to_that_company_only():
    t = tables()
    s1 = split_sale(t)
    ceramics_id = int(s1["custom_sage_order_id"].split(", ")[1])
    t["Sales Invoice"]["R1"] = invoice("R1", "Online", [line("CER1", -1, 1150, "Main Distribution - A")],
        is_return=1, return_against="S1")
    f, db, _ = post_return(NEW, t, "R1")
    s = sent(f)
    assert len(s) == 1 and s[0][0] == 414595 and s[0][1] == 7001 and s[0][4] == ceramics_id, s
    assert t["Sales Invoice"]["R1"]["custom_sage_companies"] == "Ceramics"


@test
def full_return_of_split_sale_one_credit_note_per_company():
    t = tables()
    split_sale(t)
    t["Sales Invoice"]["R1"] = invoice("R1", "Online", [line("HOM1", -1, 115, "JHB Atrium Home - A", "a"),
        line("CER1", -2, 1150, "Main Distribution - A", "c")], is_return=1, return_against="S1")
    f, db, _ = post_return(NEW, t, "R1")
    assert [x[0] for x in sent(f)] == [4171600, 414595], sent(f)


@test
def failed_return_company_retried_alone_and_routing_change_refused():
    t = tables()
    split_sale(t)
    t["Sales Invoice"]["R1"] = invoice("R1", "Online", [line("HOM1", -1, 115, "JHB Atrium Home - A", "a"),
        line("CER1", -1, 1150, "Main Distribution - A", "c")], is_return=1, return_against="S1")
    post_return(NEW, t, "R1", sage_fail_for={"414595"})
    r = t["Sales Invoice"]["R1"]
    assert r["custom_sage_companies"] == "Home" and r["custom_sage_sync_status"] == "Failed", r
    t2 = copy.deepcopy(t)
    f, db, _ = post_return(NEW, t, "R1")
    assert [x[0] for x in sent(f)] == [414595] and r["custom_sage_sync_status"] == "Synced"
    t2["POS Profile"]["Online"]["custom_split_by_item_company"] = 0
    f, db, _ = post_return(NEW, t2, "R1")
    assert not f.posts and t2["Sales Invoice"]["R1"]["custom_sage_sync_status"] == "Failed"


@test
def return_of_online_sale_made_before_switch_on_goes_to_home():
    t = tables(split=1)
    # sold on 18 Nov, before the box was ticked: posted wholly to Home, no Sage Companies recorded
    t["Sales Invoice"]["S0"] = invoice("S0", "Online", [line("CER1", 1, 1150, "Online Store - A")],
        custom_sage_order_id="555", custom_sage_document_number="JSSA9", custom_sage_sync_status="Synced")
    t["Sales Invoice"]["R0"] = invoice("R0", "Online", [line("CER1", -1, 1150, "Online Store - A")], is_return=1, return_against="S0")
    f, db, _ = post_return(NEW, t, "R0")
    s = sent(f)
    assert len(s) == 1 and s[0][0] == 4171600 and s[0][4] == 555, (s, t["Sales Invoice"]["R0"].get("custom_sage_sync_error"))


# ---------------------------------------------------------------- stock: own company's warehouse

def sell_from(t, d):
    db = DB(t)
    f = Frappe(db)
    doc = Doc(db, "Sales Invoice", d)
    run(os.path.join(SRV, "Sales_Invoice_-_Sell_From_Item_Company.py"), f, doc)
    return doc


def bins(t, **stock):
    for k, q in stock.items():
        code, wh = k.split("__")
        wh = {"OS": "Online Store - A", "AH": "JHB Atrium Home - A", "AF": "JHB Atrium Fashion - A",
            "AC": "JHB Atrium Ceramics - A", "MD": "Main Distribution - A", "HD": "HDSQ - A"}[wh]
        t["Bin"][code + wh] = {"item_code": code, "warehouse": wh, "actual_qty": q}


@test
def each_line_sells_from_its_own_company():
    t = tables()
    bins(t, HOM1__AH=3, FAS1__AF=1, CER1__AC=0, CER1__MD=2)
    d = invoice("D1", "Online", [line("HOM1", 1, 115, "Online Store - A", "a"), line("FAS1", 1, 230, "Online Store - A", "b"),
        line("CER1", 1, 1150, "Online Store - A", "c")], update_stock=1, docstatus=1)
    doc = sell_from(t, d)
    assert [r["warehouse"] for r in doc["items"]] == ["JHB Atrium Home - A", "JHB Atrium Fashion - A", "Main Distribution - A"]


@test
def item_held_only_by_another_company_is_stopped_on_completion_only():
    t = tables()
    bins(t, FAS1__AH=2)  # a Fashion scarf sitting in Home's Atrium warehouse
    d = invoice("D1", "Online", [line("FAS1", 1, 230, "Online Store - A")], update_stock=1, docstatus=0)
    sell_from(t, copy.deepcopy(d))  # draft: no stop
    d["docstatus"] = 1
    try:
        sell_from(t, d)
        raise AssertionError("completion was not stopped")
    except FrappeThrow as e:
        assert "JHB Atrium Home - A (2)" in str(e) and "Fashion" in str(e)


@test
def two_lines_of_one_item_share_the_stock():
    t = tables()
    bins(t, CER1__AC=1, CER1__MD=1)
    d = invoice("D1", "Online", [line("CER1", 1, 1150, "Online Store - A", "a"), line("CER1", 1, 1150, "Online Store - A", "b")],
        update_stock=1, docstatus=1)
    doc = sell_from(t, d)
    assert [r["warehouse"] for r in doc["items"]] == ["JHB Atrium Ceramics - A", "Main Distribution - A"]
    d2 = invoice("D2", "Online", [line("CER1", 2, 1150, "Online Store - A", "a"), line("CER1", 1, 1150, "Online Store - A", "b")],
        update_stock=1, docstatus=1)
    try:
        sell_from(t, d2)
        raise AssertionError("over-sold")
    except FrappeThrow:
        pass


@test
def shop_till_lines_untouched_by_warehouse_rule():
    t = tables()
    bins(t, CER1__MD=5)
    d = invoice("D1", "Hyde Park", [line("CER1", 1, 1150, "HDSQ - A")], update_stock=1, docstatus=1)
    assert sell_from(t, d)["items"][0]["warehouse"] == "HDSQ - A"


@test
def return_goes_back_where_it_was_sold():
    t = tables()
    t["Sales Invoice Item"]["si-1"] = {"warehouse": "Main Distribution - A"}
    d = invoice("R1", "Online", [dict(line("CER1", -1, 1150, "Online Store - A", "a"), sales_invoice_item="si-1"),
        line("FAS1", -1, 230, "Online Store - A", "b")], is_return=1, update_stock=1)
    doc = sell_from(t, d)
    assert [r["warehouse"] for r in doc["items"]] == ["Main Distribution - A", "JHB Atrium Fashion - A"]


@test
def till_stock_counts_only_own_company():
    for split, want in ((1, 0), (0, 2)):
        t = tables(split=split)
        bins(t, FAS1__AH=2)
        db = DB(t)
        f = Frappe(db)
        run(os.path.join(NEW, "pos-pool-stock.py"), f, form={"pos_profile": "Online", "item_code": "FAS1"})
        assert f.response["message"][0] == want, (split, f.response)


@test
def till_item_list_counts_only_own_company():
    t = tables()
    bins(t, FAS1__AH=2, HOM1__AH=3, CER1__MD=1)
    t["Item"]["HOM1"].update(disabled=0, has_variants=0, is_sales_item=1, is_fixed_asset=0)
    db = DB(t)
    f = Frappe(db)
    run(os.path.join(NEW, "pos-pool-items.py"), f, form={"pos_profile": "Online"})
    # fake get_all ignores the Item "in" list shape for pages, so check the computed quantities directly
    g = run(os.path.join(NEW, "pos-pool-items.py"), f, form={"pos_profile": "Online"})
    assert g["qty"] == {"HOM1": 3, "CER1": 1}, g["qty"]


@test
def online_split_moves_no_stock_and_no_intercompany():
    t = tables()
    bins(t, CER1__MD=2)
    db = DB(t)
    f = Frappe(db)
    d = Doc(db, "Sales Invoice", invoice("S1", "Online", [line("CER1", 1, 1150, "Online Store - A")], update_stock=1))
    run(os.path.join(NEW, "Sales_Invoice_-_Online_Auto_Transfer.py"), f, d)
    assert not db.inserted and not db.submitted
    run(os.path.join(NEW, "post-intercompany-sale-to-sage.py"), f, d)
    assert not f.posts


@test
def online_unticked_still_auto_transfers_like_today():
    def go(path):
        t = tables(split=0)
        bins(t, CER1__MD=2)
        db = DB(t)
        f = Frappe(db)
        d = Doc(db, "Sales Invoice", invoice("S1", "Online", [line("CER1", 1, 1150, "Online Store - A")], update_stock=1))
        run(path, f, d)
        return [(se.get("to_warehouse"), [(i["s_warehouse"], i["qty"]) for i in se["items"]]) for se in db.submitted]
    a = go(os.path.join(BASE, "Sales_Invoice_-_Online_Auto_Transfer.py"))
    b = go(os.path.join(NEW, "Sales_Invoice_-_Online_Auto_Transfer.py"))
    assert a == b == [("Online Store - A", [("Main Distribution - A", 1)])], (a, b)


# ---------------------------------------------------------------- other new scripts

@test
def shopify_order_without_category_is_held():
    db = DB(tables())
    f = Frappe(db)
    so = Doc(db, "Sales Order", {"shopify_order_id": "1", "shopify_order_number": "#12003", "docstatus": 0,
        "items": [{"item_code": "NOCAT", "item_name": "Mystery"}, {"item_code": "HOM1", "item_name": "Cushion"}]})
    try:
        run(os.path.join(SRV, "Sales_Order_-_Shopify_Category_Check.py"), f, so)
        raise AssertionError("not held")
    except FrappeThrow as e:
        assert "NOCAT" in str(e) and "HOM1" not in str(e) and "Retry" in str(e)
    plain = Doc(db, "Sales Order", {"docstatus": 0, "items": [{"item_code": "NOCAT"}]})
    run(os.path.join(SRV, "Sales_Order_-_Shopify_Category_Check.py"), f, plain)  # a normal Sales Order is never stopped


@test
def mailing_list_email_only_for_shopify_customers():
    db = DB(tables())
    f = Frappe(db)
    shop = Doc(db, "Customer", {"add_to_mailing_list": 1, "email_id": "a@b.c", "custom_email_address": ""})
    run(os.path.join(SRV, "Customer_-_Mailing_List_Email.py"), f, shop)
    assert shop["custom_email_address"] == ""
    web = Doc(db, "Customer", {"shopify_customer_id": "9", "add_to_mailing_list": 1, "email_id": "a@b.c", "custom_email_address": ""})
    run(os.path.join(SRV, "Customer_-_Mailing_List_Email.py"), f, web)
    assert web["custom_email_address"] == "a@b.c"
    no = Doc(db, "Customer", {"shopify_customer_id": "9", "add_to_mailing_list": 0, "email_id": "a@b.c", "custom_email_address": ""})
    run(os.path.join(SRV, "Customer_-_Mailing_List_Email.py"), f, no)
    assert no["custom_email_address"] == ""


@test
def completed_shopify_sale_closes_its_order_and_never_blocks():
    t = tables()
    t["Sales Order"]["SO1"] = {"shopify_order_id": "77", "docstatus": 1, "status": "To Deliver and Bill"}
    db = DB(t)
    f = Frappe(db)
    run(os.path.join(SRV, "Sales_Invoice_-_Close_Shopify_Order.py"), f, Doc(db, "Sales Invoice", invoice("S1", "Online", [], shopify_order_id="77")))
    assert db.status_updates == [("SO1", "Closed")]
    ret = Doc(db, "Sales Invoice", invoice("R1", "Online", [], shopify_order_id="77", is_return=1))
    run(os.path.join(SRV, "Sales_Invoice_-_Close_Shopify_Order.py"), f, ret)
    assert len(db.status_updates) == 1


def shopify_so(t, name="SO1", oid="77", lines=None, tax=None, net=None):
    lines = lines or [{"name": "i1", "item_code": "HOM1", "item_name": "Cushion", "description": "", "qty": 1, "rate": 1565.22,
        "net_amount": 1565.22, "amount": 1565.22, "uom": "Nos", "stock_uom": "Nos", "conversion_factor": 1}]
    tax = [{"item_row": "i1", "amount": 234.78}] if tax is None else tax
    t["Sales Order"][name] = {"shopify_order_id": oid, "shopify_order_number": "#12004", "docstatus": 1, "company": "Ardmore",
        "status": "To Deliver and Bill", "customer": "C1", "customer_name": "Jane", "currency": "ZAR", "transaction_date": "2026-11-21",
        "grand_total": 1800, "net_total": net if net is not None else sum(x["net_amount"] for x in lines),
        "total_taxes_and_charges": sum(x["amount"] for x in tax), "items": lines, "item_wise_tax_details": tax}


def shopify_api(t, action, user="online@ardmore-design.com", **form):
    db = DB(t)
    f = Frappe(db)
    f.session.user = user
    form.update(action=action, pos_profile="Online")
    run(os.path.join(SRV, "pos-shopify-orders.py"), f, form=form)
    return f, db


@test
def till_opens_shopify_order_at_shopify_prices_paid_by_shopify():
    t = tables()
    shopify_so(t)
    f, db = shopify_api(t, "open", sales_order="SO1")
    si = db.inserted[0]
    assert si["items"][0]["rate"] == 1800.0 and si["po_no"] == "#12004" and si["shopify_order_id"] == "77"
    assert si["taxes_and_charges"] == "South Africa Tax - A" and not si.get("tax_category")
    assert si["disable_rounded_total"] == 1
    pay = {p["mode_of_payment"]: p["amount"] for p in si["payments"]}
    assert pay == {"Credit Card": 0, "Shopify": 1800.0}, pay


@test
def discount_code_price_comes_through():
    t = tables()
    # Shopify: R1,800 less R180 discount = R1,620 incl; tax 211.30; connector rate 1408.70
    shopify_so(t, lines=[{"name": "i1", "item_code": "HOM1", "item_name": "Cushion", "description": "", "qty": 1, "rate": 1408.70,
        "net_amount": 1408.70, "amount": 1408.70, "uom": "Nos", "stock_uom": "Nos", "conversion_factor": 1}],
        tax=[{"item_row": "i1", "amount": 211.30}])
    f, db = shopify_api(t, "open", sales_order="SO1")
    assert db.inserted[0]["items"][0]["rate"] == 1620.0


@test
def international_order_opens_at_vat_zero_with_export_comment():
    t = tables()
    shopify_so(t, lines=[{"name": "i1", "item_code": "CER1", "item_name": "Bowl", "description": "", "qty": 1, "rate": 1800,
        "net_amount": 1800, "amount": 1800, "uom": "Nos", "stock_uom": "Nos", "conversion_factor": 1}], tax=[])
    t["Sales Order"]["SO1"]["shipping_address_name"] = "A1"
    t["Address"]["A1"] = {"country": "United Kingdom"}
    f, db = shopify_api(t, "open", sales_order="SO1")
    si = db.inserted[0]
    assert si["tax_category"] == "Zero Rated" and si["taxes_and_charges"] == "South Africa Zero Rated - A"
    assert si["items"][0]["rate"] == 1800 and "United Kingdom" in si["custom_export_comment"]


@test
def free_local_order_is_not_an_export():
    t = tables()
    shopify_so(t, lines=[{"name": "i1", "item_code": "HOM1", "item_name": "Cushion", "description": "", "qty": 1, "rate": 0,
        "net_amount": 0, "amount": 0, "uom": "Nos", "stock_uom": "Nos", "conversion_factor": 1}], tax=[], net=0)
    f, db = shopify_api(t, "open", sales_order="SO1")
    si = db.inserted[0]
    assert not si.get("tax_category") and si["items"][0]["discount_percentage"] == 100


@test
def order_cannot_be_completed_twice_and_draft_is_continued():
    t = tables()
    shopify_so(t)
    t["Sales Invoice"]["D1"] = {"shopify_order_id": "77", "docstatus": 0, "is_return": 0}
    f, db = shopify_api(t, "open", sales_order="SO1")
    assert f.response["message"] == {"name": "D1"} and not db.inserted
    t["Sales Invoice"]["D1"]["docstatus"] = 1
    try:
        shopify_api(t, "open", sales_order="SO1")
        raise AssertionError("opened twice")
    except FrappeThrow as e:
        assert "already completed" in str(e)
    f, db = shopify_api(t, "list")
    assert f.response["message"] == []


@test
def list_shows_waiting_orders_and_only_to_till_users():
    t = tables()
    shopify_so(t)
    f, db = shopify_api(t, "list")
    assert [o["order_no"] for o in f.response["message"]] == ["#12004"]
    try:
        shopify_api(t, "list", user="hdsqpos@ardmore-design.com")
        raise AssertionError("a Hyde Park login saw Shopify orders")
    except FrappeThrow:
        pass


@test
def hyde_park_till_cannot_open_shopify_orders():
    t = tables()
    shopify_so(t)
    db = DB(t)
    f = Frappe(db)
    try:
        run(os.path.join(SRV, "pos-shopify-orders.py"), f, form={"action": "list", "pos_profile": "Hyde Park"})
        raise AssertionError("Hyde Park till got the list")
    except FrappeThrow as e:
        assert "only on the Online till" in str(e)


if __name__ == "__main__":
    width = max(len(n) for _s, n, _m in RESULTS)
    for status, name, msg in RESULTS:
        print(f"{status}  {name.ljust(width)}  {msg}")
    failed = [r for r in RESULTS if r[0] == "FAIL"]
    print(f"\n{len(RESULTS) - len(failed)} passed, {len(failed)} failed")
    sys.exit(1 if failed else 0)
