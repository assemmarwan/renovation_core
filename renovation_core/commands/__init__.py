import frappe.app
import renovation_core.app
frappe.app.init_request.__code__ = renovation_core.app.init_request.__code__
