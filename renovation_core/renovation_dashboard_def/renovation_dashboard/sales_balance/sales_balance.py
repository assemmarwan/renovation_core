from __future__ import unicode_literals

import frappe
from frappe.utils import add_months, get_first_day, get_last_day, today, flt


def get_context(**kwargs):
	from_date, to_date = add_months(get_first_day(today()), -1), get_last_day(today())
	data = frappe.db.sql("""select sum(grand_total), DATE_FORMAT(posting_date, "%Y-%M")as c_month from `tabSales Invoice`
	 where date(posting_date) >= date('{}') and date(posting_date) <= date('{}') and docstatus=1 group by c_month order by c_month asc""".format(from_date, to_date))
	rows = {
		"before": {
			"label": from_date.strftime('%b'),
			"value": 0
		},
		"now": {
			"label": to_date.strftime("%b"),
			"value": 0
		},
		"change": 0,
		"positive": True
	}
	if len(data):
		before_data = data[0] if data[0][1] == from_date.strftime('%Y-%B') else None
		if len(data) >= 2:
			now_data = data[1]
		elif data[0][1] == to_date.strftime('%Y-%B'):
			now_data = data[0]
		else:
			now_data = None
		if before_data:
			rows['before']['value'] = before_data[0]
		if now_data:
			rows['now']['value'] = now_data[0]
		if before_data and now_data:
			rows['change'] = flt((flt(now_data[0]) - flt(before_data[0])) / (flt(before_data[0]) + flt(now_data[0])))*100
		elif before_data:
			rows['change'] = -100
		else:
			rows['change'] = 100
		rows['positive'] = rows['change'] > 0
	return rows

