# ONE-OFF (Russell, 2026-10-21): at 18:05 queue the full two-year Sales History load,
# three companies x ten three-month ranges, then switch this script off. Each pull
# replaces its own date range, so nothing doubles up with the four already loaded.
ranges = [
    ["2024-04-01", "2024-06-30"], ["2024-07-01", "2024-09-30"], ["2024-10-01", "2024-12-31"],
    ["2025-01-01", "2025-03-31"], ["2025-04-01", "2025-06-30"], ["2025-07-01", "2025-09-30"], ["2025-10-01", "2025-12-31"],
    ["2026-01-01", "2026-03-31"], ["2026-04-01", "2026-06-30"], ["2026-07-01", "2026-10-21"],
]
companies = ["Home", "Ceramics", "Fashion"]
queued = 0
for company in companies:
    for r in ranges:
        frappe.call("nest_sales_history.api.pull_sage_invoices", company=company, from_date=r[0], to_date=r[1])
        queued = queued + 1
frappe.db.set_value("Server Script", "sales-history-backfill-once", "disabled", 1)
frappe.db.commit()
frappe.log_error(message="Queued " + str(queued) + " Sales History pulls (3 companies x 10 ranges, 2024-04-01 to 2026-10-21). This script has switched itself off.", title="Sales History backfill queued")
