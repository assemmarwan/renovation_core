import frappe
import random
from frappe.auth import LoginManager
from frappe.core.doctype.sms_settings.sms_settings import send_sms
from renovation_core.utils import get_request_body, update_http_response
from frappe.utils import cint

def generate_sms_pin():
	mobile = frappe.local.form_dict.mobile
	newPIN = cint(frappe.local.form_dict.newPIN or "0")
	
	if not mobile:
		frappe.throw("No Mobile Number")
	
	# check cache for pin
	pin = frappe.cache().get("sms:" + mobile)
	if not pin or newPIN:
		# generate a pin
		pin = str(get_pin())
		frappe.cache().set("sms:" + mobile, pin)
		# save in User doc if mobile linked to any User
		user = get_linked_user(mobile)
		if user:
			frappe.db.set_value("User", user, "renovation_sms_pin", pin)
	
	msg = "Your verification PIN is: " + pin
	send_sms([mobile], msg, success_msg = False)
	update_http_response({"status": "success", "mobile": mobile})

def verify_sms_pin():
	mobile = frappe.local.form_dict.mobile
	pin = frappe.local.form_dict.pin
	login = cint(frappe.local.form_dict.loginToUser or "0")
	
	if not mobile:
		frappe.throw("No Mobile Number")
	
	verify_pin = frappe.cache().get("sms:" + mobile)
	user = get_linked_user(mobile)
	if user:
		# try to get from User
		pin_from_db = frappe.db.get_value("User", user, "renovation_sms_pin")

		if (not pin_from_db or len(pin_from_db) < 2) and verify_pin:
			frappe.db.set_value("User", user, "renovation_sms_pin", verify_pin)
		elif pin_from_db != verify_pin:
			# preference for db pin
			frappe.cache().set("sms:" + mobile, pin)
			verify_pin = pin_from_db
		
	out = "no_pin_for_mobile"
	if login:
		out = "no_linked_user"
	if verify_pin:
		out = "invalid_pin"
	if verify_pin and pin == verify_pin:
		out = "verified"
		
		if login == 1:
			if user:
				l = LoginManager()
				l.login_as(user)
			else:
				out = "user_not_found"
		
	
	update_http_response({"status": out, "mobile": mobile})

def get_linked_user(mobile_no):
	return frappe.db.get_value("User", filters={"mobile_no": mobile_no})

def get_pin(length = 6):
	return random.sample(range(int('1' + '0' * (length - 1)), int('9' * length)), 1)[0]


@frappe.whitelist(allow_guest=True)
def pin_login(user, pin, device=None):
	from frappe.sessions import clear_sessions
	login = LoginManager()
	login.check_if_enabled(user)
	p = frappe.db.get_value("User", user, "quick_login_pin")
	if pin != p:
		login.fail('Incorrect password', user=user)
		
	login.login_as(user)
	if device:
		clear_sessions(user, True, device)
	return frappe.session.user
