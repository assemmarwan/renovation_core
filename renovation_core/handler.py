import re

import frappe
# erpnext will be updated to py3, if done the otherway, this will break
from renovation_core.utils.doc import doc_handler
from renovation_core.utils.meta import get_meta
from renovation_core.utils.report import get_report
from renovation_core.utils.auth import generate_sms_pin, verify_sms_pin
from renovation_core.utils import get_request_method, get_request_path, update_http_response
# api generals are handled here
# this file will be the interface to the frappe system
# if frappe system was to make changes in the future, we will have to update it here only

@frappe.whitelist(allow_guest=True)
def handler():

	request_parts = get_request_path()[1:].split("/")
	request_method = get_request_method()
	if request_parts[3] == "doc":
		doc_handler(request_method, request_parts[4], '/'.join(request_parts[5:]))
	elif request_parts[3] == "get_meta":
		get_meta(request_parts[4])
	elif request_parts[3] == "session":
		get_session()
	elif request_parts[3] == "report":
		get_report()
	elif request_parts[3] == "auth.sms.generate":
		generate_sms_pin()
	elif request_parts[3] == "auth.sms.verify":
		verify_sms_pin()
	elif request_parts[3] == "test":
		print(request_parts[3])
		print("FORM DICT :")
		print(frappe.form_dict)
	else:
		return "Not Implemented"

def get_session():
	try:
		boot = frappe.sessions.get()
		boot_json = frappe.as_json(boot)
		# remove script tags from boot
		boot_json = re.sub(r"\<script\>[^<]*\</script\>", "", boot_json)
		update_http_response({"data": boot_json, "status": "success"})
	except Exception:
		update_http_response({"status": "failed"})
		print(frappe.get_traceback())