# Shopify item images (Russell, 3 Nov 2026): an item with no picture takes the picture its Shopify
# product shows, matched on item code = Shopify SKU (the same code Sage uses). Reads the public
# storefront feed, so no Shopify login is needed - but it only sees products that are live on the
# website. Never replaces a picture an item already has. Nightly; new Shopify products are picked
# up the next night.
# set_value, not save: no item hooks fire, and an item with an odd old value cannot block it.
STORE = "https://ardmore-design.com"

images = {}
page = 1
while page <= 40:
    try:
        r = frappe.make_get_request(STORE + "/products.json?limit=250&page=" + str(page))
    except Exception as e:
        frappe.log_error(message="Page " + str(page) + ": " + str(e)[:500], title="Shopify item images: feed failed")
        break
    products = (r or {}).get("products") or []
    if not products:
        break
    for p in products:
        first = ""
        if p.get("images"):
            first = p.get("images")[0].get("src") or ""
        for v in (p.get("variants") or []):
            sku = str(v.get("sku") or "").strip().upper()
            img = ((v.get("featured_image") or {}).get("src")) or first
            if sku and img and sku not in images:
                images[sku] = img
    page = page + 1

filled = []
if images:
    for i in frappe.db.sql("select name from `tabItem` where ifnull(image, '') = ''", as_dict=True):
        img = images.get(str(i.name).strip().upper())
        if img:
            frappe.db.set_value("Item", i.name, "image", img, update_modified=False)
            filled.append(i.name)

if filled:
    frappe.log_error(message=str(len(filled)) + " item(s) took their Shopify picture: " + ", ".join(filled[:200]), title="Shopify item images")
