# -*- coding: utf-8 -*-
# Copyright (c) 2018, GMS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class BuyNewUser(Document):

	def coba_coba_tombol(self):

		if self.buy_new_user_item :
			for i in self.buy_new_user_item :

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
				for i in self.buy_new_user_item :
					purchase_user = frappe.new_doc("Purchase User")
					purchase_user.posting_date = self.posting_date
					purchase_user.subdomain = self.subdomain
					purchase_user.enabled = 0
					purchase_user.fullname = i.fullname
					purchase_user.email = i.email
					purchase_user.current_password = i.new_password
					purchase_user.status = "Unpaid"
					purchase_user.price_list = i.price_list

					pls = frappe.get_doc("Price List", i.price_list)
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
				invoice.posting_date = self.posting_date
				invoice.subdomain = self.subdomain

				total_harga= 0 

				for i in self.buy_new_user_item :
					ch = invoice.append('invoice_item', {})
					ch.description = i.email
					ch.price_list = i.price_list
					ch.price = i.price
					ch.type = "New User"
					
					total_harga = total_harga + i.price

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
				invoice2.save()



				frappe.msgprint(""" Invoice telah terbuat {0}, silahkan membayar untuk mengaktifkan user yang anda buat """.format(invoice.name))

				self.buy_new_user_item = []
				self.total = 0

		else :
			frappe.throw("Data User harus diisi terlebih dahulu")

	
	# def coba_coba_tombol(self):

	# 	if self.buy_new_user_item :
	# 		for i in self.buy_new_user_item :

	# 			if i.fullname and i.email and i.new_password and i.price :


	# 				email_user_terdaftar = ""
	# 				get_user = frappe.db.sql("""
	# 					SELECT pu.`name`, pu.`price_user` FROM `tabPurchase User` pu
	# 					WHERE pu.`name` = "{}"

	# 				""".format(i.email), as_list=1)

	# 				if get_user :
	# 					email_user_terdaftar = email_user_terdaftar + str(get_user[0][0])

	# 			else :
	# 				frappe.throw("Fullname, Email, Password dan Price harus diisi !")


	# 		if email_user_terdaftar :
	# 			frappe.throw("User "+str(email_user_terdaftar)+" sudah terdaftar di dalam system")

	# 		else :
	# 			for i in self.buy_new_user_item :
	# 				purchase_user = frappe.new_doc("Purchase User")
	# 				purchase_user.posting_date = self.posting_date
	# 				purchase_user.subdomain = self.subdomain
	# 				purchase_user.enabled = 0
	# 				purchase_user.fullname = i.fullname
	# 				purchase_user.email = i.email
	# 				purchase_user.current_password = i.new_password
	# 				purchase_user.status = "Unpaid"

	# 				if i.price == "7 Hari Aktif / Rp 70.000" :
	# 					purchase_user.days_active = 7
	# 				elif i.price == "30 Hari Aktif / Rp 250.000" :
	# 					purchase_user.days_active = 30

	# 				purchase_user.price_user = i.price

	# 				# role
	# 				purchase_user.account_manager = i.account_manager
	# 				purchase_user.account_user = i.account_user
	# 				purchase_user.purchase_manager = i.purchase_manager
	# 				purchase_user.purchase_user = i.purchase_user
	# 				purchase_user.sales_manager = i.sales_manager
	# 				purchase_user.sales_user = i.sales_user
	# 				purchase_user.stock_manager = i.stock_manager
	# 				purchase_user.stock_user = i.stock_user
	# 				purchase_user.manufacturing_manager = i.manufacturing_manager
	# 				purchase_user.manufacturing_user = i.manufacturing_user
	# 				purchase_user.hr_manager = i.hr_manager
	# 				purchase_user.hr_user = i.hr_user

	# 				purchase_user.flags.ignore_permissions = True
	# 				purchase_user.save()



	# 			# create invoice
	# 			invoice = frappe.new_doc("Invoice")
	# 			invoice.posting_date = self.posting_date
	# 			invoice.subdomain = self.subdomain

	# 			total_harga= 0 

	# 			for i in self.buy_new_user_item :
	# 				ch = invoice.append('invoice_item', {})
	# 				ch.description = i.email
	# 				if i.price == "7 Hari Aktif / Rp 70.000" :
	# 					ch.price = 70000
	# 					total_harga = total_harga + 70000
	# 				elif i.price == "30 Hari Aktif / Rp 250.000" :
	# 					ch.price = 250000
	# 					total_harga = total_harga + 250000

	# 			invoice.total = total_harga
	# 			invoice.flags.ignore_permissions = True
	# 			invoice.save()


	# 			frappe.msgprint("Invoice telah terbuat, silahkan membayar untuk mengaktifkan user yang anda buat")




	# 	else :
	# 		frappe.throw("Data User harus diisi terlebih dahulu")


# @frappe.whitelist()
# def buy_now(self):
	
# 	# checking
# 	if doc.buy_new_user_item :
# 		for i in doc.buy_new_user_item :

# 			if i.fullname and i.email and i.password and i.price :


# 				email_user_terdaftar = ""
# 				get_user = frappe.db.sql("""
# 					SELECT pu.`name`, pu.`price_user` FROM `tabPurchase User` pu
# 					WHERE pu.`name` = "{}"

# 				""".format(i.email), as_list=1)

# 				if get_user :
# 					email_user_terdaftar = email_user_terdaftar + str(get_user[0][0])

# 			else :
# 				frappe.throw("Fullname, Email, Password dan Price harus diisi !")


# 		if email_user_terdaftar :
# 			frappe.throw("User "+str(email_user_terdaftar)+" sudah terdaftar di dalam system")

# 		else :
# 			for i in doc.buy_new_user_item :
# 				purchase_user = frappe.new_doc("Purchase User")
# 				purchase_user.posting_date = doc.posting_date
# 				purchase_user.subdomain = doc.subdomain
# 				purchase_user.enabled = 0
# 				purchase_user.fullname = i.fullname
# 				purchase_user.email = i.email
# 				purchase_user.current_password = i.new_password
# 				purchase_user.status = "Unpaid"

# 				if i.price == "7 Hari Aktif / Rp 70.000" :
# 					purchase_user.days_active = 7
# 				elif i.price == "30 Hari Aktif / Rp 250.000" :
# 					purchase_user.days_active = 30

# 				purchase_user.price_user = i.price

# 				# role
# 				purchase_user.account_manager = i.account_manager
# 				purchase_user.account_user = i.account_user
# 				purchase_user.purchase_manager = i.purchase_manager
# 				purchase_user.purchase_user = i.purchase_user
# 				purchase_user.sales_manager = i.sales_manager
# 				purchase_user.sales_user = i.sales_user
# 				purchase_user.stock_manager = i.stock_manager
# 				purchase_user.stock_user = i.stock_user
# 				purchase_user.manufacturing_manager = i.manufacturing_manager
# 				purchase_user.manufacturing_user = i.manufacturing_user
# 				purchase_user.hr_manager = i.hr_manager
# 				purchase_user.hr_user = i.hr_user

# 				purchase_user.flags.ignore_permissions = True
# 				purchase_user.save()



# 			# create invoice
# 			invoice = frappe.new_doc("Invoice")
# 			invoice.posting_date = doc.posting_date
# 			invoice.subdomain = doc.subdomain

# 			total_harga= 0 

# 			for i in doc.buy_new_user_item :
# 				ch = invoice.append('invoice_item', {})
# 				ch.description = i.email
# 				if i.price == "7 Hari Aktif / Rp 70.000" :
# 					ch.price = 70000
# 					total_harga = total_harga + 70000
# 				elif i.price == "30 Hari Aktif / Rp 250.000" :
# 					ch.price = 250000
# 					total_harga = total_harga + 250000

# 			invoice.total = total_harga
# 			invoice.flags.ignore_permissions = True
# 			invoice.save()


# 			return "success"




# 	else :
# 		frappe.throw("Data User harus diisi terlebih dahulu")

# 	return "failed"