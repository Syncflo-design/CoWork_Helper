# Frappe Webhook headers are NOT rendered through Jinja

**Date:** 2026-05-27
**Site:** `ardmore.jh.frappe.cloud`
**Frappe:** v16 (Python 3.14)

## What bit us

We tried to keep an Omnisend API key out of the plaintext `Webhook Header` row by setting the header value to `{{ frappe.conf.omnisend_api_key }}`, with the actual key in `site_config.json`. Looked clean, would have been ideal.

Result: Omnisend returned `403 Forbidden`. The literal string `{{ frappe.conf.omnisend_api_key }}` was sent in the `X-API-KEY` header — Jinja never expanded it.

## Why

Frappe's `Webhook` doctype renders **only two** fields through Jinja:

| Field | Jinja-rendered? |
|---|---|
| `webhook_json` (request body) | ✅ Yes |
| `request_url` (when `is_dynamic_url` is checked) | ✅ Yes |
| `webhook_headers[].value` | ❌ No — literal string |
| `webhook_headers[].key` | ❌ No — literal string |
| `condition` | Evaluated as Python (not Jinja) |

`webhook.get_webhook_headers()` returns `{h.key: h.value for h in self.webhook_headers}` with no `frappe.render_template()` call. There's no PR fixing this on `develop` as of this writing.

## Workarounds (best → worst)

1. **Accept the literal key in the header.** Lock down Webhook read perms to System Manager only. This is fine for single-admin sites — the field is already in the database; the only attack surface is "another admin browsing Webhook list." Add a comment in the Webhook description noting the key is in this header row.

2. **Promote to a custom app with a server-side `after_insert`/`on_update` hook.** The Python handler can read `frappe.conf.your_api_key` freely and call `requests.post(...)`. Worth it if you need richer logic anyway (retries, idempotency keys, unsubscribe sync). Overkill if you just want to hide one secret.

3. **Don't try to reference `frappe.conf` from a Webhook header.** Wastes time and leaves an empty/literal header that fails auth in confusing ways.

## How to detect this exact failure

- `Webhook Request Log` shows the response from the receiver — usually `401`/`403` with a generic auth error.
- The traceback in the `error` column will be the receiver's `raise_for_status()` failure, not a Jinja error.
- To confirm: temporarily put a literal key back in the header. If requests succeed, the header was the problem.

## Related

Playbook: [`playbooks/frappe-webhook-to-omnisend.md`](../playbooks/frappe-webhook-to-omnisend.md) — has a "Security note" section updated to point at this gotcha rather than recommending the `frappe.conf` route.
