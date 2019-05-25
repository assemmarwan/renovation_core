import frappe
from renovation_core.renovation_core.doctype.renovation_docfield.renovation_docfield import add_all_reqd_table_fields

def execute():
    frappe.reload_doc('renovation_core', 'doctype', 'renovation_docfield', force=True)
    frappe.reload_doc('renovation_core', 'doctype', 'renovation_docfield_user', force=True)
    frappe.reload_doc('renovation_core', 'doctype', 'renovation_docfield_role_profile', force=True)
    add_all_reqd_table_fields()
