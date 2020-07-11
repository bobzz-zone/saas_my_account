from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import utils,throw, msgprint, _
import os
import requests
import json
import re
import subprocess
from frappe.utils.background_jobs import enqueue
from frappe.utils import date_diff, month_diff, today, get_first_day, get_last_day
from my_account.my_account.doctype.buy_new_user.buy_new_user import create_xendit_invoice
from frappe.commands import pass_context, get_site

@frappe.whitelist(allow_guest=True)
def get_price_list():
	return frappe.db.sql("SELECT * FROM `tabPrice List`",as_dict=True);

@frappe.whitelist(allow_guest=True)
def get_price_per_quota():
	return frappe.db.get_single_value("Additional Settings","price_quota")

@frappe.whitelist(allow_guest=True)
def get_extra_module():
	return frappe.db.sql(""" SELECT module_name,module_price FROM `tabAdditional Modules` WHERE parenttype = "Additional Settings" """, as_dict=1)

@frappe.whitelist()
def get_current_quota(subdomain):
	# print(subdomain)
	return frappe.db.get_value("Master Subdomain",subdomain,"quota")

@frappe.whitelist()
def update_quota(_subdomain, new_quota):
	subdomain = frappe.get_doc("Master Subdomain",_subdomain)
	active_user = float(enabled_user(_subdomain))
	quota = float(new_quota) - float(subdomain.quota)
	price_per_quota = float(frappe.db.get_single_value("Additional Settings","price_quota"))

	if float(new_quota) > float(subdomain.quota):
		# print("nambah")
		# create invoice for new quota
		# count days left in month

		days_left = 0
		total = 0
		if subdomain.periodic == "Monthly":
			days_left = date_diff(get_last_day(today()),today()) + 1
			total = int(int(price_per_quota) * int(quota) * days_left/30)
		# full_days = date_diff(get_last_day(today()),get_first_day(utils.today())) + 1
		else:
			days_left = date_diff(get_last_day(today()),today()) + 1
			year = utils.today().split("-")[0]
			months_left = utils.month_diff("{}-12-31".format(year),utils.today()) - 1
			cur_mth = int(int(price_per_quota) * int(quota) * days_left/30)
			mth_left = int(price_per_quota) * int(quota) * mth_left
			total = cur_mth + mth_left

		inv = frappe.new_doc("Invoice")
		inv.status = "Unpaid"
		inv.subdomain = _subdomain.lower()
		inv.total_user = quota
		inv.total = total
		inv.owner = subdomain.user
		inv.discount = 0
		inv.grand_total = total
		inv.flags.ignore_permissions = True

		ch = inv.append('invoice_item', {})
		ch.type = "Add Quota"

		inv.save()
		desc = "Invoice for subdomain {}, add quota {}".format(inv.subdomain,quota)
		# return create_xendit_invoice(inv.name, desc)
		link = create_xendit_invoice(inv.name,desc)
		return 1, _("After invoice paid, quota will be up to date.<br>Here is link to pay invoice {} ".format(link))
	else:
		
		if float(active_user) > float(new_quota):
			# new quota can't more than 
			return 0, _("Please disable {} user/s to proceed.".format(active_user-new_quota))
		else:
			subdomain.quota = new_quota
			subdomain.save(ignore_permissions=True)
			return 1, _("""Next invoice will be charged for {} extra users""".format(new_quota))

def test_days_left():
	days_left = utils.date_diff(utils.get_last_day(utils.today()),utils.today()) + 1
	full_days = utils.date_diff(utils.get_last_day(utils.today()),utils.get_first_day(utils.today())) + 1
	harga = 200000
	total = int(200000 * 1 * days_left/full_days)
	return total

def test_yearly():
	days_left = utils.date_diff(utils.get_last_day(utils.today()),utils.today()) + 1
	year = utils.today().split("-")[0]
	months_left = utils.month_diff("{}-12-31".format(year),utils.today()) - 1
	return months_left

@frappe.whitelist()
def enabled_user(subdomain):
	# hasil returnnya jelek "[\"0\"]"
	# stream = os.popen("cd /home/frappe/frappe-bench;bench --site {}.solubis.id execute frappe.core.doctype.user.user.get_enabled_users".format(subdomain))
	# result = stream.read().strip()

	stream = subprocess.call(['bench','--site',"{}.solubis.id".format(subdomain),'execute','frappe.core.doctype.user.user.get_enabled_users'])

	return stream

@frappe.whitelist()
def add_subdomain(subdomain,email, solubis_plan,periodic):

	plist = frappe.get_doc("Price List",solubis_plan)
	full_name = frappe.db.get_value("User", email, "full_name")
	# create subdomain
	sdm = frappe.new_doc("Master Subdomain")
	sdm.subdomain = subdomain.lower()
	sdm.is_created = 0
	sdm.user = email
	sdm.active_plan = solubis_plan
	sdm.quota = 1
	sdm.periodic = periodic
	sdm.flags.ignore_permissions = True
	sdm.save()
	frappe.db.commit()

	inv = frappe.new_doc("Invoice")
	inv.status = "Unpaid"
	inv.subdomain = subdomain.lower()
	inv.total_user = 1
	inv.append("invoice_item",{
			"description": email,
			"price_list": solubis_plan,
			"price_list_rate": plist.normal_price,
			"fullname": full_name,
			"discount":0,
			"discount_rate": plist.discount_price,
			"price": plist.normal_price,
			"type":"Add Subdomain"
		})

	days_left = 0
	total = 0
	if periodic == "Monthly":
		days_left = date_diff(get_last_day(today()),today()) + 1
		total = int(int(plist.normal_price) * days_left/30)
	# full_days = date_diff(get_last_day(today()),get_first_day(utils.today())) + 1
	else:
		days_left = date_diff(get_last_day(today()),today()) + 1
		year = utils.today().split("-")[0]
		months_left = utils.month_diff("{}-12-31".format(year),utils.today()) - 1
		cur_mth = int(int(plist.normal_price) * days_left/30)
		mth_left = int(plist.normal_price) * mth_left
		total = cur_mth + mth_left

	inv.total = total
	inv.owner = email
	inv.discount = 0
	inv.grand_total = total
	inv.flags.ignore_permissions = True
	inv.save()
	desc = "Invoice for user {}, add subdomain {}.solubis.id".format(email,subdomain)

	link = create_xendit_invoice(inv.name,desc)
	return 1, _("Here is link to pay invoice {} ".format(link))

@frappe.whitelist(allow_guest=True)
def get_active_modules(subdomain):
	# get active module
	active_modules = frappe.db.sql("SELECT group_concat(module) FROM `tabDomain Active Modules` WHERE parent = '{}';".format(subdomain),as_dict=0)
	# if len(active_modules)>0:
		# active_modules = active_modules[0]
	
	return active_modules[0][0]

@frappe.whitelist()
def update_module(subdomain, enable_module):
	# if remove update subdomain
	# print("update module {} ".format(subdomain))
	# print("update modules {} ".format(enable_module))

	curmodule = get_active_modules(subdomain)
	if curmodule:
		curmodule = curmodule.split(",")

	reqmodule = enable_module.split(",")
	owner = frappe.db.get_value("Master Subdomain",subdomain,"user")
	periodic = frappe.db.get_value("Master Subdomain",subdomain,"periodic")
	add_module = []
	remove_module = curmodule

	for module in reqmodule:
		if curmodule:
			for x in curmodule:
				print(x)
				print(module)
				if x == module:
					add_module.append(module)
					remove_module.remove(module)
		else:
			add_module.append(module)

	
	total = 0
	if remove_module:
		for delmod in remove_module:
			frappe.db.sql("DELETE FROM `tabDomain Active Modules` WHERE parent = '{}' and module = '{}'".format(subdomain,delmod),as_dict=0)
		frappe.db.commit()
		return 1, _("Module List Updated")


	if add_module:
		for newmod in add_module:
			price = frappe.db.sql(""" SELECT module_price FROM `tabAdditional Modules` WHERE parenttype = "Additional Settings" and module_name = "{}" """.format(newmod))[0][0]
			total = total + price

		# if add create invoice
		inv = frappe.new_doc("Invoice")
		inv.status = "Unpaid"
		inv.subdomain = subdomain.lower()
		inv.total_user = 0

		days_left = 0
		total = 0
		if periodic == "Monthly":
			days_left = date_diff(get_last_day(today()),today()) + 1
			total = int(int(total) * days_left/30)
		# full_days = date_diff(get_last_day(today()),get_first_day(utils.today())) + 1
		else:
			days_left = date_diff(get_last_day(today()),today()) + 1
			year = utils.today().split("-")[0]
			months_left = utils.month_diff("{}-12-31".format(year),utils.today()) - 1
			cur_mth = int(int(total) * days_left/30)
			mth_left = int(total) * mth_left
			total = cur_mth + mth_left


		inv.total = total
		inv.owner = owner
		inv.discount = 0
		inv.grand_total = total
		inv.flags.ignore_permissions = True

		ch = inv.append('invoice_item', {})
		ch.type = "Add Module"
		ch.fullname = enable_module

		inv.save()
		frappe.db.commit()
		desc = "Invoice for site {}, add module {}".format(subdomain,enable_module)
		link = create_xendit_invoice(inv.name,desc)
		return 1, _("After invoice paid, quota will be up to date. <br> Here is link to pay invoice {} ".format(link))


	# return subdomain,enable_module

def auto_invoice_monthly():
	# formula
	# invoice amount = package price + quota-1*(price per quota) + additional module price
	subdomain_list = frappe.db.sql("SELECT * FROM `tabMaster Subdomain` where is_created = 1 and periodic = 'Monthly' and extend_trial = 0",as_dict=1)
	for subdomain in subdomain_list:
		subdomain.disable_if_not_pay = 1
		plist = frappe.get_doc("Price List",subdomain.active_plan)

		# additional module
		total_module = 0
		if subdomain.active_modules:
			for mod in subdomain.active_modules:
				price = frappe.db.sql(""" SELECT module_price FROM `tabAdditional Modules` WHERE parenttype = "Additional Settings" and module_name = "{}" """.format(mod))[0][0]
				total_module = total_module + price

		inv = frappe.new_doc("Invoice")
		inv.status = "Unpaid"
		inv.subdomain = subdomain.name.lower()
		inv.total_user = 1
		inv.append("invoice_item",{
				"description": subdomain.user,
				"price_list": subdomain.active_plan,
				"price_list_rate": plist.normal_price,
				"discount":0,
				"discount_rate": plist.discount_price,
				"price": plist.normal_price,
				"type":"Perpanjangan"
			})
		inv.total = plist.normal_price + int(get_price_per_quota())*(int(subdomain.quota)-1) + total_module
		inv.owner = subdomain.user
		inv.discount = 0
		inv.grand_total = inv.total
		inv.flags.ignore_permissions = True
		inv.save()
		desc = "Invoice for user {}, add subdomain {}.solubis.id".format(subdomain.user,subdomain.name)
		create_xendit_invoice(inv.name, desc)

def auto_invoice_yearly():
	# formula
	# invoice amount = package price + quota-1*(price per quota) + additional module price
	subdomain_list = frappe.db.sql("SELECT * FROM `tabMaster Subdomain` where is_created = 1 and periodic = 'Yearly' and extend_trial = 0",as_dict=1)
	for subdomain in subdomain_list:
		subdomain.disable_if_not_pay = 1

		plist = frappe.get_doc("Price List",subdomain.active_plan)

		total_module = 0
		if subdomain.active_modules:
			for mod in subdomain.active_modules:
				price = frappe.db.sql(""" SELECT module_price FROM `tabAdditional Modules` WHERE parenttype = "Additional Settings" and module_name = "{}" """.format(mod))[0][0]
				total_module = total_module + price

		inv = frappe.new_doc("Invoice")
		inv.status = "Unpaid"
		inv.subdomain = subdomain.name.lower()
		inv.total_user = 1
		inv.append("invoice_item",{
				"description": subdomain.user,
				"price_list": subdomain.active_plan,
				"price_list_rate": plist.normal_price,
				"discount":0,
				"discount_rate": plist.discount_price,
				"price": plist.normal_price,
				"type":"Perpanjangan"
			})
		inv.total = int(plist.normal_price + int(get_price_per_quota())*(int(subdomain.quota)-1) + total_module) * 12
		inv.owner = subdomain.user
		inv.discount = 0
		inv.grand_total = int(plist.normal_price + int(get_price_per_quota())*int(subdomain.quota) + total_module) * 12
		inv.flags.ignore_permissions = True
		inv.save()
		desc = "Invoice for user {}, add subdomain {}.solubis.id".format(subdomain.user,subdomain.name)
		create_xendit_invoice(inv.name, desc)


def set_site_disabled():
	subdomain_list = frappe.db.sql("select * FROM `tabMaster Subdomain` where disable_if_not_pay = 1 and extend_trial = 0",as_dict=1)
	for subdomain in subdomain_list:
		site = "{}.solubis.id".format(subdomain.name)
		# f = open("./sites/{}/site_config.json".format(site),"w")
		data = ""

		# disable site
		with open("/home/frappe/frappe-bench/sites/{}/site_config.json".format(site)) as read_file:
			data = json.load(read_file)
			data.update({"site_disabled":1})

		with open("/home/frappe/frappe-bench/sites/{}/site_config.json".format(site),"w") as write_file:
			json.dump(data,write_file, indent=2)

		# from frappe.installer import update_site_config
		# site = get_site(context)
		# print(site)
		# try:
		# 	frappe.init(site="coba1.solubis.id")
		# 	update_site_config('site_disabled', 1)

		# finally:
		# 	frappe.destroy()

@frappe.whitelist()
def remove_extend_trial():
	frappe.db.sql("update `tabMaster Subdomain` set extend_trial = 0")
	frappe.db.commit()