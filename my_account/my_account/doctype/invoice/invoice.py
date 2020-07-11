# -*- coding: utf-8 -*-
# Copyright (c) 2017, GMS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

from frappe import utils

class Invoice(Document):

	def validate(self):

		asd = 0
		count = 0
		if self.random_code :
			asd = 0
		else :
			# hitung jumlah user
			count = 0

			for i in self.invoice_item :
				if i.type not in ['Add Quota',"Add Subdomain"]:
					count = count + 1
				else:
					count = self.total_user

			self.total_user = count

			# generate random code
			if self.posting_date :
				new_combination = self.name + str(self.posting_date)
			else :
				new_combination = self.name

			new_random_code = hash(new_combination)
			self.random_code = new_random_code


	def use_promo(self):

		if self.promo_code :

			ambil_type_promo = frappe.get_value("Promo Code", {"promo_name":self.promo_code}, "promo_type")

			if ambil_type_promo :

				ambil_data_promo = frappe.get_doc("Promo Code", self.promo_code)
				promo_status = ambil_data_promo.status
				valid_until = ambil_data_promo.valid_until

				# frappe.throw("Ini today = "+str(utils.today())+" Ini valid until = "+str(valid_until))

				if promo_status == "Disabled" :
					frappe.throw("Please input valid promo")

				if frappe.utils.formatdate(utils.today(), 'dd-MM-YYYY') >= frappe.utils.formatdate(valid_until, 'dd-MM-YYYY') :
					frappe.throw("Please input valid promo")


				discount = 0
				discount_rate = 0

				self.sales_partner = frappe.get_value("Promo Code", {"promo_name":self.promo_code}, "sales_partner")
				self.keterangan_promo = frappe.get_value("Promo Code", {"promo_name":self.promo_code}, "keterangan_promo")

				if ambil_type_promo == "Discount" :
					discount = frappe.get_doc("Promo Code", self.promo_code).discount

					nominal_discount = self.total * discount / 100
					self.discount = nominal_discount * -1
					self.total_after_discount = self.total - nominal_discount

					self.tax_package = self.total_after_discount * 10 / 100

					grand_total = self.total_after_discount + self.tax_package
					
					self.grand_total = grand_total


				elif ambil_type_promo == "Nominal" :
					discount_rate = frappe.get_doc("Promo Code", self.promo_code).nominal

					self.discount = discount_rate * -1

					self.total_after_discount = self.total - discount_rate

					self.tax_package = self.total_after_discount * 10 / 100

					grand_total = self.total_after_discount + self.tax_package
					
					self.grand_total = grand_total



				self.flags.ignore_permissions = True
				self.save()


			else :
				frappe.throw("Please input valid promo")

		else :
			frappe.throw("You must input the promo code first")

	
	