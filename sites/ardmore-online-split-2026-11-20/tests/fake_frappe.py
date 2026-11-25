"""A small stand-in for the parts of Frappe the Ardmore Server Scripts use, so the real script text can be
run against test data on a machine without Frappe. It records what would be sent to Sage and every db_set.
Not a Frappe emulator: only the calls these scripts make, with the same shapes."""

import copy
import datetime
import itertools


class FrappeThrow(Exception):
    pass


class Row(dict):
    """A document or child row: attribute and .get access, like frappe._dict / Document."""

    def __getattribute__(self, k):
        # a stored field wins over dict's own methods (an invoice's "items" is its lines, not dict.items)
        if not k.startswith("_") and dict.__contains__(self, k):
            return dict.__getitem__(self, k)
        return object.__getattribute__(self, k)

    def __getattr__(self, k):
        if k.startswith("__"):
            raise AttributeError(k)
        return self.get(k)

    def __setattr__(self, k, v):
        self[k] = v


class Doc(Row):
    def __init__(self, db, doctype, data):
        super().__init__(copy.deepcopy(data))
        object.__setattr__(self, "_db", db)
        self["doctype"] = doctype
        self.setdefault("flags", Row())
        for k, v in list(dict.items(self)):
            if isinstance(v, list):
                self[k] = [Row(x) if isinstance(x, dict) else x for x in v]

    # --- Document methods the scripts call ---
    def submit(self):
        self["docstatus"] = 1
        self._db.submitted.append(self)

    def save(self, **k):
        self._db.saved.append(self)

    def add_comment(self, *a, **k):
        pass

    def update_status(self, status):
        self["status"] = status
        self._db.status_updates.append((self.get("name"), status))

    def reset_mode_of_payments(self):
        rows = [r for r in self._db._rows("POS Payment Method", {"parent": self.get("pos_profile")})]
        self["payments"] = [Row(mode_of_payment=r["mode_of_payment"], default=r.get("default", 0), amount=0) for r in rows]

    def db_set(self, field, value, update_modified=True):
        self[field] = value
        self._db.db_sets.append((self.get("name"), field, value))
        stored = self._db.tables.get(self["doctype"], {}).get(self.get("name"))
        if stored is not None:
            stored[field] = value

    def get_password(self, field):
        return "secret-" + field

    def append(self, table, row):
        self.setdefault(table, []).append(Row(row))

    def insert(self, **k):
        # stand-in for ERPNext's totals: the till's prices include VAT, so the total is rate x qty
        if self.get("doctype") == "Sales Invoice":
            self["name"] = self.get("name") or "SINV-NEW-%d" % (len(self._db.inserted) + 1)
            self["grand_total"] = round(sum(float(i.get("rate") or 0) * float(i.get("qty") or 0) for i in self.get("items", [])), 2)
        self._db.inserted.append(self)
        return self


def _match(rec, filters):
    for k, v in (filters or {}).items():
        have = rec.get(k)
        if isinstance(v, list):
            op, val = v[0], v[1]
            if op == "in" and have not in val:
                return False
            if op == "not in" and have in val:
                return False
            if op == ">" and not (have or 0) > val:
                return False
            if op == "<" and not (have or 0) < val:
                return False
            if op == "is" and val == "set" and not have:
                return False
            if op == "is" and val == "not set" and have:
                return False
        elif have != v:
            return False
    return True


class DB:
    def __init__(self, tables, singles=None):
        self.tables = tables  # {doctype: {name: {field: value}}}
        self.singles = singles or {}
        self.db_sets = []
        self.inserted = []
        self.submitted = []
        self.saved = []
        self.status_updates = []

    def _rows(self, doctype, filters):
        for name, rec in self.tables.get(doctype, {}).items():
            r = dict(rec, name=name)
            if _match(r, filters):
                yield r

    def get_value(self, doctype, filters, fieldname="name", as_dict=False, **kw):
        if filters is None:
            return None
        if isinstance(filters, str):
            rec = self.tables.get(doctype, {}).get(filters)
            r = dict(rec, name=filters) if rec is not None else None
        else:
            r = next(self._rows(doctype, filters), None)
        if r is None:
            return None
        if isinstance(fieldname, (list, tuple)):
            vals = {f: r.get(f) for f in fieldname}
            return Row(vals) if as_dict else [vals[f] for f in fieldname]
        return r.get(fieldname)

    def exists(self, doctype, filters=None):
        if isinstance(doctype, dict):
            return None
        if isinstance(filters, str):
            return filters if filters in self.tables.get(doctype, {}) else None
        r = next(self._rows(doctype, filters or {}), None)
        return r["name"] if r else None

    def get_single_value(self, doctype, field):
        return self.singles.get(doctype, {}).get(field)


class Utils:
    flt = staticmethod(lambda v, p=None: round(float(v or 0), p) if p is not None else float(v or 0))
    cint = staticmethod(lambda v: int(float(v or 0)))
    nowdate = staticmethod(lambda: "2026-11-21")
    formatdate = staticmethod(lambda d, fmt=None: str(d))
    add_days = staticmethod(lambda d, n: str(datetime.date.fromisoformat(str(d)) + datetime.timedelta(days=n)))


class Frappe:
    def __init__(self, db, sage_fail_for=(), sage_timeout_for=()):
        self.db = db
        self.utils = Utils()
        self.response = {}
        self.form_dict = Row()
        self.session = Row(user="online@ardmore-design.com")
        self.posts = []  # (url, payload) sent to Sage
        self.errors = []
        self.messages = []
        self.sage_fail_for = set(sage_fail_for)  # customer ids Sage refuses
        self.sage_timeout_for = set(sage_timeout_for)
        self._ids = itertools.count(9001)

    def throw(self, msg, exc=None, title=None):
        raise FrappeThrow(msg)

    def msgprint(self, msg, *a, **k):
        self.messages.append(msg)

    def log_error(self, message=None, title=None, **k):
        self.errors.append((title, message))

    def get_doc(self, doctype, name=None):
        rec = self.db.tables.get(doctype, {}).get(name)
        if rec is None:
            raise FrappeThrow(f"{doctype} {name} not found")
        return Doc(self.db, doctype, dict(rec, name=name))

    def new_doc(self, doctype):
        return Doc(self.db, doctype, {})

    def get_all(self, doctype, filters=None, fields=None, pluck=None, order_by=None, limit_page_length=None, **k):
        rows = list(self.db._rows(doctype, filters if isinstance(filters, dict) else {}))
        if pluck:
            return [r.get(pluck) for r in rows]
        return [Row({f: r.get(f) for f in (fields or ["name"])}) for r in rows]

    def make_post_request(self, url, json=None, headers=None):
        self.posts.append((url, copy.deepcopy(json)))
        body = (json or {}).get("invoice") or (json or {}).get("customerReturn") or json or {}
        cust = str(body.get("customerId") or (body.get("customer") or {}).get("id"))
        if cust in self.sage_timeout_for:
            raise Exception("Read timed out")
        if cust in self.sage_fail_for:
            return {"success": False, "errorMessage": "Sage refused"}
        n = next(self._ids)
        return {"success": True, "sageOrderId": n, "documentNumber": f"INV{n}"}


def run(script_path, frappe, doc=None, form=None):
    text = open(script_path, encoding="utf-8").read()
    if form is not None:
        frappe.form_dict = Row(form)
    g = {"frappe": frappe, "doc": doc, "__builtins__": __builtins__}
    exec(compile(text, script_path, "exec"), g)
    return g
