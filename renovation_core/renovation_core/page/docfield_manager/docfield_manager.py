import frappe
from frappe.utils import cint
from renovation_core.renovation_core.doctype.renovation_docfield.renovation_docfield import toggle_enabled as enable_field
import json
from six import string_types


@frappe.whitelist()
def get_selected_values(doctype, user=None):
	meta = frappe.get_meta(doctype)
	doctypes = [x.options for x in meta.fields if x.get('fieldtype')=="Table"]
	doctypes.append(doctype)
	disabled_fields = get_user_disable_fields(user)
	values = {}
	for d in frappe.get_all("Renovation DocField", {"renovation_enabled":1, 'p_doctype': ('in', doctypes)}, ['p_doctype' ,'fieldname', 'name']):
		if d.name in disabled_fields:
			continue
		row = values.setdefault(d.p_doctype, [])
		row.append(d.fieldname)
	return values


@frappe.whitelist()
def update_values(values):
	if isinstance(values, string_types):
		values = json.loads(values)
	toggler = {
		"selected_values": 1,
		"unselected_values":0
	}
	for key, val in toggler.items():
		for doctype, fields in values.get(key, {}).items():
			for fieldname in fields or []:
				enable_field(doctype, fieldname, val)
	return


@frappe.whitelist()
def get_docfield_and_selected_val(doctype, user=None, role_profile=None):
	return {
		"doctypes_fields": get_doctypes_fields(doctype),
		"selected_values": get_all_enable_fields(doctype, user, role_profile)
	}


def get_all_enable_fields(doctype, user=None, role_profile=None):
	meta = frappe.get_meta(doctype)
	cdoctypes = [x.options for x in meta.fields if x.fieldtype=="Table"]
	cdoctypes.append(doctype)
	global_val = frappe.get_all("Renovation DocField", {"p_doctype": ('in', cdoctypes), "renovation_enabled": 1}, ['p_doctype', 'fieldname', 'name'])
	g_val = get_map_data(global_val)

	user_data = {}
	if user:
		user_data = get_map_data(frappe.db.sql("""select p.p_doctype, p.fieldname from `tabRenovation DocField User` ct
		 left join `tabRenovation DocField` p on ct.parent = p.name
		 where ct.user='{}' and p.p_doctype in ('{}')""".format(user, "', '".join(cdoctypes)), as_dict=True))
	
	role_profile_data = {}
	if role_profile:
		role_profile_data = get_map_data(frappe.db.sql("""select p.p_doctype, p.fieldname from `tabRenovation DocField Role Profile` ct
		 left join `tabRenovation DocField` p on ct.parent = p.name
		 where ct.role_profile='{}' and p.p_doctype in ('{}')""".format(role_profile, "', '".join(cdoctypes)), as_dict=True))
	return {
		"Global": g_val,
		"User": user_data,
		"Role Profile": role_profile_data
	}


def get_map_data(data):
	map_data = {}
	for x in data:
		d = map_data.setdefault(x.p_doctype, [])
		d.append(x.fieldname)
	return map_data


@frappe.whitelist()
def get_doctypes_fields(doctype):
	meta = frappe.get_meta(doctype)
	cdoctypes = [x.options for x in meta.fields if x.fieldtype=="Table"]
	doc_map = {doctype: meta.fields}
	for d in cdoctypes:
		doc_map[d] = frappe.get_meta(d).fields
	return doc_map


def get_user_disable_fields(user, doctype=None):
	filters = [["Renovation DocField User", "user", "=", user]]
	if doctype:
		filters.append(['Renovation DocField', 'p_doctype', '=', doctype])
	return [x.parent for x in frappe.get_all("Renovation DocField User", filters, 'parent') if x.parent]