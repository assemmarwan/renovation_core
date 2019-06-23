import frappe, json
from six import string_types
from frappe.desk.form.save import savedocs as org_savedocs


@frappe.whitelist()
def savedocs(doc, action):
	if not isinstance(doc, string_types):
		doc = json.dumps(doc)
	return org_savedocs(doc, action)