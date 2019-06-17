import frappe
import jwt
from frappe.auth import HTTPRequest, LoginManager, get_lang_code, check_session_stopped, CookieManager
from frappe import _


class CookingManagerExtendand(CookieManager):
	def flush_cookies(self, response):
		pass


class HTTPRequestExtend(HTTPRequest):
	def __init__(self):
		# Get Environment variables
		self.domain = frappe.request.host
		if self.domain and self.domain.startswith('www.'):
			self.domain = self.domain[4:]

		if frappe.get_request_header('X-Forwarded-For'):
			frappe.local.request_ip = (frappe.get_request_header(
				'X-Forwarded-For').split(",")[0]).strip()

		elif frappe.get_request_header('REMOTE_ADDR'):
			frappe.local.request_ip = frappe.get_request_header('REMOTE_ADDR')

		else:
			frappe.local.request_ip = '127.0.0.1'

		# language
		self.set_lang()

		# load cookies
		frappe.local.cookie_manager = CookieManager()

		# set db
		self.connect()

		# login
		if frappe.local.is_ajax and frappe.get_request_header("Authorization"):
			token_header = frappe.get_request_header(
				"Authorization").split(" ")
			token = token_header[-1]
			token_info = jwt.decode(token, frappe.utils.password.get_encryption_key())
			if token_info.get('ip') != frappe.local.request_ip:
				frappe.throw(frappe._("Invalide IP", frappe.AuthenticationError))
			frappe.form_dict['sid'] = token_info.get('sid')
			frappe.local.cookie_manager = CookingManagerExtendand()
		frappe.local.login_manager = LoginManager()
		if not (frappe.local.is_ajax and frappe.get_request_header("Authorization")):
			self.validate_csrf_token()

		if frappe.form_dict._lang:
			lang = get_lang_code(frappe.form_dict._lang)
			if lang:
				frappe.local.lang = lang


		# write out latest cookies
		frappe.local.cookie_manager.init_cookies()

		# check status
		check_session_stopped()
