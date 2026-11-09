user = frappe.session.user
has_pos = frappe.db.exists('Has Role', {'parent': user, 'role': ['in', ['POS Manager', 'Sales Assistant']], 'parenttype': 'User'})
has_bypass = frappe.db.exists('Has Role', {'parent': user, 'role': ['in', ['System Manager', 'Accounts Manager']], 'parenttype': 'User'})

if has_pos and not has_bypass:
    pos_profiles = frappe.db.get_all('POS Profile User',
        filters={'user': user, 'parenttype': 'POS Profile'},
        pluck='parent')
    if pos_profiles:
        quoted = ["'" + p + "'" for p in pos_profiles]
        conditions = '`tabSales Invoice`.pos_profile IN (' + ', '.join(quoted) + ')'
    else:
        conditions = '1=0'