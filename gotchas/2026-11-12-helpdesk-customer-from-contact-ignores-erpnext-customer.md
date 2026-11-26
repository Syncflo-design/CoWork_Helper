# Helpdesk "auto set customer from contact" never fires for ERPNext customers

**Date:** 2026-11-12
**Domain:** Frappe Helpdesk / ERPNext — HD Ticket, Contacts
**Severity:** annoying (silent: every email ticket on nesterp had a blank Customer)

## Symptom

Email tickets on nesterp got the right Contact (matched on the sender address), but Customer stayed
blank, even though HD Settings > `auto_set_customer_from_contact` was on and the Contact was linked
to the ERPNext Customer.

## Cause

Helpdesk's `HDTicket.set_customer` (run in `before_validate`) uses `helpdesk.utils.get_customers`, which
only reads **HD Customer Member** rows (the Contacts table on an **HD Customer**). A Contact's Dynamic
Link to an ERPNext **Customer** is ignored. HD Customer is a separate list (it has an `erpnext_customer`
Data field and a `domain` field), so unless someone has mirrored the customer and added the contact as a
member, nothing matches.

Also: if `customer` is set and is not one of the contact's HD customers, `set_customer` **throws**
unless the current user is an agent (Administrator counts). Email pulls run as Administrator, so they are
safe. Portal tickets created by customers are not.

## Fix

Server Script, DocType Event, HD Ticket, **Before Insert** (runs before Helpdesk's `before_validate`):
skip if `customer` is already set or `via_customer_portal`. Otherwise:
1. Use the HD Customer whose `domain` matches the sender's domain, if any.
2. Otherwise find the sender's Contact (Contact Email table, not just the primary email), take its linked
   ERPNext Customer **only if there is exactly one**, and find or create the HD Customer for it
   (`erpnext_customer` = Customer name, name = customer name).
3. Wrap it all in try/except + `frappe.log_error`, so a failure never blocks ticket creation.

Live on nesterp as "HD Ticket - customer from sender".

## Why this is non-obvious

- The setting's name says "from contact", and the contact *is* linked to a customer, just not the
  Helpdesk kind.
- Creating a test HD Ticket over the API fires the site's "New support ticket" notice to the
  agents (presales@ + hello@ on nesterp). Acknowledgements to the sender were off, so nothing reached the
  customer. Check `send_acknowledgement_email` in HD Settings before testing with a real customer's address.

## See also

- `sites/nesterp.md`
