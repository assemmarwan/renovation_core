# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "renovation_core"
app_title = "Renovation Core"
app_publisher = "LEAM Technology System"
app_description = "Core App for LEAM Technology System"
app_icon = "octicon octicon-plug"
app_color = "green"
app_email = "mainul.islam@leam.ae"
app_license = "MIT"

clear_cache = "renovation_core.clear_cache"
on_login = "renovation_core.on_login"
on_session_creation = "renovation_core.on_session_creation"

# Includes in <head>
# ------------------

fixtures = [
	{
		"dt": "Custom Field",
		"filters": [["app_name", "=", "renovation_core"]]
	},
	{
		"dt": "Property Setter",
		"filters": [["app_name", "=", "renovation_core"]]
	}
]

treeviews = ["Renovation Sidebar"]

# include js, css files in header of desk.html
# app_include_css = "/assets/renovation_core/css/renovation_core.css"
# app_include_js = "/assets/renovation_core/js/renovation_core.js"

# include js, css files in header of web template
# web_include_css = "/assets/renovation_core/css/renovation_core.css"
# web_include_js = "/assets/renovation_core/js/renovation_core.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "renovation_core.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "renovation_core.install.before_install"
after_install = "renovation_core.install.after_install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "renovation_core.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"user": {
		"before_save": "renovation_core.doc_eventd.user.before_save"
	},
	"*": {
		"on_update":"renovation_core.renovation_dashboard_def.utils.clear_cache_on_doc_events",
		"on_cancel":"renovation_core.renovation_dashboard_def.utils.clear_cache_on_doc_events",
		"on_trash":"renovation_core.renovation_dashboard_def.utils.clear_cache_on_doc_events",
		"on_update_after_submit":"renovation_core.renovation_dashboard_def.utils.clear_cache_on_doc_events"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"renovation_core.tasks.all"
# 	],
# 	"daily": [
# 		"renovation_core.tasks.daily"
# 	],
# 	"hourly": [
# 		"renovation_core.tasks.hourly"
# 	],
# 	"weekly": [
# 		"renovation_core.tasks.weekly"
# 	]
# 	"monthly": [
# 		"renovation_core.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "renovation_core.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
override_whitelisted_methods = {
	"frappe.auth.get_logged_user": "renovation_core.get_logged_user",
	"renovation": "renovation_core.handler.handler",
	"frappe.desk.form.save.savedocs": "renovation_core.utils.save.savedocs",
	"frappe.integrations.oauth2.openid_profile": "renovation_core.utils.oauth2.openid_profile_endpint"
}

