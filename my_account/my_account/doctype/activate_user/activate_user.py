# -*- coding: utf-8 -*-
# Copyright (c) 2018, GMS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import utils


import os
import requests
import json
import subprocess
from frappe.utils.background_jobs import enqueue



class ActivateUser(Document):
	
	def aktivasi_user(self):

		# validate
		if not self.subdomain :
			frappe.throw("Harus pilih subdomainnya terlebih dahulu !")

		if not self.invoice :
			frappe.throw("Harus pilih invoicenya terlebih dahulu !")

		if not self.keterangan_bypass :
			frappe.throw("Keterangan Bypass harus diisi !")


		# mengubah invoice menjadi paid

		data_invoice = frappe.get_doc("Invoice", self.invoice)
		data_invoice.status = "Paid"
		data_invoice.bypass = 1
		data_invoice.keterangan_bypass = self.keterangan_bypass
		data_invoice.flags.ignore_permissions = True
		data_invoice.save()

		# mengaktifkan user


		os.chdir("/home/frappe/frappe-bench")

		for i in data_invoice.invoice_item :
			if i.type == "New User" or i.type == "Perpanjangan User" :

				user = i.description
				price_list = frappe.get_doc("Price List", data_invoice.package_type)

				data_user = frappe.get_doc("Purchase User", user)
				data_user.enabled = 1
				data_user.status = "Paid"
				data_user.days_active = price_list.active_days
				data_user.flags.ignore_permissions = True
				data_user.save()

				lengkap = "{}.antusias.id".format(self.subdomain)
				enqueue("frappe.custom_dns_api.create_new_user_on_erp_site", newsitename=lengkap, email=data_user.email, fullname=data_user.fullname, password=data_user.current_password)


				

		# history_payment = frappe.new_doc("History Payment")
		# history_payment.posting_date = utils.today()
		# history_payment.subdomain = self.subdomain
		# history_payment.invoice = self.invoice
		# history_payment.paid_amount = data_invoice.total
		# history_payment.note = ""







@frappe.whitelist()
def create_user_baru(fullname_user, email, password):
	user = frappe.get_doc({
		"doctype":"User",
		"email" : email,
		"first_name" : fullname_user,

		"enabled" : 1,
		"send_welcome_email" : 0,
		"thread_notify" : 0,
		"new_password" : password,
		"block_modules" : [
			{"module" : "Agriculture"},
			{"module" : "BOM"},
			{"module" : "Chapter"},
			{"module" : "Contacts"},
			{"module" : "Core"},
			{"module" : "Course"},
			{"module" : "Course Schedule"},
			{"module" : "Crop"},
			{"module" : "Crop Cycle"},
			{"module" : "Desk"},
			{"module" : "Data Import Tool"},
			{"module" : "Disease"},
			{"module" : "Donor"},
			{"module" : "Education"},
			{"module" : "Email Inbox"},
			{"module" : "Fees"},
			{"module" : "Fertilizer"},
			{"module" : "File Manager"},
			{"module" : "Grant Application"},
			{"module" : "Healthcare"},
			{"module" : "Hub"},
			{"module" : "Instructor"},
			{"module" : "Integrations"},
			{"module" : "Issue"},
			{"module" : "Item"},
			{"module" : "Land Unit"},
			{"module" : "Lead"},
			{"module" : "Learn"},
			{"module" : "Maintenance"},
			{"module" : "Member"},
			{"module" : "Non Profit"},
			{"module" : "Plant Analysis"},
			{"module" : "Profit and Loss Statement"},
			{"module" : "Program"},
			{"module" : "Project"},
			{"module" : "Projects"},
			{"module" : "Production Order"},
			{"module" : "Restaurant"},
			{"module" : "Room"},
			{"module" : "Sales Order"},
			{"module" : "Setup"},
			{"module" : "Soil Analysis"},
			{"module" : "Soil Texture"},
			{"module" : "Student"},
			{"module" : "Student Applicant"},
			{"module" : "Student Attendance Tool"},
			{"module" : "Student Group"},
			{"module" : "Supplier"},
			{"module" : "Support"},
			{"module" : "Task"},
			{"module" : "ToDo"},
			{"module" : "Volunteer"},
			{"module" : "Water Analysis"},
			{"module" : "Weather"},
			{"module" : "Website"}
		],
		"roles" : [
			{"role" : "GMS Support Role"},
			{"role" : "System Manager"},
			{"role" : "Website Manager"},
			{"role" : "Accounts Manager"},
			{"role" : "Accounts User"},
			{"role" : "HR Manager"},
			{"role" : "HR User"},
			{"role" : "Manufacturing Manager"},
			{"role" : "Manufacturing User"},
			{"role" : "Purchase Manager"},
			{"role" : "Purchase User"},
			{"role" : "Sales Manager"},
			{"role" : "Sales User"},
			{"role" : "Stock Manager"},
			{"role" : "Stock User"},
			{"role" : "Sales Master Manager"},
			{"role" : "Purchase Master Manager"},
			
		],
	})
	user.flags.ignore_permissions = True
	user.insert()






		# if self.buy_new_user_item :
		# 	for i in self.buy_new_user_item :

		# 		if i.fullname and i.email and i.new_password and i.price :


		# 			email_user_terdaftar = ""
		# 			get_user = frappe.db.sql("""
		# 				SELECT pu.`name`, pu.`price_user` FROM `tabPurchase User` pu
		# 				WHERE pu.`name` = "{}"

		# 			""".format(i.email), as_list=1)

		# 			if get_user :
		# 				email_user_terdaftar = email_user_terdaftar + str(get_user[0][0])

		# 		else :
		# 			frappe.throw("Fullname, Email, Password dan Price List harus diisi !")


		# 	if email_user_terdaftar :
		# 		frappe.throw("User "+str(email_user_terdaftar)+" sudah terdaftar di dalam system")

		# 	else :
		# 		for i in self.buy_new_user_item :
		# 			purchase_user = frappe.new_doc("Purchase User")
		# 			purchase_user.posting_date = self.posting_date
		# 			purchase_user.subdomain = self.subdomain
		# 			purchase_user.enabled = 0
		# 			purchase_user.fullname = i.fullname
		# 			purchase_user.email = i.email
		# 			purchase_user.current_password = i.new_password
		# 			purchase_user.status = "Unpaid"
		# 			purchase_user.price_list = i.price_list

		# 			pls = frappe.get_doc("Price List", i.price_list)
		# 			purchase_user.days_active = pls.active_days


		# 			# role
		# 			purchase_user.account_manager = i.account_manager
		# 			purchase_user.account_user = i.account_user
		# 			purchase_user.purchase_manager = i.purchase_manager
		# 			purchase_user.purchase_user = i.purchase_user
		# 			purchase_user.sales_manager = i.sales_manager
		# 			purchase_user.sales_user = i.sales_user
		# 			purchase_user.stock_manager = i.stock_manager
		# 			purchase_user.stock_user = i.stock_user
		# 			purchase_user.manufacturing_manager = i.manufacturing_manager
		# 			purchase_user.manufacturing_user = i.manufacturing_user
		# 			purchase_user.hr_manager = i.hr_manager
		# 			purchase_user.hr_user = i.hr_user

		# 			purchase_user.flags.ignore_permissions = True
		# 			purchase_user.save()

		# 		# create invoice
		# 		invoice = frappe.new_doc("Invoice")
		# 		invoice.posting_date = self.posting_date
		# 		invoice.subdomain = self.subdomain

		# 		total_harga= 0 

		# 		for i in self.buy_new_user_item :
		# 			ch = invoice.append('invoice_item', {})
		# 			ch.description = i.email
		# 			ch.price_list = i.price_list
		# 			ch.price = i.price
					
		# 			total_harga = total_harga + i.price

		# 		invoice.total = total_harga

		# 		invoice.flags.ignore_permissions = True
		# 		invoice.save()


		# 		invoice2 = frappe.get_doc("Invoice", invoice.name)
		# 		invoice2.petunjuk_pembayaran = """

		# 			Petunjuk Pembayaran
		# 			<br><br>
		# 			Invoice {0}
		# 			<br>
		# 			Total : Rp. {1}
		# 			<br>
		# 			Berita : {0}
		# 			<br><br>
		# 			*Ketikkan berita di atas pada saat Anda melakukan pembayaran melalui ATM Non-Tunai, setoran Bank, atau Internet Banking
		# 			Data Bank
		# 			<br>
		# 			<br>
		# 			BCA KCP PTC
		# 			<br>
		# 			No. Rek. xxxxxxxxxx
		# 			<br>
		# 			a/n PT GMS
		# 			<br><br>
		# 			Jangan lupa konfirmasi

		# 		""".format(invoice.name, invoice.total)

		# 		invoice2.konfirmasi_pembayaran = """

		# 			Segera lakukan konfirmasi setelah Anda melakukan pembayaran. Konfirmasi dapat dilakukan melalui email :
		# 			<br><br>
		# 			Kirimkan Email ke <b>ptglobalmediasolusindo@gmail.com</b> dengan format berikut :
		# 			<br><br>
		# 			BAYAR
		# 			<br>
		# 			INV : {0}
		# 			<br>
		# 			JML :
		# 			<br> 
		# 			BANK :
		# 			<br> 
		# 			ATAS NAMA :
		# 			<br><br>

		# 			*Mohon konfirmasi Email dilakukan di hari yang sama
		# 			<br>
		# 			Pembayaran yang tidak dikonfirmasikan tidak akan diproses!

		# 			""".format(invoice.name)

		# 		invoice2.flags.ignore_permissions = True
		# 		invoice2.save()



		# 		frappe.msgprint(""" Invoice telah terbuat {0}, silahkan membayar untuk mengaktifkan user yang anda buat """.format(invoice.name))

		# else :
		# 	frappe.throw("Data User harus diisi terlebih dahulu")
