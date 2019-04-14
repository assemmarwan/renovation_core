import frappe
import json

def get_request_method():
	return frappe.local.request.method

def get_request_body(as_json=False):
	print(frappe.local.form_dict.data)
	return json.loads(frappe.local.form_dict.data or '{}') if as_json else frappe.local.form_dict.data
	
def get_request_path():
	"""
	/api/renovation/
	request_parts:
		0. api
		1. method
		2. renovation
		3. [doc		|	config	| session	| get_meta]
		4. [DocType	|	] ('Sales Invoice')
		5. [DocName	|	] ('SINV-0001')
	"""
	return frappe.request.path
	
def update_http_response(dict):
	frappe.local.response.update(dict)