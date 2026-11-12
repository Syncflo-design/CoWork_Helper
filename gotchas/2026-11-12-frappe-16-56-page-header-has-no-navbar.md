# Frappe 16.56: there is no top navbar; the page head is the header, and one hook reaches every view

**Date:** 2026-11-12
**Domain:** Frappe v16.56 desk / custom-app global JS
**Severity:** annoying

## Symptom

Asked for a Home button "in the page header bar on every page". Older notes said to keep
widgets out of `header.desktop-navbar` (click interception, gotcha 2026-05-07). On 16.56 that
element does not exist at all, so there is nowhere obvious to put it.

## Cause

16.56 has no top navbar. The top bar of each view is that page's own `.page-head`, built by
`frappe.ui.Page.make()` (`add_main_section` renders the `page` template, then
`setup_main_sidebar_toggle`). Forms, lists, reports (`frappe.make_page`) and Workspaces
(`frappe.standard_pages.Workspaces`) all go through `frappe.ui.make_app_page` -> `new frappe.ui.Page`.

Layout of `.page-head .page-title`: `button.sidebar-toggle-btn.navbar-brand` (CSS hides it at
>= 992px), then `.title-area` with the `nav.es-breadcrumbs` title.

## Fix

From an `app_include_js`, wrap the prototype once and also cover pages built before the file ran:

```js
var make = frappe.ui.Page.prototype.make;
frappe.ui.Page.prototype.make = function () {
	var result = make.apply(this, arguments);
	add_button(this.wrapper);   // find .page-head .page-title, insert after .sidebar-toggle-btn
	return result;
};
$(document).on("app_ready", function () { add_button(document.body); });
```

Plain jQuery click handlers on a button there receive real mouse clicks (tested 2026-11-12).
An empty route renders `frappe.views.pageview.show("")`, which opens the desk Page named
`boot.home_page`. On nest_home sites route to `frappe.boot.nest_home_landing || frappe.boot.home_page`:
nest_home only puts Page landings in `home_page`, route landings (`query-report/...`) live in
`nest_home_landing`. Icons: `frappe.utils.icon("house", "md")` (Lucide sprite).
Live example: nest_home 0.0.38 `public/js/nest_home_redirect.js`.

## Why this is non-obvious

- The 2026-05-07 navbar gotcha points you away from the header entirely; it predates 16.56.
- `frappe.ui.Page.prototype` methods can't be dumped through the Chrome extension (output
  blocked). Pull `/assets/frappe/dist/js/desk.bundle.<hash>.js` with curl (name from
  `assets.json`) and grep it instead.

## See also

- `gotchas/2026-05-07-frappe-v16-modern-desk-click-interception.md`
- `gotchas/2026-11-12-frappe-16-56-saved-layouts-and-text-button-labels.md`
