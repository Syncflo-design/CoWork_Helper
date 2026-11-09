frappe.ui.form.on('Customer', {
  refresh: function(frm) {
    if (frm.is_new()) return;
    var btn = frm.add_custom_button(__('Activity Hub'), function() {
      frappe.set_route('party-activity', 'Customer', frm.doc.name);
    });
    btn.css({ 'background-color': '#F4D03F', 'border-color': '#F4D03F', 'color': '#212529' });
  }
});
