# -*- coding: utf-8 -*-
# Copyright (c) 2015, erpx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from my_account.my_account.doctype.frappeclient import FrappeClient
import json
import os
import requests
import subprocess
from frappe.utils.background_jobs import enqueue
from frappe.utils import get_site_name

class SyncServerSettings(Document):
	pass


@frappe.whitelist()
def enqueue_sync():
	enqueue("my_account.my_account.doctype.sync_server_settings.sync_invoice_to_sales_invoice")


@frappe.whitelist()
def sync_invoice_to_sales_invoice():

	# nb yang perlu di ganti sesuai dengan site tujuannya, ku kasih comment perlu di ganti


	# perlu di ganti
	clientroot = FrappeClient("https://demo.antusias.id/", "Administrator", "D4s@tm21")
	

	# query invoice
	get_invoice = frappe.db.sql(""" 
		SELECT 
		i.`name`, 
		i.`subdomain`, 
		i.`total_user`, 
		i.`status`, 
		i.`posting_date`,
		i.`total`, 
		i.`discount`, 
		i.`total_after_discount`, 
		i.`tax_package`, 
		i.`grand_total`,
		ifnull(i.`sales_partner`,"")

		FROM `tabInvoice` i
		WHERE i.`status` = "Paid"
		AND i.`sync_domain` = 0
		AND i.`subdomain` IS NOT NULL

		ORDER BY i.`subdomain`, i.`posting_date`
	""", as_list=1)

	if get_invoice :

		for i in get_invoice :

			invoice_name = i[0]
			subdomain = i[1]
			total_user = i[2]
			posting_date = i[4]
			total = i[5]
			if i[6] < 0 :
				discount = i[6] * -1
			else :
				discount = i[6]
			total_after_discount = i[7]
			tax_package = i[8]
			grand_total = i[9]
			sales_partner = i[10]

			# cek customer
			customer_name = "subdomain-"+str(subdomain)
			customer_tujuan = clientroot.get_value("Customer", "name", {"name":customer_name})

			if customer_tujuan :
				count = 0
			else :
				# create customer
				doc_customer = {"doctype":"Customer"}
				doc_customer["customer_name"] = customer_name
				# perlu di ganti
				doc_customer["customer_type"] = "Individual"
				# perlu di ganti
				doc_customer["customer_group"] = "All Customer Groups"
				# perlu di ganti
				doc_customer["territory"] = "All Territories"
				clientroot.insert(doc_customer)


			# insert sales invoice
			doc_invoice = {
				"doctype":"Sales Invoice",
				"customer":customer_name,
				"company":"PT. Demo Antusias",
				"set_posting_time":"1",
				"posting_date":str(posting_date),
				"is_pos":"1",
				"update_stock":"0",
				"items":[{	
							"parenttype" : "Sales Invoice",
							"parentfield" : "items",
					    	"item_code": "Package User",
					    	"item_name": "Package User",
					    	"description": "Package User",
					    	"stock_uom": "User",
					    	"uom": "User",
					    	"conversion_factor": 1,
					    	"rate": str(int(total) / int(total_user)),
					    	"amount" : str(total),
					    	"qty" : str(total_user)
					    }],
				"apply_discount_on":"Net Total",
				"discount_amount":discount,
				"taxes":[{
							"parenttype" : "Sales Invoice",
							"parentfield" : "taxes",
					    	"charge_type": "On Net Total",
					    	"account_head": "2103.0100 - PPN Keluaran - PDA",
					    	"cost_center": "Main - PDA",
					    	"description": "PPN",
					    	"rate": 10
					    }],
				"payments":[{
								"parenttype" : "Sales Invoice",
								"parentfield" : "payments",		
						    	"default": 1,
						    	"mode_of_payment": "Cash",
						    	"amount": str(grand_total)
						    }],
				"sales_partner":sales_partner,
				"remarks":invoice_name

			}


			# doc_invoice["customer"] = customer_name
			# # perlu di ganti
			# doc_invoice["company"] = "PT. Demo Antusias"
			# doc_invoice["set_posting_time"] = "1"
			# doc_invoice["posting_date"] = posting_date
			# doc_invoice["is_pos"] = "1"
			# doc_invoice["update_stock"] = "0"


			# doc_invoice["items"] = [{
			# 					    	"item_code": "Package User",
			# 					    	"item_name": "Package User",
			# 					    	"description": "Package User",
			# 					    	"stock_uom": "User",
			# 					    	"uom": "User",
			# 					    	"conversion_factor": 1,
			# 					    	"rate": int(total) / int(total_user),
			# 					    	"amount" : int(total),
			# 					    	"qty" : int(total_user)
			# 					    }]
			# # doc_invoice["total"] = total
			# # doc_invoice["net_total"] = total
			# doc_invoice["apply_discount_on"] = "Net Total"
			# doc_invoice["discount_amount"] = discount
			# doc_invoice["taxes"] = [{
			# 					    	"charge_type": "On Net Total",
			# 					    	"account_head": "2103.0100 - PPN Keluaran - PDA",
			# 					    	"cost_center": "Main - PDA",
			# 					    	"description": "PPN",
			# 					    	"rate": 10
			# 					    }]
			# doc_invoice["payments"] = [{
										
			# 					    	"default": 1,
			# 					    	"mode_of_payment": "Cash",
			# 					    	"amount": int(grand_total)
			# 					    }]
			# doc_invoice["sales_partner"] = sales_partner
			# doc_invoice["remarks"] = invoice_name

			# frappe.throw(json.dumps( doc_invoice ))

			result = clientroot.insert(doc_invoice)

			sinv_doc = clientroot.get_doc("Sales Invoice", result["name"])
			clientroot.submit(sinv_doc)

			# frappe.throw(result["name"])


			frappe.db.sql(""" UPDATE `tabInvoice` SET sync_domain = 1 WHERE NAME = "{}" """.format(invoice_name))
			frappe.db.commit()


			

			



				



	