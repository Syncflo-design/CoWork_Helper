# Frappe v16 modern desk navbar swallows mouse clicks — even at document-level capture phase

**Date:** 2026-05-07
**Bit me on:** `nest_theme` v0.1 → v0.1.1 → v0.1.2. Toolbar widgets (density segment + font scaler) injected as `<div>` siblings of `header.desktop-navbar .desktop-notifications` rendered correctly, but **mouse clicks** never fired our handlers. Programmatic `el.click()` from the console DID fire them. Three escalating fix attempts all failed.

## Symptom

Build a button in the v16 modern desk navbar (anywhere inside `header.desktop-navbar`). Real mouse clicks don't trigger your handlers. Programmatic `.click()` does. So:

```js
// Console:
const btn = document.querySelector('.your-custom-button');
const before = document.body.className;
btn.click();
console.log(document.body.className !== before);  // → true ✓
```

But:

```
[user clicks the same button with mouse]  →  nothing happens
```

## Three things that didn't work

1. **Bubble-phase `addEventListener('click', fn)` on the button.** v0.1.x. Doesn't fire.
2. **MutationObserver to keep widget alive across re-renders.** Widget DOES survive (and Stage 1 console probes confirm `widget_li_present: true` continually), but clicks still don't fire.
3. **Document-level `addEventListener('click', fn, { capture: true })` with `e.stopPropagation()`.** v0.1.2. Should run before any bubble-phase Frappe handlers and prevent them from also firing. Still nothing — our capture handler doesn't even fire on real mouse clicks.

A defensive `mousedown` capture listener with `stopPropagation` was added on top of the click capture handler. Also nothing.

## Likely cause

Frappe v16 desk uses Vue under the hood. Theory:
- Vue's event system attaches listeners with `{ capture: true }` on `window` or `document` very early in app boot — possibly before our `app_include_js` runs, possibly via passive listeners that intercept events before any user-script capture handler can react.
- OR there's pointer-events / focus-trap manipulation on navbar children that consumes the click before it bubbles into the regular DOM event path.
- OR the navbar children sit inside a Vue portal / teleport that's rendered via JSX into a different DOM root, and our injected elements are technically in the wrong tree to receive bubbled events.

We did not isolate the exact mechanism — verifying would require reading Frappe v16's `frontend/src/desk` Vue source.

## What worked: don't fight it

`nest_theme` v0.2.0 dropped the toolbar widgets entirely. The theme is now apply-only (palette body class + logo swap) — no interactive controls in the navbar. This sidestepped the whole problem.

For future widget work in v16: don't render into `header.desktop-navbar`. Options worth trying:
- Render widgets in a fixed-position panel **outside** the navbar (e.g. bottom-right floating, top-right modal, Frappe's existing notification panel).
- Use Frappe's native page-action API (`frm.add_custom_button` etc.) which goes through their own dispatch.
- Build a Frappe page (`/app/<your-page>`) instead of a navbar widget.

## Detection recipe

Whenever a click handler in the navbar isn't firing:

1. Console: `el.click()` programmatically. If this triggers your handler → it's not a binding issue, it's mouse-event interception.
2. Try `addEventListener('click', fn, { capture: true })` on `document`. If still nothing → Frappe is consuming the event before any document-level listener.
3. Try `mousedown` instead of `click`. If still nothing → it's not just a `click` event problem, mouse events themselves aren't reaching your handlers.
4. Inspect parent `pointer-events` style — if it's `none`, that explains it. (Wasn't the case here.)
5. At this point — pivot. Render widgets outside the navbar.

## Cross-reference

- `projects/theme_studio/SCOPE.md` § v0.2.0 — full record of the build log (v0.1 → v0.1.2 → v0.2.0 scope cut).
- `sites/nesterp.md` — installation notes for `nest_theme` on `Syncflo_internal_V16`.
