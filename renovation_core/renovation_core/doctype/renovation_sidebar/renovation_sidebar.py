# -*- coding: utf-8 -*-
# Copyright (c) 2019, LEAM Technology System and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.nestedset import NestedSet
from frappe.model.naming import make_autoname


class RenovationSidebar(NestedSet):
	nsm_parent_field = "parent_renovation_sidebar"

	def autoname(self):
		self.name = self.renovation_sidebar_name if self.flags.ignore_mandatory else make_autoname('hash')
	
	def on_update(self):
		keys = [self.get(self.nsm_parent_field), 'All Renovation Sidebar']
		if self.is_group:
			keys.append(self.name)
		for key in keys:
			frappe.cache().hdel('renovation_sidbar', key)
