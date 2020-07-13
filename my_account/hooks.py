# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "my_account"
app_title = "My Account"
app_publisher = "GMS"
app_description = "Account Setting"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "ptglobalmediasolusindo@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/my_account/css/my_account.css"
# app_include_js = "/assets/my_account/js/my_account.js"

# include js, css files in header of web template
# web_include_css = "/assets/my_account/css/my_account.css"
# web_include_js = "/assets/my_account/js/my_account.js"

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
# get_website_user_home_page = "my_account.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "my_account.install.before_install"
# after_install = "my_account.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "my_account.notifications.get_notification_config"

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
#
doc_events = {
#	"User": {
#		"on_update": "my_account.my_account.doctype.custom_method.validate_user_quota"
		# "on_submit": "my_account.custom_dns_api.take_new_site"
		# "on_submit" : my_account.doctype.sync_server_settings.create_new_user
#	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	# "all": [
	# 	"my_account.tasks.all"
	# ],
	"daily": [
		"my_account.my_account.doctype.custom_method.reduce_days_active_user",  
		# "my_account.my_account.doctype.sync_server_settings.enqueue_sync"
	],
	# "hourly": [
		# "my_account.my_account.doctype.custom_method.reduce_days_active_user"
	# ],
	# "weekly": [
	# 	"my_account.tasks.weekly"
	# ]
	# "monthly": [
		# "my_account.my_account.doctype.api_data.auto_invoice_monthly"
	# 	"my_account.tasks.monthly"
	# ],
	# "yearly": [
		# "my_account.my_account.doctype.api_data.auto_invoice_yearly"

	# ],
	# tiap tanggal 25 setiap bulan
	"0 0 20 * *":[
		"my_account.my_account.doctype.api_data.auto_invoice_monthly"
	],
	# tiap tanggal 25 bulan Desember
	"0 0 25 12 *":[
		"my_account.my_account.doctype.api_data.auto_invoice_yearly"
	],
	"0 0 1 * *":[
		"my_account.my_account.doctype.api_data.set_site_disabled"
	],
	"0 0 2 * *":[
		"my_account.my_account.doctype.api_data.remove_extend_trial"
	]
}

# Testing
# -------

# before_tests = "my_account.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "my_account.event.get_events"
# }
