import frappe
import os

def execute():
	path = frappe.get_app_path('renovation_core', 'renovation_data', 'sidebar.json')
	if not os.path.exists(path):
		print('"{}" File not Fould'.format(path))
		return
	data = frappe.get_file_json(path)
	for k in sorted(data.keys()):
		for d in data[k]:
			doc = frappe.get_doc(d)
			if doc.name == doc.renovation_sidebar_name:
				doc.flags.ignore_mandatory = True
			try:
				doc.insert()
			except Exception as e:
				print(e)
		frappe.db.commit()
