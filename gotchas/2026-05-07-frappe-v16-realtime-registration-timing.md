# Frappe v16: realtime listeners must be registered AFTER socket.connected

**Date:** 2026-05-07
**Bit me on:** `nest_theme` v0.3.0. The shipped `app_include_js` bundle contained `frappe.realtime.on('syn_palette_changed', cb)` calls that ran early (gated only on `frappe.realtime.on` existing). Diagnostic `Object.keys(frappe.realtime.socket._callbacks).filter(k => k.includes('syn'))` after page load returned 0 listeners for the event we registered. A manual `frappe.realtime.on('syn_palette_changed', ...)` pasted in console at the same moment WORKED — confirming `frappe.realtime.on` itself is functional, just our timing was wrong.

## Symptom

You include realtime listeners in your app's `app_include_js` bundle. Console events log `palette_event` for any manual `.on()` listener you paste later, but your shipped listener never fires:

```js
const cbs = frappe.realtime.socket._callbacks;
(cbs['$your_event'] || []).length   // → 0   (your shipped one missing)
```

After re-pasting the same `frappe.realtime.on('your_event', cb)` from the console, the count becomes 1 and that one fires correctly on every subsequent event.

## Root cause

Frappe v16's realtime layer initialises in stages:
1. `frappe.realtime` object exists early as a stub (probably so other early code can call `.on()` without errors).
2. The actual socket connects asynchronously.
3. Once connected, Frappe likely rebuilds or replaces the realtime layer's state — and your early stub registrations get thrown out.

By the time the user's manual `.on()` runs (much later, in the console), Frappe is fully initialised and the registration sticks.

## Fix

Defer registration until the socket is actually connected. Also re-register on `reconnect` so listeners survive disconnect cycles:

```js
function registerRealtime() {
  frappe.realtime.on('your_event', yourHandler);
}

function attachRealtime() {
  if (!window.frappe || !frappe.realtime || !frappe.realtime.socket) {
    setTimeout(attachRealtime, 500);
    return;
  }
  const sock = frappe.realtime.socket;
  if (sock.connected) {
    registerRealtime();
  } else {
    sock.on('connect', registerRealtime);
  }
  sock.on('reconnect', registerRealtime);
}
attachRealtime();
```

Don't gate on `frappe.realtime.on` existing — that's true very early. Gate on `frappe.realtime.socket.connected`.

## Detection recipe

Whenever a shipped realtime listener doesn't fire:

1. Console:
   ```js
   const cbs = frappe.realtime.socket._callbacks || {};
   Object.keys(cbs).filter(k => k.toLowerCase().includes('your_keyword'))
   ```
   If returns `[]` → your listener never registered. Apply the fix above.

2. Sanity check that `frappe.realtime.on` works at all by manually pasting your registration in the console. If THAT works, registration mechanism is fine; only your timing is wrong.

3. If even the manual registration doesn't trigger your callback, the issue is server-side (event isn't being published, room scoping wrong, `after_commit=True` not firing).

## Cross-reference

- `projects/theme_studio/SCOPE.md` § v0.3.1 — the fix in the nest_theme codebase.
- `gotchas/2026-05-07-frappe-v16-modern-desk-click-interception.md` — different v16 gotcha, click events at navbar level.
