# Graph Report - CoWork_Helper  (2026-11-09)

## Corpus Check
- 35 files · ~165,315 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1380 nodes · 1955 edges · 136 communities (91 shown, 45 thin omitted)
- Extraction: 90% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 184 edges (avg confidence: 0.84)
- Token cost: 584,138 input · 0 output

## Community Hubs (Navigation)
- CoWork Helper Knowledge Base
- Ardmore UAT and Sage Lock
- Insights v3 Dashboards
- Frappe v16 Desk and Patches
- Ardmore Bulk Data Traps
- nesterp Site and Theme
- erpnext_sbca and Cowork Sync
- Frappe Cloud Stale Assets
- Insights Fork and Charts
- Frappe v16 Validation Gotchas
- Ardmore Laptop Handover
- IIS and ASP.NET Hosting
- Listview Client Script Traps
- Insights Fork and Fuse Apps
- Ardmore Go-Live Requirements
- POS Register and Closing
- Import Price Handling
- Sage Stock and Item Sync
- Ardmore Warehouse Structure
- Pharoh Item Lookup
- Quick Purchase Invoice JS
- Quick Purchase Invoice Controller
- Sunday 8 Nov Switch-On
- Insights Query and Filters
- First Live Stock Pull
- Sage Default Price Lists
- Intercompany Posting
- Cowork and Git Tooling
- Sage Sales and Returns Posting
- Print Formats and Job Cards
- Pharoh Inventory Controller
- Item Queue and Pharoh Contract
- Ardmore Tills and Stores
- Session Bootstrap and KB Layout
- POS and Grid UI Fixes
- Sage Item Cost and Adjustment
- Frappe Cloud Deploy Issues
- Insights v3 Customisation
- Link Queries and Customize Form
- Stock Adjustment Journals
- Home Fashion Importer Script
- Insights Theme Userscript
- Frappe v16 App Layout
- Zero Valuation Stock
- Project Index Entries
- Kiln Importer Script
- Manufacturing Dashboard Styling
- Sage Bank Reconciliation
- POS Cart Quantity Script
- POS Sales Other Script
- Insights Layout and Tables
- Transaction Deletion Workflow
- TEST Company Lock
- Frappe Webhook Mailing List
- Party Balance Sync
- Pharoh and Company Integration
- Patching Live Scripts
- Ardmore 9 Nov Handover
- Claude Desktop Config
- Webhook Header Gotchas
- Price List VAT Conflict
- Warehouse Stock Diagnosis
- Price List VAT Gotcha
- Disabled Default Price List
- Fuse Demo Restore
- Account Sales to Sage
- Two-Machine Working Rules
- Inventory Pagination Contract
- Site and Playbook Index
- Ardmore Companies and Sites
- Git and File Corruption
- Migrate and Missing Controllers
- Omnisend Customer Webhook
- Nest Home Role Permissions
- Server Script Sandbox
- Customize Form Int Limits
- Set Value and Meta Cache
- Set Value Column Writes
- Lead Status Reverts
- Frappe v16 Query Changes
- Post New Item Contract
- New Workstation Setup
- UAT Items and Site Notes
- Sales History and Insights
- Party Group Constraint
- App Permissions Overwrite
- Custom Role Provisioning
- Grid Settings and SQL Limits
- New Form Numbers and Workflow
- DocPerm and Child DocTypes
- Supplier Last Rate Helpers
- Quick Purchase Invoice Item
- Review and Definition of Done
- Account Sync and GL
- Cowork Mount Staleness
- Blomo Site and Connector
- CRM Keep List
- Reconciliation Commit Script
- Insights Cross References
- POS Sales Rep Dropdown
- POS Recent Orders Fixes
- POS Return Item Picker
- Gotcha: git on network drive needs safe.
- Write a 5-line gotcha before closing a s
- Gotcha: modules.txt rename without folde
- Gotcha: style Insights dashboards via in
- Gotcha: Sage item cost rules and more Se
- Playbook: insights-v3
- 177 fabric items moved to Meter
- quick_purchase_invoice
- Nest Home Settings single doctype
- Nest Home Tile (data-driven quick-launch
- nest_theme (palette + customer logo)
- role_home_page + per-user landing overri
- get-sales-rep-ids-from-sage hourly sched

## God Nodes (most connected - your core abstractions)
1. `CoWork_Helper knowledge base` - 104 edges
2. `Ardmore UAT Sage TEST lock register` - 23 edges
3. `Syncflo_internal_V16 / nesterp site` - 19 edges
4. `Gotcha: till sales never reached Sage, QOH sync leaked stock` - 18 edges
5. `Ardmore hand-over, 9 Nov 2026` - 18 edges
6. `get-inventory-qtyonhand-for-erpnext` - 17 edges
7. `post_new_item_to_sage` - 16 edges
8. `Ardmore Sunday 8 Nov 2026 step list and applied log` - 15 edges
9. `Gotcha: POS Invoice client scripts run inside the POS page` - 14 edges
10. `Ardmore hand-over to site laptop 27 Oct 2026` - 14 edges

## Surprising Connections (you probably didn't know these)
- `allowed_roles Honoured Only on Library Fallback` --semantically_similar_to--> `Frappe Permissions Are Additive — No Per-User Deny`  [INFERRED] [semantically similar]
  gotchas/2026-05-28-nest-home-tile-needs-layout-not-just-library.md → playbooks/frappe-role-based-access-control.md
- `Child-Table Updates Replace, Not Merge` --semantically_similar_to--> `Custom Role Provisioning Workflow`  [INFERRED] [semantically similar]
  gotchas/2026-05-28-nest-home-tile-needs-layout-not-just-library.md → playbooks/frappe-role-based-access-control.md
- `"Why this is non-obvious" section` --semantically_similar_to--> `The five mistakes that wasted a day`  [INFERRED] [semantically similar]
  templates/gotcha-template.md → skills/frappe-insights-v3-dashboard/SKILL.md
- `get-inventory-qtyonhand-for-erpnext` --conceptually_related_to--> `frappe.db.set_value skips the hooks that make a change real`  [AMBIGUOUS]
  sites/ardmore.md → gotchas/2026-08-12-db-set-value-skips-the-hooks-that-make-a-change-real.md
- `Ardmore UAT Round 3` --conceptually_related_to--> `Gotcha: Ardmore guides rebuild and screenshot traps`  [INFERRED]
  sites/ardmore.md → gotchas/2026-09-29-ardmore-guides-rebuild-and-screenshot-traps.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Ardmore POS barcode rollout (2026-08-03)** — gotchas_2026_08_03_label_width_caps_barcode_character_count_custom_pos_barcode, gotchas_2026_08_03_frappe_child_row_insert_bypasses_parent_validation_item_barcode_child_table, gotchas_2026_08_03_frappe_child_row_insert_bypasses_parent_validation_standalone_child_row_insert, gotchas_2026_08_03_label_width_caps_barcode_character_count_code128_width_formula, gotchas_2026_08_03_label_width_caps_barcode_character_count_zebra_zd230, gotchas_2026_08_03_label_width_caps_barcode_character_count_ardmore_barcode_label_zpl [EXTRACTED 1.00]
- **Ardmore VAT price-basis alignment (ordered fix)** — gotchas_2026_08_12_price_list_holding_two_vat_conventions_at_once_ex_vs_incl_vat_conflict, gotchas_2026_08_12_price_list_holding_two_vat_conventions_at_once_sage_price_sync, gotchas_2026_06_10_server_script_sandbox_and_xlsx_ardmore_kiln_sheet_importers, gotchas_2026_08_12_price_list_holding_two_vat_conventions_at_once_included_in_print_rate, gotchas_2026_08_12_price_list_holding_two_vat_conventions_at_once_custom_from_sheet_flag [EXTRACTED 1.00]
- **Cowork Host↔Bash Filesystem Desync Family** — gotchas_2026_05_17_cowork_write_tool_silent_truncation_write_tool_silent_truncation, gotchas_2026_05_22_bash_mount_stale_not_host_stale_bash_mount, gotchas_2026_05_20_cowork_sandbox_cannot_git_init_on_windows_mount_9p_writeback_race, gotchas_2026_05_22_bash_mount_stale_not_host_outputs_mount_escape_hatch, gotchas_2026_05_17_cowork_write_tool_silent_truncation_post_write_verification [EXTRACTED 1.00]
- **Cowork host-tool vs bash-mount write integrity failures** — gotchas_2026_05_11_host_vs_bash_write_truncation_null_padded_tail, gotchas_2026_05_14_cowork_edit_tool_flips_lf_to_crlf_crlf_eol_flip, gotchas_2026_05_14_cowork_edit_tool_flips_lf_to_crlf_bash_is_ground_truth, gotchas_2026_05_14_cowork_edit_tool_flips_lf_to_crlf_bash_heredoc_write [EXTRACTED 1.00]
- **ERPNext Clean-Books Restart Flow (count → TDR → verify, CRM preserved)** — playbooks_erpnext_wipe_company_transactions_batched_count_query, playbooks_erpnext_wipe_company_transactions_tdr_desk_ui_workflow, gotchas_2026_05_28_erpnext_clean_company_restart_transaction_deletion_record, gotchas_2026_05_28_erpnext_clean_company_restart_only_lead_opportunity_company_tagged, gotchas_2026_05_28_erpnext_clean_company_restart_new_company_pivot, playbooks_erpnext_wipe_company_transactions_keep_list_masters_crm [EXTRACTED 1.00]
- **Frappe Cloud Stale-Asset Delivery Chain (build → CDN → browser)** — gotchas_2026_05_06_frappe_cloud_update_vs_deploy_assets_update_skips_bench_build, gotchas_2026_05_06_frappe_cloud_cdn_stale_assets_cdn_stale_assets, gotchas_2026_05_06_frappe_cloud_cdn_stale_assets_bundle_css_convention, claude_fresh_deploy_after_push [EXTRACTED 1.00]
- **Frappe v16 modern desk hostility to injected custom JS/DOM** — gotchas_2026_05_07_frappe_v16_modern_desk_click_interception_navbar_click_interception, gotchas_2026_05_11_frappe_v16_listview_formatters_stripped_to_text_formatters_html_stripped, gotchas_2026_05_11_frappe_v16_modern_desk_listview_hooks_untrustworthy_listview_settings_unreliable, gotchas_2026_05_10_frappe_v16_page_api_drift_variant_2_silent_empty_body, gotchas_2026_05_11_frappe_v16_modern_desk_listview_hooks_untrustworthy_default_to_custom_page [EXTRACTED 1.00]
- **Frappe v16 hand-scaffolded app install checklist** — gotchas_2026_05_11_frappe_app_init_needs_version_app_init_version, gotchas_2026_05_11_frappe_new_app_missing_nested_module_folder_nested_module_folder, gotchas_2026_05_08_frappe_patches_txt_needs_both_section_headers_both_section_headers, gotchas_2026_05_08_frappe_module_folder_vs_modulestxt_mismatch_modules_txt_folder_mismatch [EXTRACTED 1.00]
- **Insights v3 chart assembly (source → data → chart → dashboard)** — playbooks_insights_v3_insights_query_v3, playbooks_insights_v3_insights_chart_v3, playbooks_insights_v3_insights_dashboard_v3, playbooks_insights_v3_two_query_sandwich, playbooks_insights_v3_layout_i_key [EXTRACTED 1.00]
- **Insights v3 two-query sandwich pipeline** — skills_frappe_insights_v3_dashboard_skill_insights_workbook, skills_frappe_insights_v3_dashboard_skill_insights_query_v3, skills_frappe_insights_v3_dashboard_skill_insights_chart_v3, skills_frappe_insights_v3_dashboard_skill_insights_dashboard_v3, skills_frappe_insights_v3_dashboard_skill_two_query_sandwich [EXTRACTED 1.00]
- **nest_theme boot / realtime / asset pipeline** — projects_theme_studio_scope_body_class_injection_at_boot, projects_theme_studio_scope_nest_theme_settings, projects_theme_studio_scope_realtime_instance_config_push, projects_theme_studio_scope_bundle_naming_convention, projects_theme_studio_scope_cached_settings_read [EXTRACTED 1.00]
- **Monthly AR/AP payment reconciliation flow** — projects_erpnext_sbca_opus_prompt_paymentreconciliation_reconciliation_py, projects_erpnext_sbca_pharoh_reconciliation_endpoint_prompt_reconciliationsynccontroller, projects_erpnext_sbca_pharoh_reconciliation_endpoint_prompt_partybalancedto, projects_erpnext_sbca_payment_reconciliation_design_reconciliation_journal_entry, projects_erpnext_sbca_payment_reconciliation_design_sage_payments_clearing, projects_erpnext_sbca_opus_prompt_paymentreconciliation_sage_reconciliation_log [EXTRACTED 1.00]
- **Quality Inspection save-inspect-submit path traps** — gotchas_2026_10_13_validate_check_refusing_drafts_blocks_inspected_lines_qi_parent_chicken_and_egg, gotchas_2026_10_13_validate_check_refusing_drafts_blocks_inspected_lines_gate_inspection_on_submit, gotchas_2026_10_13_submit_after_quality_inspection_needs_reload_timestampmismatcherror, gotchas_2026_10_13_submit_after_quality_inspection_needs_reload_reload_before_submit [EXTRACTED 1.00]
- **One-time Sage → ERPNext stock cutover** — projects_erpnext_sbca_pharoh_getstocklevels_endpoint_prompt_get_stock_levels_brief, projects_erpnext_sbca_pharoh_getstocklevels_endpoint_prompt_opening_stock_reconciliation, projects_erpnext_sbca_pharoh_disableqtytracking_endpoint_prompt_disable_qty_tracking_brief, projects_erpnext_sbca_pharoh_disableqtytracking_endpoint_prompt_stock_cutover, projects_erpnext_sbca_technical_items_as_sage_services [EXTRACTED 1.00]
- **Frappe Cloud deploys broken or misreported by something other than the app shipped** — gotchas_2026_09_29_insights_fork_sqlglot_pin_breaks_frappe_migrate_insights_fork, gotchas_2026_09_29_insights_fork_sqlglot_pin_breaks_frappe_migrate_frappe_cloud_recovered_status, gotchas_2026_10_13_frappe_cloud_deploy_upgrades_frappe_and_drops_font_awesome_font_awesome_dropped, gotchas_2026_10_13_installed_application_version_lags_deployed_code_installed_application_lag [INFERRED 0.75]
- **Frappe changes that save correctly but are not what the user is served** — gotchas_2026_08_12_db_set_value_skips_the_hooks_that_make_a_change_real_doctype_meta_cache, gotchas_2026_08_12_customize_form_blocks_int_to_float_property_setter_fieldtype_trap, gotchas_2026_08_24_frappe_grid_columns_overridden_by_user_settings_user_settings_gridview, gotchas_2026_08_24_erpnext_lead_status_reverts_to_opportunity_status_updater, gotchas_2026_08_06_client_script_listview_settings_assignment_wipes_indicators_listview_settings_assignment, gotchas_2026_08_18_page_css_served_stale_when_the_cache_buster_is_not_bumped_build_marker_cache_buster [INFERRED 0.85]
- **Insights v3 Positional CSS Theming Chain** — gotchas_2026_05_06_insights_spa_no_frappe_runtime_vgl_layout_selectors, gotchas_2026_05_06_insights_dashboard_client_script_styling_nth_child_selector_strategy, gotchas_2026_05_06_insights_filter_order_vs_css_nth_child_filter_last_in_items, gotchas_2026_05_06_insights_spa_no_frappe_runtime_positional_layout_convention, apply_dashboard_styling [INFERRED 0.85]
- **Ardmore till client scripts loaded inside the POS page** — playbooks_frappe_webhook_to_omnisend_pos_customer_ux_client_script, gotchas_2026_09_07_pos_invoice_client_scripts_run_inside_pos_page_pos_split_payment_autobalance, gotchas_2026_09_07_pos_invoice_client_scripts_run_inside_pos_page_pos_voucher_ref, gotchas_2026_09_07_pos_invoice_client_scripts_run_inside_pos_page_pos_return_item_picker, gotchas_2026_09_21_pos_sales_never_reached_sage_stock_leak_pos_till_scripts_loader [INFERRED 0.95]
- **Ardmore ERPNext-to-Sage posting pipeline under the TEST-only lock** — gotchas_2026_09_21_pos_sales_never_reached_sage_stock_leak_post_taxinvoice_to_sage, gotchas_2026_09_21_pos_sales_never_reached_sage_stock_leak_post_customerreturn_to_sage, gotchas_2026_09_29_sage_returns_and_retry_retry_failed_sage_sync, gotchas_2026_09_21_pos_sales_never_reached_sage_stock_leak_sage_force_company_lock, gotchas_2026_09_21_pos_sales_never_reached_sage_stock_leak_qoh_sync, gotchas_2026_09_22_ardmore_uat_sage_test_lock_register_intercompany_transfer_to_sage [INFERRED 0.95]
- **Three scripts that carry the Sage TEST-only lock** — sites_ardmore_sage_test_only_lock, sites_ardmore_post_new_item_to_sage, sites_ardmore_post_taxinvoice_to_sage, sites_ardmore_post_customerreturn_to_sage [EXTRACTED 1.00]
- **Scheduled Sage to ERPNext pull syncs through Pharoh** — sites_ardmore_get_inventory_for_erpnext, sites_ardmore_get_inventory_qtyonhand_for_erpnext, sites_ardmore_get_additional_prices_for_erpnext, sites_ardmore_get_customers_for_erpnext_new [INFERRED 0.85]
- **Client Scripts that customise the till** — sites_ardmore_pos_till_scripts_loader, sites_ardmore_pos_customer_ux, sites_ardmore_pos_voucher_ref, sites_ardmore_pos_split_payment_autobalance, sites_ardmore_pos_return_item_picker, sites_ardmore_pos_recent_orders_sales_returns, sites_ardmore_pos_new_invoice_from_recent_orders, sites_ardmore_pos_item_tile_names, sites_ardmore_pos_cart_quantity, sites_ardmore_pos_no_submit_confirm [INFERRED 0.85]
- **Ardmore item import to Sage pipeline** — sites_ardmore_handover_2026_11_09_kiln_sheet_importer, sites_ardmore_handover_2026_11_09_home_fashion_importer, sites_ardmore_handover_2026_11_09_custom_sage_post_status, sites_ardmore_handover_2026_11_09_custom_sage_adjust_qty, sites_ardmore_handover_2026_11_09_post_pending_items_to_sage, sites_ardmore_post_new_item_to_sage, sites_ardmore_handover_2026_11_09_update_item_in_sage, gotchas_2026_11_08_sage_item_cost_and_frappe_sandbox_post_item_adjustment_to_sage [EXTRACTED 1.00]
- **Ardmore intercompany posting to both Sage companies** — sites_ardmore_golive_requirements_2026_11_01_intercompany_pair, sites_ardmore_golive_requirements_2026_11_01_post_intercompany_transfer_to_sage, sites_ardmore_golive_requirements_2026_11_01_post_intercompany_sale_to_sage, sites_ardmore_golive_requirements_2026_11_01_supplierinvoice_endpoint, sites_ardmore_sage_intercompany_account, gotchas_2026_09_21_pos_sales_never_reached_sage_stock_leak_sage_item_selection [INFERRED 0.85]
- **Cowork host and bash file integrity failures** — readme_gotcha_host_vs_bash_fs_sync, readme_gotcha_bash_mount_stale_not_host, readme_gotcha_host_vs_bash_write_truncation, readme_gotcha_cowork_write_tool_silent_truncation, readme_gotcha_cowork_edit_tool_flips_lf_to_crlf [INFERRED 0.85]
- **Till reporting sources in Sales Invoice mode** — gotchas_2026_07_20_sage_return_script_blocks_pos_closing_pos_closing_entry, gotchas_2026_10_28_pos_register_empty_in_sales_invoice_mode_sales_payment_summary_report, gotchas_2026_10_28_pos_register_empty_in_sales_invoice_mode_sales_register_report [EXTRACTED 1.00]
- **Sage to ERPNext price feed paths** — sites_ardmore_get_additional_prices_for_erpnext, sites_ardmore_get_inventory_for_erpnext, gotchas_2026_11_02_sage_default_price_list_empty_in_erpnext_sync_home_retail_prices [EXTRACTED 1.00]
- **Frappe v16 Server Script sandbox traps** — gotchas_2026_11_08_sage_item_cost_and_frappe_sandbox_strftime_sandbox_failure, gotchas_2026_11_08_sage_item_cost_and_frappe_sandbox_subscript_augmented_assignment, gotchas_2026_11_08_sage_item_cost_and_frappe_sandbox_frappe_cache_set_value_failure [EXTRACTED 1.00]

## Communities (136 total, 45 thin omitted)

### Community 0 - "CoWork Helper Knowledge Base"
Cohesion: 0.03
Nodes (62): CoWork_Helper knowledge base, Gotcha: Linux sandbox cannot push a Windows-created repo, Gotcha: double-clicked .bat needs pause, Gotcha: Batch reference to an unsaved document fails, Gotcha: counter sales of inspected items need QI-after-delivery setting, Gotcha: Cowork Edit tool flips LF to CRLF, Gotcha: disabled default Price List and stale bootinfo, Gotcha: clean restart means a new company (+54 more)

### Community 1 - "Ardmore UAT and Sage Lock"
Cohesion: 0.07
Nodes (46): ardmoreceramics.c.frappe.cloud (Ardmore site), Gotcha: POS Invoice client scripts run inside the POS page, Ardmore POS Receipt print format, custom_voucher_ref custom field, make_sales_return (copies every line negated), POS Closing - Cashier UX client script, POS Return Item Picker client script, POS Split Payment Autobalance client script (+38 more)

### Community 2 - "Insights v3 Dashboards"
Cohesion: 0.05
Nodes (33): Gotcha: Insights v3 dashboard filters, chart labels and DuckDB trap, measure_name / dimension_name are the on-screen labels, Insights v3 dashboard filter item (links keyed by chart name), Raw SQL runs in DuckDB: Duplicate CTE name when a table is referenced twice, is_public dashboards are served without login, Insights 3.12.2 dashboard grid is 20 columns, not 12, nest_theme (Frappe v16 theme app), Nest Theme Settings (Single DocType) (+25 more)

### Community 3 - "Frappe v16 Desk and Patches"
Cohesion: 0.06
Nodes (23): Introspect schema via referencing doctypes instead of DocField, nest_theme custom Frappe v16 theme app, Render custom widgets outside header.desktop-navbar, attachRealtime() deferred-registration helper, Workspace autoname field:title defeats frappe.client.insert, workspace.new_page() permission guard (session.user == for_user), Frappe Cloud bench layer vs site layer separation, Frappe module discovery maps title-case module to snake_case folder (+15 more)

### Community 4 - "Ardmore Bulk Data Traps"
Cohesion: 0.07
Nodes (36): Gotcha: POS page custom script breaks returns, Frappe child-row insert bypasses parent validation, One bad row poisons a whole batch (recurring failure mode), Bulk-updating 6,000 Items: insert the child row directly instead of `item.save()`, Cause, Document.save() revalidates every parent field, Fix, Item Barcode child table (+28 more)

### Community 5 - "nesterp Site and Theme"
Cohesion: 0.07
Nodes (29): claude_desktop_config.json (seven frappe-* MCP servers with API keys), MIT License (Syncflo, 2026), Quick Purchase Invoice (Frappe module), patches.txt pre/post model sync sections, Customer logo override (Nest Theme Settings.customer_logo), nest_theme Deploy recipe, Palette switching live test (v0.3.0 addendum), nest_theme DevTools smoke test (+21 more)

### Community 6 - "erpnext_sbca and Cowork Sync"
Cohesion: 0.07
Nodes (22): Post-Write Verification via bash (wc/tail/node --check), Read Tool Serves Harness Tracked Intent, Not Disk, 9p/virtio Mount Writeback Race on Dotfiles, stat mtime Disambiguation Rule, party_activity.js (nest_crm_tasks), Customer/Supplier category -> group sync (ensure_party_group), Company Sage Integration child table, Doreen (9t9it Frappe partner, app author) (+14 more)

### Community 7 - "Frappe Cloud Stale Assets"
Cohesion: 0.10
Nodes (28): Page CSS served stale when cache-buster not bumped, A desk Page's CSS is served stale after deploy unless you bump its cache-buster, BUILD_MARKER CSS cache-buster, Cause, Committed-but-not-pushed hides Frappe Cloud 'Update Available', Fingerprinted desk Page JS bundle, Fix, fuse_floor.js (had no cache-buster) (+20 more)

### Community 8 - "Insights Fork and Charts"
Cohesion: 0.08
Nodes (16): COLOR_MAP (charts/colors.ts), Frappe Cloud fork deploy sequence, frontend/src2/main.ts entry point, syncflo-custom-chart-palette.ts, syncflo-custom-overrides.css, Tampermonkey per-device userscript, Chart-not-rendering diagnostic ladder, Insights Chart v3 (+8 more)

### Community 9 - "Frappe v16 Validation Gotchas"
Cohesion: 0.12
Nodes (20): Gotcha: ERPNext v16 QI reading_1 vs reading_value, Certificate of Analysis print format, fuse_manufacturing quality.py create_for_line, Gotcha: submit after Quality Inspection needs reload, fuse_manufacturing app (0.10.3 / 0.10.4), TimestampMismatchError on parent submit after QI submit, Gotcha: validate-time inspection check refusing drafts blocks inspected lines, check_inspections doc_event hook (+12 more)

### Community 10 - "Ardmore Laptop Handover"
Cohesion: 0.10
Nodes (23): Playbook: mirror the Claude Code set-up on another laptop, Claude memory keyed by project path (C--ClaudeCode), not Windows user, Coming back: copy trip memory back (newer wins), push CoWork_Helper, Robocopy transfer via external drive (MSYS_NO_PATHCONV), Ardmore hand-over to site laptop 27 Oct 2026, Ardmore POS Receipt print format, Company Sage Integration seller details, Accounts Settings delete_linked_ledger_entries (+15 more)

### Community 11 - "IIS and ASP.NET Hosting"
Cohesion: 0.15
Nodes (21): ASP.NET cold start makes the first page slow, Cause, debug=true shipped by copy/paste deploy, machine.config <deployment retail="true">, Fix, IIS AlwaysRunning + preloadEnabled (Application Initialization), IIS app pool idle recycle (20 min default), ASP.NET on-demand page compilation (+13 more)

### Community 12 - "Listview Client Script Traps"
Cohesion: 0.14
Nodes (16): Client Script assigning listview_settings wipes indicators, A List Client Script that *assigns* `frappe.listview_settings[dt]` wipes the app's own list settings — statuses go back to "Submitted", Cause, Fix, get_indicator() list status indicator, Sales Invoice / Sales Order - Hide Cancelled Client Scripts, Lead List Status Colours (reference implementation), Assigning frappe.listview_settings[dt] replaces app list settings (+8 more)

### Community 13 - "Insights Fork and Fuse Apps"
Cohesion: 0.16
Nodes (13): Gotcha: Insights fork sqlglot pin breaks Frappe migrate, Syncflo-design/insights fork (syncflo-custom-theme), sql_metadata 3.x (Frappe core dependency), Compare fork pins with upstream pyproject files, Gotcha: Batch reference to unsaved document fails, fuse_water_chemical app, flags.ignore_links (does not skip the source read), fuse_water_chemical dilution.py number_batch (+5 more)

### Community 14 - "Ardmore Go-Live Requirements"
Cohesion: 0.14
Nodes (16): Ardmore go-live weekend hand-over (27 Oct 2026), Gotcha: register of Ardmore UAT Sage TEST locks, Gotcha: till returns and Sage retry, Hyde Park count lines not loaded 1 Nov, Monday go-live watch list, Not used at go-live (SO, PO, PI, Account Sale, Airport till, wholesale prices), post-customerreturn-to-sage (Server Script and Pharoh endpoint), post-taxinvoice-to-sage (Server Script and Pharoh endpoint) (+8 more)

### Community 15 - "POS Register and Closing"
Cohesion: 0.15
Nodes (15): POS Closing Entry, post-customerreturn-to-sage Server Script, post-taxinvoice-to-sage Server Script, apply_to_all_doctypes User Permission Flag, User Permission Diagnosis Shortcut (list + Bin check), Ardmore Store Stock & POS Guide v1.2, POS Closing Recovery Procedure, POS Opening Entry (+7 more)

### Community 16 - "Import Price Handling"
Cohesion: 0.16
Nodes (10): Item Price.custom_from_sheet, get-additional-prices-for-erpnext, Ardmore Getting Stock In Guide, Guides web page (/guides), Home Fashion Importer - Import, Kiln Sheet Importer - Import, Jon Berning, Russell (+2 more)

### Community 17 - "Sage Stock and Item Sync"
Cohesion: 0.16
Nodes (12): Item.custom_qty_pending_sage, Item.custom_sage_qoh_by_company, get-inventory-for-erpnext, get-inventory-qtyonhand-for-erpnext, Nozy, Sage Item Selection, Ardmore: switching on Hyde Park and the online tills (plan, 13 Oct), Ardmore Go-Live Plan document (S:\Ardmore, Appendix A checklist) (+4 more)

### Community 18 - "Ardmore Warehouse Structure"
Cohesion: 0.14
Nodes (17): Airport AORT - A, Caversham ACA - A, Company Sage Integration Default Warehouse (stock sync switch), JHB Atrium Ceramics - A (transit), JHB Atrium Fashion - A, JHB Main Holding JHBM - A (retired), Main Distribution - A (Ceramics holding), Online Store - A (+9 more)

### Community 19 - "Pharoh Item Lookup"
Cohesion: 0.15
Nodes (13): API Server Script ardmore-count-load, POST /api/InventorySync/get-items-by-code-for-erpnext, Controllers/InventorySyncController.cs, Pharoh middleware (SageErpNextAPI), Sage companies Home, Ceramics, Fashion, Hyde Park count load (check, align, load), get-item-selectionid-for-erpnext, get-sales-history-for-erpnext (+5 more)

### Community 20 - "Quick Purchase Invoice JS"
Cohesion: 0.22
Nodes (12): compute_amount(), entry_ref(), entry_type(), fill_from_account(), fill_from_item(), flt(), items_add(), paint_row_classes() (+4 more)

### Community 22 - "Sunday 8 Nov Switch-On"
Cohesion: 0.15
Nodes (17): POS Profile.custom_till_login and Sales Person.custom_email, nest_account_sale app, nest_sales_history app, nest_stock_request app, nest_support app, Picking up Ardmore on another machine, Shared till login tickets, Credit note cannot mix Sales Other with stock lines (+9 more)

### Community 23 - "Insights Query and Filters"
Cohesion: 0.15
Nodes (15): Purchase Invoice Item child doctype, Insights v3 code Operation (Python/ibis), Insights Query v3 DocType, Insights v3 sql / raw_sql Operation, Dashboard Filter Requires Column in Source Query SELECT, getAdhocFilters (dashboard.ts), Row-Level Source + Summarize-in-data_query Refactor, Dashboard items Layout Needs Unique i Key (+7 more)

### Community 24 - "First Live Stock Pull"
Cohesion: 0.23
Nodes (8): v16 custom sidebar patch fails on removed app, add_to_site_dock, check_docked_app, frappe.patches.v16_0.convert_custom_sidebars, Newer HRMS requires Frappe 16.50 or later, nesterpdemo.c.frappe.cloud, Ardmore first live stock pull, ardmore-count-load align

### Community 25 - "Sage Default Price Lists"
Cohesion: 0.18
Nodes (15): Gotcha: Sage default price list empty in ERPNext, AdditionalItemPricesSync, Ardmore - Retail price list, auto_insert_price_list_rate_if_missing, Hyde Park POS Profile, custom_sage_sync_done=1 with offset 0, sync-home-retail-prices Server Script, Ceramics/ACA till price rule (open) (+7 more)

### Community 26 - "Intercompany Posting"
Cohesion: 0.14
Nodes (15): custom_sage_entity (POS Profile / Warehouse), Stock Entry.custom_stock_already_owned, Intercompany posting pair (seller tax invoice, buyer supplier invoice), post-intercompany-sale-to-sage, post-intercompany-transfer-to-sage, post-supplierinvoice-to-sage, block-sale-without-wholesale-price Server Script, block-transfer-without-wholesale-price Server Script (+7 more)

### Community 27 - "Cowork and Git Tooling"
Cohesion: 0.17
Nodes (12): Git / Deploy Conventions (Git Bash MINGW64), Host vs Bash Mount Desync Warning, git reset HEAD Half-Staged State Recovery, update-push.bat, Windows-Owned .git Blocks Linux Bash Sandbox Pushes, Windows .bat Needs pause to Stay Debuggable, push-to-github.bat, Git Bash Bracketed-Paste Mangles Multi-Line Commands (+4 more)

### Community 28 - "Sage Sales and Returns Posting"
Cohesion: 0.16
Nodes (10): Gotcha: Sage return script blocks POS closing, POS Ceramic Price Edit, post-customerreturn-to-sage, post-taxinvoice-to-sage, retry-failed-sage-sync, Sage link is per company, not per store (category split), Ardmore on-site visit 14 Oct 2026 recap, Airport sells at retail excluding VAT (design not agreed) (+2 more)

### Community 29 - "Print Formats and Job Cards"
Cohesion: 0.23
Nodes (8): Print format PDF margins come from .print-format CSS, 2026 Quotation and 2026 Invoice print formats, Print Format margin fields, Job card save refused before earlier step, JobCard.validate, OperationSequenceError, validate_sequence_id, Work Order planned and delivery dates allow changes on submit

### Community 30 - "Pharoh Inventory Controller"
Cohesion: 0.14
Nodes (8): POST disable-qty-tracking, POST get-stock-levels-for-erpnext, InventorySyncController (merged), ERPNext-side route map, Disable Sage Qty Tracking endpoint brief, Get Stock Levels endpoint brief, API/stock.py import_stock_levels_from_sage(), Opening Stock reconciliation

### Community 31 - "Item Queue and Pharoh Contract"
Cohesion: 0.20
Nodes (13): Pharoh endpoint brief: Get Items By Code, Gotcha: Pharoh Copilot prompts need a structured format, Item.custom_sage_post_status (Create, Update, Repair), KSI-00018 repair (85 items), PHAROH_READY flag, post-pending-items-to-sage (Server Script, cron every 5 minutes), update-item-in-sage, Sage price list ids per company (+5 more)

### Community 32 - "Ardmore Tills and Stores"
Cohesion: 0.17
Nodes (15): AORT - A (Airport), Ardmore Tax Invoice print format, Company Ardmore, Company Home, HDSQ - A (Hyde Park), JHBM - A (JHB Main Holding), Main Distribution - A, nest_stock_request (+7 more)

### Community 33 - "Session Bootstrap and KB Layout"
Cohesion: 0.18
Nodes (8): Active Projects and Sites Register, CoWork_Helper Knowledge Base, CoWork_Helper Folder Layout, Russell's Working Style Rules, graphifyy knowledge-graph build workflow, Non-Frappe workstreams outside CoWork_Helper, Paste-ready session bootstrap prompt, Start-of-task prompt guide

### Community 34 - "POS and Grid UI Fixes"
Cohesion: 0.15
Nodes (9): Customer-Quick-Invoice Client Script, frappe.ui.Dialog Table Grid, col-xs-N max-width Cap Blocks flex-grow, qi-dialog Wrapper Scope Class, setup_visible_columns, getpage Serves Page Script from Bench Files, Not DB, Mata101/server_script App, nest_help Defensive Pill-Span Shim (+1 more)

### Community 35 - "Sage Item Cost and Adjustment"
Cohesion: 0.20
Nodes (6): Sage item cost and Frappe Server Script sandbox traps, post-item-adjustment-to-sage, Bare 400 Failed to create item in Sage, post_new_item_to_sage, post-new-item-to-sage category and prices extension, Sage adjustment cost becomes the new average

### Community 36 - "Frappe Cloud Deploy Issues"
Cohesion: 0.19
Nodes (13): Fresh Deploy After Pushing a Frappe Cloud App, Item-less Purchase Invoice Row (direct GL expense), quick_purchase_invoice app, Frappe .bundle.css Fingerprinted Asset Convention, Frappe Cloud CDN Serves Stale Assets After Deploy, Rename-the-Asset-File Cache-Bust Fix, Stale-Asset Detection Recipe (?v= probe), bench build --app <app> SSH shortcut (+5 more)

### Community 37 - "Insights v3 Customisation"
Cohesion: 0.22
Nodes (10): Dashboard Layout Rebalance (KPI row, hero chart, paired tables), Client Script <style> Injection for Insights Dashboards, Insights Dashboard v3 DocType, Positional :nth-child Tile Selector Strategy, vue-grid-layout, Keep Dashboard Filter LAST in the items Array, syncflo-custom-overrides.css (Soft Professional theme), Insights v3 Is a Standalone Vue SPA (no frappe runtime) (+2 more)

### Community 38 - "Link Queries and Customize Form"
Cohesion: 0.27
Nodes (13): Gotcha: Warehouse User Permission blocks Stock Transfer, A link query that ignores txt looks like missing data, frappe.call sends nested filters as a JSON string, in_stock_items link query (ignores txt), item_query restricted to Bin in-stock codes, server_scripts third-party app (Paul Christian Mata), Client Script set_query override on next tick (setTimeout 0), Stock Transfer doctype (server_scripts app) (+5 more)

### Community 39 - "Stock Adjustment Journals"
Cohesion: 0.18
Nodes (8): POST post-financial-stock-reconciliation-to-sage, Multi-row lines[] journal payload, POST post-journalentry-to-sage, Sage Effect enum (1=Debit, 2=Credit), entryType metadata values, push_stock_adjustment_on_submit toggle, StockAdjustmentSyncController, Journal Entry push (journal_entry.py)

### Community 41 - "Insights Theme Userscript"
Cohesion: 0.27
Nodes (12): buildCSS(), CHART_PALETTE_EXTRAS, getChartPalette(), getTheme(), injectTheme(), isNeutralFill(), paletteSet, recolorAllCharts() (+4 more)

### Community 42 - "Frappe v16 App Layout"
Cohesion: 0.20
Nodes (9): git push origin HEAD Rule of Thumb, DocType Folder Three-File Requirement, Frappe v16 App File Layout, Frappe Cloud Deploy Flow, modules.txt (Title-Case Module Name), patches.txt (Both Section Headers Required), pyproject.toml (flit_core, PEP 621), Whitelisted Methods in api.py (+1 more)

### Community 43 - "Zero Valuation Stock"
Cohesion: 0.23
Nodes (12): Zero-valuation seed stock warns on every transfer, allow_zero_valuation_rate (the wrong fix), Cause, Fix, Item.valuation_rate default vs stock ledger valuation, Batched Stock Reconciliation re-valuation (chunks of 25), Sage QOH sync (get-inventory-qtyonhand-for-erpnext), See also (+4 more)

### Community 44 - "Project Index Entries"
Cohesion: 0.18
Nodes (12): erpnext_sbca ASSESSMENT.md (historical), erpnext_sbca TECHNICAL.md, Gotcha: app-created documents trip the app's own hooks, Gotcha: v16 listview formatters stripped to text, Gotcha: v16 navbar swallows mouse clicks, Gotcha: v16 listview hooks untrustworthy, default to a custom Page, Gotcha: Page JS API drift from v15 to v16, Project: erpnext_sbca (Sage to ERPNext bridge) (+4 more)

### Community 46 - "Manufacturing Dashboard Styling"
Cohesion: 0.20
Nodes (7): Negative-Value Conditional Formatting, custom-dashboard-styling.css, Friendlier KPI Card Names, Manufacturing Operations Dashboard Polish, Chart config.order_by (correct home for ordering), data_query order_by Op Crashes with NoneType column_name, Number-Card KPI Label Comes from measure_name

### Community 47 - "Sage Bank Reconciliation"
Cohesion: 0.20
Nodes (7): push_reconciliation_on_schedule toggle, API/reconciliation.py daily worker, last_reconciliation_sync shared timestamp, Reconciliation Journal Entry, Sage Payments Clearing account, Sage CustomerTransactionListing report, ReconciliationSyncController

### Community 48 - "POS Cart Quantity Script"
Cohesion: 0.42
Nodes (10): apply_qty(), build(), ensure_style(), fmt(), get_row(), paint(), pos(), schedule() (+2 more)

### Community 49 - "POS Sales Other Script"
Cohesion: 0.38
Nodes (8): ask_for_line(), has_other(), offer_to_remove(), open_button(), paint_button(), patch(), pos(), warn()

### Community 50 - "Insights Layout and Tables"
Cohesion: 0.22
Nodes (7): skills/frappe-insights-v3-dashboard/templates/chart_table.json, data_query needs a summarize operation, not just source, insights/frontend/src2/dashboard/DashboardBuilder.vue, insights/frontend/src2/dashboard/Dashboard.vue, dashboard_vertical_compact lives in localStorage, not the doctype, Empty text spacer item blocks the compact pass, insights/frontend/src2/dashboard/VueGridLayout.vue

### Community 51 - "Transaction Deletion Workflow"
Cohesion: 0.28
Nodes (5): Ledger Link Guards Block Voucher and Company Deletes, Transaction Deletion Record (TDR), Batched Non-Zero Count Query (MCP get_count), Company-Scoped Transaction DocType Candidate List, Payment Ledger Entry / Advance Payment Ledger Entry

### Community 52 - "TEST Company Lock"
Cohesion: 0.28
Nodes (7): Gotcha: outdated POS Opening Entry blocks till, ardmore-send-invoice-to-sage, Company Ardmore Ceramics TEST, POS Profile POS_Test2, Switch-on order of work (decisions, fixes, item checks, lock lift), Staff training setup on TEST company, Ardmore UAT Round 3

### Community 53 - "Frappe Webhook Mailing List"
Cohesion: 0.22
Nodes (5): add_to_mailing_list Custom Field, Frappe Webhook Record (Customer on_update), Omnisend Contacts v3 API, Webhook Request Log verification, Sage Reconciliation Log DocType

### Community 54 - "Party Balance Sync"
Cohesion: 0.22
Nodes (4): sageId → custom_sage_customer_id match key, PartyBalanceDTO, Price List.custom_sage_price_list_id bridge field, Sales Person sync (custom_sage_rep_id)

### Community 55 - "Pharoh and Company Integration"
Cohesion: 0.29
Nodes (6): Gotcha: chatty cron on unconfigured third-party app, Company Sage Integration, Go-live 2 November 2026, Ardmore Go-Live Plan v1.0, Doreen (Sage app author), Pharoh (SageErpNextAPI)

### Community 57 - "Ardmore 9 Nov Handover"
Cohesion: 0.29
Nodes (7): Gotcha: Ardmore guide rebuild and screenshot traps, custom_from_sheet price stamp, Ardmore hand-over, 9 Nov 2026, Item.custom_category (never touch), Open Ardmore tickets 0128 Quotes and 0148 Online stock, Price sync may add VAT twice (get-additional-prices-for-erpnext), Ardmore staff guides out of date

### Community 58 - "Claude Desktop Config"
Cohesion: 0.52
Nodes (4): Claude Desktop MSIX hides claude_desktop_config.json, claude_desktop_config.json, Claude_pzs8sxrjxfjjc MSIX Package Family Name, request_cowork_directory tool

### Community 59 - "Webhook Header Gotchas"
Cohesion: 0.33
Nodes (4): Frappe Webhook DocType, webhook.get_webhook_headers(), Channel Status Vocabulary (subscribed/nonSubscribed/unsubscribed), Omnisend Classic v3 POST /contacts

### Community 60 - "Price List VAT Conflict"
Cohesion: 0.52
Nodes (7): Ardmore Kiln Sheet / Home Fashion importers, Price list holding two VAT conventions at once, Item Price custom_from_sheet precedence flag, Ex-VAT vs incl-VAT price conflict on one price list, included_in_print_rate on every company's VAT template, Sage price sync (get-additional-prices-for-erpnext), standard_rate relabelled 'Retail Price Excl Vat' (decoy field)

### Community 61 - "Warehouse Stock Diagnosis"
Cohesion: 0.29
Nodes (7): Cause, Fix, How to prove it in one call, See also, Symptom, "The warehouse only has ceramics" — a link query that ignores the typed text, Why this is non-obvious

### Community 62 - "Price List VAT Gotcha"
Cohesion: 0.29
Nodes (7): Cause, Fix, One price list, two VAT conventions — the till charging 15% wrong depending on who wrote last, See also, Symptom, The mistake worth not repeating, Why this is non-obvious

### Community 63 - "Disabled Default Price List"
Cohesion: 0.48
Nodes (5): Gotcha: disabled default price list and stale bootinfo cache, erpnext.stock.get_item_details.apply_price_list, POS Profiles Airport/Caversham/Joburg on disabled Standard Selling, Selling Settings Default Price List, Standard Selling price list (disabled)

### Community 64 - "Fuse Demo Restore"
Cohesion: 0.43
Nodes (6): Gotcha: Fuse demo restore replays Intacct control IDs, fuse_core.rules.control_id_for, Demo profile restore rewinds naming series, fuse_core.gateway.read pages the whole object before truncating, leadertread-DEV has no TASKID on AP/AR lines, fuse_manufacturing post_movements flag

### Community 65 - "Account Sales to Sage"
Cohesion: 0.33
Nodes (5): Ardmore - Wholesale price list, build-ardmore-wholesale-price-list, get-customers-for-erpnext-new, nest_account_sale, Sage Customer Selection

### Community 66 - "Two-Machine Working Rules"
Cohesion: 0.33
Nodes (3): Design→Dev handoff checklist, Machine A — Design & Layout, Machine B — Development, Review & Testing

### Community 67 - "Inventory Pagination Contract"
Cohesion: 0.33
Nodes (4): POST get-inventory-for-erpnext, {TotalResults, ReturnedResults, Items} envelope, Pagination audit Copilot brief (txt edition), Services/SageService.cs $skip layer

### Community 68 - "Site and Playbook Index"
Cohesion: 0.29
Nodes (7): Gotcha: custom JS on point-of-sale Page breaks returns, Gotcha: Frappe Webhook headers are not Jinja-rendered, Gotcha: Nest Home tile needs the Layout, not just the library, Gotcha: Omnisend phone identifier needs channels.sms, Playbook: Frappe Webhook to Omnisend Contacts v3, Project: nest_home, Site: Ardmore (ardmoreceramics.c.frappe.cloud)

### Community 69 - "Ardmore Companies and Sites"
Cohesion: 0.29
Nodes (7): ACA - A (Caversham), Ardmore_KZN bench, ardmoreceramics.c.frappe.cloud, Company Ceramics, Company Fashion, Company SageTesting, frappe-ardmore MCP connector

### Community 70 - "Git and File Corruption"
Cohesion: 0.40
Nodes (3): rstrip-NULL rewrite fix for padded files, Write large files via bash heredoc to dodge mount truncation, Bash-side file/wc/git diff is ground truth, not the host Read tool

### Community 72 - "Omnisend Customer Webhook"
Cohesion: 0.33
Nodes (6): Gotcha: webhook headers not Jinja-rendered, Gotcha: Omnisend phone identifier requires SMS channel, Playbook: Frappe webhook to Omnisend, Customer to Omnisend webhook, Omnisend, POS Customer UX

### Community 73 - "Nest Home Role Permissions"
Cohesion: 0.33
Nodes (4): allowed_roles Honoured Only on Library Fallback, resolve_layout() / boot._resolve_landing, nest_home api.tiles_for_user(), block_modules User Field (Cosmetic Layer)

### Community 74 - "Server Script Sandbox"
Cohesion: 0.53
Nodes (4): Server Script safe_exec sandbox limits + reading .xlsx, Server Script functions cannot see script-level names, Syncflo-design repos use HTTPS remotes only, nest_sheets app (read_sheet API)

### Community 75 - "Customize Form Int Limits"
Cohesion: 0.33
Nodes (6): Cause, Customize Form refuses Int → Float, and forcing it past the check corrupts the data, Fix, See also, Symptom, Why this is non-obvious

### Community 76 - "Set Value and Meta Cache"
Cohesion: 0.67
Nodes (5): frappe.db.set_value skips the hooks that make a change real, Server-side doctype meta cache, frappe.db.set_value raw column write, Load-and-save (doc.save) to fire on_update, Version records (audit trail)

### Community 77 - "Set Value Column Writes"
Cohesion: 0.33
Nodes (6): Cause, Fix, `frappe.db.set_value` writes the row but skips everything that makes the change take effect, See also, Symptom, Why this is non-obvious

### Community 78 - "Lead Status Reverts"
Cohesion: 0.60
Nodes (6): ERPNext Lead status reverts to Opportunity, doc.flags not cleared by doc.reload(), Frappe save order (before_validate -> validate -> before_save), Read core source from GitHub at the installed app version, ERPNext StatusUpdater (status_map / get_status / set_status), Lead Sticky Status capture/restore Server Scripts

### Community 79 - "Frappe v16 Query Changes"
Cohesion: 0.40
Nodes (5): Gotcha: Frappe v16 query, notification and assignment changes, limit_page_length / limit_start deprecated (use limit / offset), nest_assistant app, Notification Log type is a Link to Notification Type, SQL functions as strings refused in fields; use dict syntax {COUNT: *}

### Community 80 - "Post New Item Contract"
Cohesion: 0.40
Nodes (5): POST post-new-item-to-sage, tax.py::build_price_pair (4dp round-trip), Item Tax Template Sage Map child table, tax.py::resolve_sage_tax, Sage Tax DocType (per-tenant sage_idx)

### Community 81 - "New Workstation Setup"
Cohesion: 0.53
Nodes (6): Cowork start-prompt desktop shortcut, graphify CLI and skill (graphifyy), graphify-out built graph artifacts, install.bat / install.ps1, New workstation setup, start-prompt.txt

### Community 82 - "UAT Items and Site Notes"
Cohesion: 0.40
Nodes (6): Ardmore Site Notes, Ardmore handover 2026-11-09, Ardmore Sunday 2026-11-08 log, Ardmore UAT item set (22 Sep 2026), POS_Test2 UAT till, UAT 100-SKU set (Ceramics 37, Home 33, Fashion 30)

### Community 83 - "Sales History and Insights"
Cohesion: 0.33
Nodes (5): Ardmore Sales Insights dashboard, Ardmore Sales - Year on Year dashboard, Insights fork (syncflo-custom-theme), nest_sales_history, Sales History DocType

### Community 84 - "Party Group Constraint"
Cohesion: 0.40
Nodes (4): ensure_party_group(), erpnext_sbca/API/helper_function.py, ERPNext Nested-Set Group Tree, Sage Customer/Supplier Category Sync

### Community 85 - "App Permissions Overwrite"
Cohesion: 0.40
Nodes (4): App JSON permissions[] Is the Complete Allow-List, business_subscription.json, Presales User Role (nesterp Reference Implementation), Mandatory Security Audit Checklist

### Community 86 - "Custom Role Provisioning"
Cohesion: 0.40
Nodes (3): Child-Table Updates Replace, Not Merge, Nest Home Layout DocType, Script Manager role (on System Admin Role Profile)

### Community 87 - "Grid Settings and SQL Limits"
Cohesion: 0.70
Nodes (5): Frappe grid columns overridden by user settings, in_list_view / columns Property Setters on child DocType, frappe.db.sql is read-only in System Console / Server Scripts, Grid gear 'Reset to default', __UserSettings GridView per-user grid layout

### Community 89 - "DocPerm and Child DocTypes"
Cohesion: 0.40
Nodes (5): Child DocType istable Flag, DocType JSON Shape, DocType JSON permissions[] Array, Custom DocPerm Record, DocType Permission Levels (permlevel)

### Community 94 - "Account Sync and GL"
Cohesion: 0.50
Nodes (3): Two-phase account sync (cleanup then additive), Account.custom_sage_account_id, Sage Account Opening Balance DocType

### Community 95 - "Cowork Mount Staleness"
Cohesion: 0.50
Nodes (4): Gotcha: bash mount serves stale truncated copy, Gotcha: Cowork Write tool truncates files over ~20 KB, Gotcha: Cowork host and bash mount desync, Gotcha: bash mount keeps old size with NULL padding

### Community 96 - "Blomo Site and Connector"
Cohesion: 0.50
Nodes (4): blomoplastics.jh.frappe.cloud site, frappe-blomo MCP connector, Operator Run DocType, wo_wip app (Works Order WIP)

### Community 97 - "CRM Keep List"
Cohesion: 1.00
Nodes (3): Lead-source-reqd / Lead-utm_source-reqd Property Setters, Only Lead and Opportunity Are Company-Tagged, Masters + CRM Keep List

### Community 99 - "Insights Cross References"
Cohesion: 0.67
Nodes (3): Gotcha: Insights v3 is a standalone SPA without Frappe runtime, Playbook: Insights v3 minimal-fork theming, Template: insights-theme-all-sites.user.js (Tampermonkey)

### Community 100 - "POS Sales Rep Dropdown"
Cohesion: 0.67
Nodes (3): server_scripts.public.py.pos.get_sales_reps, point-of-sale Page doc (custom script field), POS sales-rep dropdown restore script

### Community 101 - "POS Recent Orders Fixes"
Cohesion: 0.67
Nodes (3): POS Customer History Open Invoice, POS New Invoice From Recent Orders, POS Recent Orders Sales Returns

## Ambiguous Edges - Review These
- `frappe.db.set_value skips the hooks that make a change real` → `get-inventory-qtyonhand-for-erpnext`  [AMBIGUOUS]
  sites/ardmore.md · relation: conceptually_related_to
- `apply-dashboard-styling.js` → `Insights v3 Is a Standalone Vue SPA (no frappe runtime)`  [AMBIGUOUS]
  DASHBOARD-POLISH-GUIDE.md · relation: conceptually_related_to
- `Bash-side file/wc/git diff is ground truth, not the host Read tool` → `Stale .git/index.lock and HEAD.lock block git writes`  [AMBIGUOUS]
  gotchas/2026-05-07-git-stale-index-lock.md · relation: conceptually_related_to
- `POST /api/InventorySync/get-items-by-code-for-erpnext` → `Hyde Park count load (check, align, load)`  [AMBIGUOUS]
  sites/ardmore-golive-requirements-2026-11-01.md · relation: conceptually_related_to

## Knowledge Gaps
- **252 isolated node(s):** `quick_purchase_invoice`, `POS Closing - Cashier UX client script`, `Stock Reconciliation over 100 rows is queued`, `Chrome background-tab screenshot traps`, `fuse_core.gateway.read pages the whole object before truncating` (+247 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 457 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **45 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Syncflo_internal_V16 / nesterp site` connect `nesterp Site and Theme` to `Transaction Deletion Workflow`, `erpnext_sbca and Cowork Sync`, `Migrate and Missing Controllers`?**
  _High betweenness centrality (0.175) - this node is a cross-community bridge._
- **What connects `quick_purchase_invoice`, `POS Closing - Cashier UX client script`, `Stock Reconciliation over 100 rows is queued` to the rest of the system?**
  _252 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `CoWork Helper Knowledge Base` be split into smaller, more focused modules?**
  _Cohesion score 0.03225806451612903 - nodes in this community are weakly interconnected._
- **Why does `erpnext_sbca (Sage <-> ERPNext bridge app)` connect `erpnext_sbca and Cowork Sync` to `Insights Fork and Charts`, `Frappe v16 Desk and Patches`, `nesterp Site and Theme`?**
  _High betweenness centrality (0.136) - this node is a cross-community bridge._
- **Should `Ardmore UAT and Sage Lock` be split into smaller, more focused modules?**
  _Cohesion score 0.06721311475409836 - nodes in this community are weakly interconnected._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `frappe.db.set_value skips the hooks that make a change real` and `get-inventory-qtyonhand-for-erpnext`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `apply-dashboard-styling.js` and `Insights v3 Is a Standalone Vue SPA (no frappe runtime)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._