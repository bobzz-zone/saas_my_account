# -*- coding: utf-8 -*-
# Copyright (c) 2018, GMS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.model.document import Document
from frappe.utils import strip, cint, today
from frappe.utils.background_jobs import enqueue
from frappe import _
import subprocess
import os
from frappe import utils

class BuyNewUser(Document):

	def coba_coba_tombol(self):

		if not self.type_package :
			frappe.throw("Choose your package first")

		if not self.buy_new_user_package :
			frappe.throw("Input your User first")

		user_qty = frappe.get_doc("Price List", self.type_package).user_qty
		days_active = frappe.get_doc("Price List", self.type_package).active_days

		count = 0
		for i in self.buy_new_user_package :
			count += 1

		if count < user_qty or count > user_qty :
			frappe.throw("Total User you must be input is "+str(user_qty))

		for i in self.buy_new_user_item :
			if i.fullname and i.email and i.new_password :
				email_user_terdaftar = ""

				get_user = frappe.db.sql("""
					SELECT pu.`name`, pu.`price_user` FROM `tabPurchase User` pu
					WHERE pu.`name` = "{}"

				""".format(i.email), as_list=1)

				if get_user :
					email_user_terdaftar = email_user_terdaftar + ", " + str(get_user[0][0])

			else :
				frappe.throw("Fullname, Email and Password are required")


		if email_user_terdaftar :
			frappe.throw(str(email_user_terdaftar)+" already registered")

		else :
			for i in self.buy_new_user_item :

				# create purchased user
				purchase_user = frappe.new_doc("Purchase User")
				purchase_user.posting_date = self.posting_date
				purchase_user.subdomain = self.subdomain
				purchase_user.enabled = 0
				purchase_user.fullname = i.fullname
				purchase_user.email = i.email
				purchase_user.current_password = i.new_password
				purchase_user.status = "Unpaid"
				purchase_user.price_list = self.type_package
				purchase_user.days_active = days_active

				purchase_user.flags.ignore_permissions = True
				purchase_user.save()

			# create invoice
			invoice = frappe.new_doc("Invoice")
			invoice.posting_date = self.posting_date
			invoice.subdomain = self.subdomain
			invoice.package_type = self.type_package
			 
			total_user = 0
			for i in self.buy_new_user_package :
				ch = invoice.append('invoice_item', {})
				ch.description = i.email
				ch.fullname = i.fullname
				ch.type = "New User"
				
				total_user = total_user + 1


			invoice.total_user = total_user
			invoice.total = self.net_total_package
			invoice.tax_package = self.tax_package
			invoice.discount = 0
			invoice.grand_total = self.grand_total_package
			invoice.flags.ignore_permissions = True
			invoice.save()


			invoice2 = frappe.get_doc("Invoice", invoice.name)
			if invoice2.posting_date :
				new_combination = invoice2.name + str(invoice2.posting_date)
			else :
				new_combination = invoice2.name

			new_random_code = hash(new_combination)
			invoice2.random_code = new_random_code
			
			invoice2.flags.ignore_permissions = True
			invoice2.save()


			# info invoice created
			frappe.msgprint(""" Invoice {0} created, Please pay your invoice to activate your User """.format(invoice.name))


			# reset page
			self.type_package = ""
			self.net_total_package = 0
			self.tax_package = 0
			self.grand_total_package = 0
			self.buy_new_user_package = []
			

@frappe.whitelist(allow_guest=True)
def buy_user(posting_date, subdomain, new_users):

	# validate field fullname, email, dan password harus terisi dan memastikan tidak ada di purchase user
	# jika belum terdaftar membuat Purchase User untuk setiap row
	# generate Invoice 

	# convert json into frappe._dict
	# frappe.throw(new_users)
	new_users = json.loads(new_users)
	order_users = []

	for user in new_users:
		order_users.append(frappe._dict(user))

	# return order_users
	
	if order_users :
		for i in order_users :
			if i.fullname and i.email and i.new_password and i.price :

				email_user_terdaftar = ""
				get_user = frappe.db.sql("""
					SELECT pu.`name`, pu.`price_user` FROM `tabPurchase User` pu
					WHERE pu.`name` = "{}"

				""".format(i.email), as_list=1)

				if get_user :
					email_user_terdaftar = email_user_terdaftar + str(get_user[0][0])

			else :
				frappe.throw("Fullname, Email, Password dan Price List harus diisi !")


		if email_user_terdaftar :
			frappe.throw("User "+str(email_user_terdaftar)+" sudah terdaftar di dalam system")

		else :
			for i in order_users :
				purchase_user = frappe.new_doc("Purchase User")
				purchase_user.posting_date = posting_date
				purchase_user.subdomain = subdomain
				purchase_user.enabled = 0
				purchase_user.fullname = i.fullname
				purchase_user.email = i.email
				purchase_user.current_password = i.new_password
				purchase_user.status = "Unpaid"
				purchase_user.price_list = i.price_list['price_list']
				# purchase_user.price_list = i.price_list

				pls = frappe.get_doc("Price List", i.price_list['price_list'])
				# pls = frappe.get_doc("Price List", i.price_list)
				purchase_user.days_active = pls.active_days


				# role
				purchase_user.account_manager = i.account_manager
				purchase_user.account_user = i.account_user
				purchase_user.purchase_manager = i.purchase_manager
				purchase_user.purchase_user = i.purchase_user
				purchase_user.sales_manager = i.sales_manager
				purchase_user.sales_user = i.sales_user
				purchase_user.stock_manager = i.stock_manager
				purchase_user.stock_user = i.stock_user
				purchase_user.manufacturing_manager = i.manufacturing_manager
				purchase_user.manufacturing_user = i.manufacturing_user
				purchase_user.hr_manager = i.hr_manager
				purchase_user.hr_user = i.hr_user

				purchase_user.flags.ignore_permissions = True
				purchase_user.save()

			# create invoice
			invoice = frappe.new_doc("Invoice")
			invoice.posting_date = posting_date
			invoice.subdomain = subdomain
			invoice.fullname = frappe.db.get_value("User", frappe.session.user, "full_name")

			total_harga= 0 
			total_user = 0

			for i in order_users :
				ch = invoice.append('invoice_item', {})
				ch.description = i.email
				ch.fullname = i.fullname
				# multiple pricelist
				ch.price_list = i.price_list['price_list']
				ch.price_list_rate = float(i.price_list['discount_price'])
				ch.price = float(i.price_list['discount_price'])
				total_harga = total_harga + float(i.price_list['discount_price'])

				# ch.price_list = i.price_list
				# ch.price_list_rate = float(i.price)
				# ch.price = float(i.price)
				# total_harga = total_harga + float(i.price)
				
				ch.type = "New User"
				
				total_user = total_user + 1

			invoice.total = total_harga
			invoice.total_user = total_user

			invoice.flags.ignore_permissions = True
			invoice.save()
			frappe.db.commit()


			invoice2 = frappe.get_doc("Invoice", invoice.name)
			if invoice2.posting_date :
				new_combination = invoice2.name + str(invoice2.posting_date)
			else :
				new_combination = invoice2.name

			new_random_code = hash(new_combination)
			invoice2.random_code = new_random_code
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
				BCA KCP PTC
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
			desc = """ Invoice telah terbuat {0} untuk subdomain {1} atas nama {2} """.format(invoice.name, invoice.subdomain, invoice.owner)
			invoice2.desc=desc
			invoice2.save()

			# untuk xendit
			return create_xendit_invoice(invoice.name,desc)


	else :
		frappe.throw("Data User harus diisi terlebih dahulu")

@frappe.whitelist(allow_guest=True)
def create_xendit_invoice(invoice=None, desc=None,redirect_to=None):
	if invoice:
		_invoice = frappe.get_doc("Invoice",invoice)
	else:
		return "Invoice not found"
	setting = frappe.get_single("Additional Settings")
	# desc = "coba aja z"
	# secret_key = "xnd_production_qXyMROfECQOTStkkyEVg1xTLfpsc5rty2MSUHJVla1jyAZbZoG97tOod9qSXl:"
	#secret_key = "xnd_development_SmS5uOy95uoosiId9BaTSPmQbqM8AaAQQMMwlSsg7LtgUEIslleo8MbWov97Gye:"
	external_id = """ external_id="{}" """.format(_invoice.name)
	payer_email = """ payer_email="{}" """.format(_invoice.owner)
	amount = """ amount={}""".format(_invoice.total)
	description = """ description="{}" """.format(desc)
	if not redirect_to:
		redirect_to="{}dashboard".format(setting.billing_url)
	success_redirect = """ success_redirect_url="{}" """.format(redirect_to)

	response = subprocess.check_output("""curl https://api.xendit.co/v2/invoices -X POST -u {} -d {} -d {} -d {} -d {} -d {}
			""".format(setting.xendit, external_id, payer_email, description, amount,success_redirect),shell=True, universal_newlines=True)

	result = json.loads(response)

	if "invoice_url" in result:
		_invoice.xendit_url = result['invoice_url']
		_invoice.xendit_code = result['id']
		_invoice.save(ignore_permissions=True)
		#frappe.db.commit()

		return _invoice.xendit_url
	else:
		frappe.throw("""Error {}""".format(result))

@frappe.whitelist(allow_guest=True)
def invoice_paid(**data):
	print(data['status'])
	print(data['merchant_name'])
	if data['status'] == "PAID" and data['merchant_name'] == 'PT Digital Asia Solusindo':

		# os.chdir("/home/frappe/frappe-bench")
		# os.system("""bench --site reg.solubis.id execute my_account.my_account.doctype.custom_api_payment.payment_success_with_payment_gateway --args '["{}"]' """.format(data['external_id']))
		note_payment = "Xendit"
		# mengubah invoice menjadi paid
		data_invoice = frappe.get_doc("Invoice", data['external_id'])
		data_invoice.status = "Paid"
		data_invoice.paid_date = today()
		data_invoice.status_payment = "Success"
		data_invoice.flags.ignore_permissions = True
		data_invoice.save()
		# mengaktifkan user

		_subdomain = frappe.get_doc("Master Subdomain", data_invoice.subdomain)


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
					os.chdir("/home/frappe/frappe-bench")
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
				os.chdir("/home/frappe/frappe-bench")
				enqueue("my_account.custom_dns_api.create_new_site_subprocess", newsitename=lengkap, sitesubdomain=subdom_name, subdomuser=_subdomain.user,  fullname_user=full_name)
			if i.type == "Add Module":
				print("Add Module")
				mods = i.fullname.split(",")
				for x in mods:
					_subdomain.append("active_modules",{"module":x})

			if i.type == "Perpanjangan":
				_subdomain.disable_if_not_pay = 0
				_subdomain.on_trial = 0
				_subdomain.block=0

		_subdomain.save(ignore_permissions=True)

		history_payment = frappe.new_doc("History Payment")
		history_payment.posting_date = utils.today()
		history_payment.subdomain = data_invoice.subdomain
		history_payment.invoice = data['external_id']
		history_payment.paid_amount = data_invoice.grand_total
		history_payment.note = note_payment
		history_payment.flags.ignore_permissions = True
		history_payment.save()
		return "Successful"

	if data['status'] == "EXPIRED":
		frappe.db.sql("UPDATE `tabInvoice` set status = 'Expired' where name = '{}' ".format(data['external_id']))
		frappe.db.commit()

		return "Successful"
		
@frappe.whitelist(allow_guest=True)
def receipt_mail(invoice):
	subdomain = frappe.db.get_value("Invoice", invoice, 'subdomain')
	template = frappe.get_doc("Receipt Template", subdomain)
	
	sender = 'no-reply@antzman.com'
	subject = "Solubis Invoice Paid Receipt number {}".format(invoice)
	inv = frappe.get_doc("Invoice", invoice)

	context = {"doc": inv, "invoice_no": inv.name,"invoice_amount":inv.total, "invoice_paid_date": inv.paid_date, "full_name": template.full_name}
	message = frappe.render_template(template.email_body, context)

	recipients = []
	for new_user in inv.invoice_item:
		recipients.append(new_user.description)
	recipients.append(template.full_name)

	# for trial
	# recipients = ["macflamerz@gmail.com","helper.ptdas@gmail.com"]

	frappe.sendmail(recipients=recipients, sender=sender, subject=subject, message=message, args=None, header=[subject, "green"],
			delayed=True, retry=3)
	# print(temp)

@frappe.whitelist(allow_guest=True)
def fetch_data_subdomain(subdomain):
	user = frappe.db.get_value("Master Subdomain", subdomain, 'user')
	full_name = frappe.db.get_value("User", user, 'full_name')
	return user, full_name