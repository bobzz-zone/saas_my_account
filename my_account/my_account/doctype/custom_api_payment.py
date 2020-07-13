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
from frappe.utils import strip, cint, today
from frappe import throw, msgprint, _
import re
from frappe import utils

import json


class custom_api_payment(Document):
	pass



@frappe.whitelist(allow_guest=True)
def ding():
	return "dong"


@frappe.whitelist(allow_guest=True)
def get_data_invoice_by_random_code():
	
	random_code = frappe.form_dict.get('random_code')

	temp_parent = []

	get_invoice = frappe.db.sql(
		"""
		SELECT u.`name`, u.`subdomain`, u.`grand_total`, u.`total_user` FROM `tabInvoice` u
		WHERE u.`random_code` = "{0}"
		AND u.`status` != "Paid"
		
		""".format(random_code), as_list=1 )


	if get_invoice :
		for p in get_invoice :

			temp_parent = {}
			temp_parent['name'] = p[0]
			temp_parent['subdomain'] = p[1]
			temp_parent['total'] = p[2]
			temp_parent['total_user'] = p[3]
			temp_parent['isi_array'] = "ada"

	else :
		temp_parent = {}
		temp_parent['name'] = "kosong"
		temp_parent['subdomain'] = "kosong"
		temp_parent['total'] = "kosong"
		temp_parent['total_user'] = "kosong"
		temp_parent['isi_array'] = "tidak ada"

	
	return temp_parent

@frappe.whitelist(allow_guest=True)
def payment_success_with_payment_gateway(invoice):
	
	# invoice = frappe.form_dict.get('invoice')

	# invoice = frappe.form_dict.get('order_id')
	# data = json.loads(str(data))

	# invoice = data["invoice"]
	# note_payment = data["note_payment"]
	note_payment = "Xendit"
	

	# mengubah invoice menjadi paid
	data_invoice = frappe.get_doc("Invoice", invoice)
	data_invoice.status = "Paid"
	data_invoice.paid_date = today()
	data_invoice.status_payment = "Success"
	data_invoice.flags.ignore_permissions = True
	data_invoice.save()
	# mengaktifkan user

	_subdomain = frappe.get_doc("Master Subdomain", data_invoice.subdomain)
	
	


	os.chdir("/home/frappe/frappe-bench")

	for i in data_invoice.invoice_item :
		if i.type == "New User" or i.type == "Perpanjangan User" :

			user = i.description
			price_list = frappe.get_doc("Price List", i.price_list)

			data_user = frappe.get_doc("Purchase User", user)
			data_user.enabled = 1
			data_user.status = "Paid"
			data_user.days_active = price_list.active_days
			data_user.flags.ignore_permissions = True
			data_user.save()

			lengkap = "{}.solubis.id".format(data_invoice.subdomain)
			if _subdomain.is_created == 0:
				subdom_name = _subdomain.name.lower()
				lengkap = "{}.solubis.id".format(subdom_name)
				full_name = frappe.db.get_value("User", _subdomain.user, 'full_name')

				email = _subdomain.user
				tidaklengkap = subdom_name
				# create site setelah user bayar (flow no trial)
				enqueue("my_account.custom_dns_api.create_new_site_subprocess", newsitename=lengkap, sitesubdomain=subdom_name, subdomuser=_subdomain.user,  fullname_user=full_name)
			_subdomain.disable_if_not_pay = 0	

		if i.type == "Add Quota":
			print('add quota')
			_subdomain.quota = _subdomain.quota + int(data_invoice.total_user)

		if i.type == "Add Subdomain":
			print('add subdomain')
			subdom_name = _subdomain.name.lower()
			lengkap = "{}.solubis.id".format(subdom_name)
			full_name = frappe.db.get_value("User", _subdomain.user, 'full_name')
			enqueue("my_account.custom_dns_api.create_new_site_subprocess", newsitename=lengkap, sitesubdomain=subdom_name, subdomuser=_subdomain.user,  fullname_user=full_name)


		if i.type == "Add Module":
			print("Add Module")
			mods = i.fullname.split(",")
			for x in mods:
				_subdomain.append("active_modules",{"module":x})

		if i.type == "Perpanjangan":
			_subdomain.disable_if_not_pay = 0
			_subdomain.on_trial = 0

	_subdomain.save(ignore_permissions=True)

	history_payment = frappe.new_doc("History Payment")
	history_payment.posting_date = utils.today()
	history_payment.subdomain = data_invoice.subdomain
	history_payment.invoice = invoice
	history_payment.paid_amount = data_invoice.grand_total
	history_payment.note = note_payment
	history_payment.flags.ignore_permissions = True
	history_payment.save()

@frappe.whitelist()
def update_quota(subdomain,quota):
	_subdomain = frappe.get_doc("Master Subdomain", subdomain)
	_subdomain.quota = _subdomain.quota + int(quota)
	_subdomain.save(ignore_permissions=True)


def test_reset():
	frappe.db.set_value("Purchase User","macflamerz@gmail.com","status","Unpaid")
	frappe.db.set_value("Invoice","INV/06/2020/00004","status","Unpaid")
	frappe.db.set_value("Master Subdomain","coba1","is_created",0)


# @frappe.whitelist(allow_guest=True)
# def check_new_user_buy():
	
# 	user = frappe.form_dict.get('user')
# 	cek_user = frappe.db.sql(
# 		"""
# 		SELECT * FROM `tabPurchase User` u
# 		WHERE u.`name` = "{0}"
		
# 		""".format(user), as_list=1 )

# 	if cek_user :
# 		return "Not Available"

# 	else :
# 		return "Available"



# @frappe.whitelist(allow_guest=True)
# def get_user_list_by_user():
	
# 	user = frappe.form_dict.get('user')

# 	temp_data = []
# 	temp_parent = []

# 	parent = frappe.db.sql(
# 		"""
# 		SELECT 

# 		u.`name`, 
# 		u.`enabled`, 
# 		u.`status`,
# 		u.`fullname`

# 		FROM `tabPurchase User` u
# 		WHERE u.`owner` = "{0}"
		
# 		""".format(user), as_list=1 )


# 	if parent :
# 		for p in parent :

# 			temp_parent = {}
# 			temp_parent['email'] = p[0]
# 			temp_parent['enabled'] = p[1]
# 			temp_parent['status'] = p[2]
# 			temp_parent['fullname'] = p[3]

# 			temp_data.append(temp_parent)
			
# 		return temp_data

# 	else :

# 		return "Not Found"



# @frappe.whitelist(allow_guest=True)
# def get_detail_user_by_user():
	
# 	user = frappe.form_dict.get('user')

# 	temp_data = []
# 	temp_parent = []

# 	parent = frappe.db.sql(
# 		"""
# 		SELECT 

# 		u.`name`,
# 		u.`status`,
# 		u.`enabled`,
# 		u.`fullname`,
# 		u.`subdomain`,
# 		u.`days_active`,
# 		u.`price_list`,
# 		u.`account_manager`,
# 		u.`account_user`,
# 		u.`purchase_manager`,
# 		u.`purchase_user`,
# 		u.`sales_manager`,
# 		u.`sales_user`,
# 		u.`manufacturing_manager`,
# 		u.`manufacturing_user`,
# 		u.`stock_manager`,
# 		u.`stock_user`,
# 		u.`hr_manager`,
# 		u.`hr_user`

# 		FROM `tabPurchase User` u
# 		WHERE u.`name` = "{0}"
		
# 		""".format(user), as_list=1 )


# 	if parent :
# 		for p in parent :

# 			temp_parent = {}
# 			temp_parent['name'] = p[0]
# 			temp_parent['status'] = p[1]
# 			temp_parent['enabled'] = p[2]
# 			temp_parent['fullname'] = p[3]

# 			temp_parent['subdomain'] = p[4]
# 			temp_parent['days_active'] = p[5]
# 			temp_parent['price_list'] = p[6]

# 			temp_parent['account_manager'] = p[7]
# 			temp_parent['account_user'] = p[8]

# 			temp_parent['purchase_manager'] = p[9]
# 			temp_parent['purchase_user'] = p[10]

# 			temp_parent['sales_manager'] = p[11]
# 			temp_parent['sales_user'] = p[12]

# 			temp_parent['manufacturing_manager'] = p[13]
# 			temp_parent['manufacturing_user'] = p[14]

# 			temp_parent['stock_manager'] = p[15]
# 			temp_parent['stock_user'] = p[16]

# 			temp_parent['hr_manager'] = p[17]
# 			temp_parent['hr_user'] = p[18]

			

# 			temp_data.append(temp_parent)
			
# 		return temp_data

# 	else :

# 		return "Not Found"





# @frappe.whitelist(allow_guest=True)
# def get_price_list():
	
# 	# user = frappe.form_dict.get('user')

# 	temp_data = []
# 	temp_parent = []

# 	parent = frappe.db.sql(
# 		"""
# 		SELECT 
# 		pl.`name`, 
# 		pl.`normal_price`, 
# 		pl.`discount_price`,
# 		pl.`active_days` 

# 		FROM `tabPrice List` pl
# 		WHERE pl.`disabled` = 0
		
# 		""", as_list=1 )

# 	if parent :
# 		for p in parent :

# 			temp_parent = {}
# 			temp_parent['price_list'] = p[0]
# 			temp_parent['normal_price'] = p[1]
# 			temp_parent['discount_price'] = p[2]
# 			temp_parent['active_days'] = p[3]

# 			temp_data.append(temp_parent)
			
# 		return temp_data

# 	else :

# 		return "Not Found"






# @frappe.whitelist(allow_guest=True)
# def get_invoice_by_user():
# 	try :

# 		user = frappe.form_dict.get('user')

# 		temp_child = []
# 		temp_parent = []

# 		parent = frappe.db.sql(
# 			"""
# 			SELECT  

# 			inv.`name`,
# 			inv.`owner`,
# 			inv.`status`,
# 			inv.`posting_date`,
# 			inv.`posting_time`,
# 			inv.`subdomain`,
# 			inv.`total`,
# 			inv.`petunjuk_pembayaran`,
# 			inv.`konfirmasi_pembayaran`

# 			FROM `tabInvoice` inv
# 			WHERE inv.`owner` = "{0}"
			
# 			""".format(user), as_list=1 )


# 		if parent :
# 			for p in parent :

# 				temp_parent = {}
# 				temp_parent['name'] = p[0]
# 				temp_parent['owner'] = p[1]
# 				temp_parent['status'] = p[2]
# 				temp_parent['posting_date'] = p[3]
# 				temp_parent['posting_time'] = p[4]
# 				temp_parent['subdomain'] = p[5]
# 				temp_parent['total'] = p[6]
# 				temp_parent['petunjuk_pembayaran'] = p[6]
# 				temp_parent['konfirmasi_pembayaran'] = p[6]
# 				temp_parent['items'] = []

# 				child = frappe.db.sql(
# 					"""

# 					SELECT
# 					inv_i.`parent`,
# 					inv_i.`description`,
# 					inv_i.`price_list`,
# 					inv_i.`price`
# 					FROM `tabInvoice Item` inv_i
# 					WHERE inv_i.`parent` = "{0}"
# 					ORDER BY inv_i.`idx`

# 					""".format(p[0]), as_list=1 )

# 				if child :
# 					items = []
# 					for c in child :

# 						temp_child = {}
# 						temp_child['parent'] = c[0]
# 						temp_child['description'] = c[1]
# 						temp_child['price_list'] = c[2]
# 						temp_child['price'] = c[3]

# 						items.append(temp_child)

# 					temp_parent['items'] = items





# 		return temp_parent

# 	except :
# 		return "not found"


# @frappe.whitelist(allow_guest=True)
# def check_new_subdomain():

# 	subdomain = frappe.form_dict.get('subdomain')
# 	new_subdomain = subdomain.lower()

# 	cari_subdomain = frappe.db.sql(""" SELECT ms.`name` FROM `tabMaster Subdomain` ms WHERE ms.`subdomain` = "{}" """.format(new_subdomain))

# 	if cari_subdomain :
# 		return "Not Available"
# 	else :
# 		return "Available"




# @frappe.whitelist(allow_guest=True)
# def create_new_user_register_and_subdomain():
	
# 	data = frappe.form_dict.get('data')
# 	data = json.loads(str(data))

# 	email = data["email"]
# 	full_name = data["full_name"]
# 	subdomain = data["subdomain"]
# 	password = data["password"]

# 	# create user
# 	user = frappe.get_doc({
# 		"doctype":"User",
# 		"email": email,
# 		"first_name": full_name,
# 		"enabled": 1,
# 		"new_password": password,
# 		"user_type": "Website User",
		
# 		"subdomain" : subdomain.lower(),
# 		"block_modules" : [
# 			{"module" : "Contacts"},
# 			{"module" : "Desk"},
# 			{"module" : "File Manager"},
# 			{"module" : "Integrations"},
# 			{"module" : "Setup"},
# 			{"module" : "Core"},
# 			{"module" : "Email Inbox"},
# 			{"module" : "Website"}
# 		],
# 		"roles" : [
# 			{"role" : "My Account Role"},
# 			{"role" : "GMS Support Role"},
# 		]
# 	})

# 	user.flags.ignore_permissions = True
# 	user.insert()

# 	# create subdomain
# 	sdm = frappe.new_doc("Master Subdomain")
# 	sdm.subdomain = subdomain.lower()
# 	sdm.is_created = 0
# 	sdm.user = email
# 	sdm.flags.ignore_permissions = True
# 	sdm.save()

# 	# create purchase user
# 	purchase_user = frappe.new_doc("Purchase User")
# 	purchase_user.fullname = full_name
# 	purchase_user.email = email
# 	purchase_user.enabled = 1
# 	purchase_user.status = "Free"
# 	purchase_user.subdomain = subdomain.lower()
# 	purchase_user.days_active = 90
# 	# purchase_user.price_list = "Monthly"

# 	purchase_user.flags.ignore_permissions = True
# 	purchase_user.save()

# 	frappe.db.sql(""" UPDATE `tabPurchase User` SET owner = "{0}", modified_by = "{1}" WHERE name = "{2}" """.format(email, email, email))
# 	frappe.db.commit()

# 	return "success"


	
# @frappe.whitelist(allow_guest=True)
# def activate_subdomain_and_install_erp():
	
# 	data = frappe.form_dict.get('data')
# 	data = json.loads(str(data))

# 	user = data["email"]
# 	full_name = data["full_name"]
# 	subdomain = data["subdomain"]
# 	new_password = data["password"]


# 	subdom = frappe.get_all('Master Subdomain', filters={'user': user}, fields=['name', 'user', 'is_created'])
# 	subdom_name = subdomain
# 	subdom_is_created = subdom[0]["is_created"]
# 	subdom_user = user
# 	subdom_pass = new_password

# 	# get fullname
# 	fullname_user = fullname
# 	user_subdomain = subdomain

# 	if subdom_is_created == 0:
# 		lengkap = "{}.crativate.com".format(subdom_name)
# 		tidaklengkap = subdom_name
# 		enqueue("my_account.custom_dns_api.create_new_site_subprocess", newsitename=lengkap, sitesubdomain=tidaklengkap, subdomuser=subdom_user, subdompass=subdom_pass, fullname_user=fullname_user)

# 		return "success"

# 	return "subdomain already created"



# @frappe.whitelist(allow_guest=True)
# def create_new_user_buy_by_user():
	
# 	data = frappe.form_dict.get('data')
# 	data = json.loads(str(data))

# 	user = data["user"]
# 	subdomain = data["subdomain"]
# 	total = data["total"]
# 	new_user = data["new_user"]
# 	posting_date = data["posting_date"]
	
# 	for i in new_user :
# 		purchase_user = frappe.new_doc("Purchase User")
# 		purchase_user.posting_date = posting_date
# 		purchase_user.subdomain = subdomain
# 		purchase_user.enabled = 0
# 		purchase_user.fullname = i["fullname"]
# 		purchase_user.email = i["email"]
# 		purchase_user.current_password = i["new_password"]
# 		purchase_user.status = "Unpaid"
# 		purchase_user.price_list = i["price_list"]
# 		pls = frappe.get_doc("Price List", i["price_list"])
# 		purchase_user.days_active = pls.active_days

# 		# role
# 		purchase_user.account_manager = i["account_manager"]
# 		purchase_user.account_user = i["account_user"]
# 		purchase_user.purchase_manager = i["purchase_manager"]
# 		purchase_user.purchase_user = i["purchase_user"]
# 		purchase_user.sales_manager = i["sales_manager"]
# 		purchase_user.sales_user = i["sales_user"]
# 		purchase_user.stock_manager = i["stock_manager"]
# 		purchase_user.stock_user = i["stock_user"]
# 		purchase_user.manufacturing_manager = i["manufacturing_manager"]
# 		purchase_user.manufacturing_user = i["manufacturing_user"]
# 		purchase_user.hr_manager = i["hr_manager"]
# 		purchase_user.hr_user = i["hr_user"]

# 		purchase_user.flags.ignore_permissions = True
# 		purchase_user.save()


# 	# create invoice
# 	invoice = frappe.new_doc("Invoice")
# 	invoice.posting_date = posting_date
# 	invoice.subdomain = subdomain

# 	total_harga= 0 

# 	for i in new_user :
# 		ch = invoice.append('invoice_item', {})
# 		ch.description = i["email"]
# 		ch.price_list = i["price_list"]
# 		ch.price = i["price"]
# 		ch.type = "New User"
		
# 		total_harga = total_harga + i["price"]

# 	invoice.total = total_harga

# 	invoice.flags.ignore_permissions = True
# 	invoice.save()


# 	invoice2 = frappe.get_doc("Invoice", invoice.name)
# 	invoice2.petunjuk_pembayaran = """

# 		Petunjuk Pembayaran
# 		<br><br>
# 		Invoice {0}
# 		<br>
# 		Total : Rp. {1}
# 		<br>
# 		Berita : {0}
# 		<br><br>
# 		*Ketikkan berita di atas pada saat Anda melakukan pembayaran melalui ATM Non-Tunai, setoran Bank, atau Internet Banking
# 		Data Bank
# 		<br>
# 		<br>
# 		BANK BCA
# 		<br>
# 		No. Rek. 8630196150
# 		<br>
# 		a/n Bobby Hartanto Kurniawan
# 		<br><br>
# 		Jangan lupa konfirmasi

# 	""".format(invoice.name, invoice.total)

# 	invoice2.konfirmasi_pembayaran = """

# 		Segera lakukan konfirmasi setelah Anda melakukan pembayaran. Konfirmasi dapat dilakukan melalui email :
# 		<br><br>
# 		Kirimkan Email ke <b>ptglobalmediasolusindo@gmail.com</b> dengan format berikut :
# 		<br><br>
# 		BAYAR
# 		<br>
# 		INV : {0}
# 		<br>
# 		JML :
# 		<br> 
# 		BANK :
# 		<br> 
# 		ATAS NAMA :
# 		<br><br>

# 		*Mohon konfirmasi Email dilakukan di hari yang sama
# 		<br>
# 		Pembayaran yang tidak dikonfirmasikan tidak akan diproses!

# 		""".format(invoice.name)

# 	invoice2.flags.ignore_permissions = True
# 	invoice2.save()

# 	return  "success, check your invoice : "+str(invoice.name)



# @frappe.whitelist(allow_guest=True)
# def activate_new_user_buy_and_add_to_erp_after_payment():
	
# 	data = frappe.form_dict.get('data')
# 	data = json.loads(str(data))

# 	user = data["user"]
# 	subdomain = data["subdomain"]
# 	invoice = data["invoice"]
	
# 	# mengubah invoice menjadi paid

# 	data_invoice = frappe.get_doc("Invoice", invoice)
# 	data_invoice.status = "Paid"
# 	data_invoice.flags.ignore_permissions = True
# 	data_invoice.save()

# 	# mengaktifkan user


# 	os.chdir("/home/frappe/frappe-bench")

# 	for i in data_invoice.invoice_item :
# 		if i.type == "New User" or i.type == "Perpanjangan User" :

# 			user = i.description
# 			price_list = frappe.get_doc("Price List", i.price_list)

# 			data_user = frappe.get_doc("Purchase User", user)
# 			data_user.enabled = 1
# 			data_user.status = "Paid"
# 			data_user.days_active = price_list.active_days
# 			data_user.flags.ignore_permissions = True
# 			data_user.save()

# 			lengkap = "{}.crativate.com".format(subdomain)
# 			enqueue("my_account.custom_dns_api.create_new_user_on_erp_site", newsitename=lengkap, email=data_user.email, fullname=data_user.fullname, password=data_user.current_password)


			

# 	history_payment = frappe.new_doc("History Payment")
# 	history_payment.posting_date = utils.today()
# 	history_payment.subdomain =subdomain
# 	history_payment.invoice =invoice
# 	history_payment.paid_amount = data_invoice.total
# 	history_payment.note = ""

# 	return  "success"