import frappe
from frappe.utils import cint
from renovation_core.renovation_core.doctype.renovation_docfield.renovation_docfield import toggle_enabled as enable_field

@frappe.whitelist()
def get_doctype_fields(doctype):
	fields_enabled_dict = frappe._dict()
	fields = frappe.get_all("Renovation DocField", fields=["fieldname", "renovation_enabled"], filters={"p_doctype": doctype})
	for field in fields:
		fields_enabled_dict[field.fieldname] = field.renovation_enabled
	
	# going by meta because that way it comes in order it is viewed
	doctype_meta = frappe.get_meta(doctype)
	return {
		"enabled_dict": fields_enabled_dict,
		"meta_fields": doctype_meta.fields
	}

@frappe.whitelist()
def toggle_enabled(doctype, fieldname, enabled=0):
	enable_field(doctype, fieldname, cint(enabled or "0"))