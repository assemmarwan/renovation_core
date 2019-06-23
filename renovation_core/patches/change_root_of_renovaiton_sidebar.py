import frappe


def execute():
	existing_data = frappe.get_all('Renovation Sidebar', [['Renovation Sidebar', 'parent_renovation_sidebar', 'in', ('All', 'Role', 'Role Profile', 'User')]])
	for d in existing_data:
		doc = frappe.get_doc('Renovation Sidebar', d.name)
		doc.parent_renovation_sidebar = 'All Renovation Sidebar'
		doc.save()

	for d in ('All', 'Role', 'Role Profile', 'User'):
		if frappe.db.exists('Renovation Sidebar', d):
			doc = frappe.get_doc('Renovation Sidebar', d)
			try:
				doc.delete()
			except Exception as e:
				print("Unable to Delete for '{}' please delete Renovation Sidebar '{}' Manually".format(e, d))
