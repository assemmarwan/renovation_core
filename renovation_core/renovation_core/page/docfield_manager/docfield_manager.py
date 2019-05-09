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
def get_docfield_and_selected_val(doctype, user=None):
	return {
		"doctypes_fields": get_doctypes_fields(doctype, user),
		"selected_values": get_selected_values(doctype, user)
	}


@frappe.whitelist()
def get_doctypes_fields(doctype, user=None):
	meta = frappe.get_meta(doctype)
	doctypes = [x.options for x in meta.fields if x.fieldtype=="Table"]
	doctypes.append(doctype)
	doc_map = {}
	enabled_field = []
	if user:
		enabled_field = ["{}:{}".format(x.p_doctype, x.fieldname) for x in frappe.get_all("Renovation DocField", 
		{"p_doctype": ("in", doctypes), "renovation_enabled": 1},['p_doctype' ,'fieldname'])]
	for f in meta.fields:
		n = "{}:{}".format(f.parent, f.fieldname) 
		if user and n not in enabled_field:
			continue
		doc = doc_map.setdefault(f.parent, [])
		doc.append(f)
	return doc_map


def get_user_disable_fields(user, doctype=None):
	filters = [["Renovation DocField User", "user", "=", user]]
	if doctype:
		filters.append(['Renovation DocField', 'p_doctype', '=', doctype])
	return [x.parent for x in frappe.get_all("Renovation DocField User", filters, 'parent') if x.parent]