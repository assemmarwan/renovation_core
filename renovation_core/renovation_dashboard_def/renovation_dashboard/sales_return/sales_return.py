from __future__ import unicode_literals

import frappe
from frappe.utils import flt


def get_context(**kwargs):
	# do your magic here
	total_invoices = frappe.db.count("Sales Invoice", {"docstatus": 1})
	total_returns = frappe.db.count("Sales Invoice", {"docstatus": 1, "is_return":1})
	return {
		"value": flt(flt(total_returns)/flt(total_invoices))*100
	}
