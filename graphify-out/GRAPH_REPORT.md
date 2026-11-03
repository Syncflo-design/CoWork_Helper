# Graph Report - CoWork_Helper  (2026-11-02)

## Corpus Check
- 2 files · ~139,651 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1147 nodes · 1815 edges · 86 communities (69 shown, 17 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 201 edges (avg confidence: 0.84)
- Token cost: 323,666 input · 0 output

## Community Hubs (Navigation)
- Ardmore UAT Sage TEST lock register
- Frappe App Permissions & Layout
- Windows-Owned .git Blocks Linux Bash Sandbox Pushes
- Insights v3 Queries & KPIs
- v16 modern desk navbar swallows real mouse clicks
- A desk Page's CSS is served stale after deploy unless you bump its cache-buster
- erpnext_sbca (Sage ↔ ERPNext bridge app)
- Frappe Dialog Grid Gotchas
- Minimal Fork Overlay Pattern
- Ardmore Wholesale Pricing
- Gotcha: scheduler script fires on enable; Phone field needs country code
- Windows-Owned .git Blocks Linux Bash Sandbox Pushes
- Bulk-updating 6,000 Items: insert the child row directly instead of `item.save()`
- Gotcha: Insights fork sqlglot pin breaks Frappe migrate
- Ardmore POS Print & Payments
- "The site takes 30 seconds to load" is ASP.NET cold start, not slow code
- Ardmore Sage Invoice Posting
- Price List Bootinfo Cache
- API/reconciliation.py daily worker
- Ardmore Site Config Notes
- Sage QOH & Reconciliation Sync
- quick_purchase_invoice.js
- QuickPurchaseInvoice
- Sage Default Price List Gap
- Outdated POS Opening Entry Blocks the Till
- "The warehouse only has ceramics" — a link query that ignores the typed text
- Ardmore Stock Locations & R0.01
- post-taxinvoice-to-sage
- Bulk-updating 6,000 Items: insert the child row directly instead of `item.save()`
- API/reconciliation.py daily worker
- Ardmore Go-Live Structure
- insights-theme-all-sites.user.js
- Ardmore first live stock pull gotcha
- POST /api/InventorySync/get-items-by-code-for-erpnext
- Warehouse ownership by Sage company (1 Nov)
- The five mistakes that wasted a day
- API/reconciliation.py daily worker
- Ardmore hand-over to site laptop 27 Oct 2026
- nest_theme Deploy recipe (4)
- The five mistakes that wasted a day (2)
- Intercompany posting: tax invoice in seller + supplier invoice in buyer
- The five mistakes that wasted a day
- vue-grid-layout verticalCompact hoists dashboard items
- Bulk-updating 6,000 Items: insert the child row directly instead of `item.save()`
- InventorySyncController (merged)
- InventorySyncController (merged)
- Ardmore Final Test Plan
- The five mistakes that wasted a day
- "The warehouse only has ceramics" — a link query that ignores the typed text
- "The warehouse only has ceramics" — a link query that ignores the typed text
- "The warehouse only has ceramics" — a link query that ignores the typed text
- Bulk-updating 6,000 Items: insert the child row directly instead of `item.save()`
- One writer per file boundary rule
- InventorySyncController (merged)
- InventorySyncController (merged)
- nest_theme Deploy recipe
- Shrink-overwrite leaves a NULL-padded tail on the bash mount
- "The warehouse only has ceramics" — a link query that ignores the typed text
- "The warehouse only has ceramics" — a link query that ignores the typed text
- "The warehouse only has ceramics" — a link query that ignores the typed text
- Gotcha: Frappe v16 query, notification and assignment changes
- InventorySyncController (merged)
- nest_theme Deploy recipe (3)
- ardmoreceramics.c.frappe.cloud site
- The five mistakes that wasted a day
- ensure_party_group
- Claude Desktop MSIX config path gotcha
- "The warehouse only has ceramics" — a link query that ignores the typed text
- Gotcha: print format PDF margins come from .print-format CSS
- SageErpNextAPI (Pharoh middleware)
- get_supplier_last_rate
- QuickPurchaseInvoiceItem
- nest_theme Deploy recipe (5)
- Gotcha: new form numbers are zero and workflow needs Cancelled state
- commit_reconciliation_feature.sh
- Gotcha: git on network drive needs safe.directory
- quick_purchase_invoice

## God Nodes (most connected - your core abstractions)
1. `ardmoreceramics.c.frappe.cloud site` - 92 edges
2. `Ardmore UAT Sage TEST lock register` - 23 edges
3. `Syncflo_internal_V16 / nesterp site` - 19 edges
4. `Gotcha: till sales never reached Sage, QOH sync leaked stock` - 18 edges
5. `CoWork_Helper README (knowledge-base index)` - 17 edges
6. `nest_home app` - 16 edges
7. `Ardmore hand-over to site laptop 27 Oct 2026` - 16 edges
8. `get-inventory-qtyonhand-for-erpnext (QOH sync)` - 16 edges
9. `post-taxinvoice-to-sage Server Script` - 16 edges
10. `Pharoh gateway (C# SageErpNextAPI, owned by Russell)` - 15 edges

## Surprising Connections (you probably didn't know these)
- `SQL functions as strings refused in fields; use dict syntax {COUNT: *}` --semantically_similar_to--> `Instance cleaned for go-live (13 Oct, temp API script wipe)`  [INFERRED] [semantically similar]
  gotchas/2026-10-23-frappe-v16-query-and-assignment-changes.md → sites/ardmore.md
- `"Why this is non-obvious" section` --semantically_similar_to--> `The five mistakes that wasted a day`  [INFERRED] [semantically similar]
  templates/gotcha-template.md → skills/frappe-insights-v3-dashboard/SKILL.md
- `Customer/Supplier category -> group sync (ensure_party_group)` --semantically_similar_to--> `get-customers-for-erpnext-new (hourly Sage customer sync)`  [INFERRED] [semantically similar]
  projects/erpnext_sbca/ASSESSMENT.md → sites/ardmore.md
- `allowed_roles Honoured Only on Library Fallback` --semantically_similar_to--> `Frappe Permissions Are Additive — No Per-User Deny`  [INFERRED] [semantically similar]
  gotchas/2026-05-28-nest-home-tile-needs-layout-not-just-library.md → playbooks/frappe-role-based-access-control.md
- `Child-Table Updates Replace, Not Merge` --semantically_similar_to--> `Custom Role Provisioning Workflow`  [INFERRED] [semantically similar]
  gotchas/2026-05-28-nest-home-tile-needs-layout-not-just-library.md → playbooks/frappe-role-based-access-control.md

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
- **Hyde Park count load check/align/load flow** — sites_ardmore_golive_requirements_2026_11_01_count_loader, sites_ardmore_golive_requirements_2026_11_01_get_item_selectionid_for_erpnext, sites_ardmore_golive_requirements_2026_11_01_sage_item_selection, sites_ardmore_handover_2026_10_27_stock_already_owned, sites_ardmore_golive_requirements_2026_11_01_jhb_atrium_home_a, sites_ardmore_golive_requirements_2026_11_01_hyde_park_hdsq_a [EXTRACTED 1.00]
- **SAGE_FORCE_COMPANY TEST lock lifted in five posting scripts** — sites_ardmore_golive_requirements_2026_11_01_sage_test_lock, sites_ardmore_golive_requirements_2026_11_01_post_taxinvoice_to_sage, sites_ardmore_golive_requirements_2026_11_01_post_customerreturn_to_sage, sites_ardmore_golive_requirements_2026_11_01_post_intercompany_transfer_to_sage, sites_ardmore_golive_requirements_2026_11_01_post_intercompany_sale_to_sage, sites_ardmore_golive_requirements_2026_11_01_post_new_item_to_sage [EXTRACTED 1.00]
- **Frappe Cloud deploys broken or misreported by something other than the app shipped** — gotchas_2026_09_29_insights_fork_sqlglot_pin_breaks_frappe_migrate_insights_fork, gotchas_2026_09_29_insights_fork_sqlglot_pin_breaks_frappe_migrate_frappe_cloud_recovered_status, gotchas_2026_10_07_v16_custom_sidebar_patch_fails_on_removed_app_orphaned_site_sidebars, gotchas_2026_10_13_frappe_cloud_deploy_upgrades_frappe_and_drops_font_awesome_font_awesome_dropped, gotchas_2026_10_13_installed_application_version_lags_deployed_code_installed_application_lag [INFERRED 0.75]
- **Frappe changes that save correctly but are not what the user is served** — gotchas_2026_08_12_db_set_value_skips_the_hooks_that_make_a_change_real_doctype_meta_cache, gotchas_2026_08_12_customize_form_blocks_int_to_float_property_setter_fieldtype_trap, gotchas_2026_08_24_frappe_grid_columns_overridden_by_user_settings_user_settings_gridview, gotchas_2026_08_24_erpnext_lead_status_reverts_to_opportunity_status_updater, gotchas_2026_08_06_client_script_listview_settings_assignment_wipes_indicators_listview_settings_assignment, gotchas_2026_08_18_page_css_served_stale_when_the_cache_buster_is_not_bumped_build_marker_cache_buster [INFERRED 0.85]
- **QOH stock sync batch failure modes and fixes** — gotchas_2026_11_01_ardmore_first_live_stock_pull_fractional_qty_whole_number_uom, gotchas_2026_11_01_ardmore_first_live_stock_pull_negative_sage_average_cost, gotchas_2026_11_01_ardmore_first_live_stock_pull_stock_reconciliation_batch_failure, sites_ardmore_golive_requirements_2026_11_01_get_inventory_qtyonhand_for_erpnext, sites_ardmore_handover_2026_10_27_qoh_sync_failed_batch_fix [INFERRED 0.85]
- **Insights v3 Positional CSS Theming Chain** — gotchas_2026_05_06_insights_spa_no_frappe_runtime_vgl_layout_selectors, gotchas_2026_05_06_insights_dashboard_client_script_styling_nth_child_selector_strategy, gotchas_2026_05_06_insights_filter_order_vs_css_nth_child_filter_last_in_items, gotchas_2026_05_06_insights_spa_no_frappe_runtime_positional_layout_convention, apply_dashboard_styling [INFERRED 0.85]
- **Ardmore till client scripts loaded inside the POS page** — playbooks_frappe_webhook_to_omnisend_pos_customer_ux_client_script, gotchas_2026_09_07_pos_invoice_client_scripts_run_inside_pos_page_pos_split_payment_autobalance, gotchas_2026_09_07_pos_invoice_client_scripts_run_inside_pos_page_pos_voucher_ref, gotchas_2026_09_07_pos_invoice_client_scripts_run_inside_pos_page_pos_return_item_picker, gotchas_2026_09_21_pos_sales_never_reached_sage_stock_leak_pos_till_scripts_loader [INFERRED 0.95]
- **Ardmore ERPNext-to-Sage posting pipeline under the TEST-only lock** — gotchas_2026_09_21_pos_sales_never_reached_sage_stock_leak_post_taxinvoice_to_sage, gotchas_2026_09_21_pos_sales_never_reached_sage_stock_leak_post_customerreturn_to_sage, gotchas_2026_09_29_sage_returns_and_retry_retry_failed_sage_sync, gotchas_2026_09_21_pos_sales_never_reached_sage_stock_leak_sage_force_company_lock, gotchas_2026_09_21_pos_sales_never_reached_sage_stock_leak_qoh_sync, gotchas_2026_09_22_ardmore_uat_sage_test_lock_register_intercompany_transfer_to_sage [INFERRED 0.95]
- **TEST-only lock scripts unlocked together at go-live** — sites_ardmore_sage_test_only_lock, sites_ardmore_post_taxinvoice_to_sage, sites_ardmore_post_customerreturn_to_sage, sites_ardmore_post_new_item_to_sage [EXTRACTED 1.00]
- **Sage -> ERPNext pull syncs through Pharoh** — sites_ardmore_get_inventory_for_erpnext, sites_ardmore_get_inventory_qtyonhand_for_erpnext, sites_ardmore_get_additional_prices_for_erpnext, sites_ardmore_get_customers_for_erpnext_new, sites_ardmore_pharoh, sites_ardmore_sync_home_retail_prices [INFERRED 0.85]
- **Ardmore POS till client scripts loaded on every till** — sites_ardmore_pos_till_client_scripts, sites_ardmore_pos_customer_ux, sites_ardmore_pos_voucher_ref, sites_ardmore_pos_cart_quantity, sites_ardmore_pos_no_submit_confirm, sites_ardmore_pos_item_tile_names, sites_ardmore_pos_recent_orders_sales_returns, sites_ardmore_pos_new_invoice_from_recent_orders, sites_ardmore_pos_ceramic_price_edit, sites_ardmore_pos_item_warehouse_lock, sites_ardmore_pos_second_warehouse [EXTRACTED 1.00]
- **Default price list sync gap (why Home - Retail Price stayed empty)** — gotchas_2026_11_02_sage_default_price_list_empty_in_erpnext_custom_is_default, gotchas_2026_11_02_sage_default_price_list_empty_in_erpnext_additionalitempricessync, gotchas_2026_11_02_sage_default_price_list_empty_in_erpnext_get_additional_prices_for_erpnext, gotchas_2026_11_02_sage_default_price_list_empty_in_erpnext_custom_sage_sync_offset_done, gotchas_2026_11_02_sage_default_price_list_empty_in_erpnext_home_retail_price [EXTRACTED 1.00]
- **Home retail price fix flow (inventory feed to Hyde Park till)** — gotchas_2026_11_02_sage_default_price_list_empty_in_erpnext_pharoh_inventory_feed, gotchas_2026_11_02_sage_default_price_list_empty_in_erpnext_standard_rate_incl, gotchas_2026_11_02_sage_default_price_list_empty_in_erpnext_sync_home_retail_prices, gotchas_2026_11_02_sage_default_price_list_empty_in_erpnext_home_retail_price, gotchas_2026_11_02_sage_default_price_list_empty_in_erpnext_hyde_park_pos_profile [EXTRACTED 1.00]

## Communities (86 total, 17 thin omitted)

### Community 0 - "Ardmore UAT Sage TEST lock register"
Cohesion: 0.07
Nodes (43): ardmoreceramics.c.frappe.cloud (Ardmore site), Gotcha: POS Invoice client scripts run inside the POS page, Ardmore POS Receipt print format, custom_voucher_ref custom field, make_sales_return (copies every line negated), POS Closing - Cashier UX client script, POS Return Item Picker client script, POS Split Payment Autobalance client script (+35 more)

### Community 1 - "Frappe App Permissions & Layout"
Cohesion: 0.05
Nodes (38): App JSON permissions[] Is the Complete Allow-List, business_subscription.json, load_doctype_module / run_module_method, Nest Home Layout Tile DocType, allowed_roles Honoured Only on Library Fallback, Child-Table Updates Replace, Not Merge, Nest Home Layout DocType, resolve_layout() / boot._resolve_landing (+30 more)

### Community 2 - "Windows-Owned .git Blocks Linux Bash Sandbox Pushes"
Cohesion: 0.06
Nodes (38): Fresh Deploy After Pushing a Frappe Cloud App, Git / Deploy Conventions (Git Bash MINGW64), Host vs Bash Mount Desync Warning, Negative-Value Conditional Formatting, custom-dashboard-styling.css, Dashboard Layout Rebalance (KPI row, hero chart, paired tables), Manufacturing Operations Dashboard Polish, git reset HEAD Half-Staged State Recovery (+30 more)

### Community 3 - "Insights v3 Queries & KPIs"
Cohesion: 0.06
Nodes (46): Friendlier KPI Card Names, Purchase Invoice Item child doctype, Insights v3 code Operation (Python/ibis), Insights Query v3 DocType, Insights v3 sql / raw_sql Operation, Dashboard Filter Requires Column in Source Query SELECT, getAdhocFilters (dashboard.ts), Row-Level Source + Summarize-in-data_query Refactor (+38 more)

### Community 4 - "v16 modern desk navbar swallows real mouse clicks"
Cohesion: 0.07
Nodes (22): Introspect schema via referencing doctypes instead of DocField, nest_theme custom Frappe v16 theme app, Render custom widgets outside header.desktop-navbar, attachRealtime() deferred-registration helper, Workspace autoname field:title defeats frappe.client.insert, workspace.new_page() permission guard (session.user == for_user), Frappe Cloud bench layer vs site layer separation, Frappe module discovery maps title-case module to snake_case folder (+14 more)

### Community 5 - "A desk Page's CSS is served stale after deploy unless you bump its cache-buster"
Cohesion: 0.07
Nodes (33): Page CSS served stale when cache-buster not bumped, A desk Page's CSS is served stale after deploy unless you bump its cache-buster, BUILD_MARKER CSS cache-buster, Cause, Fingerprinted desk Page JS bundle, Fix, fuse_floor.js (had no cache-buster), fuse_home.js / fuse_home.css (fuse_theme) (+25 more)

### Community 6 - "erpnext_sbca (Sage ↔ ERPNext bridge app)"
Cohesion: 0.07
Nodes (23): Inherited Frappe app audit recipe, Post-Write Verification via bash (wc/tail/node --check), Read Tool Serves Harness Tracked Intent, Not Disk, 9p/virtio Mount Writeback Race on Dotfiles, stat mtime Disambiguation Rule, party_activity.js (nest_crm_tasks), Company Sage Integration child table, Doreen (9t9it Frappe partner, app author) (+15 more)

### Community 7 - "Frappe Dialog Grid Gotchas"
Cohesion: 0.07
Nodes (22): Customer-Quick-Invoice Client Script, frappe.ui.Dialog Table Grid, col-xs-N max-width Cap Blocks flex-grow, qi-dialog Wrapper Scope Class, setup_visible_columns, git push origin HEAD Rule of Thumb, DocType Folder Three-File Requirement, getpage Serves Page Script from Bench Files, Not DB (+14 more)

### Community 8 - "Minimal Fork Overlay Pattern"
Cohesion: 0.07
Nodes (19): COLOR_MAP (charts/colors.ts), Frappe Cloud fork deploy sequence, frontend/src2/main.ts entry point, syncflo-custom-chart-palette.ts, syncflo-custom-overrides.css, Tampermonkey per-device userscript, Chart-not-rendering diagnostic ladder, Insights Chart v3 (+11 more)

### Community 9 - "Ardmore Wholesale Pricing"
Cohesion: 0.10
Nodes (24): Ardmore - Wholesale price list (stockists / Account Sale), build-ardmore-wholesale-price-list (hourly merge into Ardmore - Wholesale), Item Price.custom_from_sheet flag, Item.custom_opening_qty, Item.custom_qty_pending_sage (local-qty flag), Exact-match str.replace patcher via temp API Server Script, get-additional-prices-for-erpnext (price list sync), Home/Fashion importer (Server Script) (+16 more)

### Community 10 - "Gotcha: scheduler script fires on enable; Phone field needs country code"
Cohesion: 0.10
Nodes (25): Gotcha: ERPNext v16 QI reading_1 vs reading_value, Certificate of Analysis print format, fuse_manufacturing quality.py create_for_line, Gotcha: submit after Quality Inspection needs reload, fuse_manufacturing app (0.10.3 / 0.10.4), TimestampMismatchError on parent submit after QI submit, Gotcha: validate-time inspection check refusing drafts blocks inspected lines, check_inspections doc_event hook (+17 more)

### Community 11 - "Windows-Owned .git Blocks Linux Bash Sandbox Pushes"
Cohesion: 0.09
Nodes (17): Active Projects and Sites Register, CoWork_Helper Knowledge Base, CoWork_Helper Folder Layout, Russell's Working Style Rules, Lead-source-reqd / Lead-utm_source-reqd Property Setters, Ledger Link Guards Block Voucher and Company Deletes, Only Lead and Opportunity Are Company-Tagged, Transaction Deletion Record (TDR) (+9 more)

### Community 12 - "Bulk-updating 6,000 Items: insert the child row directly instead of `item.save()`"
Cohesion: 0.11
Nodes (26): Frappe child-row insert bypasses parent validation, One bad row poisons a whole batch (recurring failure mode), Bulk-updating 6,000 Items: insert the child row directly instead of `item.save()`, Cause, Document.save() revalidates every parent field, Fix, Item Barcode child table, See also (+18 more)

### Community 13 - "Gotcha: Insights fork sqlglot pin breaks Frappe migrate"
Cohesion: 0.12
Nodes (17): Gotcha: Insights fork sqlglot pin breaks Frappe migrate, Syncflo-design/insights fork (syncflo-custom-theme), sql_metadata 3.x (Frappe core dependency), Compare fork pins with upstream pyproject files, Gotcha: v16 convert_custom_sidebars patch fails on removed app, dock.check_docked_app, frappe.patches.v16_0.convert_custom_sidebars, nesterpdemo.c.frappe.cloud (NestERP demo site) (+9 more)

### Community 14 - "Ardmore POS Print & Payments"
Cohesion: 0.11
Nodes (23): Airport POS Profile (recreated disabled; Airport not in go-live), Ardmore POS Receipt print format, Ardmore Tax Invoice print format (A4, item pictures), POS payment amounts entered cents-style (upstream quirk), Credit note numbering ACC-CRN (Before Insert script), Go-live day fixes 2 Nov 2026 (Hyde Park till), Home - Retail Price list (Hyde Park till), Hyde Park POS Profile (HDSQ - A) (+15 more)

### Community 15 - ""The site takes 30 seconds to load" is ASP.NET cold start, not slow code"
Cohesion: 0.15
Nodes (21): ASP.NET cold start makes the first page slow, Cause, debug=true shipped by copy/paste deploy, machine.config <deployment retail="true">, Fix, IIS AlwaysRunning + preloadEnabled (Application Initialization), IIS app pool idle recycle (20 min default), ASP.NET on-demand page compilation (+13 more)

### Community 16 - "Ardmore Sage Invoice Posting"
Cohesion: 0.18
Nodes (13): ardmore-send-invoice-to-sage (Send to Sage button), Pharoh TaxInvoice/get-sales-history-for-erpnext, get-sales-history-for-erpnext (readback), tmp-sage-test-readback temporary script, nest_account_sale app (Account Sale screen), Jon Berning (director), Ken Silversten (director), POS Ceramic Price Edit client script (Rate unlocked for Ceramics) (+5 more)

### Community 17 - "Price List Bootinfo Cache"
Cohesion: 0.15
Nodes (16): Gotcha: disabled default price list and stale bootinfo cache, erpnext.stock.get_item_details.apply_price_list, POS Profiles Airport/Caversham/Joburg on disabled Standard Selling, Selling Settings Default Price List, Standard Selling price list (disabled), Importer rejects invalid Select value and shows the first option, Item sync wiped custom_size on every item (line removed), get-inventory-for-erpnext (item sync) (+8 more)

### Community 18 - "API/reconciliation.py daily worker"
Cohesion: 0.12
Nodes (11): Frappe Webhook DocType, webhook.get_webhook_headers(), Channel Status Vocabulary (subscribed/nonSubscribed/unsubscribed), Omnisend Classic v3 POST /contacts, add_to_mailing_list Custom Field, Frappe Webhook Record (Customer on_update), Omnisend Contacts v3 API, Webhook Request Log verification (+3 more)

### Community 19 - "Ardmore Site Config Notes"
Cohesion: 0.20
Nodes (18): allow_in_returns on POS Payment Methods, ardmoreceramics.c.frappe.cloud site, Frappe 16.51 desk route /app -> /desk breaks hand-written links, 177 fabric items moved to Meter (direct table writes), Feet Through Door field on POS Closing (hidden for online tills), Ardmore Getting Stock In Guide, Guides Web Page (/guides) and Guides tile, Cheri Marshall (JHBM warehouse + Online store manager) (+10 more)

### Community 20 - "Sage QOH & Reconciliation Sync"
Cohesion: 0.16
Nodes (15): Payment reconciliation job (Sage Reconciliation Log), custom_last_qtyonhand_sync cursor (rewind to force a re-pull), Disabled items block Stock Reconciliation (skip-disabled guard), First full QOH pull skips zero-on-hand items (incl_zero false), get-inventory-qtyonhand-for-erpnext (QOH sync), Ardmore Go-Live Plan v1.0 - Hyde Park and Online (docx), Pharoh gateway (C# SageErpNextAPI, owned by Russell), Phase 2: post a customer receipt to Sage with each invoice (+7 more)

### Community 21 - "quick_purchase_invoice.js"
Cohesion: 0.22
Nodes (12): compute_amount(), entry_ref(), entry_type(), fill_from_account(), fill_from_item(), flt(), items_add(), paint_row_classes() (+4 more)

### Community 23 - "Sage Default Price List Gap"
Cohesion: 0.20
Nodes (15): AdditionalItemPricesSync (Sage endpoint), Ardmore - Retail (ERPNext price list), Stock Settings auto_insert_price_list_rate_if_missing, Sage default price list (custom_is_default=1), custom_sage_sync_offset / custom_sage_sync_done (price list sync state), get-additional-prices-for-erpnext (Server Script), get-inventory-for-erpnext (Server Script), Home - Retail Price (ERPNext price list) (+7 more)

### Community 24 - "Outdated POS Opening Entry Blocks the Till"
Cohesion: 0.14
Nodes (11): POS Closing Entry, post-customerreturn-to-sage Server Script, post-taxinvoice-to-sage Server Script, apply_to_all_doctypes User Permission Flag, User Permission Diagnosis Shortcut (list + Bin check), Ardmore Store Stock & POS Guide v1.2, POS Closing Recovery Procedure, POS Opening Entry (+3 more)

### Community 25 - ""The warehouse only has ceramics" — a link query that ignores the typed text"
Cohesion: 0.24
Nodes (14): A link query that ignores txt looks like missing data, frappe.call sends nested filters as a JSON string, in_stock_items link query (ignores txt), item_query restricted to Bin in-stock codes, server_scripts third-party app (Paul Christian Mata), Client Script set_query override on next tick (setTimeout 0), Stock Transfer doctype (server_scripts app), Customize Form blocks Int to Float (+6 more)

### Community 26 - "Ardmore Stock Locations & R0.01"
Cohesion: 0.16
Nodes (14): Stock Settings auto_insert_price_list_rate_if_missing (R0.01 till rows), nest_home.api.build_profile_view (tile naming series stuck on NEST-TILE-0001), JHB Main Holding JHBM - A (retired), JHBM - A (JHB Main Holding), nest_home app (tiles, layouts, landing page), nest_home pos_pricing R0.01 sentinel override, nest_stock_request app (store -> head office stock requests), Sales Assistant role and Nest Home layout (+6 more)

### Community 27 - "post-taxinvoice-to-sage"
Cohesion: 0.19
Nodes (14): nest_stock_request 0.3.0, Ardmore hand-over to site laptop 27 Oct 2026, Export Proof tile and export-proof-count, Nest Home Tile count badges, POS Split Payment Autobalance / Voucher Ref route gate, pos-sales-people API Server Script, POS Sales Person client script (Select POS User), POS Till Scripts Loader (+6 more)

### Community 28 - "Bulk-updating 6,000 Items: insert the child row directly instead of `item.save()`"
Cohesion: 0.21
Nodes (13): Zero-valuation seed stock warns on every transfer, allow_zero_valuation_rate (the wrong fix), Cause, Fix, Item.valuation_rate default vs stock ledger valuation, Batched Stock Reconciliation re-valuation (chunks of 25), Sage QOH sync (get-inventory-qtyonhand-for-erpnext), See also (+5 more)

### Community 29 - "API/reconciliation.py daily worker"
Cohesion: 0.18
Nodes (8): POST post-financial-stock-reconciliation-to-sage, Multi-row lines[] journal payload, POST post-journalentry-to-sage, Sage Effect enum (1=Debit, 2=Credit), entryType metadata values, push_stock_adjustment_on_submit toggle, StockAdjustmentSyncController, Journal Entry push (journal_entry.py)

### Community 30 - "Ardmore Go-Live Structure"
Cohesion: 0.24
Nodes (13): custom_sage_entity on POS Profile and Warehouse, Stock Entry custom_stock_already_owned flag, Instance cleaned for go-live (13 Oct, temp API script wipe), Go-live structure: one company Ardmore, one till + warehouse per store, Main Distribution - A (single warehouse all stock moves through), Online POS Profile (sells from Main Distribution), Opening count loads = transfers out of Main Distribution after first full QOH pull, post-intercompany-sale-to-sage (point 2) (+5 more)

### Community 31 - "insights-theme-all-sites.user.js"
Cohesion: 0.27
Nodes (12): buildCSS(), CHART_PALETTE_EXTRAS, getChartPalette(), getTheme(), injectTheme(), isNeutralFill(), paletteSet, recolorAllCharts() (+4 more)

### Community 32 - "Ardmore first live stock pull gotcha"
Cohesion: 0.26
Nodes (11): Ardmore first live stock pull gotcha, Seven fabrics changed from each to Meter UOM, Fractional Sage quantity on whole-number UOM, Negative Sage average cost, One bad line fails the whole 25-line Stock Reconciliation batch, tmp-compare-sage-stock temporary API script, Ardmore go-live requirements and Sunday runbook, Company Sage Integration Default Warehouse as stock-sync switch (+3 more)

### Community 33 - "POST /api/InventorySync/get-items-by-code-for-erpnext"
Cohesion: 0.24
Nodes (10): Pharoh selectionid lookup fails at 25+ codes per call, Pharoh Get Items By Code endpoint brief, apikey selects the Sage company (one call per company), get-inventory-for-erpnext, POST /api/InventorySync/get-items-by-code-for-erpnext, Process codes independently (one bad code must not abort the rest), ardmore-count-load API Server Script, POST /api/InventorySync/get-item-selectionid-for-erpnext (+2 more)

### Community 34 - "Warehouse ownership by Sage company (1 Nov)"
Cohesion: 0.21
Nodes (12): Airport AORT - A, Caversham ACA - A, Home Fashion Importer, Hyde Park HDSQ - A, JHB Atrium Ceramics - A (goods in transit), JHB Atrium Fashion - A, JHB Atrium Home - A, Kiln Sheet Importer (+4 more)

### Community 35 - "The five mistakes that wasted a day"
Cohesion: 0.27
Nodes (9): Gotcha: Insights v3 dashboard filters, chart labels and DuckDB trap, measure_name / dimension_name are the on-screen labels, Insights v3 dashboard filter item (links keyed by chart name), Raw SQL runs in DuckDB: Duplicate CTE name when a table is referenced twice, is_public dashboards are served without login, Insights 3.12.2 dashboard grid is 20 columns, not 12, Insights dashboards Ardmore Sales + Year on Year (workbook 4), Non-stock line filter on dashboard source queries (+1 more)

### Community 36 - "API/reconciliation.py daily worker"
Cohesion: 0.20
Nodes (7): push_reconciliation_on_schedule toggle, API/reconciliation.py daily worker, last_reconciliation_sync shared timestamp, Reconciliation Journal Entry, Sage Payments Clearing account, Sage CustomerTransactionListing report, ReconciliationSyncController

### Community 37 - "Ardmore hand-over to site laptop 27 Oct 2026"
Cohesion: 0.24
Nodes (11): post-new-item-to-sage bare 400 on duplicate code, Ardmore Ceramics TEST training company, post-customerreturn-to-sage, post_new_item_to_sage, post-taxinvoice-to-sage, Sage TEST lock (SAGE_FORCE_COMPANY), Sales rep = person picked in Select POS User, Discount percentage sent as fraction fix (+3 more)

### Community 38 - "nest_theme Deploy recipe (4)"
Cohesion: 0.20
Nodes (8): MIT License (Syncflo, 2026), Quick Purchase Invoice (Frappe module), patches.txt pre/post model sync sections, Accounting Crisp palette, drop_user_preference_doctype patch, Nest Theme User Preference (DocType, retired), Toolbar density / font-scale widgets (retired), production_floor app (RM Issue module)

### Community 39 - "The five mistakes that wasted a day (2)"
Cohesion: 0.20
Nodes (9): Palette switching live test (v0.3.0 addendum), Six-palette gallery (light + dark variants), Soft Professional palette, SVG chart palette recolourer, Industrial Pro theme (retired), Syncflo-design/insights fork (syncflo-custom-theme), KPI drill-through modal (syncflo-custom-drill-through.ts), Soft Professional Insights theme (+1 more)

### Community 40 - "Intercompany posting: tax invoice in seller + supplier invoice in buyer"
Cohesion: 0.24
Nodes (10): Intercompany Failed has no automatic retry, Intercompany posting: tax invoice in seller + supplier invoice in buyer, post-intercompany-sale-to-sage, post-intercompany-transfer-to-sage, post-supplierinvoice-to-sage, block-sale-without-wholesale-price Server Script, block-transfer-without-wholesale-price Server Script, Stock already owned flag (custom_stock_already_owned) (+2 more)

### Community 41 - "The five mistakes that wasted a day"
Cohesion: 0.22
Nodes (5): Manufacturing Operations dashboard (0qj8e3nb4t), MD Overview dashboard (2uljes564g), "Site DB" data source name, Chart config column binding, Data query source-op wrapper

### Community 42 - "vue-grid-layout verticalCompact hoists dashboard items"
Cohesion: 0.22
Nodes (7): skills/frappe-insights-v3-dashboard/templates/chart_table.json, data_query needs a summarize operation, not just source, insights/frontend/src2/dashboard/DashboardBuilder.vue, insights/frontend/src2/dashboard/Dashboard.vue, dashboard_vertical_compact lives in localStorage, not the doctype, Empty text spacer item blocks the compact pass, insights/frontend/src2/dashboard/VueGridLayout.vue

### Community 43 - "Bulk-updating 6,000 Items: insert the child row directly instead of `item.save()`"
Cohesion: 0.33
Nodes (9): Price list holding two VAT conventions at once, Item Price custom_from_sheet precedence flag, Ex-VAT vs incl-VAT price conflict on one price list, included_in_print_rate on every company's VAT template, Sage price sync (get-additional-prices-for-erpnext), standard_rate relabelled 'Retail Price Excl Vat' (decoy field), Committed-but-not-pushed hides Frappe Cloud 'Update Available', Ardmore site (ardmoreceramics.c.frappe.cloud) (+1 more)

### Community 44 - "InventorySyncController (merged)"
Cohesion: 0.22
Nodes (4): sageId → custom_sage_customer_id match key, PartyBalanceDTO, Price List.custom_sage_price_list_id bridge field, Sales Person sync (custom_sage_rep_id)

### Community 45 - "InventorySyncController (merged)"
Cohesion: 0.25
Nodes (4): POST get-stock-levels-for-erpnext, Get Stock Levels endpoint brief, API/stock.py import_stock_levels_from_sage(), Opening Stock reconciliation

### Community 46 - "Ardmore Final Test Plan"
Cohesion: 0.36
Nodes (8): Final-test plan (option 1: real tills under the TEST lock), frappe_update with docstatus 1 submits when frappe.client.submit hits TimestampMismatch, Go-live target Monday 2 November 2026 (switch-on Sunday), TEST-only lock (SAGE_FORCE_COMPANY = Ardmore Ceramics TEST), Training warehouses Test-Main Distribution / Test-JHB Holding / Test-POS - ACT, Training logins testpos / testonline / testmanager, Training setup on Ardmore Ceramics TEST (no Sage connection), Go-live weekend plan (Sat count, Sun training + switch-on, Mon live)

### Community 47 - "The five mistakes that wasted a day"
Cohesion: 0.29
Nodes (7): Insights Chart v3 doctype, Insights Dashboard v3 doctype, Insights Query v3 doctype, Frappe Insights v3 Dashboard Construction skill, Insights Workbook doctype, Full build recipe — one chart start to finish, Append chart to dashboard items JSON

### Community 48 - ""The warehouse only has ceramics" — a link query that ignores the typed text"
Cohesion: 0.43
Nodes (6): Server Script safe_exec sandbox limits + reading .xlsx, Ardmore Kiln Sheet / Home Fashion importers, Server Script functions cannot see script-level names, Syncflo-design repos use HTTPS remotes only, nest_sheets app (read_sheet API), Server Script sandbox has no re module; write digit filter as a loop

### Community 49 - ""The warehouse only has ceramics" — a link query that ignores the typed text"
Cohesion: 0.29
Nodes (7): Cause, Fix, How to prove it in one call, See also, Symptom, "The warehouse only has ceramics" — a link query that ignores the typed text, Why this is non-obvious

### Community 50 - ""The warehouse only has ceramics" — a link query that ignores the typed text"
Cohesion: 0.52
Nodes (6): frappe.db.set_value skips the hooks that make a change real, Server-side doctype meta cache, frappe.db.set_value raw column write, Load-and-save (doc.save) to fire on_update, Version records (audit trail), 116 items' excl price overwritten via db.set_value (no Version)

### Community 51 - "Bulk-updating 6,000 Items: insert the child row directly instead of `item.save()`"
Cohesion: 0.29
Nodes (7): Cause, Fix, One price list, two VAT conventions — the till charging 15% wrong depending on who wrote last, See also, Symptom, The mistake worth not repeating, Why this is non-obvious

### Community 52 - "One writer per file boundary rule"
Cohesion: 0.33
Nodes (3): Design→Dev handoff checklist, Machine A — Design & Layout, Machine B — Development, Review & Testing

### Community 53 - "InventorySyncController (merged)"
Cohesion: 0.29
Nodes (4): POST disable-qty-tracking, InventorySyncController (merged), ERPNext-side route map, Disable Sage Qty Tracking endpoint brief

### Community 54 - "InventorySyncController (merged)"
Cohesion: 0.33
Nodes (4): POST get-inventory-for-erpnext, {TotalResults, ReturnedResults, Items} envelope, Pagination audit Copilot brief (txt edition), Services/SageService.cs $skip layer

### Community 56 - "Shrink-overwrite leaves a NULL-padded tail on the bash mount"
Cohesion: 0.40
Nodes (3): rstrip-NULL rewrite fix for padded files, Write large files via bash heredoc to dodge mount truncation, Bash-side file/wc/git diff is ground truth, not the host Read tool

### Community 57 - ""The warehouse only has ceramics" — a link query that ignores the typed text"
Cohesion: 0.33
Nodes (6): Cause, Customize Form refuses Int → Float, and forcing it past the check corrupts the data, Fix, See also, Symptom, Why this is non-obvious

### Community 58 - ""The warehouse only has ceramics" — a link query that ignores the typed text"
Cohesion: 0.33
Nodes (6): Cause, Fix, `frappe.db.set_value` writes the row but skips everything that makes the change take effect, See also, Symptom, Why this is non-obvious

### Community 59 - ""The warehouse only has ceramics" — a link query that ignores the typed text"
Cohesion: 0.60
Nodes (6): ERPNext Lead status reverts to Opportunity, doc.flags not cleared by doc.reload(), Frappe save order (before_validate -> validate -> before_save), Read core source from GitHub at the installed app version, ERPNext StatusUpdater (status_map / get_status / set_status), Lead Sticky Status capture/restore Server Scripts

### Community 60 - "Gotcha: Frappe v16 query, notification and assignment changes"
Cohesion: 0.40
Nodes (5): Gotcha: Frappe v16 query, notification and assignment changes, limit_page_length / limit_start deprecated (use limit / offset), nest_assistant app, Notification Log type is a Link to Notification Type, SQL functions as strings refused in fields; use dict syntax {COUNT: *}

### Community 61 - "InventorySyncController (merged)"
Cohesion: 0.40
Nodes (5): POST post-new-item-to-sage, tax.py::build_price_pair (4dp round-trip), Item Tax Template Sage Map child table, tax.py::resolve_sage_tax, Sage Tax DocType (per-tenant sage_idx)

### Community 62 - "nest_theme Deploy recipe (3)"
Cohesion: 0.33
Nodes (3): Customer logo override (Nest Theme Settings.customer_logo), nest_theme Deploy recipe, nest_theme DevTools smoke test

### Community 63 - "ardmoreceramics.c.frappe.cloud site"
Cohesion: 0.40
Nodes (6): Home_Fashion_Import_Template.xlsx (uom column, Allowed values sheet), Insights fork incompatibility blocks every deploy (telemetry import, sqlglot pin), nest_help app (in-app help pages, POS shims), POS Item Tile Names client script (full name, SKU + ID row), Create POS Opening Entry dialog Not now button (nest_help), Static asset cache-bust (?v=nest_help version) for immutable /assets

### Community 64 - "The five mistakes that wasted a day"
Cohesion: 0.33
Nodes (5): Insights render diagnostic ladder, Gotcha template, Diagnostic ladder section, Playbook template, Skill template (SKILL.md frontmatter shape)

### Community 65 - "ensure_party_group"
Cohesion: 0.40
Nodes (4): ensure_party_group(), erpnext_sbca/API/helper_function.py, ERPNext Nested-Set Group Tree, Sage Customer/Supplier Category Sync

### Community 66 - "Claude Desktop MSIX config path gotcha"
Cohesion: 0.70
Nodes (5): Claude Desktop MSIX config path gotcha, claude_desktop_config.json, Syncing Claude Desktop config between machines, MSIX file-system redirection (LocalCache\Roaming), Stale 'Could not load app settings' dialog

### Community 67 - ""The warehouse only has ceramics" — a link query that ignores the typed text"
Cohesion: 0.70
Nodes (5): Frappe grid columns overridden by user settings, in_list_view / columns Property Setters on child DocType, frappe.db.sql is read-only in System Console / Server Scripts, Grid gear 'Reset to default', __UserSettings GridView per-user grid layout

### Community 68 - "Gotcha: print format PDF margins come from .print-format CSS"
Cohesion: 0.60
Nodes (3): Gotcha: print format PDF margins come from .print-format CSS, Line Amount uses item.amount, not net_amount, Repeating letterhead drawn in the top margin

### Community 69 - "SageErpNextAPI (Pharoh middleware)"
Cohesion: 0.40
Nodes (5): InventorySyncController.cs, SageErpNextAPI (Pharoh middleware), Ardmore POS Receipt print format, Company Sage Integration seller details, get-sales-rep-ids-from-sage hourly scheduler

### Community 72 - "nest_theme Deploy recipe (5)"
Cohesion: 0.50
Nodes (4): blomoplastics.jh.frappe.cloud site, frappe-blomo MCP connector, Operator Run DocType, wo_wip app (Works Order WIP)

## Ambiguous Edges - Review These
- `apply-dashboard-styling.js` → `Insights v3 Is a Standalone Vue SPA (no frappe runtime)`  [AMBIGUOUS]
  DASHBOARD-POLISH-GUIDE.md · relation: conceptually_related_to
- `Bash-side file/wc/git diff is ground truth, not the host Read tool` → `Stale .git/index.lock and HEAD.lock block git writes`  [AMBIGUOUS]
  gotchas/2026-05-07-git-stale-index-lock.md · relation: conceptually_related_to

## Knowledge Gaps
- **148 isolated node(s):** `quick_purchase_invoice`, `Syncflo-design repos use HTTPS remotes only`, `COLOR_MAP (charts/colors.ts)`, `syncflo-custom-overrides.css`, `Tampermonkey per-device userscript` (+143 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 298 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ardmoreceramics.c.frappe.cloud site` connect `Ardmore Site Config Notes` to `Frappe App Permissions & Layout`, `erpnext_sbca (Sage ↔ ERPNext bridge app)`, `Frappe Dialog Grid Gotchas`, `Ardmore Wholesale Pricing`, `Gotcha: scheduler script fires on enable; Phone field needs country code`, `Windows-Owned .git Blocks Linux Bash Sandbox Pushes`, `Bulk-updating 6,000 Items: insert the child row directly instead of `item.save()``, `Ardmore POS Print & Payments`, `Ardmore Sage Invoice Posting`, `Price List Bootinfo Cache`, `API/reconciliation.py daily worker`, `Sage QOH & Reconciliation Sync`, `Outdated POS Opening Entry Blocks the Till`, `"The warehouse only has ceramics" — a link query that ignores the typed text`, `Ardmore Stock Locations & R0.01`, `Ardmore Go-Live Structure`, `The five mistakes that wasted a day`, `Ardmore Final Test Plan`, `ardmoreceramics.c.frappe.cloud site`?**
  _High betweenness centrality (0.463) - this node is a cross-community bridge._
- **What connects `quick_purchase_invoice`, `Syncflo-design repos use HTTPS remotes only`, `COLOR_MAP (charts/colors.ts)` to the rest of the system?**
  _148 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Ardmore UAT Sage TEST lock register` be split into smaller, more focused modules?**
  _Cohesion score 0.07380520266182698 - nodes in this community are weakly interconnected._
- **Why does `erpnext_sbca (Sage <-> ERPNext bridge app)` connect `erpnext_sbca (Sage ↔ ERPNext bridge app)` to `Frappe App Permissions & Layout`, `v16 modern desk navbar swallows real mouse clicks`, `Minimal Fork Overlay Pattern`, `Gotcha: scheduler script fires on enable; Phone field needs country code`, `Ardmore Site Config Notes`, `Sage QOH & Reconciliation Sync`?**
  _High betweenness centrality (0.143) - this node is a cross-community bridge._
- **Should `Frappe App Permissions & Layout` be split into smaller, more focused modules?**
  _Cohesion score 0.05333333333333334 - nodes in this community are weakly interconnected._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `apply-dashboard-styling.js` and `Insights v3 Is a Standalone Vue SPA (no frappe runtime)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Bash-side file/wc/git diff is ground truth, not the host Read tool` and `Stale .git/index.lock and HEAD.lock block git writes`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._