import frappe
from .images import is_image_path

@frappe.whitelist()
def get_attachments(doctype, name, only_images=False, ignore_permissions=False):
  fields = ["name", "file_name", "file_url", "file_size", "content_hash", "folder", "thumbnail_url", "is_private"]
  filters = {"attached_to_doctype": doctype, "attached_to_name": name}
  att = frappe.get_all("File", filters=filters, fields=fields) if ignore_permissions else \
      frappe.get_list("File", filters=filters, fields=fields)
  
  ret = []
  for f in att:
    if (only_images and is_image_path(f.file_name)) or not only_images:
      ret.append(f)
  return ret