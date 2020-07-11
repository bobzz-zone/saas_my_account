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


class custom_method(Document):
	pass



@frappe.whitelist(allow_guest=True)
def ding():
	return "dong"


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