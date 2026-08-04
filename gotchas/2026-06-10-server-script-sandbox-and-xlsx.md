# Server Script (safe_exec) sandbox limits + reading .xlsx — 2026-06-10

**Context:** Building the Ardmore Kiln Sheet / Home Fashion importers. We hit the
RestrictedPython `safe_exec` limits one error at a time over many iterations.
Capture so we never do that again.

## Server Scripts run in safe_exec — these are BLOCKED
- `import` / `from x import y` → `ImportError: __import__ not found`. **No imports.**
  ⇒ a Server Script **cannot parse .xlsx** (no openpyxl in-sandbox).
- **Any name starting with `_`** (`_receipt`, `_uom`, ...) → `"_receipt" is an invalid
  variable name because it starts with "_"`. RestrictedPython rejects it **at compile
  time, i.e. when the script RUNS** — and the Server Script form *saves it happily*
  (`check_if_compilable_in_restricted_context` only `msgprint`s a warning nobody sees
  over the API). One such name anywhere breaks the ENTIRE script. See the 2026-07-28
  section below.
- **Functions defined in a Server Script cannot see script-level names.** `safe_exec`
  runs `exec(code, _globals, _locals)`; `doc` and every top-level variable land in
  `_locals`, while a `def` captures `_globals`. So `def f(): return doc.company` dies
  with `name 'doc' is not defined` **only when f() is called**. Pass them as arguments.
- `frappe.db.commit()` / `rollback()` / `add_index()` → available in **API** and
  **Scheduler Event** scripts, but **stripped from DocType Event scripts** —
  `ServerScript.execute_doc()` calls `safe_exec(..., restrict_commit_rollback=True)`,
  which pops them from the namespace → `module has no attribute 'rollback'`. In a
  DocType Event just don't call them; the request commits on its own.
- `frappe.parse_json()` → `module has no attribute 'parse_json'`. **Use `json.loads`**
  (`json.loads` / `json.dumps` ARE exposed via `NamespaceDict`).
- Tuple unpacking `a, b = func()` and `for i, x in enumerate()` →
  `name '_unpack_sequence_' is not defined`. Use index access + `for i in range(len())`.
- `.format()` on str → "unsafe attribute"; use `+` concatenation.
- `frappe.get_roles()` not available → `frappe.db.exists('Has Role', {...})`.
- Avoid `isinstance` / `hasattr` / `+=` (treated unsafe / unavailable in this build).

## Available in safe_exec (confirmed)
`frappe.db.get_value/set_value/exists`, `frappe.get_doc/new_doc`, `doc.insert/save/
append/set`, `frappe.throw/msgprint`, `frappe.make_post_request`, `json.loads/dumps`,
`float/int/str/round/range/len`, string methods, list comprehensions, `def`.
`frappe.get_doc('File', name).get_content()` reads an attached file's bytes (decode
utf-8) — this is how to read **.txt/.csv** in-sandbox.

## Reading .xlsx → the `nest_sheets` app pattern
Sandbox can't read xlsx, so a real-Python app does it:
- `nest_sheets` (GitHub `Syncflo-design/nest_sheets`): whitelisted
  `nest_sheets.api.read_sheet(file_url)` → rows (xlsx via openpyxl, or delimited
  text). Global JS `window.nestSheets`. Doctype-agnostic — reuse anywhere.
- Consumer DocType: Attach field + hidden `sheet_data` (Long Text). A Client Script
  `attach_*` handler calls `read_sheet` **on attach** and stores rows as JSON in
  `sheet_data`. The Server Script does `rows = json.loads(doc.sheet_data)` and maps.
- UX: **one action = Save** (file auto-reads on attach). Do NOT add a separate
  "Import" button next to Save — Russell: two do-it buttons is confusing.

## 2026-07-28 — three latent breaks, all invisible until the script actually runs
The Ardmore importers were edited on 2026-07-28 and *saved clean*, but every import
then failed. Three separate causes, each only reachable at runtime:
1. `_receipt` / `_uom` — leading-underscore names (whole script refused to compile).
2. `frappe.db.commit()` / `rollback()` — stripped in DocType Event scripts.
3. `def make_receipt(...)` referencing `doc` — functions can't see script-level names.

**Rule: after ANY Server Script edit, execute it once against real data.** Saving
proves nothing. The safest edit route over MCP is a throwaway **API** Server Script
that does exact `str.replace()` on the target's `script` field and re-saves the doc —
no retyping of a 9 kB script, no transcription drift.

**Sweep recipe** (run over `Server Script` where `script_type = 'DocType Event'`):
flag any line containing `frappe.db.commit` / `frappe.db.rollback`, any line whose
stripped form starts with `_`, and any `def _`. Note `LIKE '%def _%'` is useless —
`_` is a SQL wildcard; escape it or filter in Python.

## MCP note
Server Scripts need the **Script Manager** role. As of 2026-07-20 that role is on the
`System Admin` **Role Profile**, so the `erpnext@ardmore-design.com` API user CAN
create/edit/delete Server Scripts over MCP on Ardmore. Elsewhere it may still need to
be pasted by hand. Client Scripts + custom DocTypes/Fields CAN be created via MCP.

## Git
Syncflo-design repos use **HTTPS** remotes only (no SSH keys). Never hand over a
`git@github.com:` URL — it fails "Permission denied (publickey)".
