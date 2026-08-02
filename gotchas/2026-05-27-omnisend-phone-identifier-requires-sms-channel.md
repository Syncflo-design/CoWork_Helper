# Omnisend v3 phone identifier requires an SMS channel block

**Date:** 2026-05-27
**Site:** `ardmore.jh.frappe.cloud`
**API:** Omnisend Classic v3 — `POST https://api.omnisend.com/v3/contacts`

## What bit us

Sent a phone identifier in the contacts payload without a `channels.sms` block:

```json
{
  "identifiers": [
    {
      "type": "email",
      "id": "user@example.com",
      "channels": { "email": { "status": "subscribed" } }
    },
    {
      "type": "phone",
      "id": "+27 11 555 0001"
    }
  ],
  ...
}
```

Omnisend returned **400 Bad Request**:
```json
{"error":"Provide sms channel for phone identifier."}
```

## Fix

Every identifier needs a `channels` block, even if you're not subscribing them. For phone identifiers where you don't have explicit SMS opt-in, use `nonSubscribed`:

```json
{
  "type": "phone",
  "id": "+27 11 555 0001",
  "channels": {
    "sms": { "status": "nonSubscribed" }
  }
}
```

Same rule applies in reverse — email identifiers need `channels.email`. Omnisend validates this strictly.

## Allowed `status` values for `channels.sms`

- `subscribed` — explicit opt-in (handle GDPR / TCPA implications)
- `nonSubscribed` — captured but not opted in
- `unsubscribed` — explicitly opted out

Use the same vocabulary for `channels.email`.

## Symptom-to-cause map

| Response | Cause |
|---|---|
| `403 Forbidden` (no body) or `{"error":"Forbidden"}` | Bad / missing `X-API-KEY` header. On Frappe Webhook this often means you tried Jinja in the header value — see [`2026-05-27-frappe-webhook-headers-not-jinja-rendered.md`](2026-05-27-frappe-webhook-headers-not-jinja-rendered.md). |
| `{"error":"Provide sms channel for phone identifier."}` | This gotcha — add `channels.sms.status`. |
| `{"error":"Provide email channel for email identifier."}` (extrapolated) | Same shape — add `channels.email.status`. |

## Related

Playbook: [`playbooks/frappe-webhook-to-omnisend.md`](../playbooks/frappe-webhook-to-omnisend.md) — template includes the conditional phone block with the correct SMS channel structure.
