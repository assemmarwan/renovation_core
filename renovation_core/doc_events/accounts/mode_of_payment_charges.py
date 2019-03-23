import frappe
import erpnext.accounts.doctype.sales_invoice.sales_invoice
from erpnext.accounts.party import get_party_account

# Mode of Payment Charges
# eg: Credit Card charges of 2.5%
# Cases:
# -	Credit Card Charges (2.25%) to be paid to payment processor (EXPENSE)
#	- Pass to Customer and Deducted Auto
#	  Sales Taxes and Charges in .taxes will be added. (charge_acoount -> MOP)
#		Customer -> MOP Acc
#		MOP Acc -> charge_account
#		charge_account net balance = 0 <--- important
#
#	- Not passed to Customer and Deducted Auto
#     Pass a GL from Mop account to expense account
#		charge_account will have debit balance
# 	- Pass to Customer and Not deducted auto
#	  Money is with us (.taxes -> MOP), so we make Payable -> Expense Account entry
#	- Not Passed to Customer and not deducted auto
#
#	(INCOME) Cash on Delivery Extra Charges as Income
#	- mop.is_income
#

# Override info
# We are overriding the already defined get_gl_entries function defined in SalesInvoice
# to inject our own GL Ledger Entries
#
# How do we make sure that this function is replaced ?
# get_gl_entries() is called on on_submit() of Sales Invoice
# Before on_submit() runs, validate() is ran which invokes
# the function defined in this module, apply_mode_of_payment_charges
# So for a submit http request, this module will be ran before the actual
# on_submit() is ran

sinv_get_gl_entries = erpnext.accounts.doctype.sales_invoice.sales_invoice.SalesInvoice.get_gl_entries
def _get_gl_entries(self, *args, **kwargs):
	gl_entries = sinv_get_gl_entries(self, *args, **kwargs)
	
	default_cost_center = frappe.db.get_value("Company", self.company, "cost_center")
	for p in self.payments:
		if not p.get("has_additional_charges", 0) or p.get("income_charge"):
			continue
		
		if not p.get("deducted_automatically", 0):
			# Payable -> Expense Account
			if not p.get("charge_party_type") or not p.get("charge_party"):
				frappe.throw("Please defined Party Type and Party in Mode of Payment {}".format(p.mode_of_payment))

			payable_acc = get_party_account(p.charge_party_type, p.charge_party, self.company)
			if not payable_acc:
				frappe.throw("Cant find payable account for {}".format(p.charge_party))
			
			# no neeed to modify existing gl_entries, just append to it
			gl_entries.append(
				self.get_gl_dict({
					"account": payable_acc,
					"credit": p.charge_amount,
					"party_type": p.charge_party_type,
					"party": p.charge_party,
					"against": p.charge_amount,
					"remarks": "Mode of Payment {} Charges".format(p.mode_of_payment)
				})
			)

			gl_entries.append(
				self.get_gl_dict({
					"account": p.charge_account,
					"debit": p.charge_amount,
					"against": p.charge_party,
					"remarks": "Mode of Payment {} Charges".format(p.mode_of_payment),
					"cost_center": p.get("charge_cost_center") or default_cost_center
				})
			)
		else:
			# Deduct AUTO
			# from the gl_entries, find those two entries that
			# Debits to this MOP
			# Credited from this MOP
			# And make the required change there itself
			for gl in gl_entries:
				if gl.account == p.account:
					# subtract debited amount
					gl.debit -= p.charge_amount
				elif gl.against == p.account:
					# subtract credit
					gl.credit -= p.charge_amount
					
					gl_entries.append(
						self.get_gl_dict({
							"account": gl.account,
							"credit": p.charge_amount,
							"party_type": "Customer",
							"party": self.customer,
							"against": p.charge_account,
							"remarks": "Mode of Payment {} Charges".format(p.mode_of_payment)
						})
					)
					
					gl_entries.append(
						self.get_gl_dict({
							"account": p.charge_account,
							"debit": p.charge_amount,
							"against": gl.account,
							"remarks": "Mode of Payment {} Charges".format(p.mode_of_payment),
							"cost_center": p.get("charge_cost_center") or default_cost_center
						})
					)

	return gl_entries

# override get_gl_entries default method
erpnext.accounts.doctype.sales_invoice.sales_invoice.SalesInvoice.get_gl_entries = _get_gl_entries


# DOC EVENTS
# Sales Invoice
# Sales Order

# Sales Invoice on validate
def sales_invoice_handler(doc, action="validate"):
	if not doc.get("payments") or len(doc.payments) == 0:
		return

	remove_existing_charges(doc, action)
	default_cost_center = get_cost_center(doc.company)

	for p in doc.payments:
		mop_details = get_mop_details(p.mode_of_payment, default_cost_center)

		if not mop_details or not mop_details.get("has_additional_charges"):
			continue
		
		validate_mop_details(mop_details)
		charge_amount = get_mop_charge_amount(mop_details, p.amount)
		# copy values to Sales Invoice Payment
		p.update(mop_details)
		p.charge_amount = charge_amount

		add_mop_taxes_and_charges(p.mode_of_payment, mop_details, doc, charge_amount, p.idx)
	
	doc.calculate_taxes_and_totals()

# Sales Order On valdiate
def sales_order_handler(doc, action="validate"):
	if not doc.get("mode_of_payment"): return

	remove_existing_charges(doc, action)
	default_cost_center = get_cost_center(doc.company)

	mop_details = get_mop_details(doc.mode_of_payment, default_cost_center)

	if not mop_details or not mop_details.get("has_additional_charges"):
		return

	validate_mop_details(mop_details)
	charge_amount = get_mop_charge_amount(mop_details, doc.grand_total)

	add_mop_taxes_and_charges(doc.mode_of_payment, mop_details, doc, charge_amount, 0)

	doc.calculate_taxes_and_totals()

def validate_mop_details(mop_details):
	if not mop_details.charge_account:
		frappe.throw("Please define the payable account related to the Mode of Payment {} first".format(p.mode_of_payment))
	
	if mop_details.charge_type not in ["Percent", "Fixed"]:
		frappe.throw("Unsupported Charge Type in {}".format(p.mode_of_payment))

def add_mop_taxes_and_charges(mop, mop_details, doc, charge_amount, rowIdx):
	if not mop_details.pass_to_customer and not mop_details.income_charge:
		return
	
	charge = frappe.get_doc({
		"doctype": "Sales Taxes and Charges",
		"parenttype": doc.doctype,
		"parentfield": "taxes",
		"parent": doc.name,
		"ref_data": get_ref_data(mop, rowIdx),
		"charge_type": "Actual",
		"cost_center": mop_details.get("charge_cost_center"),
		"tax_amount": charge_amount,
		"account_head": mop_details.charge_account,
		"description": u"Payment Charges for {}".format(mop)
	})
	doc.taxes.append(charge)

def get_mop_charge_amount(mop_details, payment_amount):
		if mop_details.charge_type == "Percent":
			return (payment_amount or 0) * (mop_details.charge_percent or 0 ) / 100
		else:
			return mop_details.charge_amount
	
def remove_existing_charges(doc, action):
	doc.taxes = doc.get("taxes") or []
	if action == "validate":
		doc.taxes = [x for x in doc.taxes if "mop-charge-" not in (x.ref_data or "")]

def get_ref_data(mop, idx):
	return u"mop-charge-{}-{}".format(mop, idx)

def get_cost_center(company):
	return frappe.db.get_value("Company", company, "cost_center")
	

def get_mop_details(mop, default_cost_center):
	mop_details = frappe.db.get_value("Mode of Payment", mop, fieldname=[
		"has_additional_charges", "charge_cost_center", "charge_account", "income_charge",
		"charge_type", "charge_percent", "charge_amount", "pass_to_customer", "deducted_automatically",
		"charge_party_type", "charge_party"
	], as_dict=1)

	if not mop_details.get("charge_cost_center"):
		mop_details.charge_cost_center = default_cost_center

	return mop_details