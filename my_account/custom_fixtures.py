from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import os
import requests
import json
import subprocess
from frappe.utils.background_jobs import enqueue
import re
from frappe import utils
from frappe.core.doctype.data_import.data_import import import_doc, export_json
import json
from frappe.utils.password import get_decrypted_password


def export():
	# export_json("Custom Field", frappe.get_app_path("my_account", "fixtures", frappe.scrub("Custom Field") + ".json"), filters=None, or_filters=None)
	export_json("Property Setter", frappe.get_app_path("my_account", "fixtures", frappe.scrub("Property Setter") + ".json"), filters=None, or_filters=None)
	export_json("Custom DocPerm", frappe.get_app_path("my_account", "fixtures", frappe.scrub("Custom DocPerm") + ".json"), filters={
		"role": ["in",("Micro","Silver","Gold","Accounting","Faktur Pajak")]}, or_filters=None)
	export_json("Role", frappe.get_app_path("my_account", "fixtures", frappe.scrub("Role") + ".json"), filters={
		"name": ["in",("Micro","Silver","Gold","Accounting","Faktur Pajak")]}, or_filters=None)

def import_fixtures():
	# import_doc(frappe.get_app_path("my_account", "fixtures", "custom_field.json"), ignore_links=False, overwrite=True)
	import_doc(frappe.get_app_path("my_account", "fixtures", "property_setter.json"), ignore_links=False, overwrite=True)
	import_doc(frappe.get_app_path("my_account", "fixtures", "custom_docperm.json"), ignore_links=False, overwrite=True)
	import_doc(frappe.get_app_path("my_account", "fixtures", "role.json"), ignore_links=False, overwrite=True)
	import_doc(frappe.get_app_path("my_account", "fixtures", "setup_wizard_system_manager.json"), ignore_links=False, overwrite=True)