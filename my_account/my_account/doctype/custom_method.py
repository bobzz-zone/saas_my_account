# -*- coding: utf-8 -*-
# Copyright (c) 2015, Myme and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import os
import requests
import json
import subprocess
from frappe.utils.background_jobs import enqueue
import re
from frappe.utils import cint, flt


class custom_method(Document):
	pass

@frappe.whitelist()
def get_enabled_users():
	return frappe.db.sql("""select CAST(COUNT(*) AS CHAR) from `tabUser`
		where enabled = 1 and name not in ("Administrator","Guest","info@solubis.id") """)[0][0]

@frappe.whitelist()
def validate_user_quota(doc,method):
	if doc.name in ["Administrator","Guest"]:
		return
	desktop = frappe.db.sql("SELECT defvalue FROM `tabDefaultValue` WHERE defkey = 'desktop:home_page'")[0][0]
	is_created = 1
	try:
		subdomain = frappe.local.site.strip(".")[0]
	except:
		frappe.throw("Domain not found")
	if subdomain == "reg":
		is_created = frappe.db.get_value("Master Subdomain",subdomain,"is_created")
	# print(desktop)
	# print("is_created = {}".format(is_created))
	# print("site = {}".format(subdomain))
	quota = 0
	if desktop != "setup-wizard" and is_created == 1:
		
		quota = subprocess.check_output("""bench --site reg.solubis.id execute my_account.my_account.doctype.api_data.get_current_quota --args "['{}']" """.format(str(subdomain)),shell=True,universal_newlines=True)
		# print("quota = {}".format(float(quota)))
		enabled_users = get_enabled_users()

		# print("enabled = {}".format(enabled_users))
		# print("quota = {}".format(quota))
		if flt(quota) < flt(enabled_users)+1:
			# if user created delete user
			usr_enabled = frappe.get_doc("User",username)
			if usr_enabled.enabled == 1:
				frappe.db.sql("UPDATE `tabUser` set enabled = 0 where name = '{}'".format(username))
				frappe.db.commit()
			frappe.throw("Max enabled users reached")
	# custom saas andy for solubis check for update password
	if doc.new_password:
		# check if my account installed
		my_acc = frappe.db.sql('SELECT * FROM `tabDefaultValue` WHERE defkey = "installed_apps" AND defvalue LIKE CONCAT("%","my_account","%");')
		usrexist = frappe.db.sql('SELECT * FROM `tabUser` WHERE name = "{}" and name not in ("Administrator","Guest")'.format(doc.name),as_dict=1)
		if len(my_acc) > 0 and len(usrexist) > 0:
			pu = frappe.get_doc("Purchase User", user)
			pu.current_password = pwd
			pu.save(ignore_permissions=True)

@frappe.whitelist(allow_guest=True)
def reduce_days_active_user():
	
	cari_user = frappe.db.sql(""" SELECT pu.`name` FROM `tabPurchase User` pu WHERE pu.`enabled` = 1 """, as_list=1)

	if cari_user :
		for i in cari_user :
			purchase_user = frappe.get_doc("Purchase User", i[0])
			current_days = purchase_user.days_active - 1
			purchase_user.days_active = current_days
			# purchase_user.flags.ignore_permissions = True
			purchase_user.save(ignore_permissions=True)



@frappe.whitelist(allow_guest=True)
def check_subdomain(subdomain):
	new_subdomain = subdomain.lower()

	cari_subdomain = frappe.db.sql(""" SELECT ms.`name` FROM `tabMaster Subdomain` ms WHERE ms.`subdomain` = "{}" """.format(new_subdomain))

	# frappe.throw(str(cari_subdomain))

	if cari_subdomain :
		return "sudah ada"
	else :
		return "belum ada"

@frappe.whitelist(allow_guest=True)
def check_lower_case_and_alphabet_only(subdomain):
	
	if re.match(r'^[a-zA-Z0-9_]+$', subdomain):
		return "bisa"
	else :
		return "tidak bisa"

def create_invoice():
	inv = frappe.new_doc("Invoice")
	inv.status = "Paid"
	inv.subdomain = "andy.solubis.id"
	inv.owner = "macflamerz@gmail.com"
	inv.total_user = 1
	inv.append("invoice_item",{
			"description": "register user",
			"price_list": "Promo 1 User",
			"price_list_rate": 0,
			"discount":0,
			"discount_rate":0,
			"price": 0,
			"type":"New User"
		})
	inv.total = 0
	inv.discount = 0
	inv.grand_total = 0
	inv.flags.ignore_permissions = True
	inv.save()

@frappe.whitelist(allow_guest=True)		
def get_invoice_detail(inv_no):
	details = frappe.db.sql("SELECT price_list_rate,description, price, discount_rate, type, price_list FROM `tabInvoice Item` where parent = '{}' ".format(inv_no), as_dict = 1)
	data = []
	for item in details:
		data.append(item)
	result = {'data':data}
	return result