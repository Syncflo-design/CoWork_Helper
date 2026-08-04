# Graph Report - .  (2026-08-02)

## Corpus Check
- 128 files · ~88,800 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 573 nodes · 681 edges · 48 communities (45 shown, 3 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 92 edges (avg confidence: 0.83)
- Token cost: 742,714 input · 0 output

## Community Hubs (Navigation)
- Omnisend Webhook & Reconciliation
- Sage Bridge Integration Contract
- Blomoplastics Insights Theming
- Insights Fork-Overlay Pattern
- Cowork Host/Bash Mount Desync
- Frappe v16 Desk API Limits
- nest_theme Palette System
- Ardmore Site Operations
- DocType Permissions & Migrate
- Frappe Grid & Dialog Quirks
- Sage Stock Cutover Endpoints
- Quick Purchase Invoice Form JS
- Quick Purchase Invoice Controller
- Pharoh Pagination & Envelopes
- Git Bash Windows Conventions
- nest_theme Deploy & Boot Injection
- Frappe Cloud Asset Staleness
- Insights Dashboard Styling
- Insights Two-Query Sandwich
- Master Insights Userscript
- Clean Company Restart (TDR)
- Frappe App Scaffold Requirements
- Insights Table & Vue Grid Layout
- Dashboard Polish Scripts
- CoWork_Helper Knowledge Base
- Webhook Headers & Omnisend API
- Two-Machine Workflow
- Knowledge Base Index
- Insights SQL Join Workaround
- Git Locks & File Corruption
- Party Group Leaf Constraint
- Purchase Invoice API Helpers
- Quick Purchase Invoice Child Row
- custom_subscription App
- Reconciliation Commit Script
- Ardmore POS Page Script
- Quick Purchase Invoice App

## God Nodes (most connected - your core abstractions)
1. `Gotchas Index` - 19 edges
2. `QuickPurchaseInvoice` - 11 edges
3. `Windows-Owned .git Blocks Linux Bash Sandbox Pushes` - 9 edges
4. `CoWork_Helper README Index` - 8 edges
5. `Frappe Cloud Update Skips bench build` - 8 edges
6. `InventorySyncController (merged)` - 8 edges
7. `compute_amount()` - 7 edges
8. `CoWork_Helper Knowledge Base` - 7 edges
9. `Cowork Host vs Linux Bash Mount Filesystem Desync` - 7 edges
10. `Chart data_query Auto-Created Empty` - 7 edges

## Surprising Connections (you probably didn't know these)
- `allowed_roles Honoured Only on Library Fallback` --semantically_similar_to--> `Frappe Permissions Are Additive — No Per-User Deny`  [INFERRED] [semantically similar]
  gotchas/2026-05-28-nest-home-tile-needs-layout-not-just-library.md → playbooks/frappe-role-based-access-control.md
- `Child-Table Updates Replace, Not Merge` --semantically_similar_to--> `Custom Role Provisioning Workflow`  [INFERRED] [semantically similar]
  gotchas/2026-05-28-nest-home-tile-needs-layout-not-just-library.md → playbooks/frappe-role-based-access-control.md
- `Body class injection at boot` --semantically_similar_to--> `Syncflo-design/insights fork (syncflo-custom-theme)`  [INFERRED] [semantically similar]
  projects/theme_studio/SCOPE.md → sites/blomoplastics.md
- `"Why this is non-obvious" section` --semantically_similar_to--> `The five mistakes that wasted a day`  [INFERRED] [semantically similar]
  templates/gotcha-template.md → skills/frappe-insights-v3-dashboard/SKILL.md
- `Tampermonkey Userscript Injection` --conceptually_related_to--> `insights-theme-all-sites.user.js Master Userscript`  [INFERRED]
  gotchas/2026-05-06-insights-spa-no-frappe-runtime.md → README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Insights v3 Silent-Failure Cluster (no error, empty/blank result)** — gotchas_2026_05_06_insights_dashboard_layout_i_key_layout_i_key, gotchas_2026_05_06_insights_data_query_empty_stub_data_query_empty_stub, gotchas_2026_05_06_insights_dashboard_filter_needs_source_column_filter_needs_source_column, gotchas_2026_05_06_insights_explicit_join_wrong_schema_explicit_join_temp_main [INFERRED 0.85]
- **Insights v3 Positional CSS Theming Chain** — gotchas_2026_05_06_insights_spa_no_frappe_runtime_vgl_layout_selectors, gotchas_2026_05_06_insights_dashboard_client_script_styling_nth_child_selector_strategy, gotchas_2026_05_06_insights_filter_order_vs_css_nth_child_filter_last_in_items, gotchas_2026_05_06_insights_spa_no_frappe_runtime_positional_layout_convention, dashboard_polish_guide_apply_dashboard_styling_js [INFERRED 0.85]
- **Frappe Cloud Stale-Asset Delivery Chain (build → CDN → browser)** — gotchas_2026_05_06_frappe_cloud_update_vs_deploy_assets_update_skips_bench_build, gotchas_2026_05_06_frappe_cloud_cdn_stale_assets_cdn_stale_assets, gotchas_2026_05_06_frappe_cloud_cdn_stale_assets_bundle_css_convention, claude_fresh_deploy_after_push [EXTRACTED 1.00]
- **Frappe v16 hand-scaffolded app install checklist** — gotchas_2026_05_11_frappe_app_init_needs_version_app_init_version, gotchas_2026_05_11_frappe_new_app_missing_nested_module_folder_nested_module_folder, gotchas_2026_05_08_frappe_patches_txt_needs_both_section_headers_both_section_headers, gotchas_2026_05_08_frappe_module_folder_vs_modulestxt_mismatch_modules_txt_folder_mismatch [EXTRACTED 1.00]
- **Frappe v16 modern desk hostility to injected custom JS/DOM** — gotchas_2026_05_07_frappe_v16_modern_desk_click_interception_navbar_click_interception, gotchas_2026_05_11_frappe_v16_listview_formatters_stripped_to_text_formatters_html_stripped, gotchas_2026_05_11_frappe_v16_modern_desk_listview_hooks_untrustworthy_listview_settings_unreliable, gotchas_2026_05_10_frappe_v16_page_api_drift_variant_2_silent_empty_body, gotchas_2026_05_11_frappe_v16_modern_desk_listview_hooks_untrustworthy_default_to_custom_page [EXTRACTED 1.00]
- **Cowork host-tool vs bash-mount write integrity failures** — gotchas_2026_05_11_host_vs_bash_write_truncation_null_padded_tail, gotchas_2026_05_14_cowork_edit_tool_flips_lf_to_crlf_crlf_eol_flip, gotchas_2026_05_14_cowork_edit_tool_flips_lf_to_crlf_bash_is_ground_truth, gotchas_2026_05_14_cowork_edit_tool_flips_lf_to_crlf_bash_heredoc_write [EXTRACTED 1.00]
- **Cowork Host↔Bash Filesystem Desync Family** — gotchas_2026_05_17_cowork_write_tool_silent_truncation_write_tool_silent_truncation, gotchas_2026_05_22_bash_mount_stale_not_host_stale_bash_mount, gotchas_2026_05_20_cowork_sandbox_cannot_git_init_on_windows_mount_9p_writeback_race, gotchas_2026_05_22_bash_mount_stale_not_host_outputs_mount_escape_hatch, gotchas_2026_05_17_cowork_write_tool_silent_truncation_post_write_verification [EXTRACTED 1.00]
- **Server Script Latent Runtime-Only Failure Cluster** — gotchas_2026_06_10_server_script_sandbox_and_xlsx_leading_underscore_ban, gotchas_2026_06_10_server_script_sandbox_and_xlsx_commit_rollback_stripped, gotchas_2026_06_10_server_script_sandbox_and_xlsx_function_scope_globals_locals, gotchas_2026_06_10_server_script_sandbox_and_xlsx_execute_after_edit_rule, gotchas_2026_06_10_server_script_sandbox_and_xlsx_safe_exec_sandbox [EXTRACTED 1.00]
- **ERPNext Clean-Books Restart Flow (count → TDR → verify, CRM preserved)** — playbooks_erpnext_wipe_company_transactions_batched_count_query, playbooks_erpnext_wipe_company_transactions_tdr_desk_ui_workflow, gotchas_2026_05_28_erpnext_clean_company_restart_transaction_deletion_record, gotchas_2026_05_28_erpnext_clean_company_restart_only_lead_opportunity_company_tagged, gotchas_2026_05_28_erpnext_clean_company_restart_new_company_pivot, playbooks_erpnext_wipe_company_transactions_keep_list_masters_crm [EXTRACTED 1.00]
- **One-time Sage → ERPNext stock cutover** — projects_erpnext_sbca_pharoh_getstocklevels_endpoint_prompt_get_stock_levels_brief, projects_erpnext_sbca_pharoh_getstocklevels_endpoint_prompt_opening_stock_reconciliation, projects_erpnext_sbca_pharoh_disableqtytracking_endpoint_prompt_disable_qty_tracking_brief, projects_erpnext_sbca_pharoh_disableqtytracking_endpoint_prompt_stock_cutover, projects_erpnext_sbca_technical_items_as_sage_services [EXTRACTED 1.00]
- **Monthly AR/AP payment reconciliation flow** — projects_erpnext_sbca_opus_prompt_paymentreconciliation_reconciliation_py, projects_erpnext_sbca_pharoh_reconciliation_endpoint_prompt_reconciliationsynccontroller, projects_erpnext_sbca_pharoh_reconciliation_endpoint_prompt_partybalancedto, projects_erpnext_sbca_payment_reconciliation_design_reconciliation_journal_entry, projects_erpnext_sbca_payment_reconciliation_design_sage_payments_clearing, projects_erpnext_sbca_opus_prompt_paymentreconciliation_sage_reconciliation_log [EXTRACTED 1.00]
- **Insights v3 chart assembly (source → data → chart → dashboard)** — playbooks_insights_v3_insights_query_v3, playbooks_insights_v3_insights_chart_v3, playbooks_insights_v3_insights_dashboard_v3, playbooks_insights_v3_two_query_sandwich, playbooks_insights_v3_layout_i_key [EXTRACTED 1.00]
- **Ardmore Sage stock round-trip (sheet -> Sage -> ERPNext stock)** — sites_ardmore_kiln_sheet_importer, sites_ardmore_home_fashion_importer, sites_ardmore_post_new_item_to_sage, sites_ardmore_get_inventory_qtyonhand_for_erpnext, sites_ardmore_custom_opening_qty, sites_ardmore_custom_qty_pending_sage [EXTRACTED 1.00]
- **Insights v3 two-query sandwich pipeline** — skills_frappe_insights_v3_dashboard_skill_insights_workbook, skills_frappe_insights_v3_dashboard_skill_insights_query_v3, skills_frappe_insights_v3_dashboard_skill_insights_chart_v3, skills_frappe_insights_v3_dashboard_skill_insights_dashboard_v3, skills_frappe_insights_v3_dashboard_skill_two_query_sandwich [EXTRACTED 1.00]
- **nest_theme boot / realtime / asset pipeline** — projects_theme_studio_scope_body_class_injection_at_boot, projects_theme_studio_scope_nest_theme_settings, projects_theme_studio_scope_realtime_instance_config_push, projects_theme_studio_scope_bundle_naming_convention, projects_theme_studio_scope_cached_settings_read [EXTRACTED 1.00]

## Communities (48 total, 3 thin omitted)

### Community 0 - "Omnisend Webhook & Reconciliation"
Cohesion: 0.07
Nodes (34): add_to_mailing_list Custom Field, Frappe Webhook Record (Customer on_update), Webhook headers are not Jinja-rendered, Every Omnisend identifier needs a channels block, Omnisend Contacts v3 API, on_update over after_insert, POS Customer UX Client Script, Webhook Request Log verification (+26 more)

### Community 1 - "Sage Bridge Integration Contract"
Cohesion: 0.06
Nodes (33): Per-stage Definition of Done, Independent review (no self-certification), Customer/Supplier category → group sync, Company Sage Integration child table, erpnext_sbca (Sage ↔ ERPNext bridge app), MCP audit recipe for inherited Frappe apps, OAuth redirect_back_to is stored, not computed, Sage Business Cloud Accounting (SBCA) (+25 more)

### Community 2 - "Blomoplastics Insights Theming"
Cohesion: 0.07
Nodes (33): Soft Professional palette, Insights fork telemetry ImportError blocking deploys, SVG chart palette recolourer, Industrial Pro theme (retired), Syncflo-design/insights fork (syncflo-custom-theme), Invisible spacer tile (vue-grid vertical compact lock), KPI drill-through modal (syncflo-custom-drill-through.ts), Manufacturing Operations dashboard (0qj8e3nb4t) (+25 more)

### Community 3 - "Insights Fork-Overlay Pattern"
Cohesion: 0.07
Nodes (32): COLOR_MAP (charts/colors.ts), Frappe Cloud fork deploy sequence, frontend/src2/main.ts entry point, Minimal Fork Overlay Pattern, Object.assign(COLOR_MAP) singleton mutation, syncflo-custom-chart-palette.ts, syncflo-custom-overrides.css, Tampermonkey per-device userscript (+24 more)

### Community 4 - "Cowork Host/Bash Mount Desync"
Cohesion: 0.07
Nodes (31): Bash Heredoc Big-File Write Pattern, Post-Write Verification via bash (wc/tail/node --check), Read Tool Serves Harness Tracked Intent, Not Disk, Cowork Write/Edit Silent Truncation at ~20 KB, 9p/virtio Mount Writeback Race on Dotfiles, Author in Sandbox, Run Git on Windows Host, Sandbox git init Fails on Windows Mount, Git Bash Backslash Path Collapse (+23 more)

### Community 5 - "Frappe v16 Desk API Limits"
Cohesion: 0.09
Nodes (30): Frappe MCP user cannot read Company / DocField, Introspect schema via referencing doctypes instead of DocField, v16 modern desk navbar swallows real mouse clicks, nest_theme custom Frappe v16 theme app, Render custom widgets outside header.desktop-navbar, attachRealtime() deferred-registration helper, Realtime listeners must register after socket.connected, Workspace autoname field:title defeats frappe.client.insert (+22 more)

### Community 6 - "nest_theme Palette System"
Cohesion: 0.07
Nodes (30): MIT License (Syncflo, 2026), Quick Purchase Invoice (Frappe module), patches.txt pre/post model sync sections, Palette switching live test (v0.3.0 addendum), Accounting Crisp palette, body[class*="syn-palette-"] prefix selector refactor, drop_user_preference_doctype patch, Nest Theme User Preference (DocType, retired) (+22 more)

### Community 7 - "Ardmore Site Operations"
Cohesion: 0.08
Nodes (29): allow_in_returns on POS Payment Methods, ardmoreceramics.c.frappe.cloud site, Item.custom_opening_qty, Item.custom_qty_pending_sage (local-qty flag), frappe-ardmore MCP connector, get-additional-prices-for-erpnext (price list sync), get-inventory-for-erpnext (item sync), get-inventory-qtyonhand-for-erpnext (QOH sync) (+21 more)

### Community 8 - "DocType Permissions & Migrate"
Cohesion: 0.10
Nodes (26): App JSON permissions[] Is the Complete Allow-List, business_subscription.json, Grant Access via User Roles, Not DocType Perms, bench migrate Reimports and Replaces DocPerms, load_doctype_module / run_module_method, Missing DocType Controller Hard-Fails Site Migrate, Nest Home Layout Tile DocType, allowed_roles Honoured Only on Library Fallback (+18 more)

### Community 9 - "Frappe Grid & Dialog Quirks"
Cohesion: 0.09
Nodes (24): Customer-Quick-Invoice Client Script, Delegated Grid-Wrapper Listener, frappe.ui.Dialog Table Grid, Shared df.onchange First-Row `this` Binding, col-xs-N max-width Cap Blocks flex-grow, Grid Leftover Flex Space (Fat Pencil Column Illusion), qi-dialog Wrapper Scope Class, setup_visible_columns (+16 more)

### Community 10 - "Sage Stock Cutover Endpoints"
Cohesion: 0.11
Nodes (20): 2026-05-15 three-controller merge, POST disable-qty-tracking, POST get-stock-levels-for-erpnext, InventorySyncController (merged), Physical is always false on Sage items, POST post-new-item-to-sage, ERPNext-side route map, Disable Sage Qty Tracking endpoint brief (+12 more)

### Community 11 - "Quick Purchase Invoice Form JS"
Cohesion: 0.22
Nodes (12): compute_amount(), entry_ref(), entry_type(), fill_from_account(), fill_from_item(), flt(), items_add(), paint_row_classes() (+4 more)

### Community 12 - "Quick Purchase Invoice Controller"
Cohesion: 0.16
Nodes (7): Document, QuickPurchaseInvoice, Quick Purchase Invoice — staging doc that creates a real Purchase Invoice on…, Build, insert, and (conditionally) submit the real Purchase Invoice. Returns…, True if the current user has any of AUTO_SUBMIT_ROLES., Force per-row invariants (Account rows have qty=1, link_doctype mirrors…, Best-effort header tax preview based on the chosen template. We sum the…

### Community 13 - "Pharoh Pagination & Envelopes"
Cohesion: 0.13
Nodes (16): sageId → custom_sage_customer_id match key, Two callers expect different response envelopes, POST get-inventory-for-erpnext, {TotalResults, ReturnedResults, Items} envelope, Pagination audit Copilot brief (txt edition), Pass-through pagination rule, Envelope conversion breaks ERPNext consumers, Services/SageService.cs $skip layer (+8 more)

### Community 14 - "Git Bash Windows Conventions"
Cohesion: 0.17
Nodes (15): Git / Deploy Conventions (Git Bash MINGW64), Host vs Bash Mount Desync Warning, git reset HEAD Half-Staged State Recovery, Pick One Side and Stay There (do all git from Windows), update-push.bat, Windows-Owned .git Blocks Linux Bash Sandbox Pushes, Windows .bat Needs pause to Stay Debuggable, push-to-github.bat (+7 more)

### Community 15 - "nest_theme Deploy & Boot Injection"
Cohesion: 0.15
Nodes (14): Customer logo override (Nest Theme Settings.customer_logo), Frappe Cloud full Deploy vs Update, Git Bash bracketed-paste mangling, nest_theme Deploy recipe, nest_theme DevTools smoke test, Prior-art evaluation deprioritised, Body class injection at boot, .bundle.css / .bundle.js hash-fingerprint naming (+6 more)

### Community 16 - "Frappe Cloud Asset Staleness"
Cohesion: 0.19
Nodes (13): Fresh Deploy After Pushing a Frappe Cloud App, Item-less Purchase Invoice Row (direct GL expense), quick_purchase_invoice app, Frappe .bundle.css Fingerprinted Asset Convention, Frappe Cloud CDN Serves Stale Assets After Deploy, Rename-the-Asset-File Cache-Bust Fix, Stale-Asset Detection Recipe (?v= probe), bench build --app <app> SSH shortcut (+5 more)

### Community 17 - "Insights Dashboard Styling"
Cohesion: 0.22
Nodes (12): Dashboard Layout Rebalance (KPI row, hero chart, paired tables), Client Script <style> Injection for Insights Dashboards, Insights Dashboard v3 DocType, Positional :nth-child Tile Selector Strategy, vue-grid-layout, Keep Dashboard Filter LAST in the items Array, syncflo-custom-overrides.css (Soft Professional theme), Server-Side Fork-Overlay Theming Pattern (+4 more)

### Community 18 - "Insights Two-Query Sandwich"
Cohesion: 0.23
Nodes (13): Insights v3 code Operation (Python/ibis), Insights Query v3 DocType, Dashboard Filter Requires Column in Source Query SELECT, getAdhocFilters (dashboard.ts), Row-Level Source + Summarize-in-data_query Refactor, Dashboard items Layout Needs Unique i Key, WorkbookDashboardItem TypeScript type, Chart data_query Auto-Created Empty (+5 more)

### Community 19 - "Master Insights Userscript"
Cohesion: 0.27
Nodes (12): buildCSS(), CHART_PALETTE_EXTRAS, getChartPalette(), getTheme(), injectTheme(), isNeutralFill(), paletteSet, recolorAllCharts() (+4 more)

### Community 20 - "Clean Company Restart (TDR)"
Cohesion: 0.24
Nodes (11): Lead-source-reqd / Lead-utm_source-reqd Property Setters, Ledger Link Guards Block Voucher and Company Deletes, New-Company Restart Beats Wiping the Old One, Only Lead and Opportunity Are Company-Tagged, TDR via API = Hollow Success (document_count 0), Transaction Deletion Record (TDR), Batched Non-Zero Count Query (MCP get_count), Company-Scoped Transaction DocType Candidate List (+3 more)

### Community 21 - "Frappe App Scaffold Requirements"
Cohesion: 0.29
Nodes (9): Frappe Cloud bench layer vs site layer separation, Site Update is the app-install path on Frappe Cloud, Frappe module discovery maps title-case module to snake_case folder, modules.txt rename without folder rename causes silent update loop, patches.txt must contain both pre_model_sync and post_model_sync headers, <app>/__init__.py must declare __version__, pyproject.toml dynamic = ["version"] with flit, modules.txt uses title-case module names (+1 more)

### Community 22 - "Insights Table & Vue Grid Layout"
Cohesion: 0.22
Nodes (9): skills/frappe-insights-v3-dashboard/templates/chart_table.json, data_query needs a summarize operation, not just source, Insights v3 Table chart requires rows + values config, insights/frontend/src2/dashboard/DashboardBuilder.vue, insights/frontend/src2/dashboard/Dashboard.vue, dashboard_vertical_compact lives in localStorage, not the doctype, Empty text spacer item blocks the compact pass, vue-grid-layout verticalCompact hoists dashboard items (+1 more)

### Community 23 - "Dashboard Polish Scripts"
Cohesion: 0.32
Nodes (8): apply-dashboard-styling.js, Negative-Value Conditional Formatting, custom-dashboard-styling.css, Friendlier KPI Card Names, Manufacturing Operations Dashboard Polish, Number-Card KPI Label Comes from measure_name, frappe-insights-v3-dashboard Skill, install.bat First-Time Setup

### Community 24 - "CoWork_Helper Knowledge Base"
Cohesion: 0.29
Nodes (7): Active Projects and Sites Register, CoWork_Helper Knowledge Base, Cross-Model Plain-Markdown Playbooks, CoWork_Helper Folder Layout, Capture-a-Gotcha-Before-Session-End Habit, Gotcha to Playbook to Skill Promotion Ladder, Russell's Working Style Rules

### Community 25 - "Webhook Headers & Omnisend API"
Cohesion: 0.33
Nodes (7): API-Key-in-Header Workaround Ladder, Frappe Webhook DocType, webhook.get_webhook_headers(), Frappe Webhook Headers Are Not Jinja-Rendered, Channel Status Vocabulary (subscribed/nonSubscribed/unsubscribed), Omnisend Classic v3 POST /contacts, Phone Identifier Requires channels.sms Block

### Community 26 - "Two-Machine Workflow"
Cohesion: 0.33
Nodes (7): One writer per file boundary rule, Branch is truth for code, KB for conventions, Frappe/ERPNext work is not split, Design→Dev handoff checklist, Machine A — Design & Layout, Machine B — Development, Review & Testing, Repo copy wins over KB synced copy

### Community 27 - "Knowledge Base Index"
Cohesion: 0.29
Nodes (7): graphify Skill (machine-wide), CoWork_Helper README Index, insights-theme-all-sites.user.js Master Userscript, Playbooks Index, Projects Index, Sites Index, Templates Index

### Community 28 - "Insights SQL Join Workaround"
Cohesion: 0.33
Nodes (5): Purchase Invoice Item child doctype, Insights v3 sql / raw_sql Operation, Implicit Comma-Join Workaround, Insights DuckDB Query Planner / Translation Layer, Explicit JOIN Routes Child Tables to temp.main

### Community 29 - "Git Locks & File Corruption"
Cohesion: 0.40
Nodes (6): Stale .git/index.lock and HEAD.lock block git writes, Shrink-overwrite leaves a NULL-padded tail on the bash mount, rstrip-NULL rewrite fix for padded files, Write large files via bash heredoc to dodge mount truncation, Bash-side file/wc/git diff is ground truth, not the host Read tool, Edit/Write tool silently flips a repo file from LF to CRLF

### Community 30 - "Party Group Leaf Constraint"
Cohesion: 0.40
Nodes (5): ensure_party_group(), erpnext_sbca/API/helper_function.py, Leaf-Only Party Group Constraint, ERPNext Nested-Set Group Tree, Sage Customer/Supplier Category Sync

### Community 31 - "Purchase Invoice API Helpers"
Cohesion: 0.40
Nodes (4): get_supplier_last_rate(), Whitelisted helpers used by the Quick Purchase Invoice form., Return the most recent rate this supplier charged for ``item_code``. Looks at…, whitelist

### Community 32 - "Quick Purchase Invoice Child Row"
Cohesion: 0.40
Nodes (3): Document, QuickPurchaseInvoiceItem, Child row of Quick Purchase Invoice. Validation is intentionally light here —…

### Community 34 - "custom_subscription App"
Cohesion: 0.50
Nodes (4): Business Subscription DocType, custom_subscription app, bench migrate overwrites live DocType permissions, Stuck-forever scheduler (== today -> <=) fix

## Ambiguous Edges - Review These
- `apply-dashboard-styling.js` → `Insights v3 Is a Standalone Vue SPA (no frappe runtime)`  [AMBIGUOUS]
  DASHBOARD-POLISH-GUIDE.md · relation: conceptually_related_to
- `Stale .git/index.lock and HEAD.lock block git writes` → `Bash-side file/wc/git diff is ground truth, not the host Read tool`  [AMBIGUOUS]
  gotchas/2026-05-07-git-stale-index-lock.md · relation: conceptually_related_to

## Knowledge Gaps
- **107 isolated node(s):** `quick_purchase_invoice`, `SITE_THEMES`, `CHART_PALETTE_EXTRAS`, `paletteSet`, `Fresh Deploy After Pushing a Frappe Cloud App` (+102 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `apply-dashboard-styling.js` and `Insights v3 Is a Standalone Vue SPA (no frappe runtime)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Stale .git/index.lock and HEAD.lock block git writes` and `Bash-side file/wc/git diff is ground truth, not the host Read tool`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `Sage credentials envelope + apikey query param` connect `Sage Bridge Integration Contract` to `Sage Stock Cutover Endpoints`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Why does `InventorySyncController (merged)` connect `Sage Stock Cutover Endpoints` to `Omnisend Webhook & Reconciliation`, `Sage Bridge Integration Contract`, `Pharoh Pagination & Envelopes`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Why does `erpnext_sbca (Sage ↔ ERPNext bridge app)` connect `Sage Bridge Integration Contract` to `Omnisend Webhook & Reconciliation`, `Insights Fork-Overlay Pattern`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Windows-Owned .git Blocks Linux Bash Sandbox Pushes` (e.g. with `Git Bash Bracketed-Paste Mangles Multi-Line Commands` and `packed-refs Trailing-NULL Corruption`) actually correct?**
  _`Windows-Owned .git Blocks Linux Bash Sandbox Pushes` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `quick_purchase_invoice`, `SITE_THEMES`, `CHART_PALETTE_EXTRAS` to the rest of the system?**
  _107 weakly-connected nodes found - possible documentation gaps or missing edges._