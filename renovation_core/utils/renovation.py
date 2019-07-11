import frappe

global_list = []

@frappe.whitelist()
def get_sidebar(user=None):
	if not user:
		user = frappe.session.user
	parent= "All Renovation Sidebar"
	cache_sidebar = frappe.cache().hget('renovation_sidebar', user)
	if not cache_sidebar:
		cache_sidebar = get_user_sidebar(parent, user)
		frappe.cache().hset('renovation_sidebar', user, cache_sidebar)
	return cache_sidebar


def get_user_sidebar(parent, user, rows=None):
	global global_list
	global_list = []
	if not frappe.db.exists("Renovation Sidebar", parent):
		return []

	data= get_data(parent, user)
	if not rows:
		rows =[]
	return process_data(data, rows, parent)


def get_data(parent, user=None, child_name=None):
	lft, rgt = frappe.db.get_value("Renovation Sidebar", parent, ["lft", "rgt"])
	conditions = "lft >= {0} and rgt <= {1}".format(lft, rgt)
	if child_name:
		conditions += " and rs.name ='{}'".format(child_name)
	
	if user:
		role_profile = frappe.db.get_value('User', user, 'role_profile_name')
		roles = frappe.get_roles(user)
		or_coditions = " (p_type is null and p_name is null) or (p_type='User' and (p_name is null or p_name='{}'))".format(user)
		if role_profile:
			or_coditions += "or (p_type='Role Profile' and (p_name is null or p_name='{}'))".format(role_profile)
		if len(roles):
			or_coditions += "or (p_type='Role' and (p_name is null or p_name in ('{}')))".format("', '".join(roles))
		conditions += ' and ({})'.format(or_coditions)
	
	data = frappe.db.sql("""select renovation_sidebar_name as title, title_ar, subtitle, subtitle_ar, tooltip, is_group, type,
	if (STRCMP(type, "Link")=0, link, target) as target, rs.name, parent_renovation_sidebar as parent,
	concat(sidebar_group) as include_from from `tabRenovation Sidebar` rs
	left join `tabRenovation Sidebar Child` rsc on rs.name = rsc.parent
	where {} """.format(conditions), as_dict=True)
	return data

def process_data(data, rows, key=None):
	names = [x.name for x in data]
	for d in data:
		if d.parent == key:
			if d.is_group:
				d['children'] = []
				process_data(data, d['children'], d.name)
			if d.include_from:
				include_from = d.include_from.split(',')
				for p in include_from:
					doc = frappe.get_doc("Renovation Sidebar",p)
					if p not in names:
						data + get_data(doc.parent_renovation_sidebar,None, p)
					dchild = d.setdefault('children', [])
					obj = frappe._dict({
						"name": doc.name,
						"parent": doc.parent,
						"title": doc.renovation_sidebar_name,
						"is_group": doc.is_group,
						"tooltip": doc.tooltip,
						"include_from": ",".join([x.sidebar_group for x in doc.get('include_from',[])]),
						"type": doc.type,
						"target": doc.link if doc.type=="Link" else doc.target 
					})
					dchild.append(obj)
					data.append(obj)
					edchild = dchild[-1].setdefault('children', [])
					process_data(data, edchild, p)
			del d['include_from']
			del d['parent']
			del d['name']
			if d not in global_list:
				global_list.append(d)
				rows.append(d)
	return rows
