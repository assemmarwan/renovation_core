from __future__ import unicode_literals

import frappe


def get_context(**kwargs):
	data = frappe.db.sql("select count(*), source from `tabLead` group by source")
	return {"data":[{"label": x[1], "value": x[0]} for x in data]}
