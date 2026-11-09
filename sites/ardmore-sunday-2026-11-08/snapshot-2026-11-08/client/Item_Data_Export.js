frappe.listview_settings['Item'] = {
    onload: function(listview) {
        listview.page.add_button("Item Import", () => {
            frappe.new_doc("Item Importer");
            
        });
        listview.page.add_inner_button(__('Export Data'), function() {
            // Redirect to Data Export page
            frappe.route_options = {
                reference_doctype: "Item",
                file_type: "Excel",
                export_fields: "'item_code,custom_category,item_name,custom_sub_category,custom_collection,custom_design,custom_colour,custom_size,custom_base_cloth,image,custom_sculptor_c,custom_thrower_c,custom_painter_c,custom_condition,description"
            };
            
            frappe.set_route("data-export");
        });
    }
};