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
from frappe.utils.password import update_password as _update_password
from frappe import utils,throw, msgprint, _
from frappe.utils import cint, flt, has_gravatar, format_datetime, now_datetime, get_formatted_email, today,cstr, date_diff, get_first_day, get_last_day
import re
from my_account.my_account.doctype.buy_new_user.buy_new_user import create_xendit_invoice
from frappe.utils import get_url
import json
from frappe.utils.user import get_user_fullname

class custom_method(Document):
	pass

@frappe.whitelist(allow_guest=True)
def sign_up(email, full_name , subdomain, phone, plan,password, periodic, redirect_to):
	setting = frappe.get_single("Additional Settings")
	if not redirect_to:
		redirect_to=setting.billing_url
	user = frappe.db.get("User", {"email": email})
	
	# check subdomain exist
	domain_exist = frappe.db.get("Master Subdomain", {"name": subdomain})

	if domain_exist:
		return 0, _("Subdomain Exist")

	if user:
		if user.disabled:
			return 0, _("Email Registered but disabled")
		else:
			return 0, _("Email Already Registered")
	else:
		if frappe.db.sql("""select count(*) from tabUser where
			HOUR(TIMEDIFF(CURRENT_TIMESTAMP, TIMESTAMP(modified)))=1""")[0][0] > 300:

			frappe.respond_as_web_page(_('Temperorily Disabled'),
				_('Too many users signed up recently, so the registration is disabled. Please try back in an hour'),
				http_status_code=429)

		
		
		# flow without trial

		plist = frappe.get_doc("Price List",plan)

		inv = frappe.new_doc("Invoice")
		inv.status = "Unpaid"
		inv.subdomain = subdomain.lower()
		inv.total_user = 1
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

		inv.append("invoice_item",{
				"description": email,
				"price_list": plan,
				"price_list_rate": plist.normal_price,
				"fullname": full_name,
				"discount":0,
				"discount_rate": plist.discount_price,
				"price": plist.normal_price,
				"type":"New User"
			})
		inv.total = int(total)
		inv.owner = email
		inv.discount = 0
		inv.grand_total = int(total)
		inv.flags.ignore_permissions = True
		inv.save()
		desc = "Invoice for {} Register with plan {}".format(subdomain.lower(), plist.name)

		pay_link = create_xendit_invoice(inv.name, desc)
		# end flow

		# create purchase user
		purchase_user = frappe.new_doc("Purchase User")
		purchase_user.fullname = full_name
		purchase_user.email = email
		purchase_user.enabled = 0
		purchase_user.status = "Unpaid"
		purchase_user.phone = phone
		purchase_user.subdomain = subdomain.lower()
		purchase_user.days_active = 0
		purchase_user.price_list = plan
		purchase_user.flags.ignore_permissions = True
		purchase_user.owner = email
		purchase_user.current_password =password
		purchase_user.save()

		user = frappe.get_doc({
			"doctype":"User",
			"email": email,
			"first_name": full_name,
			"enabled": 1,
			"send_welcome_email" :0,
			"new_password": password,
			"user_type": "Website User",
			"phone": phone,
			# "subdomain" : subdomain.lower(),
			"block_modules" : [
				{"module" : "Contacts"},
				{"module" : "Desk"},
				{"module" : "File Manager"},
				{"module" : "Integrations"},
				{"module" : "Setup"},
				{"module" : "Core"},
				{"module" : "Email Inbox"},
				{"module" : "Website"}
			],
			"roles" : [
				{"role" : "My Account Role"}
			]
		})
		user.flags.ignore_permissions = True
		user.insert()

		pl = frappe.get_doc("Price List",plan)
		# create subdomain
		sdm = frappe.new_doc("Master Subdomain")
		sdm.subdomain = subdomain.lower()
		sdm.is_created = 0
		sdm.user = email
		sdm.active_plan = plan
		sdm.quota = pl.user_qty
		sdm.disable_if_not_pay = 1
		sdm.on_trial = 0
		sdm.periodic = periodic
		sdm.flags.ignore_permissions = True
		sdm.fullname=fullname
		sdm.password=password
		sdm.save()

		#edited bobby - added
		subdom_name = subdomain.lower()
		lengkap = "{}.{}".format(subdom_name,setting.url)
		tidaklengkap = subdom_name
		# flow trial 
		# enqueue("my_account.custom_dns_api.create_new_site_subprocess", newsitename=lengkap, sitesubdomain=subdom_name, subdomuser=email,  fullname_user=full_name)
		#end add

		#welcome email sent

		#link = user.reset_password()
		subject = None
		method = frappe.get_hooks("welcome_email")
		if method:
			subject = frappe.get_attr(method[-1])()
		if not subject:
			site_name = frappe.db.get_default('site_name') or frappe.get_conf().get("site_name")
			if site_name:
				subject = _("Welcome to {0}".format(site_name))
			else:
				subject = _("Complete Registration")

		# custom andy email to pay site registration flow invoice bayar baru create site
		#invoice = frappe.get_doc("Invoice",{"owner":self.name})
		# print(invoice.xendit_url)
		user.send_login_mail(subject, "new_user",
				dict(
					#link=link,
					site_url=get_url(),
					# custom andy email to pay site registration flow invoice bayar baru create site
					pay_link=pay_link
				))

		if redirect_to:
			frappe.cache().hset('redirect_after_login', user.name, redirect_to)

		return 1, _("Please check your email for new account verification"), pay_link
		
@frappe.whitelist(allow_guest=True)
def update_password(new_password, logout_all_sessions=0, key=None, old_password=None):
	setting = frappe.get_single("Additional Settings")
	
	res = _get_user_for_update_password(key, old_password)
	if res.get('message'):
		#start custom
		#frappe.local.response.http_status_code = 410
		return res['message']
	else:
		user = res['user']
	subdom = frappe.get_all('Master Subdomain', filters={'user': user}, fields=['name', 'user', 'is_created'])
	subdom_name = subdom[0]["name"]
	subdom_is_created = subdom[0]["is_created"]
	subdom_user = subdom[0]["user"]
	subdom_pass = new_password
	_update_password(user, new_password, logout_all_sessions=int(logout_all_sessions))

	# get fullname
	user_data = frappe.get_doc("User",user)
	fullname_user = user_data.first_name
	user_subdomain = user_data.subdomain
	# edited rico - enqueue create site
	# edited bobby comment
	lengkap = "{}.{}".format(subdom_name,setting.url)

	# create site setelah user set password (flow trial)
	#if subdomain.is_created == 0:
	#	enqueue("my_account.custom_dns_api.create_new_site_subprocess", newsitename=lengkap, sitesubdomain=subdom_name, subdomuser=email,  fullname_user=full_name)


	user_doc, redirect_url = reset_user_data(user)
	frappe.local.login_manager.login_as(user)

	frappe.db.set_value("User", user, "last_password_reset_date", today())
	frappe.db.set_value("User", user, "reset_password_key", "")

	if user_doc.user_type == "System User":
		#return "/desk"
		# return "https://"+lengkap
		# nanti ini direplace dengan solubis.id
		return setting.billing_url+"login"
	else:
		return "https://"+lengkap

@frappe.whitelist(allow_guest=True)
def check_new_user_register():
	
	user = frappe.form_dict.get('user')
	cek_user = frappe.db.sql(
		"""
		SELECT * FROM `tabUser` u
		WHERE u.`name` = "{0}"
		
		""".format(user), as_list=1 )

	if cek_user :
		return "Not Available"

	else :
		return "Available"


@frappe.whitelist(allow_guest=True)
def check_new_user_buy():
	
	user = frappe.form_dict.get('user')
	cek_user = frappe.db.sql(
		"""
		SELECT * FROM `tabPurchase User` u
		WHERE u.`name` = "{0}"
		
		""".format(user), as_list=1 )

	if cek_user :
		return "Not Available"

	else :
		return "Available"



@frappe.whitelist(allow_guest=True)
def get_user_list_by_user():
	
	user = frappe.form_dict.get('user')

	temp_data = []
	temp_parent = []

	parent = frappe.db.sql(
		"""
		SELECT 

		u.`name`, 
		u.`enabled`, 
		u.`status`,
		u.`fullname`

		FROM `tabPurchase User` u
		WHERE u.`owner` = "{0}"
		
		""".format(user), as_list=1 )


	if parent :
		for p in parent :

			temp_parent = {}
			temp_parent['email'] = p[0]
			temp_parent['enabled'] = p[1]
			temp_parent['status'] = p[2]
			temp_parent['fullname'] = p[3]

			temp_data.append(temp_parent)
			
		return temp_data

	else :

		return "Not Found"



@frappe.whitelist(allow_guest=True)
def get_detail_user_by_user():
	
	user = frappe.form_dict.get('user')

	temp_data = []
	temp_parent = []

	parent = frappe.db.sql(
		"""
		SELECT 

		u.`name`,
		u.`status`,
		u.`enabled`,
		u.`fullname`,
		u.`subdomain`,
		u.`days_active`,
		u.`price_list`,
		u.`account_manager`,
		u.`account_user`,
		u.`purchase_manager`,
		u.`purchase_user`,
		u.`sales_manager`,
		u.`sales_user`,
		u.`manufacturing_manager`,
		u.`manufacturing_user`,
		u.`stock_manager`,
		u.`stock_user`,
		u.`hr_manager`,
		u.`hr_user`

		FROM `tabPurchase User` u
		WHERE u.`name` = "{0}"
		
		""".format(user), as_list=1 )


	if parent :
		for p in parent :

			temp_parent = {}
			temp_parent['name'] = p[0]
			temp_parent['status'] = p[1]
			temp_parent['enabled'] = p[2]
			temp_parent['fullname'] = p[3]

			temp_parent['subdomain'] = p[4]
			temp_parent['days_active'] = p[5]
			temp_parent['price_list'] = p[6]

			temp_parent['account_manager'] = p[7]
			temp_parent['account_user'] = p[8]

			temp_parent['purchase_manager'] = p[9]
			temp_parent['purchase_user'] = p[10]

			temp_parent['sales_manager'] = p[11]
			temp_parent['sales_user'] = p[12]

			temp_parent['manufacturing_manager'] = p[13]
			temp_parent['manufacturing_user'] = p[14]

			temp_parent['stock_manager'] = p[15]
			temp_parent['stock_user'] = p[16]

			temp_parent['hr_manager'] = p[17]
			temp_parent['hr_user'] = p[18]

			

			temp_data.append(temp_parent)
			
		return temp_data

	else :

		return "Not Found"





@frappe.whitelist(allow_guest=True)
def get_price_list():
	
	# user = frappe.form_dict.get('user')

	temp_data = []
	temp_parent = []

	parent = frappe.db.sql(
		"""
		SELECT 
		pl.`name`, 
		pl.`normal_price`, 
		pl.`discount_price`,
		pl.`active_days` 

		FROM `tabPrice List` pl
		WHERE pl.`disabled` = 0
		
		""", as_list=1 )

	if parent :
		for p in parent :

			temp_parent = {}
			temp_parent['price_list'] = p[0]
			temp_parent['normal_price'] = p[1]
			temp_parent['discount_price'] = p[2]
			temp_parent['active_days'] = p[3]

			temp_data.append(temp_parent)
			
		return temp_data

	else :

		return "Not Found"


@frappe.whitelist(allow_guest=True)
def get_invoice_list_by_user():
	
	user = frappe.form_dict.get('user')

	temp_child = []
	temp_parent = []

	parent = frappe.db.sql(
		"""
		SELECT  

		inv.`name`,
		inv.`owner`,
		inv.`status`,
		inv.`posting_date`,
		inv.`posting_time`,
		inv.`subdomain`,
		inv.`total`,
		inv.`petunjuk_pembayaran`,
		inv.`konfirmasi_pembayaran`,
		inv.`random_code`

		FROM `tabInvoice` inv
		WHERE inv.`owner` = "{0}"
		
		""".format(user), as_list=1 )


	if parent :
		for p in parent :

			temp_child = {}
			temp_child['name'] = p[0]
			temp_child['owner'] = p[1]
			temp_child['status'] = p[2]
			temp_child['posting_date'] = p[3]
			temp_child['posting_time'] = p[4]
			temp_child['subdomain'] = p[5]
			temp_child['total'] = p[6]
			temp_child['random_code'] = p[9]
			

			temp_parent.append(temp_child)

	return temp_parent




@frappe.whitelist(allow_guest=True)
def get_invoice_detail_by_invoice():
	user = frappe.form_dict.get('invoice')

	temp_child = []
	temp_parent = []

	parent = frappe.db.sql(
		"""
		SELECT  

		inv.`name`,
		inv.`owner`,
		inv.`status`,
		inv.`posting_date`,
		inv.`posting_time`,
		inv.`subdomain`,
		inv.`total`,
		inv.`petunjuk_pembayaran`,
		inv.`konfirmasi_pembayaran`,
		inv.`random_code`

		FROM `tabInvoice` inv
		WHERE inv.`name` = "{0}"
		
		""".format(user), as_list=1 )


	if parent :
		for p in parent :

			temp_parent = {}
			temp_parent['name'] = p[0]
			temp_parent['owner'] = p[1]
			temp_parent['status'] = p[2]
			temp_parent['posting_date'] = p[3]
			temp_parent['posting_time'] = p[4]
			temp_parent['subdomain'] = p[5]
			temp_parent['total'] = p[6]
			temp_parent['petunjuk_pembayaran'] = p[7]
			temp_parent['konfirmasi_pembayaran'] = p[8]
			temp_parent['random_code'] = p[9]
			temp_parent['items'] = []

			child = frappe.db.sql(
				"""

				SELECT
				inv_i.`parent`,
				inv_i.`description`,
				inv_i.`price_list`,
				inv_i.`price`
				FROM `tabInvoice Item` inv_i
				WHERE inv_i.`parent` = "{0}"
				ORDER BY inv_i.`idx`

				""".format(p[0]), as_list=1 )

			if child :
				items = []
				for c in child :

					temp_child = {}
					temp_child['parent'] = c[0]
					temp_child['description'] = c[1]
					temp_child['price_list'] = c[2]
					temp_child['price'] = c[3]

					items.append(temp_child)

				temp_parent['items'] = items





	return temp_parent




@frappe.whitelist(allow_guest=True)
def get_history_payment_by_user():
	
	user = frappe.form_dict.get('user')

	temp_child = []
	temp_parent = []

	parent = frappe.db.sql(
		"""
		SELECT  

		inv.`name`,
		inv.`owner`,
		inv.`posting_date`,
		inv.`posting_time`,
		inv.`subdomain`,
		inv.`paid_amount`,
		inv.`note`

		FROM `tabHistory Payment` inv
		WHERE inv.`owner` = "{0}"
		
		""".format(user), as_list=1 )


	if parent :
		for p in parent :

			temp_child = {}
			temp_child['name'] = p[0]
			temp_child['owner'] = p[1]
			temp_child['posting_date'] = p[2]
			temp_child['posting_time'] = p[3]
			temp_child['subdomain'] = p[4]
			temp_child['paid_amount'] = p[5]
			temp_child['note'] = p[6]
			

			temp_parent.append(temp_child)

	return temp_parent

	






@frappe.whitelist(allow_guest=True)
def check_new_subdomain():

	subdomain = frappe.form_dict.get('subdomain')
	new_subdomain = subdomain.lower()

	cari_subdomain = frappe.db.sql(""" SELECT ms.`name` FROM `tabMaster Subdomain` ms WHERE ms.`subdomain` = "{}" """.format(new_subdomain))

	if cari_subdomain :
		return "Not Available"
	else :
		return "Available"




@frappe.whitelist(allow_guest=True)
def create_new_user_register_and_subdomain():
	
	data = frappe.form_dict.get('data')
	data = json.loads(str(data))

	# return data

	email = data["email"]
	full_name = data["full_name"]
	subdomain = data["subdomain"]
	password = data["password"]

	# create user
	user = frappe.get_doc({
		"doctype":"User",
		"email": email,
		"first_name": full_name,
		"enabled": 1,
		"new_password": password,
		"user_type": "Website User",
		
		"subdomain" : subdomain.lower(),
		"block_modules" : [
			{"module" : "Contacts"},
			{"module" : "Desk"},
			{"module" : "File Manager"},
			{"module" : "Integrations"},
			{"module" : "Setup"},
			{"module" : "Core"},
			{"module" : "Email Inbox"},
			{"module" : "Website"}
		],
		"roles" : [
			{"role" : "My Account Role"},
			{"role" : "GMS Support Role"},
		]
	})

	user.flags.ignore_permissions = True
	user.insert()

	# create subdomain
	sdm = frappe.new_doc("Master Subdomain")
	sdm.subdomain = subdomain.lower()
	sdm.is_created = 0
	sdm.user = email
	sdm.flags.ignore_permissions = True
	sdm.save()

	# create purchase user
	purchase_user = frappe.new_doc("Purchase User")
	purchase_user.fullname = full_name
	purchase_user.email = email
	purchase_user.enabled = 1
	purchase_user.status = "Free"
	purchase_user.subdomain = subdomain.lower()
	purchase_user.days_active = 90
	# purchase_user.price_list = "Monthly"

	purchase_user.flags.ignore_permissions = True
	purchase_user.save()

	frappe.db.sql(""" UPDATE `tabPurchase User` SET owner = "{0}", modified_by = "{1}" WHERE name = "{2}" """.format(email, email, email))
	
	return "success"


	
@frappe.whitelist(allow_guest=True)
def activate_subdomain_and_install_erp():
	setting = frappe.get_single("Additional Settings")
	data = frappe.form_dict.get('data')
	data = json.loads(str(data))

	user = data["email"]
	full_name = data["full_name"]
	subdomain = data["subdomain"]
	new_password = data["password"]


	subdom = frappe.get_all('Master Subdomain', filters={'user': user}, fields=['name', 'user', 'is_created'])
	subdom_name = subdomain
	subdom_is_created = subdom[0]["is_created"]
	subdom_user = user
	subdom_pass = new_password

	# get fullname
	fullname_user = full_name
	user_subdomain = subdomain

	if subdom_is_created == 0:
		lengkap = "{}.{}".format(subdom_name,setting.url)
		tidaklengkap = subdom_name
		enqueue("my_account.custom_dns_api.create_new_site_subprocess", newsitename=lengkap, sitesubdomain=tidaklengkap, subdomuser=subdom_user, subdompass=subdom_pass, fullname_user=fullname_user)

		return "success"

	return "subdomain already created"



@frappe.whitelist(allow_guest=True)
def create_new_user_buy_by_user():
	
	data = frappe.form_dict.get('data')
	data = json.loads(str(data))

	user = data["user"]
	subdomain = data["subdomain"]
	total = data["total"]
	new_user = data["new_user"]
	posting_date = data["posting_date"]
	
	for i in new_user :
		purchase_user = frappe.new_doc("Purchase User")
		purchase_user.posting_date = posting_date
		purchase_user.subdomain = subdomain
		purchase_user.enabled = 0
		purchase_user.fullname = i["fullname"]
		purchase_user.email = i["email"]
		purchase_user.current_password = i["new_password"]
		purchase_user.status = "Unpaid"
		purchase_user.price_list = i["price_list"]
		pls = frappe.get_doc("Price List", i["price_list"])
		purchase_user.days_active = pls.active_days

		# role
		purchase_user.account_manager = i["account_manager"]
		purchase_user.account_user = i["account_user"]
		purchase_user.purchase_manager = i["purchase_manager"]
		purchase_user.purchase_user = i["purchase_user"]
		purchase_user.sales_manager = i["sales_manager"]
		purchase_user.sales_user = i["sales_user"]
		purchase_user.stock_manager = i["stock_manager"]
		purchase_user.stock_user = i["stock_user"]
		purchase_user.manufacturing_manager = i["manufacturing_manager"]
		purchase_user.manufacturing_user = i["manufacturing_user"]
		purchase_user.hr_manager = i["hr_manager"]
		purchase_user.hr_user = i["hr_user"]

		purchase_user.flags.ignore_permissions = True
		purchase_user.save()

		frappe.db.sql(""" UPDATE `tabPurchase User` SET owner = "{0}", modified_by = "{1}" WHERE name = "{2}" """.format(user, user, user))
		
	# create invoice
	invoice = frappe.new_doc("Invoice")
	invoice.posting_date = posting_date
	invoice.subdomain = subdomain

	total_harga= 0 

	for i in new_user :
		ch = invoice.append('invoice_item', {})
		ch.description = i["email"]
		ch.price_list = i["price_list"]
		ch.price = i["price"]
		ch.type = "New User"
		
		total_harga = total_harga + i["price"]

	invoice.total = total_harga

	invoice.flags.ignore_permissions = True
	invoice.save()


	invoice2 = frappe.get_doc("Invoice", invoice.name)
	invoice2.petunjuk_pembayaran = """

		Petunjuk Pembayaran
		<br><br>
		Invoice {0}
		<br>
		Total : Rp. {1}
		<br>
		Berita : {0}
		<br><br>
		*Ketikkan berita di atas pada saat Anda melakukan pembayaran melalui ATM Non-Tunai, setoran Bank, atau Internet Banking
		Data Bank
		<br>
		<br>
		BANK BCA
		<br>
		No. Rek. 8630196150
		<br>
		a/n Bobby Hartanto Kurniawan
		<br><br>
		Jangan lupa konfirmasi

	""".format(invoice.name, invoice.total)

	invoice2.konfirmasi_pembayaran = """

		Segera lakukan konfirmasi setelah Anda melakukan pembayaran. Konfirmasi dapat dilakukan melalui email :
		<br><br>
		Kirimkan Email ke <b>ptglobalmediasolusindo@gmail.com</b> dengan format berikut :
		<br><br>
		BAYAR
		<br>
		INV : {0}
		<br>
		JML :
		<br> 
		BANK :
		<br> 
		ATAS NAMA :
		<br><br>

		*Mohon konfirmasi Email dilakukan di hari yang sama
		<br>
		Pembayaran yang tidak dikonfirmasikan tidak akan diproses!

		""".format(invoice.name)

	invoice2.flags.ignore_permissions = True
	invoice2.save()

	frappe.db.sql(""" UPDATE `tabInvoice` SET owner = "{0}", modified_by = "{1}" WHERE name = "{2}" """.format(user, user, invoice2.name))

	return  "success, check your invoice : "+str(invoice.name)



@frappe.whitelist(allow_guest=True)
def activate_new_user_buy_and_add_to_erp_after_payment():
	setting = frappe.get_single("Additional Settings")
	data = frappe.form_dict.get('data')
	data = json.loads(str(data))

	user = data["user"]
	subdomain = data["subdomain"]
	invoice = data["invoice"]
	
	# mengubah invoice menjadi paid

	data_invoice = frappe.get_doc("Invoice", invoice)
	data_invoice.status = "Paid"
	data_invoice.flags.ignore_permissions = True
	data_invoice.save()

	frappe.db.sql(""" UPDATE `tabInvoice` SET owner = "{0}", modified_by = "{1}" WHERE name = "{2}" """.format(user, user, data_invoice.name))

	# mengaktifkan user


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

			lengkap = "{}.{}".format(subdomain,setting.url)
			enqueue("my_account.custom_dns_api.create_new_user_on_erp_site", newsitename=lengkap, email=data_user.email, fullname=data_user.fullname, password=data_user.current_password)

			

	history_payment = frappe.new_doc("History Payment")
	history_payment.posting_date = utils.today()
	history_payment.subdomain =subdomain
	history_payment.invoice =invoice
	history_payment.paid_amount = data_invoice.total
	history_payment.note = ""
	history_payment.flags.ignore_permissions = True
	history_payment.save()

	frappe.db.sql(""" UPDATE `tabHistory Payment` SET owner = "{0}", modified_by = "{1}" WHERE name = "{2}" """.format(user, user, history_payment.name))

	return  "success"

def _get_user_for_update_password(key, old_password):
	# verify old password
	if key:
		user = frappe.db.get_value("User", {"reset_password_key": key})
		if not user:
			return {
				#'message': _("The Link specified has either been used before or Invalid")
				'message': _("Cannot Update: Incorrect / Expired Link.")
			}

	elif old_password:
		# verify old password
		frappe.local.login_manager.check_password(frappe.session.user, old_password)
		user = frappe.session.user

	else:
		return

	return {
		'user': user
	}