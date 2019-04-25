import frappe
from frappe.model.utils.user_settings import get_user_settings
from frappe.desk.form.load import get_meta_bundle

from renovation_core.utils import update_http_response, get_request_body

@frappe.whitelist(allow_guest=True)
def get_bundle(doctype):
	bundle_obj = frappe.cache().hget("renovation_doc_bundle", doctype)
	if not bundle_obj:
		bundle_obj = {
			"metas": [],
			"user_settings": get_user_settings(doctype)
		}
		
		# update renovation_enabled
		for meta in get_meta_bundle(doctype):
			enabled_fields = frappe.get_all("Renovation DocField", fields=["fieldname"], filters={"renovation_enabled": 1, "p_doctype": meta.name})
			meta = frappe._dict(meta.as_dict())
			# renovation-core takes 1 as true since all other db-Check types are 0/1
			meta.treeview = 1 if meta.name in frappe.get_hooks("treeviews") else 0
			
			fields = []
			_fields = []
			for field in meta.get("fields"):
				if len(filter(lambda x: x.fieldname == field.get("fieldname"), enabled_fields)) > 0:
					fields.append(field)
				else:
					_fields.append(field)
			meta["fields"] = fields
			meta["_fields"] = _fields
			bundle_obj["metas"].append(meta)
			
			# Renovation Scripts
			meta["renovation_scripts"] = frappe.get_all("Renovation Script", filters={"target_dt": meta.name}, fields=["name", "code"])
			
			# reference bundle so that it can be cleared when required
			# a doctype can be referenced in multiple bundles
			ref_bundles = frappe.cache().hget("renovation_doc_ref_bundle", meta.name)
			if not ref_bundles:
				ref_bundles = []
			if doctype not in ref_bundles:
				ref_bundles.append(doctype)
				frappe.cache().hset("renovation_doc_ref_bundle", meta.name, ref_bundles)

		frappe.cache().hset("renovation_doc_bundle", doctype, bundle_obj)
	return bundle_obj

def clear_meta_cache(doctype):
	frappe.cache().hdel("renovation_doc_bundle", doctype)
	ref_bundles = frappe.cache().hget("renovation_doc_ref_bundle", doctype)
	if not ref_bundles:
		return
	for dt in ref_bundles:
		frappe.cache().hdel("renovation_doc_bundle", dt)

def clear_all_meta_cache():
	for k in frappe.cache().hkeys("renovation_doc_bundle"):
		frappe.cache().hdel("renovation_doc_bundle", k)
	for k in frappe.cache().hkeys("dashboard"):
		frappe.cache().hdel("dashboard", k)
	
	frappe.cache().hdel("dashboard_list", frappe.session.user)