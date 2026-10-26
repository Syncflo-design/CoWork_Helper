# Frappe v16: query, notification and assignment changes that bite custom apps

Found 2026-10-23 while building nest_assistant, by reading the version-16 source
(raw.githubusercontent.com/frappe/frappe/version-16/...), not by guessing.

- **get_list / get_all paging:** `limit_page_length` and `limit_start` are deprecated
  (removal in v17). Use `limit=` (and `offset=`). get_all still defaults
  `limit_page_length=0` (no limit) when you pass neither.
- **SQL functions as strings are refused** in `fields` ("SQL functions are not allowed as
  strings in SELECT"). Use dict syntax: `{"COUNT": "*", "as": "count"}`. For small sets,
  `pluck=` plus a Python `Counter` avoids GROUP BY / ONLY_FULL_GROUP_BY questions entirely.
- **Notification Log `type` is a Link to the Notification Type doctype**, not a Select.
  Standard records: Mention, Energy Point, Assignment, Share, Alert (checked on demo).
  A custom type string must exist as a record or the insert fails link validation.
- **`frappe.desk.form.assign_to.add`** silently skips a second open ToDo for the same
  user on the same document ("Already in the following Users ToDo list") and
  **auto-shares** the document when the assignee can't read it. To allow several tasks per
  person, insert the ToDo directly (its `on_update` still writes the "Assigned" comment and
  `_assign`) and call `notify_assignment(assigned_by, allocated_to, doctype, name,
  action="ASSIGN", description=...)` for the standard alert.
- **Comments:** the desk's own `add_comment` only requires READ permission on the record;
  `doc.add_comment("Comment", text, comment_by=...)` inserts with ignore_permissions.
