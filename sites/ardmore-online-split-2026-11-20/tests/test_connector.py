"""Break tests for the Shopify connector changes (fork nesterp_ecommerce_integrations), run without Frappe.

    python -I tests/test_connector.py      (from the ardmore-online-split folder)

Frappe, the shopify library and ERPNext are replaced by stand-ins; the connector's own code is the real code.
Each test prints PASS/FAIL."""

import importlib.abc
import importlib.machinery
import os
import sys
import traceback
import types
from unittest import mock

FORK = r"C:\ClaudeCode\nesterp_ecommerce_integrations"
STUB_ROOTS = ("frappe", "shopify", "pyactiveresource", "erpnext", "requests")


class AutoModule(types.ModuleType):
    """Any name not defined explicitly is a MagicMock, so deep imports resolve."""

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        value = mock.MagicMock(name=f"{self.__name__}.{name}")
        setattr(self, name, value)
        return value


class StubFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def find_spec(self, fullname, path, target=None):
        if fullname.split(".")[0] in STUB_ROOTS and fullname not in sys.modules:
            return importlib.machinery.ModuleSpec(fullname, self, is_package=True)
        return None

    def create_module(self, spec):
        return AutoModule(spec.name)

    def exec_module(self, module):
        module.__path__ = []


sys.meta_path.insert(0, StubFinder())


class _dict(dict):
    def __getattr__(self, k):
        return self.get(k)

    def __setattr__(self, k, v):
        self[k] = v


class FrappeThrow(Exception):
    pass


import frappe  # noqa: E402  (the stub)

frappe._ = lambda s, *a: s
frappe._dict = _dict
frappe.whitelist = lambda *a, **k: (lambda f: f)
frappe.flags = _dict()
frappe.ValidationError = FrappeThrow
frappe.DoesNotExistError = type("DoesNotExistError", (Exception,), {})
frappe.throw = mock.MagicMock(side_effect=lambda msg, *a, **k: (_ for _ in ()).throw(FrappeThrow(msg)))

import frappe.utils  # noqa: E402

frappe.utils.cint = lambda v: int(float(v or 0))
frappe.utils.cstr = lambda v: "" if v is None else str(v)
frappe.utils.flt = lambda v, p=None: round(float(v or 0), p) if p is not None else float(v or 0)
frappe.utils.validate_phone_number = lambda p, throw=False: bool(p) and str(p).lstrip("+").isdigit()
frappe.utils.getdate = lambda d=None: d
frappe.utils.nowdate = lambda: "2026-11-21"

import frappe.model.document  # noqa: E402

frappe.model.document.Document = type("Document", (), {})

sys.path.insert(0, FORK)
from ecommerce_integrations.shopify import constants, customer, invoice, order  # noqa: E402

RESULTS = []


def test(fn):
    try:
        with mock.patch.multiple(frappe, db=mock.MagicMock(), get_doc=mock.MagicMock(), get_all=mock.MagicMock(return_value=[]),
                get_meta=mock.MagicMock(), set_user=mock.MagicMock(), log_error=mock.MagicMock(), get_last_doc=mock.MagicMock(),
                only_for=mock.MagicMock(), enqueue=mock.MagicMock()):
            frappe.flags = _dict()
            fn()
        RESULTS.append(("PASS", fn.__name__, ""))
    except Exception as e:
        RESULTS.append(("FAIL", fn.__name__, "".join(traceback.format_exception_only(type(e), e)).strip()))
    return fn


def paid_order(**k):
    o = {"id": 19061886386472, "name": "#12001", "order_number": 12001, "financial_status": "paid", "email": "jane@x.co",
        "buyer_accepts_marketing": False, "customer": {"id": 31413424226600, "email": "jane@x.co", "first_name": "Jane"},
        "billing_address": {}, "shipping_address": {}, "line_items": []}
    o.update(k)
    return o


# ------------------------------------------------------------------ webhooks / paid-only / cut-off

@test
def orders_create_no_longer_registered_but_still_mapped():
    assert "orders/create" not in constants.WEBHOOK_EVENTS and "orders/paid" in constants.WEBHOOK_EVENTS
    assert "orders/create" in constants.EVENT_MAPPER  # old logs and Sync Old Orders still resolve


@test
def paid_webhook_without_sales_order_imports_the_order():
    with mock.patch.object(order, "get_sales_order", return_value=None), mock.patch.object(order, "sync_sales_order") as sync:
        invoice.prepare_sales_invoice(paid_order(), request_id="LOG1")
    sync.assert_called_once()
    assert sync.call_args.kwargs["request_id"] == "LOG1"


@test
def paid_webhook_with_sales_order_does_not_import_again():
    with mock.patch.object(order, "get_sales_order", return_value=mock.MagicMock()), \
            mock.patch.object(order, "sync_sales_order") as sync, \
            mock.patch.object(invoice, "create_sales_invoice"), mock.patch.object(invoice, "create_shopify_log"):
        invoice.prepare_sales_invoice(paid_order(), request_id="LOG1")
    sync.assert_not_called()


def run_sync(o, first_order_number=0, existing_so=None):
    frappe.db.get_value.return_value = existing_so
    frappe.db.get_single_value.return_value = first_order_number
    with mock.patch.object(order, "create_shopify_log") as log, mock.patch.object(order, "ShopifyCustomer") as SC, \
            mock.patch.object(order, "create_items_if_not_exist") as items, mock.patch.object(order, "create_order") as make:
        order.sync_sales_order(o, request_id="LOG1")
    return log, SC, items, make


@test
def unpaid_order_is_not_imported():
    log, SC, items, make = run_sync(paid_order(financial_status="pending"))
    make.assert_not_called()
    SC.assert_not_called()
    assert log.call_args.kwargs["status"] == "Invalid" and "not paid" in log.call_args.kwargs["message"]


@test
def order_before_cut_off_is_not_imported():
    log, SC, items, make = run_sync(paid_order(order_number=11999), first_order_number=12000)
    make.assert_not_called()
    assert "before the first order number (12000)" in log.call_args.kwargs["message"]


@test
def order_at_cut_off_is_imported():
    log, SC, items, make = run_sync(paid_order(order_number=12000), first_order_number=12000)
    make.assert_called_once()


@test
def zero_cut_off_imports_everything():
    log, SC, items, make = run_sync(paid_order(order_number=5), first_order_number=0)
    make.assert_called_once()


@test
def existing_sales_order_is_not_duplicated():
    log, SC, items, make = run_sync(paid_order(), existing_so="SAL-ORD-1")
    make.assert_not_called()
    assert log.call_args.kwargs["status"] == "Invalid"


# ------------------------------------------------------------------ customers in the order

@test
def new_buyer_matching_till_customer_by_email_is_linked_not_created():
    frappe.db.get_value.return_value = None
    frappe.db.get_single_value.return_value = 0
    with mock.patch.object(order, "create_shopify_log"), mock.patch.object(order, "ShopifyCustomer") as SC, \
            mock.patch.object(order, "create_items_if_not_exist"), mock.patch.object(order, "create_order"):
        c = SC.return_value
        c.is_synced.return_value = False
        c.link_existing_customer.return_value = True
        order.sync_sales_order(paid_order(), request_id="LOG1")
    c.link_existing_customer.assert_called_once_with("jane@x.co")
    c.sync_customer.assert_not_called()
    c.update_existing_addresses.assert_called_once()


@test
def new_buyer_without_match_is_created():
    frappe.db.get_value.return_value = None
    frappe.db.get_single_value.return_value = 0
    with mock.patch.object(order, "create_shopify_log"), mock.patch.object(order, "ShopifyCustomer") as SC, \
            mock.patch.object(order, "create_items_if_not_exist"), mock.patch.object(order, "create_order"):
        c = SC.return_value
        c.is_synced.return_value = False
        c.link_existing_customer.return_value = False
        order.sync_sales_order(paid_order(), request_id="LOG1")
    c.sync_customer.assert_called_once()


@test
def marketing_consent_problem_never_holds_the_order():
    frappe.db.get_value.return_value = None
    frappe.db.get_single_value.return_value = 0
    with mock.patch.object(order, "create_shopify_log") as log, mock.patch.object(order, "ShopifyCustomer") as SC, \
            mock.patch.object(order, "create_items_if_not_exist"), mock.patch.object(order, "create_order") as make:
        c = SC.return_value
        c.is_synced.return_value = True
        c.record_marketing_consent.side_effect = Exception("Customer validation failed")
        order.sync_sales_order(paid_order(buyer_accepts_marketing=True), request_id="LOG1")
    make.assert_called_once()
    assert log.call_args.kwargs["status"] == "Success"
    frappe.db.rollback.assert_called_with(save_point="shopify_marketing_consent")


@test
def no_marketing_tick_without_consent():
    frappe.db.get_value.return_value = None
    frappe.db.get_single_value.return_value = 0
    with mock.patch.object(order, "create_shopify_log"), mock.patch.object(order, "ShopifyCustomer") as SC, \
            mock.patch.object(order, "create_items_if_not_exist"), mock.patch.object(order, "create_order"):
        SC.return_value.is_synced.return_value = True
        order.sync_sales_order(paid_order(buyer_accepts_marketing=False), request_id="LOG1")
    SC.return_value.record_marketing_consent.assert_not_called()


@test
def shipping_left_off_when_ticked():
    taxes, items = [], [{"delivery_date": "2026-11-21"}]
    setting = _dict(leave_shipping_off=1, add_shipping_as_item=0)
    order.update_taxes_with_shipping_lines(taxes, [{"price": "150", "title": "Courier", "tax_lines": [{"price": "19.57", "rate": 0.15, "title": "VAT"}]}], setting, items, True)
    assert taxes == [] and len(items) == 1


# ------------------------------------------------------------------ ShopifyCustomer

def shopify_customer(setting):
    frappe.get_doc.return_value = setting
    return customer.ShopifyCustomer(customer_id="31413424226600")


@test
def email_match_only_in_match_groups_first_unlinked_customer():
    c = shopify_customer(_dict(customer_match_groups="Cash\nOnline Sales\n"))
    frappe.get_all.return_value = ["CUST-OLD"]
    assert c.link_existing_customer(" jane@x.co ") is True
    f = frappe.get_all.call_args.kwargs
    assert f["filters"]["customer_group"] == ["in", ["Cash", "Online Sales"]]
    assert f["filters"]["email_id"] == "jane@x.co" and f["filters"][constants.CUSTOMER_ID_FIELD] == ["is", "not set"]
    assert f["order_by"] == "creation asc" and f["limit"] == 1
    frappe.db.set_value.assert_called_once_with("Customer", "CUST-OLD", constants.CUSTOMER_ID_FIELD, "31413424226600")


@test
def no_match_groups_means_never_link():
    c = shopify_customer(_dict(customer_match_groups=""))
    assert c.link_existing_customer("jane@x.co") is False
    frappe.db.set_value.assert_not_called()


@test
def no_email_means_never_link():
    c = shopify_customer(_dict(customer_match_groups="Cash"))
    assert c.link_existing_customer(None) is False and c.link_existing_customer("") is False


@test
def marketing_tick_saves_customer_once_and_never_unticks():
    c = shopify_customer(_dict(marketing_consent_field="add_to_mailing_list"))
    frappe.get_meta.return_value.has_field.return_value = True
    cust = _dict(add_to_mailing_list=0)
    cust.set = lambda k, v: cust.__setitem__(k, v)
    cust.flags = _dict()
    cust.save = mock.MagicMock()
    with mock.patch.object(customer.ShopifyCustomer, "get_customer_doc", return_value=cust):
        c.record_marketing_consent()
        assert cust["add_to_mailing_list"] == 1 and cust.save.call_count == 1
        c.record_marketing_consent()  # already ticked: no second save
        assert cust.save.call_count == 1


@test
def marketing_tick_skipped_when_field_not_set_up():
    c = shopify_customer(_dict(marketing_consent_field=""))
    with mock.patch.object(customer.ShopifyCustomer, "get_customer_doc") as g:
        c.record_marketing_consent()
    g.assert_not_called()


@test
def shop_customer_address_never_overwritten():
    c = shopify_customer(_dict())
    frappe.get_all.return_value = []  # the customer has no address made by the connector
    with mock.patch.object(customer.ShopifyCustomer, "get_customer_doc", return_value=_dict(name="CUST-OLD")), \
            mock.patch.object(customer.ShopifyCustomer, "create_customer_address") as create:
        c._update_existing_address("Jane B", {"address1": "1 Web St", "city": "Cape Town"}, "Billing", "jane@x.co")
    create.assert_called_once()
    filters = frappe.get_all.call_args.kwargs["filters"]
    assert filters[constants.ADDRESS_ID_FIELD] == ["is", "set"] and filters["link_name"] == "CUST-OLD"
    frappe.get_doc.assert_called_once()  # only the setting at construction, no Address loaded or changed


@test
def connector_address_is_updated_in_place():
    c = shopify_customer(_dict())
    addr = _dict(address_line1="old")
    addr.update = lambda vals: dict.update(addr, vals)
    addr.flags = _dict()
    addr.save = mock.MagicMock()
    frappe.get_all.return_value = ["ADDR-SHOPIFY"]
    frappe.get_doc.side_effect = lambda *a, **k: addr
    with mock.patch.object(customer.ShopifyCustomer, "get_customer_doc", return_value=_dict(name="CUST-1")), \
            mock.patch.object(customer.ShopifyCustomer, "create_customer_address") as create:
        c._update_existing_address("Jane B", {"address1": "2 New Rd"}, "Billing", "jane@x.co")
    create.assert_not_called()
    assert addr["address_line1"] == "2 New Rd" and addr.save.called


@test
def order_addresses_are_marked_as_from_shopify():
    f = customer._map_address_fields({"address1": "1 Web St"}, "Jane", "Shipping", "jane@x.co")
    assert f[constants.ADDRESS_ID_FIELD] == "order"
    f = customer._map_address_fields({"id": 4390, "address1": "1 Web St"}, "Jane", "Billing", None)
    assert f[constants.ADDRESS_ID_FIELD] == 4390


@test
def new_customer_keeps_email_for_next_time():
    c = shopify_customer(_dict())
    with mock.patch.object(customer.EcommerceCustomer, "create_customer_contact", return_value=_dict(name="CONT-1")), \
            mock.patch.object(customer.ShopifyCustomer, "get_customer_doc", return_value=_dict(name="CUST-NEW")):
        c.create_customer_contact({"first_name": "Jane", "email": "jane@x.co", "phone": "+27821234567"})
    frappe.db.set_value.assert_called_once_with("Customer", "CUST-NEW",
        {"email_id": "jane@x.co", "mobile_no": "+27821234567", "customer_primary_contact": "CONT-1"})


@test
def consent_read_from_current_and_old_shopify_fields():
    assert customer._accepts_marketing({"email_marketing_consent": {"state": "subscribed"}})
    assert customer._accepts_marketing({"accepts_marketing": True})
    assert not customer._accepts_marketing({"email_marketing_consent": {"state": "unsubscribed"}})
    assert not customer._accepts_marketing({})


# ------------------------------------------------------------------ customer pre-load

def load_one(data, synced=False, linked=False, sync_error=None):
    counts = {"already linked": 0, "linked by email": 0, "created": 0, "skipped (no email)": 0, "failed": 0}
    failures = []
    with mock.patch.object(customer, "ShopifyCustomer") as SC:
        c = SC.return_value
        c.is_synced.return_value = synced
        c.link_existing_customer.return_value = linked
        if sync_error:
            c.sync_customer.side_effect = Exception(sync_error)
        customer._load_one_customer(data, counts, failures)
    return counts, failures, c


@test
def preload_counts_each_outcome():
    assert load_one({"id": 1, "email": "a@x"}, synced=True)[0]["already linked"] == 1
    assert load_one({"id": 2, "email": "b@x"}, linked=True)[0]["linked by email"] == 1
    counts, failures, c = load_one({"id": 3, "email": "c@x"})
    assert counts["created"] == 1 and c.sync_customer.called
    counts, failures, c = load_one({"id": 4, "email": ""})
    assert counts["skipped (no email)"] == 1 and not c.sync_customer.called


@test
def preload_one_bad_customer_does_not_stop_the_rest():
    counts, failures, c = load_one({"id": 5, "email": "e@x"}, sync_error="Duplicate name")
    assert counts["failed"] == 1 and "Duplicate name" in failures[0]
    frappe.db.rollback.assert_called_once()


@test
def preload_ticks_mailing_list_only_with_consent():
    _c, _f, c = load_one({"id": 6, "email": "f@x", "email_marketing_consent": {"state": "subscribed"}}, synced=True)
    assert c.record_marketing_consent.called
    _c, _f, c = load_one({"id": 7, "email": "g@x"}, synced=True)
    assert not c.record_marketing_consent.called


@test
def preload_is_system_manager_only():
    with mock.patch.object(customer, "create_shopify_log", return_value=_dict(name="LOG9")):
        assert customer.load_shopify_customers() == "LOG9"
    frappe.only_for.assert_called_once_with("System Manager")
    assert frappe.enqueue.call_args.kwargs["job_id"] == "shopify_load_customers"


if __name__ == "__main__":
    width = max(len(n) for _s, n, _m in RESULTS)
    for status, name, msg in RESULTS:
        print(f"{status}  {name.ljust(width)}  {msg}")
    failed = [r for r in RESULTS if r[0] == "FAIL"]
    print(f"\n{len(RESULTS) - len(failed)} passed, {len(failed)} failed")
    sys.exit(1 if failed else 0)
