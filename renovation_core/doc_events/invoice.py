import frappe
from renovation_core.doc_events.accounts.mode_of_payment_charges import sales_invoice_handler

def validate(doc, method):
	sales_invoice_handler(doc, method)
