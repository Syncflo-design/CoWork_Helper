# Frappe v16 modern desk listview strips HTML from `formatters.<field>` return values

**Date:** 2026-05-11
**Domain:** Frappe v16 / ERPNext v16 — modern desk listview
**Severity:** day-killer (silent failure with no console error)

## Symptom

You register a list-view formatter to inject a custom HTML element (e.g. a clickable pill) into a column. The formatter IS called — but only the plain-text portion of its return value renders in the listview. All HTML tags are stripped.

Concrete repro, on `/desk/todo`:

```js
// Client Script on ToDo listview
frappe.listview_settings['ToDo'].formatters = {
    description(value, df, doc) {
        let base = frappe.utils.escape_html(value || '');
        if (doc.reference_type === 'CRM Lead' && doc.reference_name) {
            base += ` <a class="lead-pill" href="/desk/lead-activity/${doc.reference_name}">👤 ${doc.reference_name}</a>`;
        }
        return base;
    }
};
```

```js
// Verify by hand from the console:
frappe.listview_settings.ToDo.formatters.description(
    cur_list.data[0].description, null, cur_list.data[0]
)
// → returns the FULL string with the <a class="lead-pill">…</a> markup ✓
```

But inspect the rendered DOM in the listview row — only the plain text portion (`"description text 👤 CRM-LEAD-0001"`) is present. The `<a>` element is gone. No console error, no warning.

Same fate for `listview_settings.button` — set it, call `cur_list.refresh()`, no button is rendered. The hook appears to be ignored.

## Cause

v16's modern desk listview renders rows through Vue components rather than the v15 jQuery template path. The Vue cell renderer for text columns treats the formatter return value as a string and escapes/strips embedded HTML before insertion. Whatever HTML the legacy formatter contract used to honour, the modern-desk cell renderer no longer does.

We did not isolate the exact Vue component — verifying would require reading `frappe/frontend/src/desk/listview/...`. But the behaviour is consistent: formatter runs, value is computed, only the plain-text remainder reaches the DOM.

## Fix

**Don't depend on HTML from `listview_settings.formatters.*` in v16's modern desk listview.** Build a custom Frappe Page (`/desk/<your-page>`) that renders the list yourself and route there.

Reference build: `nest_crm_tasks` v0.0.3 — `nest_crm_tasks/page/my_activities/` replaces the standard `/desk/todo` for sales users. Each row gets a real clickable `[👤 CRM-LEAD-...]` pill on Lead-linked ToDos, which navigates to the Lead Activity Hub at `/desk/lead-activity/<lead>`.

If you can get away with plain-text-only enrichment (e.g. appending the Lead name to the description string), the formatter does work for that — but the moment you want a styled / clickable element, switch to a custom Page.

## Why this is non-obvious

The formatter still runs. `cur_list` still exists. `frappe.listview_settings.<DocType>.formatters.<field>(...)` returns the correct HTML when invoked by hand from the console. There's no error, warning, or deprecation notice. Visually the column renders almost-correctly because the text portion survives — easy to miss that the HTML tail got dropped if you weren't specifically looking for an interactive element.

False leads we chased before pivoting to a custom Page:

1. Bubble-phase click interceptor on the row — Frappe's own row-click handler registers first and navigates to the ToDo form before our handler runs. `stopImmediatePropagation` is useless when ours is the later handler.
2. Capture-phase listeners on `cur_list.$result[0]` and `document` — never fire on the row clicks. Same family as the navbar gotcha (`gotchas/2026-05-07-frappe-v16-modern-desk-click-interception.md`).
3. `listview_settings.formatters.description` returning HTML — the formatter IS invoked, but the modern-desk cell renderer strips the HTML (this gotcha).
4. `listview_settings.button` — ignored too. No button rendered after setting and `cur_list.refresh()`.

The pattern is clear in hindsight: **the v16 modern-desk listview honours very little of the classic `listview_settings` contract.** Don't fight it; build a Page.

## Detection recipe

1. From the console, invoke your formatter directly:
   ```js
   frappe.listview_settings['<DocType>'].formatters.<field>(
       cur_list.data[0].<field>, null, cur_list.data[0]
   )
   ```
   If it returns the expected HTML → the formatter is running.
2. Inspect the rendered DOM cell (`cur_list.$result[0].querySelectorAll('.list-row')[0]`). If only the text remains → HTML is being stripped by the renderer.
3. Confirmed. Stop tweaking the formatter; build a custom Page.

## See also

- `gotchas/2026-05-11-frappe-v16-modern-desk-listview-hooks-untrustworthy.md` — the broader pattern: most `listview_settings` hooks (`onload`, `formatters`, `button`, capture-phase clicks) are unreliable on v16 modern desk. Default to a custom Page.
- `gotchas/2026-05-07-frappe-v16-modern-desk-click-interception.md` — same family of v16-modern-desk JS hostility, at the navbar layer instead of the listview.
- `gotchas/2026-05-10-frappe-v16-page-api-drift.md` — what to watch out for when you DO write a custom Page (page.body is jQuery, `frappe.client.get_list` perm drift, etc.).
- `playbooks/frappe-custom-app-v16.md` — scaffolding the custom Page properly.
- Reference build: `nest_crm_tasks` repo at `https://github.com/Syncflo-design/nest_crm_tasks`, the `my_activities` page (`nest_crm_tasks/nest_crm_tasks/page/my_activities/`).
