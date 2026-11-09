frappe.ui.form.on('ToDo', {
  refresh: function(frm) {
    frm.page.remove_inner_button && frm.page.remove_inner_button(__('My Activities'));
    frm.page.set_secondary_action('<i class="fa fa-arrow-left" style="margin-right:6px;"></i>My Activities', function() {
      frappe.set_route('my-activities');
    });
    if ((frm.doc.reference_type === 'Lead' || frm.doc.reference_type === 'Customer') && frm.doc.reference_name) {
      frm.add_custom_button(__('Party Activity Hub'), function() {
        frappe.set_route('party-activity', frm.doc.reference_type, frm.doc.reference_name);
      });
    }
  }
});
