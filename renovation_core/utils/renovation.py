import frappe


@frappe.whitelist()
def get_sidebar(parent = None):
	if not parent:
		parent = 'All Renovation Sidebar'
	cash_sidebar = frappe.cache().hget('renovation_sidbar', parent)
	if not cash_sidebar:
		cash_sidebar = get_user_sidebar(parent)
		frappe.cache().hset('renovation_sidbar', parent or 'Global', cash_sidebar)
	return cash_sidebar


def get_user_sidebar(parent):
	lft, rgt = frappe.db.get_value("Renovation Sidebar", parent, ["lft", "rgt"])
	conditions = "lft >= {0} and rgt <= {1}".format(lft, rgt)
	
	data = frappe.db.sql("""select renovation_sidebar_name as title, tooltip, is_group, type,
	if (STRCMP(type, "Link")=0, link, target) as target, name, parent_renovation_sidebar as parent from `tabRenovation Sidebar`
	where {}""".format(conditions), as_dict=True)
	rows =[]
	return process_data(data, rows, parent)


def process_data(data, rows, key=None):
	for d in data:
		if d.parent == key:
			if d.is_group:
				d['children'] = []
				process_data(data, d['children'], d.name)
			rows.append(d)
	return rows