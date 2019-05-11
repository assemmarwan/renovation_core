import frappe


def execute():
	frappe.reload_doc('renovation_core', 'doctype', frappe.scrub('Renovation Sidebar'))
	if not frappe.db.exists("Renovation Sidebar", "All Renovation Sidebar"):
		doc = frappe.new_doc("Renovation Sidebar")
		doc.set("renovation_sidebar_name", "All Renovation Sidebar")
		doc.flags.ignore_mandatory = True
		doc.insert()
