from __future__ import unicode_literals
from frappe import _
import frappe

def get_data():
	user_login = frappe.session.user
	
	# purchasing user
	if "System Manager" in frappe.get_roles(frappe.session.user):
		return [
			{
				"label": _("Menu"),
				"items": [
					
					{
						"type": "doctype",
						"name": "Buy New User"
					},
					{
						"type": "doctype",
						"name": "Purchase User"
					},
					{
						"type": "doctype",
						"name": "Invoice"
					},
					{
						"type": "doctype",
						"name": "History Payment"
					},
					
					
					
				]
			},
			{
				"label": _("Setup"),
				"items": [
					{
						"type": "doctype",
						"name": "Master Subdomain"
					},
					{
						"type": "doctype",
						"name": "Price List"
					}
					# ,{
					# 	"type": "doctype",
					# 	"name": "Activate User"
					# },
					# {
					# 	"type": "doctype",
					# 	"name": "Setting Free User"
					# },
					# {
						# "type": "doctype",
						# "name": "Promo Code"
					# },
					
				]
			},
		]

	elif "My Account Role" in frappe.get_roles(frappe.session.user):
		return [
			{
				"label": _("Menu"),
				"items": [
					
					{
						"type": "doctype",
						"name": "Buy New User"
					},
					{
						"type": "doctype",
						"name": "Purchase User"
					},
					{
						"type": "doctype",
						"name": "Invoice"
					},
					{
						"type": "doctype",
						"name": "History Payment"
					},
					
				]
			},
		]

	else :
		return [
			{
				"label": _(""),
				"items": [
					
				]
			}
		]
		# frappe.throw("Please contact the Administrator to show your report list")