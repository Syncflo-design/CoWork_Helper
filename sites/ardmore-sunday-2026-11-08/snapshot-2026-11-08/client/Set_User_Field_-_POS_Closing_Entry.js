frappe.ui.form.on('POS Closing Entry', {
	onload(frm) {
	    // Check if user field is empty and assign a value of current logged in user
		if (!frm.doc.user) {
		    frm.set_value("user", frappe.session.user);
		}
	},
	pos_opening_entry(frm) {
	    console.log("changed")
	}
});