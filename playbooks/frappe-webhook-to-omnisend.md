# Frappe Webhook → Omnisend (Contacts v3)

Push ERPNext customers into Omnisend's marketing list with **zero custom code** — built-in Frappe Webhook + a small client-script tweak. Verified live on `ardmore.jh.frappe.cloud` 2026-05-27.

## When to use this pattern

- You want new (or newly-flagged) customers automatically synced to Omnisend.
- You're OK with a hosted/upsert API call from the Frappe site (no message queue, no retry logic beyond Frappe's webhook background queue).
- You can tolerate the API key sitting in a Webhook Header row (or you'll lift it to `site_config.json`).

If you need richer logic — bidirectional sync, unsubscribe events back, audit trail with retries — promote to a custom app instead.

## What you need on the Customer doctype

Custom fields (one-off setup):

| Fieldname | Type | Why |
|---|---|---|
| `add_to_mailing_list` | Check | The opt-in flag the cashier ticks. |
| `custom_email_address` | Data | What the webhook reads. Mirror from `email_id` if the dialog only captures the standard field. |
| `custom_phone` | Phone | Optional. Sent as a second identifier if present. |

## Omnisend API shape (v3, classic API key auth)

- `POST https://api.omnisend.com/v3/contacts`
- Headers: `X-API-KEY: <key>`, `Content-Type: application/json`
- Body: at minimum one email identifier with `channels.email.status = "subscribed"`. Upsert by email — repeating the call updates rather than dupes.

```json
{
  "identifiers": [
    {
      "type": "email",
      "id": "user@example.com",
      "channels": { "email": { "status": "subscribed" } }
    }
  ],
  "firstName": "Customer Name",
  "tags": ["erpnext-pos"]
}
```

Successful response (201 new / 200 update):
```json
{"email":"user@example.com","contactID":"6a168074ab2ba7fcbda914ca","firstName":"Customer Name"}
```

## Webhook config

Doctype: **Webhook**, one record:

| Field | Value |
|---|---|
| `webhook_doctype` | `Customer` |
| `webhook_docevent` | `on_update` |
| `enabled` | ✓ |
| `condition` | `doc.add_to_mailing_list and doc.custom_email_address` |
| `request_url` | `https://api.omnisend.com/v3/contacts` |
| `request_method` | `POST` |
| `request_structure` | `JSON` |
| `timeout` | `5` |
| `webhook_headers` | `Content-Type: application/json`, `X-API-KEY: <your key>` |
| `webhook_json` | Jinja template (below) |

Jinja body template — uses `tojson` filter for safe escaping:

```jinja
{
  "identifiers": [
    {
      "type": "email",
      "id": {{ doc.custom_email_address | tojson }},
      "channels": {
        "email": { "status": "subscribed" }
      }
    }{%- if doc.custom_phone %},
    {
      "type": "phone",
      "id": {{ doc.custom_phone | tojson }},
      "channels": {
        "sms": { "status": "nonSubscribed" }
      }
    }{%- endif %}
  ],
  "firstName": {{ (doc.customer_name or '') | tojson }},
  "tags": ["erpnext-pos"]
}
```

**Why `channels.sms` on the phone identifier is non-optional:** Omnisend rejects with `400 — "Provide sms channel for phone identifier."` if you omit it. Use `nonSubscribed` when the customer only opted into email/mailing list, not SMS. Same rule for `channels.email` — every identifier needs its channel block. See [`gotchas/2026-05-27-omnisend-phone-identifier-requires-sms-channel.md`](../gotchas/2026-05-27-omnisend-phone-identifier-requires-sms-channel.md).

## Why `on_update`, not `after_insert`

If a Client Script sets `add_to_mailing_list` (or any custom field) **after** the dialog saves the Customer — e.g. via `frappe.client.set_value` because the field isn't in the dialog itself — then at `after_insert` time the flag is still 0 and the condition fails. `on_update` catches the follow-up write. The same is true for any post-create mirroring like `email_id` → `custom_email_address`.

Tradeoff: `on_update` fires on **every** customer edit afterwards too — price list change, address tweak, anything. Because Omnisend's `/v3/contacts` is upsert-by-email, this is harmless: each fire returns the same `contactID`. If chattiness ever matters, gate it in a custom app with a `last_synced_at` field.

## Client-script considerations (POS New Customer flow)

The POS "Create New Customer" dialog doesn't always expose custom fields. Russell's `POS Customer UX` script injects a footer "Add to Mailing List" checkbox and applies the flag via `frappe.client.set_value` after the dialog closes. Two adjustments matter for the webhook to fire:

1. **Validate at Save:** if the checkbox is ticked but the email input is empty, `e.preventDefault() + e.stopImmediatePropagation()` on the capture-phase click handler — and toast a red message. Otherwise you'll create flagged customers with no email and the webhook condition silently never matches.
2. **Mirror email:** after the Customer is created, read whichever email field the dialog populated (`email_id` standard or `custom_email_address` custom) and `set_value` it onto `custom_email_address` if empty. Then `set_value` the flag. Two `on_update`s, but the webhook condition only passes on the second one → one Omnisend POST.

Both live in `Client Script: POS Customer UX` on `ardmore.jh.frappe.cloud`.

## Verifying the integration

1. Pick (or create) a customer with the flag set.
2. Update its `custom_email_address` (via the desk, or `frappe.client.set_value`).
3. List **Webhook Request Log** filtered by `webhook = "<your webhook name>"`, order by creation desc.
4. The `response` column should contain Omnisend's `{"email":"...","contactID":"...","firstName":"..."}`. Empty `error` column = success.
5. Confirm in Omnisend's UI under the tag you set.

## Security note — where to keep the API key

The classic Frappe Webhook stores header values in **Webhook Header** child rows in plaintext, visible to anyone with read perms on the Webhook doctype (typically `System Manager`). Fine for single-admin sites; not fine if Webhook list is shared.

**You cannot reference `site_config.json` from a header value.** Frappe Webhook only renders Jinja in the body (`webhook_json`) and the URL (when `is_dynamic_url=1`). Header values are sent literally — `{{ frappe.conf.omnisend_api_key }}` will be POSTed as that exact string and the receiver returns `403 Forbidden`. Verified live on `ardmore.jh.frappe.cloud` Frappe v16. See [`gotchas/2026-05-27-frappe-webhook-headers-not-jinja-rendered.md`](../gotchas/2026-05-27-frappe-webhook-headers-not-jinja-rendered.md).

So your options are:

1. **Live with the literal key in the Webhook Header row.** Lock Webhook doctype read perms to System Manager. Acceptable on single-admin sites.
2. **Promote to a custom app.** A Python `on_update` hook can read `frappe.conf.omnisend_api_key` freely and call `requests.post(...)`. Worth it if you also want retries, idempotency, or unsubscribe-back sync.

## Known gotchas

- **Omnisend docs ship two APIs.** The new 2026 OAuth Bearer API lives at `/api/contacts`. The classic key-based v3 API used here is `/v3/contacts`. API keys starting with `<projectID>-<token>` are v3. Don't mix them.
- **`tojson` filter is your friend.** Hand-building JSON strings in Jinja breaks on names with quotes/apostrophes. Always `| tojson` string values.
- **Webhook fires under the modifying user's perms.** Tested fine for site Admin; if a portal user could ever update Customer, audit the resulting traffic.
