from __future__ import unicode_literals

import frappe


def get_context(**kwargs):
	colors = {
		"Return": "darkgrey",
		"Credit Note Issued": "darkgrey",
		"Unpaid": "orange",
		"Overdue": "red",
		"Paid": "green"
	}
	data = frappe.db.sql("select count(*), status from `tabSales Invoice` where docstatus=1 group by status")
	return {"data":[{"label": x[1], "value": x[0], "color": colors.get(x[1], 'gray')} for x in data]}
