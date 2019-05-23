import frappe
from frappe.app import get_site_name, _site, _sites_path, NotFound, make_form_dict

def init_request(request):
	frappe.local.request = request
	frappe.local.is_ajax = frappe.get_request_header("X-Requested-With")=="XMLHttpRequest"

	site = _site or request.headers.get('X-Frappe-Site-Name') or get_site_name(request.host)
	frappe.init(site=site, sites_path=_sites_path)

	if not (frappe.local.conf and frappe.local.conf.db_name):
		# site does not exist
		raise NotFound

	if frappe.local.conf.get('maintenance_mode'):
		raise frappe.SessionStopped
	if frappe.local.is_ajax and frappe.request.path == '/':
		frappe.conf['ignore_csrf'] = True
	else:
		frappe.conf['ignore_csrf'] = False
		
	make_form_dict(request)
	frappe.local.http_request = frappe.auth.HTTPRequest()