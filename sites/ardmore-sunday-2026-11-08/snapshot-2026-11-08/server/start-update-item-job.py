cron = frappe.get_doc("Scheduled Job Type","update_item_add_info_cron")
cron.reload()
cron.stopped = 0
cron.save()
server_script = frappe.get_doc("Server Script", "update-item-add-info")
server_script.reload()
server_script.disabled = 0
server_script.save()
