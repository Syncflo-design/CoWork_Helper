// Merge into Frappe's own ToDo list settings — do NOT reassign
// frappe.listview_settings['ToDo'], that wipes their get_indicator() (priority
// colours), add_fields and column config.
(function () {
    let settings = frappe.listview_settings['ToDo'] = frappe.listview_settings['ToDo'] || {};

    settings.add_fields = (settings.add_fields || []).concat(['reference_type', 'reference_name']);

    settings.formatters = Object.assign({}, settings.formatters, {
        description: function (value, df, doc) {
            var text = value || '';
            if ((doc.reference_type === 'Lead' || doc.reference_type === 'Customer') && doc.reference_name) {
                var safe_party = frappe.utils.escape_html(doc.reference_name);
                var href = '/desk/party-activity/' + encodeURIComponent(doc.reference_type) + '/' + encodeURIComponent(doc.reference_name);
                var icon = doc.reference_type === 'Lead' ? 'fa-user' : 'fa-building';
                var style = 'background:#1B5EA0;color:#fff;margin-right:8px;padding:2px 8px;font-size:11px;font-weight:500;text-decoration:none;border-radius:3px;display:inline-block;vertical-align:middle;line-height:1.5;';
                var badge = '<a href="' + href + '" class="nest-party-badge" onclick="event.stopPropagation();" title="Open Party Activity Hub for ' + safe_party + '" style="' + style + '"><i class="fa ' + icon + '" style="margin-right:4px;"></i>' + safe_party + '</a>';
                return badge + text;
            }
            return text;
        }
    });
})();
