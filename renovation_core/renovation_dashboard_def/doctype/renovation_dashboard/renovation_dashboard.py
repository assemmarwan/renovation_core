# -*- coding: utf-8 -*-
# Copyright (c) 2019, Leam Technology Systems and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.modules.utils import export_module_json
import os
from frappe import scrub


class RenovationDashboard(Document):
	def autoname(self):
		if not self.name:
			self.name = self.title

	def on_update(self):
		path = export_module_json(self, self.is_standard, self.module)
		if path:
			# py
			if not os.path.exists(path + '.py'):
				with open(path + '.py', 'w') as f:
					f.write("""from __future__ import unicode_literals

import frappe


def get_context(**kwargs):
	# do your magic here
	pass
""")

	def get_chart_meta(self, **kwargs):
		m = {
			"title": self.title,
			"subtitle": self.subtitle or "",
			"type": self.type,
			"exc_type": self.exc_type,
		}
		if self.exc_type == "cmd":
			m['cmd'] = self.cmd
		elif self.exc_type == "eval":
			m['eval'] = self.eval
		return m
	
	def get_chart_data(self, **kwargs):
		return {
			"Meta": self.get_chart_meta(**kwargs),
			"Data": self.ready_chart_data(**kwargs)
		}

	def ready_chart_data(self, **kwargs):
		cmd = self.cmd
		if (self.exc_type == "cmd" and not cmd) or not self.eval:
			cmd = os.path.join("{}.{}.{}.{}.{}".format(frappe.get_module_path(scrub(self.module)), scrub(self.doctype),
			scrub(self.name), scrub(self.name), 'get_context'))
			cmd = '.'.join(cmd.split('/')[-2:])
		if self.exc_type == "eval" and not self.eval:
			return eval(self.eval)
		else:
			return self.call_cmd(cmd, **kwargs)

	def call_cmd(self,cmd, **kwargs):
		dicts = self.as_dict()
		dicts.update(kwargs)
		return frappe.call(cmd or self.cmd, **dicts)
