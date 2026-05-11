# Frappe v16 — custom Page JS broken: `wrapper.main` gone, `page.body` is jQuery, `frappe.client.get_list` field-permission tightened

**Date:** 2026-05-10
**Domain:** custom-app / Frappe v16 / desk Page JS
**Severity:** day-killer (three sequential gremlins, ~1 hour to clear)
**Status:** ✅ Fix verified live on `blomoplastics.jh.frappe.cloud` 2026-05-10 (`wo_wip` v1.2.0). Page renders cards, click-into-detail works, both Work Order form buttons (Start Operator Run, Open WIP Screen) trigger correctly.

## Symptom

A custom **Page** (not a DocType form — a `frappe.pages[name]` desk page) that worked fine on Frappe v15 renders as a completely blank grey area on v16. Sidebar and tab title look right; content area is empty. No spinner, no cards, no error message visible to the user.

DevTools console shows one of three errors in this exact sequence as you fix each one:

1. `TypeError: Cannot read properties of undefined (reading 'appendChild') at new <PageClass> (...page.js:NNN)`
2. After fixing #1: `Uncaught (in promise) TypeError: mountTarget.appendChild is not a function`
3. After fixing #2: `Field not permitted in query: <fieldname>` (e.g. `item_code` on Work Order)

`bit me on:` `wo_wip`'s `Works Order - WIP` page, ported live to `blomoplastics.jh.frappe.cloud` after migrating from v15 to v16.

## Cause

Three independent v15→v16 API drifts in the same code path:

### 1. `wrapper.main` was dropped

Old v15 pattern:

```js
frappe.pages["my-page"].on_page_load = function (wrapper) {
    frappe.ui.make_app_page({ parent: wrapper, title: "...", single_column: true });
    const page = wrapper.page;
    new MyPageClass(page, wrapper);
};

class MyPageClass {
    constructor(page, wrapper) {
        this.container = document.createElement("div");
        wrapper.main.appendChild(this.container);   // ← v15: wrapper.main was a DOM element
    }
}
```

In v16's modern desk, `wrapper` no longer has a `.main` property — the page-content element moved to `page.body`. Result: `undefined.appendChild` → page never renders.

### 2. `page.body` is a jQuery object, not a raw DOM element

Naïve fix from #1:

```js
page.body.appendChild(this.container);   // ← still wrong, page.body is $(...)
```

`page.body` in v16 is wrapped in jQuery. jQuery objects have `.append()` (with no `Child`), not `.appendChild()`. Calling `.appendChild` on it throws the second error.

### 3. `frappe.client.get_list` tightened field-level permissions

v16 added stricter checks on the `frappe.client.get_list` whitelisted RPC. The list of fields you can request is now intersected with the user's column-level permissions on that DocType. Some fields that were freely queryable in v15 — including `item_code` on `Work Order` — now throw `frappe.exceptions.PermissionError: Field not permitted in query: item_code` for non-System Manager users (and even for System Manager in some configs).

## Fix

All three fixes go in the same custom Page file. The third one is per-field — drop or move offending fields out of the list query.

```diff
  class MyPageClass {
      constructor(page, wrapper) {
          this.container = document.createElement("div");
          this.container.className = "ww-wrap";
-         wrapper.main.appendChild(this.container);
+         // Frappe v16: page.body is a jQuery object (not a DOM element).
+         // v15 had wrapper.main as a raw element. Wrap in $() so jQuery's
+         // .append() handles both regardless of desk version.
+         const $mount = $((page && page.body) || (wrapper && wrapper.main) || wrapper);
+         $mount.append(this.container);
      }

      async renderList() {
          const wos = await frappe.call({
              method: "frappe.client.get_list",
              args: {
                  doctype: "Work Order",
-                 fields: ["name", "item_name", "item_code", "status", "qty",
-                          "produced_qty", "expected_delivery_date"],
+                 // v16: do NOT request item_code — frappe.client.get_list
+                 // throws "Field not permitted in query: item_code" for most
+                 // users. item_name is always populated and is what we display.
+                 fields: ["name", "item_name", "status", "qty",
+                          "produced_qty", "expected_delivery_date"],
              },
          });
      }
  }
```

If you genuinely need a restricted field for a non-Manager user, the right path is a backend whitelisted method that does the query server-side and returns the data — `frappe.client.get_list` from JS will not bypass the field-permission check.

## Why this is non-obvious

- All three errors look unrelated at first glance — TypeError, TypeError, PermissionError. You think you're hitting three independent bugs when really it's one theme: v15-era page code colliding with v16's tightened API.
- The user-facing symptom is just "blank page". No visible error, no Frappe Cloud-side log entry, no patch failure. You only see the real error if you open DevTools Console — and the **first** error swallows the rest, so you fix it, get a new error, fix that, get a third. Could easily take 2-3 deploy cycles to peel the layers.
- `page.body` being a jQuery object is **inconsistent with `wrapper.main` from v15** which was a DOM element. The naïve "search-and-replace `wrapper.main` → `page.body`" produces broken code that compiles fine but fails at runtime.
- `frappe.client.get_list` field-permission errors look like the field doesn't exist or is hidden. The error message says "permitted", not "exists" — but you instinctively check the DocType field list first and waste minutes confirming `item_code` is right there in the schema.
- Frappe Cloud's bench Update doesn't surface these to the operator at all. The migrate succeeds, the asset bundle is rebuilt, the dashboard shows green — and the user just sees a blank page. You have to know to open DevTools to find anything.

## Tell-tale (how to spot this fast)

When porting a v15 custom Page to v16, **before** even loading the page, search-and-replace audit:

```bash
grep -n "wrapper\.main" apps/<your_app>/<your_app>/<module>/page/<page>/<page>.js
grep -n "appendChild\|insertBefore\|removeChild" apps/<your_app>/<your_app>/<module>/page/<page>/<page>.js
grep -n "frappe\.client\.get_list" apps/<your_app>/<your_app>/<module>/page/<page>/<page>.js
```

- Any `wrapper.main` hit needs the `page.body` fallback wrapped in jQuery.
- Any raw DOM `appendChild` / `insertBefore` / `removeChild` against a Frappe-supplied node should switch to jQuery.
- Any `frappe.client.get_list` should have its `fields:` array audited — at minimum, drop `item_code` if querying Work Order; check the user's role gives Read at field level if you need a sensitive field.

## Reference fix template (drop into any v16 page)

```js
frappe.pages["my-page"].on_page_load = function (wrapper) {
    frappe.ui.make_app_page({ parent: wrapper, title: "My Page", single_column: true });
    const page = wrapper.page;
    new MyPageClass(page, wrapper);
};

class MyPageClass {
    constructor(page, wrapper) {
        this.page    = page;
        this.wrapper = wrapper;

        this.container = document.createElement("div");
        this.container.className = "my-wrap";
        // v15-or-v16-safe mount: page.body is jQuery in v16, wrapper.main was DOM in v15
        const $mount = $((page && page.body) || (wrapper && wrapper.main) || wrapper);
        $mount.append(this.container);

        page.set_secondary_action("Refresh", () => this.render(), "refresh");
        this.render();
    }

    async render() { /* ... */ }
}
```

## See also

- Gotcha: `gotchas/2026-05-08-frappe-patches-txt-needs-both-section-headers.md` — same kind of v16-strictness trap, also surfaces only via the migrate log.
- Gotcha: `gotchas/2026-05-07-frappe-v16-modern-desk-click-interception.md` — the v16 modern desk navbar gotcha; complementary read.
- Playbook: `playbooks/frappe-custom-app-v16.md` — should add a "Custom desk Pages — v15-to-v16 port checklist" section pointing at this gotcha.
- Source: search `frappe/public/js/frappe/views/page/page.js` for `body` and `make_app_page` to see what v16 actually exposes.
