from __future__ import unicode_literals

import frappe
from erpnext.accounts.report.financial_statements import get_period_list
from frappe import _


def get_context(**kwargs):
	# return sum of qty and amount of SO, SI, Delivery.
	view_as = kwargs.get('view_as', 'amount')
	fiscal_year = frappe.defaults.get_user_default('fiscal_year')
	if not (fiscal_year and frappe.db.exists("Fiscal Year", fiscal_year)):
		return
	period_list = get_period_list(fiscal_year, fiscal_year, "Monthly")
	values_dict = frappe._dict({
		'Sales Order': frappe._dict(),
		'Sales Invoice': frappe._dict(),
		'Delivery Note': frappe._dict()
	})
	for d in ['Sales Order', 'Sales Invoice', 'Delivery Note']:
		for item in get_data_from_sql(d, period_list[0].year_start_date, period_list[0].year_end_date):
			values_dict[d][item[2]] = item[1] if view_as =="qty" else item[0]
	group_labels = values_dict.keys()
	label = [x.label for x in period_list]
	ylabel = "Qty" if view_as =="qty" else "Amount"
	data = []
	for x, v in values_dict.items():
		row = {
			"label": label,
			"values": [],
		}
		for l in label:
			row['values'].append(v.get(l, 0))
		data.append(row)
	
	return {
		"xlabel": _("Month"),
		"ylabel": _(ylabel),
		"grouped": True,
		"group_labels": group_labels,
		"data": data
	}


def get_data_from_sql(doctype, from_date, to_date, posting_date_field=None):
	if not posting_date_field:
		if doctype == "Sales Order":
			posting_date_field='`tab{}`.transaction_date'.format(doctype)
		else:
			posting_date_field='`tab{}`.posting_date'.format(doctype)

	return frappe.db.sql("""select sum(grand_total), sum(qty), date_format({p_date_f}, "%b %Y") as month_year from `tab{doc}`
	left join `tab{doc} Item` on `tab{doc}`.name = `tab{doc} Item`.parent
	where `tab{doc}`.docstatus=1 and date({p_date_f}) >= date('{from_date}') and date({p_date_f}) <= date('{to_date}')
	 group by month_year""".format(doc=doctype, p_date_f=posting_date_field, from_date=from_date, to_date=to_date))
