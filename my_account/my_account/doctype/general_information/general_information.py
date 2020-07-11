# -*- coding: utf-8 -*-
# Copyright (c) 2017, GMS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import utils
from frappe.model.document import Document

class GeneralInformation(Document):

	def check_availability_domain1(self):
		if not self.subdomain :
			frappe.throw("You must input subdomain first !")

		subdomain = self.subdomain


		# check special character
		symbol = "~`!@#$%^&*()-+={}[]:>;',</?*-+_" + '"'
		for i in subdomain:
			if i in symbol:
				self.hasil_check = "Cannot use any special character"
				frappe.throw("Cannot use any special character")


		# check availability
		check_available = frappe.db.sql("""
			SELECT
			gi.`name`,
			gi.`subdomain`
			FROM
			`tabGeneral Information` gi

			WHERE gi.`subdomain` = "{}"


		""".format(subdomain), as_list=1)

		if check_available :
			self.hasil_check = "Not Available"
			frappe.throw("Subdomain Not Available !")

		else :
			self.hasil_check = "Available"


	# def check_availability_domain(self):
	# 	frappe.throw('test')

	def validate(self):
		pass

	def on_submit(self):
		pass
		# self.create_purchase_module()
        #
		# # create user
		# self.create_purchase_user()


	def create_purchase_module(self):

		# create purchase module
		purchase_module = frappe.new_doc("Purchase Module")
		purchase_module.company_user = self.company_user
		purchase_module.posting_date = frappe.utils.today()

		master_module = frappe.db.sql("""
			SELECT
			mm.`module_name`,
			mm.`module_description`,
			mm.`module_price`
			FROM
			`tabMaster Module` mm

		""", as_list=1)

		purchase_module.purchase_module_item = []
		if master_module :
			for i in master_module :
				pmi = purchase_module.append('purchase_module_item', {})
				pmi.module_name = i[0]
				pmi.price_per_day = i[2]
				pmi.use_this_module = 0
				pmi.module_status = "Not Installed"

		purchase_module.flags.ignore_permissions = True
		purchase_module.save()


	def create_purchase_user(self):

		# create purchase module
		purchase_user = frappe.new_doc("Purchase User")
		purchase_user.company_user = self.company_user
		purchase_user.posting_date = frappe.utils.today()

		purchase_user.status = "Free"

		purchase_user.email = self.email_for_login

		purchase_user.flags.ignore_permissions = True
		purchase_user.save()



		# master_module = frappe.db.sql("""
		# 	SELECT
		# 	mm.`module_name`,
		# 	mm.`module_description`,
		# 	mm.`module_price`
		# 	FROM
		# 	`tabMaster Module` mm

		# """, as_list=1)

		# purchase_module.purchase_module_item = []
		# if master_module :
		# 	for i in master_module :
		# 		pmi = purchase_module.append('purchase_module_item', {})
		# 		pmi.module_name = i[0]
		# 		pmi.price_per_day = i[2]
		# 		pmi.use_this_module = 0
		# 		pmi.module_status = "Not Installed"






@frappe.whitelist()
def check_availability_domain(subdomain):
	# if not subdomain :
	# 	frappe.throw("You must input subdomain first !")

	# check special character
	symbol = "~`!@#$%^&*()-+={}[]:>;',</?*-+_" + '"'
	for i in subdomain:
		if i in symbol:
			return "Cannot use any special"

	# check availability
	check_available = frappe.db.sql("""
		SELECT
		gi.`name`,
		gi.`subdomain`
		FROM
		`tabGeneral Information` gi

		WHERE gi.`subdomain` = "{}"

	""".format(subdomain), as_list=1)

	if len(check_available) > 1 :
		return "Not Available"

	else :
		return "Available"
