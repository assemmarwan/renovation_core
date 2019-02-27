# -*- coding: utf-8 -*-
# Copyright (c) 2018, Leam Technology Systems and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class RenovationImageSettings(Document):
	
	def regenerate_all_thumbs(self):
		from renovation_core.utils.images import regenerate_all_thumbnails
		frappe.enqueue(method=regenerate_all_thumbnails, queue="long", job_name="regenerate_thumbnails")
		
		frappe.msgprint("The thumbnails will be regenerated in the background. Please continue")
