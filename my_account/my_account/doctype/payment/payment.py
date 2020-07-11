# -*- coding: utf-8 -*-
# Copyright (c) 2018, GMS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Payment(Document):	
	pass


@frappe.whitelist()
def get_unpaid_user(subdomain):
	
	# check availability
	get_user = frappe.db.sql("""
		SELECT pu.`name`, pu.`price_user` FROM `tabPurchase User` pu
		WHERE pu.`status` = "Unpaid"
		AND pu.`subdomain` = "{}"

	""".format(subdomain), as_list=1)

	return get_user



@frappe.whitelist()
def get_subdomain_user(user):
	
	# check availability
	get_user = frappe.db.sql("""
		SELECT pu.`subdomain` FROM `tabUser` pu
		WHERE pu.`name` = "{}"

	""".format(user), as_list=1)

	user_subdomain = get_user[0][0]

	return user_subdomain

