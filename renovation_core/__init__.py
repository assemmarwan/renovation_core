# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe.model.meta import Meta
import frappe.model.sync
from .utils.sync import _get_doc_files, process
import frappe.core.doctype.sms_settings.sms_settings
from .utils.sms_setting import validate_receiver_nos


__version__ = '0.6.4'


Meta.process = process
frappe.model.sync.get_doc_files = _get_doc_files
frappe.core.doctype.sms_settings.sms_settings.validate_receiver_nos = validate_receiver_nos


def clear_cache():
  from .utils.meta import clear_all_meta_cache
  clear_all_meta_cache()


def on_login(login_manager):
  import frappe.permissions
  from .utils.auth import make_jwt

  append_user_info_to_response(login_manager.user)
  if "recursive_delete" not in frappe.permissions.rights:
    frappe.permissions.rights += ("recursive_delete",)
  if frappe.local.is_ajax and frappe.get_request_header("Authorization"):
    frappe.local.response['token'] = make_jwt(login_manager.user)


def append_user_info_to_response(user):
  user_details = frappe.db.get_value("User", user, ["name", "full_name", "quick_login_pin"])
  frappe.local.response = frappe._dict({
    "user": user,
    "message": "Logged In",
    "home_page": "/desk",
    "full_name": user_details[1],
    "has_quick_login_pin": user_details[2] != None,
    "lang": frappe.translate.get_user_lang()
  })

  for method in frappe.get_hooks().get("renovation_login_response", []):
    frappe.call(frappe.get_attr(method), user=user)


@frappe.whitelist()
def get_logged_user():
  user = frappe.session.user
  append_user_info_to_response(user)
