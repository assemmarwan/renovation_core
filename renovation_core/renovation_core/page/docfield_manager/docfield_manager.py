import frappe
from frappe.utils import cint
from renovation_core.renovation_core.doctype.renovation_docfield.renovation_docfield import toggle_enabled as enable_field
import json
from six import string_types


@frappe.whitelist()
def get_selected_values(doctype):
	meta = frappe.get_meta(doctype)
	doctypes = [x.options for x in meta.fields if x.get('fieldtype')=="Table"]
	doctypes.append(doctype)
	values = {}
	for d in frappe.get_all("Renovation DocField", {"renovation_enabled":1, 'p_doctype': ('in', doctypes)}, ['p_doctype' ,'fieldname']):
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
