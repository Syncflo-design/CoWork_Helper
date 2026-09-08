# "Price List Standard Selling is disabled" on every POS return — Selling Settings still pointed at the disabled list, and the fix hid behind Frappe's per-user boot cache

**Date:** 2026-09-07 · **Site:** ardmoreceramics.c.frappe.cloud · **Area:** ERPNext v16 POS / Frappe caching · **Severity:** annoying (and a time sink)

## Symptom

Clicking **Return** on a POS invoice (and sometimes New Invoice after a return)
pops a red *Message: Price List Standard Selling is disabled or does not exist*.
The return still proceeds, so cashiers learn to click it away. Console shows the
throw coming from `erpnext.stock.get_item_details.apply_price_list`.

## Cause

`Standard Selling` was deliberately disabled on 2026-07-28 (Ardmore prices per
company list). But **Selling Settings → Default Price List** still said
`Standard Selling`. ERPNext's client-side transaction code seeds
`selling_price_list` from `frappe.sys_defaults.selling_price_list` (boot) before
the POS Profile's list is applied, and `apply_price_list` throws on a disabled
list. The POS Profile then overrides it, so the sale works — you just get the
popup.

## Fix

1. Selling Settings → Default Price List = `Default Price List` (any enabled ZAR
   list; POS Profiles override it anyway). Saving Selling Settings writes the
   `__default` DefaultValue row — verified via `frappe.db.get_default`.
2. **The browser kept showing the old value for 20 minutes after that.**
   Frappe v16 caches each user's whole bootinfo in redis (`bootinfo` hash keyed
   by user, served with `from_cache: 1`). Saving Selling Settings does NOT clear
   it. Clear it by saving the **User** record (`clear_user_cache`) or having the
   user run their own *Clear Cache* (`frappe.sessions.clear`). Saving System
   Settings triggers a site-wide clear if you need everyone.
3. Then open a **new tab**. A POS tab with a draft invoice refuses to reload
   (beforeunload), and the desk SPA keeps the old `frappe.boot` — I chased a
   phantom for 15 minutes because `location.reload()` was silently not running.
   `frappe.boot.from_cache` tells you whether the server served a cached boot.

## Still open (needs Ardmore's decision)

The live POS Profiles **Airport, Caversham and Joburg** have
`selling_price_list = Standard Selling` (disabled). Those tills will hit
"price not set" (nest_home's R0.01 sentinel) until each is pointed at its real
list (Home - Airport Price? Home - Retail Price? Ceramics - Retail?). Do not
guess — ask which list each store sells from.

## Why this is non-obvious

- Four different server reads (`get_single_value`, `get_doc`, raw SQL,
  `get_default`) all said the new value while the browser said the old one.
  `fetch('/desk/…')` from inside the page even returned fresh HTML, because the
  request ran on a worker that had rebuilt the boot — the tab itself had not.
- Frappe's whitelisted `frappe.client.set_default` / `get_default` no longer
  exist in v16, and `DefaultValue` cannot be listed via the API user. A
  throw-away **API Server Script** with `frappe.db.sql` (read-only) +
  `frappe.db.get_default` is the quickest way to see what the server believes.
- `frappe.cache` is not exposed in `safe_exec` (`'NoneType' object is not
  callable`), and neither is `frappe.clear_cache` — clear caches by saving the
  documents whose hooks clear them.

## See also

- `gotchas/2026-09-07-pos-invoice-client-scripts-run-inside-pos-page.md`
- `gotchas/2026-06-10-server-script-sandbox-and-xlsx.md`
