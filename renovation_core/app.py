from __future__ import unicode_literals

import frappe
from frappe.app import make_form_dict, get_site_name, NotFound, _site, _sites_path


def init_request(request):
	import renovation_core.auth
	frappe.local.request = request
	frappe.local.is_ajax = frappe.get_request_header("X-Requested-With")=="XMLHttpRequest"

	site = _site or request.headers.get('X-Frappe-Site-Name') or get_site_name(request.host)
	frappe.init(site=site, sites_path=_sites_path)

	if not (frappe.local.conf and frappe.local.conf.db_name):
		# site does not exist
		raise NotFound

	if frappe.local.conf.get('maintenance_mode'):
		raise frappe.SessionStopped

	make_form_dict(request)

	frappe.local.http_request = renovation_core.auth.HTTPRequestExtend()
