// Download Template button.
// The template is a static asset and is served with a ONE-YEAR browser cache
// (Cache-Control: max-age=31536000, immutable). Without a version on the URL a
// browser that downloaded it once keeps handing out its old copy - which is how
// the uom column went missing for anyone who had used the button before
// (2026-09-29). The nest_help version changes with every release, so the URL
// changes and the browser fetches the new file.
frappe.ui.form.on('Home Fashion Importer', {
    refresh: function(frm) {
        frm.add_custom_button('Download Template', function() {
            var v = (frappe.boot && frappe.boot.versions && frappe.boot.versions.nest_help) || Date.now();
            window.open('/assets/nest_help/help/Home_Fashion_Import_Template.xlsx?v=' + encodeURIComponent(v), '_blank');
        }, 'fa fa-download');
    }
});