# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe.model.meta import Meta
import frappe.model.sync
from .utils.sync import _get_doc_files, process

__version__ = '11.1.11'


Meta.process = process
frappe.model.sync.get_doc_files = _get_doc_files 