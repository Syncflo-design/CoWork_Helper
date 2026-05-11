# Most `listview_settings` hooks on Frappe v16 modern desk are unreliable — default to a custom Page

**Date:** 2026-05-11
**Domain:** Frappe v16 / ERPNext v16 — modern desk listview
**Severity:** day-killer (meta-gotcha — cuts a whole class of failed approaches off at the knees)

## Symptom

You try to add non-trivial custom UX to a standard listview (e.g. `/desk/todo`) via the classic `frappe.listview_settings['<DocType>']` Client Script contract. **Most hooks either don't fire, fire too late, or have their output silently mangled** by the v16 modern-desk renderer.

Observed in this session (May 2026, Frappe v16.17.0):

| Hook | Status on v16 modern desk |
|---|---|
| `listview_settings.onload(listview)` | Fires, but `listview` shape differs from v15 — some methods missing |
| `listview_settings.refresh(listview)` | Fires |
| `listview_settings.formatters.<field>` | Fires, but **HTML stripped to plain text** before insertion (see sibling gotcha) |
| `listview_settings.button` | **Ignored.** Button never renders even after `cur_list.refresh()` |
| `listview_settings.add_fields` | Works |
| `listview_settings.get_indicator` | Works (returns colour name + label + filters) |
| Bubble-phase `addEventListener('click', fn)` on `.list-row` | Fires, but **after** Frappe's own row-click handler has already navigated away |
| Capture-phase `addEventListener('click', fn, { capture: true })` on `cur_list.$result[0]` or `document` | **Never fires** on row clicks. Same family as the navbar interception gotcha (2026-05-07) |
| `cur_list.data` mutation + manual re-render | Inconsistent — Vue reactivity may or may not pick up changes depending on the field |

The pattern: **anything that needs to inject interactive DOM or pre-empt a user click on a list row is untrustworthy.**

## Cause

v16's modern desk renders the listview through a Vue component tree rather than the v15 jQuery template path. The classic `listview_settings` contract was a v15-era set of hook points into the jQuery rendering and click dispatch. The Vue replacement honours some of them as a compatibility shim, but:

- HTML returns are sanitised to text by the cell renderer.
- The Vue dispatch consumes row-click events before they bubble into the document-level path your capture listener might attach to.
- Layout-level hooks like `button` appear to have been dropped without replacement.

We did not isolate which specific Vue component is responsible — verifying would mean reading `frappe/frontend/src/desk/listview/...` source. But the behavioural envelope is consistent across multiple hooks.

## Fix

**Default to building a custom Frappe Page for any non-trivial custom UX in v16.**

- A Frappe Page (`/desk/<your-page>`, file layout under `<app>/<module>/page/<page>/<page>.{json,py,js,css}`) runs in your own JS context. You control the DOM, the click handlers, the data fetch, the filters. No Vue listview to fight.
- Pages do come with their own gotchas — `page.body` is jQuery in v16, `frappe.client.get_list` has tightened field-level perms (see `gotchas/2026-05-10-frappe-v16-page-api-drift.md`) — but those are tractable, unlike the listview-hook quagmire.
- For nav-level integration, replace the workspace shortcut for the standard DocType with a Page link.

Reference build: `nest_crm_tasks` v0.0.3 — `my_activities` page (`/desk/my-activities`) replaces the standard `/desk/todo` for sales users, with clickable Lead pills that the listview formatter couldn't produce.

When IS it OK to use `listview_settings`?
- `add_fields` to fetch extra columns into `cur_list.data` — fine.
- `get_indicator` for colour-coded status pills — fine.
- `onload`/`refresh` for read-only metadata wiring (loading filters, setting page title) — fine.
- `formatters.<field>` for **plain-text** enrichment only (e.g. appending a name suffix) — fine.

Anything beyond that, build a Page.

## Why this is non-obvious

The Frappe docs still describe `listview_settings` as the canonical hook surface for listview customisation. There's no v15→v16 migration warning, no deprecation notice in the console. Most of the hooks even appear to fire (their function is invoked), which sends you down a long path of tweaking inputs/outputs trying to figure out why nothing renders — when the answer is that the Vue renderer downstream just isn't honouring your output.

In a typical debugging session you'll burn time on:
- "Maybe my CSS selector is wrong" — no, the DOM element isn't there at all.
- "Maybe I need to `cur_list.refresh()`" — refresh works, nothing changes.
- "Maybe my click handler needs `stopPropagation`" — capture-phase doesn't even fire.
- "Maybe a MutationObserver to re-inject after Vue's re-render" — element gets injected, then stripped on next render, then re-injected, infinite loop.

The cheap signal that you're in this trap: **your formatter returns HTML when invoked from the console, but the rendered DOM only has the plain text.** As soon as you see that, stop and pivot to a Page.

## Detection recipe

Bail out of `listview_settings` for the current hook if any of these are true:

1. Your `formatters.<field>` returns an HTML string when console-invoked, but only text shows in the rendered row → pivot to Page.
2. Your `listview_settings.button` setting doesn't produce a button in the toolbar after `cur_list.refresh()` → pivot.
3. Your row-click handler doesn't fire before Frappe's navigation → pivot.
4. Your capture-phase document listener doesn't see the row click → pivot.

Don't spend more than 30 minutes total trying to bend `listview_settings` to non-trivial UX. Scaffolding a Page is 1-2 hours and gives you something you fully control.

## See also

- `gotchas/2026-05-11-frappe-v16-listview-formatters-stripped-to-text.md` — the specific listview-formatter-HTML-stripped case that motivated this meta-gotcha.
- `gotchas/2026-05-07-frappe-v16-modern-desk-click-interception.md` — same family, at the navbar layer (toolbar widgets there are also a dead end).
- `gotchas/2026-05-10-frappe-v16-page-api-drift.md` — what to watch for when you DO build the custom Page (page.body is jQuery, `frappe.client.get_list` field perms, etc.).
- `playbooks/frappe-custom-app-v16.md` — file layout for the custom Page route.
- Reference build: `nest_crm_tasks` repo at `https://github.com/Syncflo-design/nest_crm_tasks`. The `my_activities` page (`nest_crm_tasks/nest_crm_tasks/page/my_activities/`) is the worked example of "give up on the listview and build a Page".
