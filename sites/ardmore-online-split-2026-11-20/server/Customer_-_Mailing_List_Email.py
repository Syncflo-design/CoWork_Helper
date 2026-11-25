# Server Script: DocType Event, Customer, Before Save.
# OMNISEND (Russell, 20 Nov 2026): the "Customer to Omnisend" webhook needs Add to Mailing List AND the
# mailing-list Email Address. A Shopify buyer who accepted marketing is ticked by the Shopify connector,
# which keeps the email on the customer's own email field, so copy it across when the mailing-list email
# is still empty. Nobody is ticked here: the tick comes only from the buyer's own consent (or staff).
# Shopify customers only (they carry a Shopify Customer Id): customers made at the shop tills are untouched.
if doc.get("shopify_customer_id") and doc.get("add_to_mailing_list") and not doc.get("custom_email_address") and doc.get("email_id"):
    doc.custom_email_address = doc.email_id
