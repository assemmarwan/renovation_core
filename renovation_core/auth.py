import frappe
import jwt
from frappe.auth import HTTPRequest, LoginManager, get_lang_code, check_session_stopped, CookieManager
from frappe import _


# frappe's CookieManager is having old class style
class CookieManagerJWT(CookieManager, object):
	def flush_cookies(self, response):
		if frappe.flags.jwt_clear_cookies:
			# Case when right after login
			# We set the flag on session_create
			self.cookies = frappe._dict()
		if frappe.flags.jwt:
			# Case when the incoming request has jwt token
			# We leave cookies untouched
			# There can be other browser tabs
			return
		return super(CookieManagerJWT, self).flush_cookies(response)


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
	
		# set db before jwt check, so token error handling can be stored
		# We get Internal Server Error otherwise
		self.connect()

		# JWT
		# Check for Auth Header, if present, replace the request cookie value
		if frappe.local.is_ajax and frappe.get_request_header("Authorization"):
			token_header = frappe.get_request_header(
				"Authorization").split(" ")
			token = token_header[-1]
			frappe.flags.jwt = token
			token_info = jwt.decode(token, frappe.utils.password.get_encryption_key())

			# Not checking by IP since it could change on network change (Wifi -> Mobile Network)
			# if token_info.get('ip') != frappe.local.request_ip:
			# 	frappe.throw(frappe._("Invalide IP", frappe.AuthenticationError))

			# werkzueg cookies structure is immutable
			frappe.request.cookies = frappe._dict(frappe.request.cookies)
			frappe.request.cookies['sid'] = token_info.get('sid')


		# load cookies
		frappe.local.cookie_manager = CookieManagerJWT()

		# login
		frappe.local.login_manager = LoginManager()

		if frappe.form_dict._lang:
			lang = get_lang_code(frappe.form_dict._lang)
			if lang:
				frappe.local.lang = lang

		self.validate_csrf_token()

		# write out latest cookies
		frappe.local.cookie_manager.init_cookies()

		# check status
		check_session_stopped()


		# write out latest cookies
		frappe.local.cookie_manager.init_cookies()

		# check status
		check_session_stopped()
