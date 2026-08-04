# Custom JS appended to the standard POS Page doc intermittently kills the Return flow

**Date:** 2026-07-20 · **Site:** ardmoreceramics.c.frappe.cloud · **Area:** ERPNext v16 POS

## Symptom

In the POS, clicking **Recent Orders** (or a receipt inside it) sometimes shows the
order list but the summary panel on the right never opens — so the **Return**
button is unreachable and users conclude refunds are broken. Intermittent: works
on a fresh page load, tends to break after a sale has been completed in the same
POS session. Console shows:

```
TypeError: Cannot read properties of undefined (reading 'style')
    at eval (point_of_sale.js:62:113)
```

## Cause

The site's **Page doc `point-of-sale`** (a *standard* Page, `script` field edited
in the DB, author Paul Mata) has a sales-rep selector block appended after the
stock loader. Inside a `setTimeout` it does:

```js
for(var i =0; i<$('div[class="page-title"]').length;i++){
    $('div[class="page-title"]')[i].innerHTML += salesrep;
    $('span[class="indicator-pill no-indicator-dot whitespace-nowrap blue"]')[i].style.marginRight="10px";
}
```

Two bugs: (1) it loops over **every** `div.page-title` on the desk (nest-home's
included) but indexes the pill spans with the same `i` — fewer pills than titles
→ `[i]` is `undefined` → TypeError; (2) `innerHTML +=` re-parses the title node
and destroys event listeners. The crash coincides with the summary-open chain
and leaves `.past-order-summary` at `display:none`.

## Fix — what actually worked (2026-07-20)

**Dead ends first (all attempted, all futile):**
1. API edit of the Page doc → `Only Administrator can edit`.
2. UI edit as Administrator → the Script field doesn't render on Frappe Cloud
   (developer-mode-only field), and pressing Save on the form **wipes** the DB
   script column (the form's doc never loaded it).
3. Console `frappe.client.set_value` as Administrator → reports success, DB
   stays null — and irrelevant anyway, because **`getpage` serves the script
   from the app's files on the bench, not from the DB**. The block lives in
   Paul's `Mata101/server_script` app (his latest commit "fix: multiple pos
   title" is this exact code). DB edits can never change what tills load.

**The workaround that shipped:** a defensive shim in **our** `nest_help` app
(`public/js/nest_help.js`, loaded on every desk page via `app_include_js`).
Paul's loop only crashes when a `div[class="page-title"]` exists without a span
whose class attribute exactly equals
`indicator-pill no-indicator-dot whitespace-nowrap blue`. The shim appends a
hidden span with that exact class to every such title (initial pass + a
MutationObserver), so his indexed lookup always finds an element and never
throws. His feature keeps working; nothing of his is modified. nest_help
v0.0.2. Remove the shim if/when `Mata101/server_script` lands the proper fix
(reference version: [`sites/ardmore-pos-page-script-fixed.js`](../sites/ardmore-pos-page-script-fixed.js)).

## Lesson

Never append hand-written JS to a **standard** Page doc — it survives nowhere in
git, only Administrator can maintain it, and a crash inside it looks like a core
POS bug. Put POS customisations in an app's `app_include_js` (or a Client
Script) with defensive element checks, scoped to the page's own container.
