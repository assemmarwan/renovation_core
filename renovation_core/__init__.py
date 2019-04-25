# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe.model.meta import Meta
import frappe.model.sync
from .utils.sync import _get_doc_files, process

__version__ = '11.1.11'


Meta.process = process
frappe.model.sync.get_doc_files = _get_doc_files


def clear_cache():
  from renovation_core.utils.meta import clear_all_meta_cache
  clear_all_meta_cache()


def on_login(login_manager):
  import frappe.permissions

  append_user_info_to_response(login_manager.user)
  if "recursive_delete" not in frappe.permissions.rights:
    frappe.permissions.rights += ("recursive_delete",)


def append_user_info_to_response(user):
  # send back user
  frappe.local.response["user"] = user
  frappe.local.response["has_quick_login_pin"] = frappe.db.get_value("User", "administrator", "quick_login_pin") != None

  for method in frappe.get_hooks().get("renovation_login_response", []):
    frappe.call(frappe.get_attr(method), user=user)

@frappe.whitelist()
def get_logged_user():
  user = frappe.session.user
  frappe.local.response["message"] = user # backward compatibility
  append_user_info_to_response(user)
