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
from frappe.frappeclient import FrappeClient
from frappe.core.doctype.data_import.data_import import import_doc, export_json

from frappe.utils.nestedset import rebuild_tree

# import paramiko

class custom_dns_api(Document):
	pass


@frappe.whitelist()
def halo():
	print("halo")

@frappe.whitelist()
def rebuild_tree_error():
	rebuild_tree("Account", "parent_account")


@frappe.whitelist()
def api_call_create_dns(new_site_name):

	# crativate
	# d4e84a186887da3dbd6e5e21ab2b0b39

	# rectios
	# zone id
	# 28eb32ddc9170235244354e6eae18988
	# 28eb32ddc9170235244354e6eae18988
	# antzman = 757307a566e97c7d08935340b281f925
	url = "https://api.cloudflare.com/client/v4/zones/757307a566e97c7d08935340b281f925/dns_records"

	# payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"type\"\r\n\r\nA\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"name\"\r\n\r\nnewsite.crativate.com\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"content\"\r\n\r\n35.197.133.195\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
	payload = {
		'type' : "A",
		'name' : new_site_name,
		'content': "139.162.21.199",
		'proxied' : True
	}
	headers = {
	    'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
	    'Content-Type': "application/json",
	    'X-Auth-Email': "bobby.hartanto@arlogy.co.id",
	    # api key crativate / rectios : 7eb0d91566ac6409d1957961abac095ec405c
	    # antusias : 2a7fc7cab52ed7d244db75641d75ca8bf4b93
	    'X-Auth-Key': "2a7fc7cab52ed7d244db75641d75ca8bf4b93",
	    'Cache-Control': "no-cache",
	    'Postman-Token': "b8f18408-ab53-00b4-3931-90536b6d5371"
	    }

	response = requests.request("POST", url, data=json.dumps(payload), headers=headers)

	print(response.text)

	# global api key dns
	# 7eb0d91566ac6409d1957961abac095ec405c

# @frappe.whitelist()
# def create_new_site_di_home():

# 	host="35.197.153.19"
# 	user="root"
# 	client = paramiko.SSHClient()
# 	k = paramiko.RSAKey.from_private_key_file('/home/frappe/frappe-bench/apps/frappe/frappe/id_frappe_rsa')
# 	# client.load_system_host_keys()
# 	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# 	client.connect(host, username=user,pkey = k)

# 	stdin, stdout, stderr = client.exec_command('cd /home/frappe/frappe-bench; bench execute erpnext.selling.custom_dns_api.create_new_site')
# 	# stdin, stdout, stderr = client.exec_command('ls')
# 	for line in stdout.readlines():
# 		print line
    #
	# client.close()
#added by bobby
@frappe.whitelist()
def create_new_user(newsitename,sitesubdomain, subdomuser, subdompass, fullname_user):
	os.chdir("/home/frappe/frappe-bench")
	os.system(""" bench --site {} execute my_account.custom_dns_api.create_user_baru --args "['{}','{}','{}']" """.format(newsitename,fullname_user,subdomuser,subdompass))
#end of add
@frappe.whitelist()
def create_new_site_subprocess(newsitename,sitesubdomain, subdomuser, fullname_user):
	os.chdir("/home/frappe/frappe-bench")
	print("create_new_site subprocess")
	new_site_name = newsitename
	site_sub_domain = sitesubdomain
	#api_call_create_dns(new_site_name)
	subdompass = frappe.db.get_value("Purchase User", subdomuser, 'current_password')
	plan = frappe.db.get_value("Master Subdomain",sitesubdomain,"active_plan")


	os.chdir("/home/frappe/frappe-bench")
	os.system("sudo su frappe")
	os.system("bench new-site {} --db-name db_{} --mariadb-root-username root --mariadb-root-password majuterus234@ --admin-password majuterus234@ --install-app erpnext --install-app solubis_brand".format(new_site_name,site_sub_domain))
	
	#os.system("bench setup nginx --yes")
	#os.system("sudo service nginx reload")

	os.system("bench --site {} execute my_account.custom_dns_api.disable_signup_website".format(new_site_name))
	#edited comment bobby
	os.system(""" bench --site {} execute my_account.custom_dns_api.create_user_baru --args "['{}','{}','{}','{}']" 
		""".format(newsitename,fullname_user,subdomuser,subdompass,plan))
	#end of line
	#os.system("bench --site {} migrate".format(new_site_name))

	# os.system("bench --site {} execute my_account.custom_dns_api.rebuild_tree_error".format(new_site_name))
	os.system("bench --site {} execute my_account.custom_fixtures.import_fixtures".format(new_site_name))

	# disable other roles except for purchased plan
	os.system(""" bench --site {} execute my_account.custom_dns_api.disable_other_roles --args "['{}']" """.format(plan))

	# sbd = frappe.get_doc("Master Subdomain", sitesubdomain)
	# sbd.is_created = 1
	# sbd.save(ignore_permissions=True)
	frappe.db.sql("""update `tabMaster Subdomain` set is_created = 1 where name = '{}' """.format(sitesubdomain))
	frappe.db.commit()
	enqueue("my_account.custom_dns_api.send_mail_site_created",subdomuser=subdomuser,fullname=fullname_user,newsitename=newsitename)
	# send_mail_site_created(subdomuser,fullname_user,newsitename)
	# domain = frappe.get_doc("Master Subdomain", site_sub_domain)
	# domain.is_created = 1
	# domain.flags.ignore_permissions = True
	# domain.save()
	# frappe.db.commit()


	# edited rico

	# subject = "Welcome to Solubis"
	# args = {"full_name":fullname_user,"site_url":newsitename}
	# frappe.sendmail(recipients=subdomuser, sender="info@solubis.id", subject=subject,
	# 		template="site_created", header=[subject, "green"], args=args,delayed=False)
@frappe.whitelist()
def disable_other_roles(plan):
	frappe.db.sql("update `tabRole` set disable = 1 where name not in ('Administrator','System Manager','Guest','{}') ".format(plan))
	frappe.db.commit()

@frappe.whitelist()
def send_mail_site_created(subdomuser, fullname, newsitename):
	setting = frappe.get_single("Additional Settings")
	subject = "Welcome to {}".format(setting.url)
	args = {"full_name":fullname,"site_link":newsitename}
	frappe.sendmail(recipients=subdomuser, sender=setting.email_sender, subject=subject,
			template="site_created", header=[subject, "green"], args=args,delayed=False)

@frappe.whitelist()
def inject_coa_australia_child():

	company_default = frappe.db.get_value("Global Defaults", None, "default_company")
	company = frappe.get_doc("Company", company_default)

	company_abbr = company.abbr

	# anak
	anak = ["1-1000 - Current Assets=Bank=1-1110=General Cheque Account 1=Asset=Balance Sheet",
		"1-1000 - Current Assets=Bank=1-1120=General Cheque Account 2=Asset=Balance Sheet",
		"1-1000 - Current Assets=Cash=1-1140=Petty Cash=Asset=Balance Sheet",
		"1-1000 - Current Assets=Bank=1-1150=Company Provision Account=Asset=Balance Sheet",
		"1-1000 - Current Assets=Bank=1-1160=Company Investment Account=Asset=Balance Sheet",
		"1-1000 - Current Assets=Cash=1-1180=Undeposited Funds=Asset=Balance Sheet",
		"1-1000 - Current Assets=Bank=1-1190=Electronic Clearing Account=Asset=Balance Sheet",
		"1-1000 - Current Assets=Cash=1-1200=Payroll Cheque Account=Asset=Balance Sheet",
		"1-1000 - Current Assets=Receivable=1-1310=Less Prov'n for Doubtful Debts=Asset=Balance Sheet",
		"1-1000 - Current Assets=Stock=1-1400=Inventory=Asset=Balance Sheet",
		"1-1000 - Current Assets=Expense Account=1-1500=Prepaid Insurance=Asset=Balance Sheet",
		"1-1000 - Current Assets=Expense Account=1-1600=Deposits with Suppliers=Asset=Balance Sheet",
		"1-1000 - Current Assets=Expense Account=1-1700=Trade Debtors=Asset=Balance Sheet",
		"1-1950 - Withholding Credits=Tidak Ada=1-1960=Voluntary Withholding Credits=Asset=Balance Sheet",
		"1-1950 - Withholding Credits=Tidak Ada=1-1970=ABN Withholding Credits=Asset=Balance Sheet",
		"1-2100 - Furniture & Fittings=Expense Account=1-2110=F&F-At Cost=Asset=Balance Sheet",
		"1-2100 - Furniture & Fittings=Accumulated Depreciation=1-2120=F&F-Accum Dep'n=Asset=Balance Sheet",
		"1-2200 - Plant $ Equipment=Expense Account=1-2210=P&E-At Cost=Asset=Balance Sheet",
		"1-2200 - Plant $ Equipment=Accumulated Depreciation=1-2220=P&E-Accum Dep'n=Asset=Balance Sheet",
		"1-2300 - Motor Vehicles=Expense Account=1-2310=MV-At Cost=Asset=Balance Sheet",
		"1-2300 - Motor Vehicles=Accumulated Depreciation=1-2320=MV-Accum Dep'n=Asset=Balance Sheet",
		"1-2400 - Computer Equipment=Expense Account=1-2410=Computer Equipment Original=Asset=Balance Sheet",
		"1-2400 - Computer Equipment=Accumulated Depreciation=1-2420=Computer Equipment Accum Dep'n=Asset=Balance Sheet",
		"2-0000 - Liabilities=Payable=2-2000=Trade Creditors=Liability=Balance Sheet",
		"2-0000 - Liabilities=Payable=2-2100=Bank Loans=Liability=Balance Sheet",
		"2-0000 - Liabilities=Payable=2-2110=Other Long Term Liabilities=Liability=Balance Sheet",
		"2-0000 - Liabilities=Payable=2-5000=Payroll Liabilities=Liability=Balance Sheet",
		"2-1000 - Current Liabilities=Payable=2-1600=Deposits Collected=Liability=Balance Sheet",
		"2-1100 - Credit Cards=Payable=2-1110=American Express=Liability=Balance Sheet",
		"2-1100 - Credit Cards=Payable=2-1120=Bank Card=Liability=Balance Sheet",
		"2-1100 - Credit Cards=Payable=2-1130=Master Card=Liability=Balance Sheet",
		"2-1100 - Credit Cards=Payable=2-1140=Visa Card=Liability=Balance Sheet",
		"2-1500 - Payroll Liabilities=Payable=2-1510=PAYG Withholdings Payable=Liability=Balance Sheet",
		"2-1500 - Payroll Liabilities=Payable=2-1520=Payroll Deductions Payable=Liability=Balance Sheet",
		"2-1500 - Payroll Liabilities=Payable=2-1530=Superannuation Payable=Liability=Balance Sheet",
		"2-1500 - Payroll Liabilities=Payable=2-1540=Union Fees Payable=Liability=Balance Sheet",
		"2-1500 - Payroll Liabilities=Payable=2-1550=Workers Compensation Payable=Liability=Balance Sheet",
		"2-3000 - GST Liabilites=Payable=2-3010=GST Collected=Liability=Balance Sheet",
		"2-3000 - GST Liabilites=Payable=2-3030=GST Paid=Liability=Balance Sheet",
		"2-3000 - GST Liabilites=Payable=2-3050=Sales Tax Payable=Liability=Balance Sheet",
		"2-3000 - GST Liabilites=Payable=2-3060=import Duty Payable=Liability=Balance Sheet",
		"2-3000 - GST Liabilites=Payable=2-3070=Voluntary Withholdings Payable=Liability=Balance Sheet",
		"2-3000 - GST Liabilites=Payable=2-3080=ABN Withholding Payable=Liability=Balance Sheet",
		"2-3000 - GST Liabilites=Payable=2-3090=Luxury Car Tax Payable=Liability=Balance Sheet",
		"3-0000 - Equity=Equity=3-8000=Retained Earnings=Equity=Balance Sheet",
		"3-0000 - Equity=Equity=3-9000=Current Earnings=Equity=Balance Sheet",
		"3-0000 - Equity=Equity=3-9999=Historical Balancing Account=Equity=Balance Sheet",
		"4-1000 - Sales Income=Income Account=4-1600=Sales - Other Equip=Income=Profit and Loss",
		"4-2000 - Service Income=Income Account=4-2200=Service - Other Income=Income=Profit and Loss",
		"4-5000 - Time Billing Income=Income Account=4-5100=Consultancy Income=Income=Profit and Loss",
		"4-5000 - Time Billing Income=Income Account=4-5400=KM Travelled=Income=Profit and Loss",
		"4-5000 - Time Billing Income=Income Account=4-5500=Photocopying Income=Income=Profit and Loss",
		"4-5000 - Time Billing Income=Income Account=4-5200=Travelling Time=Income=Profit and Loss",
		"4-5000 - Time Billing Income=Income Account=4-5300=Secretarial Income=Income=Profit and Loss",
		"5-0000 - Cost of Sales=Cost of Goods Sold=5-2100=Discount Given=Expense=Profit and Loss",
		"5-0000 - Cost of Sales=Cost of Goods Sold=5-2200=Inventory Adjustment=Expense=Profit and Loss",
		"5-0000 - Cost of Sales=Cost of Goods Sold=5-2300=Purchase Returns & Allowance=Expense=Profit and Loss",
		"5-1000 - Purchases=Cost of Goods Sold=5-1100=Equipment=Expense=Profit and Loss",
		"6-0000 - Expenses=Expense Account=6-5100=Wages & Salaries=Expense=Profit and Loss",
		"6-0000 - Expenses=Expense Account=6-5200=Employment Expenses=Expense=Profit and Loss",
		"6-1000 - General & Admin Expenses=Expense Account=6-1100=Accounting Fees=Expense=Profit and Loss",
		"6-1000 - General & Admin Expenses=Expense Account=6-1110=Advertising=Expense=Profit and Loss",
		"6-1000 - General & Admin Expenses=Expense Account=6-1120=Bad Debts=Expense=Profit and Loss",
		"6-1000 - General & Admin Expenses=Expense Account=6-1130=Bank Charges=Expense=Profit and Loss",
		"6-1000 - General & Admin Expenses=Expense Account=6-1140=Depreciation=Expense=Profit and Loss",
		"6-1000 - General & Admin Expenses=Expense Account=6-1150=Discounts Taken=Expense=Profit and Loss",
		"6-1000 - General & Admin Expenses=Expense Account=6-1160=Freight Paid=Expense=Profit and Loss",
		"6-1000 - General & Admin Expenses=Expense Account=6-1170=Late Fees Paid=Expense=Profit and Loss",
		"6-1000 - General & Admin Expenses=Expense Account=6-1180=Office Supplies=Expense=Profit and Loss",
		"6-1000 - General & Admin Expenses=Expense Account=6-1190=Other General Expenses=Expense=Profit and Loss",
		"6-1000 - General & Admin Expenses=Expense Account=6-1200=Subscriptions=Expense=Profit and Loss",
		"6-1000 - General & Admin Expenses=Expense Account=6-1210=Repair & Maintenance=Expense=Profit and Loss",
		"6-2000 - Operating Expenses=Expense Account=6-2100=Car Expenses=Expense=Profit and Loss",
		"6-2000 - Operating Expenses=Expense Account=6-2110=Cleaning=Expense=Profit and Loss",
		"6-2000 - Operating Expenses=Expense Account=6-2120=Electricity=Expense=Profit and Loss",
		"6-2000 - Operating Expenses=Expense Account=6-2130=Insurance=Expense=Profit and Loss",
		"6-2000 - Operating Expenses=Expense Account=6-2140=Ofice Rental=Expense=Profit and Loss",
		"6-2000 - Operating Expenses=Expense Account=6-2150=Other Operating Expenses=Expense=Profit and Loss",
		"6-2000 - Operating Expenses=Expense Account=6-2160=Photocopy=Expense=Profit and Loss",
		"6-2000 - Operating Expenses=Expense Account=6-2170=Postage=Expense=Profit and Loss",
		"6-2000 - Operating Expenses=Expense Account=6-2180=Printing=Expense=Profit and Loss",
		"6-2000 - Operating Expenses=Expense Account=6-2190=Telephone=Expense=Profit and Loss",
		"6-2000 - Operating Expenses=Expense Account=6-2200=Freight=Expense=Profit and Loss",
		"6-3000 - Payroll Expenses=Expense Account=6-3110=Other Employment Expenses=Expense=Profit and Loss",
		"6-3000 - Payroll Expenses=Expense Account=6-3120=Superannuation=Expense=Profit and Loss",
		"6-3000 - Payroll Expenses=Expense Account=6-3130=Penalties=Expense=Profit and Loss",
		"6-3000 - Payroll Expenses=Expense Account=6-3140=Sub-Contractors=Expense=Profit and Loss",
		"6-3000 - Payroll Expenses=Expense Account=6-3150=Workers Compensation=Expense=Profit and Loss",
		"8-0000 - Other Income=Income Account=8-1000=Interest Income=Income=Profit and Loss",
		"8-0000 - Other Income=Income Account=8-1110=Misc Income=Income=Profit and Loss",
		"9-0000 - Other Expenses=Expense Account=9-1000=Interest Expense=Expense=Profit and Loss",
		"9-0000 - Other Expenses=Expense Account=9-2000=Income Tax Payable=Expense=Profit and Loss",
		"9-0000 - Other Expenses=Expense Account=9-3000=Private Use=Expense=Profit and Loss",
	]
	for ap in anak :
		temp_as = ap.split("=")
		parent_account = str(temp_as[0]) + " - " + company_abbr
		account_name = str(temp_as[3])
		is_group = 0
		if str(temp_as[1]) == "Tidak Ada" :
			account_type = ""
		else :
			account_type = str(temp_as[1])
		root_type = str(temp_as[4])
		report_type = str(temp_as[5])
		account_number = str(temp_as[2])
		account = frappe.get_doc({"doctype": "Account","account_name": account_name,"company": company_default,"parent_account": parent_account,"is_group": is_group,"root_type": root_type,"report_type": report_type,"account_number": account_number,"account_type": account_type,"account_currency": frappe.db.get_value('Company',  company_default,  "default_currency")})
		account.flags.ignore_permissions = True
		account.insert()






# frappe.db.get_value(“Global Defaults”, None, “default_company”)
@frappe.whitelist()
def inject_coa_australia():

	company_default = frappe.db.get_value("Global Defaults", None, "default_company")
	company = frappe.get_doc("Company", company_default)

	company_abbr = company.abbr

	# # parent utama
	# "1-0000 - Asset"
	# "2-0000 - Liabilities"
	# "3-0000 - Equity"
	# "5-0000 - Cost of Sales"
	# "6-0000 - Expenses"
	# "8-0000 - Other Income"
	# "9-0000 - Other Expenses"

	# # other income
	# parent_account = ""
	# account_name = "Other Income"
	# is_group = 1
	# root_type = "Income"
	# report_type = "Profit and Loss"
	# account_number = "8-0000"

	# account = frappe.get_doc({"doctype": "Account","account_name": account_name,"company": company_default,"parent_account": parent_account,"is_group": is_group,"root_type": root_type,"report_type": report_type,"account_number": account_number,"account_type": "","account_currency": frappe.db.get_value('Company',  company_default,  "default_currency")})
	# account.flags.ignore_permissions = True
	# account.insert()

	# # other expense
	# parent_account = ""
	# account_name = "Other Expenses"
	# is_group = 1
	# root_type = "Expense"
	# report_type = "Profit and Loss"
	# account_number = "9-0000"

	# account = frappe.get_doc({"doctype": "Account","account_name": account_name,"company": company_default,"parent_account": parent_account,"is_group": is_group,"root_type": root_type,"report_type": report_type,"account_number": account_number,"account_type": "","account_currency": frappe.db.get_value('Company',  company_default,  "default_currency")})
	# account.flags.ignore_permissions = True
	# account.insert()

	# asset parent
	asset_parent = ["1-1000 - Current Assets","1-1950 - Withholding Credits","1-2100 - Furniture & Fittings","1-2200 - Plant $ Equipment","1-2300 - Motor Vehicles","1-2400 - Computer Equipment"]

	for ap in asset_parent :

		parent_account = "1-0000 - Asset" + " - " + company_abbr
		account_name = str(ap.split(" - ")[1])
		is_group = 1
		root_type = "Asset"
		report_type = "Balance Sheet"
		account_number = str(ap.split(" - ")[0])

		account = frappe.get_doc({"doctype": "Account","account_name": account_name,"company": company_default,"parent_account": parent_account,"is_group": is_group,"root_type": root_type,"report_type": report_type,"account_number": account_number,"account_type": "","account_currency": frappe.db.get_value('Company',  company_default,  "default_currency")})
		account.flags.ignore_permissions = True
		account.insert()

	# liability parent
	liability_parent = ["2-1000 - Current Liabilities", "2-1500 - Payroll Liabilities","2-3000 - GST Liabilites"]
	for ap in liability_parent :

		parent_account = "2-0000 - Liabilities" + " - " + company_abbr
		account_name = str(ap.split(" - ")[1])
		is_group = 1
		root_type = "Liability"
		report_type = "Balance Sheet"
		account_number = str(ap.split(" - ")[0])

		account = frappe.get_doc({"doctype": "Account","account_name": account_name,"company": company_default,"parent_account": parent_account,"is_group": is_group,"root_type": root_type,"report_type": report_type,"account_number": account_number,"account_type": "","account_currency": frappe.db.get_value('Company',  company_default,  "default_currency")})
		account.flags.ignore_permissions = True
		account.insert()

	liability_parent_2 = ["2-1100 - Credit Cards"]
	for ap in liability_parent_2 :

		parent_account = "2-1000 - Current Liabilities" + " - " + company_abbr
		account_name = str(ap.split(" - ")[1])
		is_group = 1
		root_type = "Liability"
		report_type = "Balance Sheet"
		account_number = str(ap.split(" - ")[0])

		account = frappe.get_doc({"doctype": "Account","account_name": account_name,"company": company_default,"parent_account": parent_account,"is_group": is_group,"root_type": root_type,"report_type": report_type,"account_number": account_number,"account_type": "","account_currency": frappe.db.get_value('Company',  company_default,  "default_currency")})
		account.flags.ignore_permissions = True
		account.insert()


	# equity parent
	# income parent

	income_parent = ["4-1000 - Sales Income","4-2000 - Service Income","4-5000 - Time Billing Income"]
	for ap in income_parent :

		parent_account = "4-0000 - Income" + " - " + company_abbr
		account_name = str(ap.split(" - ")[1])
		is_group = 1
		root_type = "Income"
		report_type = "Profit and Loss"
		account_number = str(ap.split(" - ")[0])

		account = frappe.get_doc({"doctype": "Account","account_name": account_name,"company": company_default,"parent_account": parent_account,"is_group": is_group,"root_type": root_type,"report_type": report_type,"account_number": account_number,"account_type": "","account_currency": frappe.db.get_value('Company',  company_default,  "default_currency")})
		account.flags.ignore_permissions = True
		account.insert()


	# expense parent

	cost_sales_parent = ["5-1000 - Purchases"]
	for ap in cost_sales_parent :

		parent_account = "5-0000 - Cost of Sales" + " - " + company_abbr
		account_name = str(ap.split(" - ")[1])
		is_group = 1
		root_type = "Expense"
		report_type = "Profit and Loss"
		account_number = str(ap.split(" - ")[0])

		account = frappe.get_doc({"doctype": "Account","account_name": account_name,"company": company_default,"parent_account": parent_account,"is_group": is_group,"root_type": root_type,"report_type": report_type,"account_number": account_number,"account_type": "","account_currency": frappe.db.get_value('Company',  company_default,  "default_currency")})
		account.flags.ignore_permissions = True
		account.insert()

	expense_parent = ["6-1000 - General & Admin Expenses","6-2000 - Operating Expenses","6-3000 - Payroll Expenses"]
	for ap in expense_parent :

		parent_account = "6-0000 - Expenses" + " - " + company_abbr
		account_name = str(ap.split(" - ")[1])
		is_group = 1
		root_type = "Expense"
		report_type = "Profit and Loss"
		account_number = str(ap.split(" - ")[0])

		account = frappe.get_doc({"doctype": "Account","account_name": account_name,"company": company_default,"parent_account": parent_account,"is_group": is_group,"root_type": root_type,"report_type": report_type,"account_number": account_number,"account_type": "","account_currency": frappe.db.get_value('Company',  company_default,  "default_currency")})
		account.flags.ignore_permissions = True
		account.insert()

	expense_parent_2 = ["6-3100 - Wages & Salaries"]
	for ap in expense_parent_2 :

		parent_account = "6-3000 - Payroll Expenses" + " - " + company_abbr
		account_name = str(ap.split(" - ")[1])
		is_group = 1
		root_type = "Expense"
		report_type = "Profit and Loss"
		account_number = str(ap.split(" - ")[0])

		account = frappe.get_doc({"doctype": "Account","account_name": account_name,"company": company_default,"parent_account": parent_account,"is_group": is_group,"root_type": root_type,"report_type": report_type,"account_number": account_number,"account_type": "","account_currency": frappe.db.get_value('Company',  company_default,  "default_currency")})
		account.flags.ignore_permissions = True
		account.insert()


	# other income parent
	# other expense parent

	# anak
	anak = ["1-1000 - Current Assets=Bank=1-1110=General Cheque Account 1=Asset=Balance Sheet",
		"1-1000 - Current Assets=Bank=1-1120=General Cheque Account 2=Asset=Balance Sheet",
		"1-1000 - Current Assets=Cash=1-1140=Petty Cash=Asset=Balance Sheet",
		"1-1000 - Current Assets=Bank=1-1150=Company Provision Account=Asset=Balance Sheet",
		"1-1000 - Current Assets=Bank=1-1160=Company Investment Account=Asset=Balance Sheet",
		"1-1000 - Current Assets=Cash=1-1180=Undeposited Funds=Asset=Balance Sheet",
		"1-1000 - Current Assets=Bank=1-1190=Electronic Clearing Account=Asset=Balance Sheet",
		"1-1000 - Current Assets=Cash=1-1200=Payroll Cheque Account=Asset=Balance Sheet",
		"1-1000 - Current Assets=Receivable=1-1310=Less Prov'n for Doubtful Debts=Asset=Balance Sheet",
		"1-1000 - Current Assets=Stock=1-1400=Inventory=Asset=Balance Sheet",
		"1-1000 - Current Assets=Expense Account=1-1500=Prepaid Insurance=Asset=Balance Sheet",
		"1-1000 - Current Assets=Expense Account=1-1600=Deposits with Suppliers=Asset=Balance Sheet",
		"1-1000 - Current Assets=Expense Account=1-1700=Trade Debtors=Asset=Balance Sheet",
		"1-1950 - Withholding Credits=Tidak Ada=1-1960=Voluntary Withholding Credits=Asset=Balance Sheet",
		"1-1950 - Withholding Credits=Tidak Ada=1-1970=ABN Withholding Credits=Asset=Balance Sheet",
		"1-2100 - Furniture & Fittings=Expense Account=1-2110=F&F-At Cost=Asset=Balance Sheet",
		"1-2100 - Furniture & Fittings=Accumulated Depreciation=1-2120=F&F-Accum Dep'n=Asset=Balance Sheet",
		"1-2200 - Plant $ Equipment=Expense Account=1-2210=P&E-At Cost=Asset=Balance Sheet",
		"1-2200 - Plant $ Equipment=Accumulated Depreciation=1-2220=P&E-Accum Dep'n=Asset=Balance Sheet",
		"1-2300 - Motor Vehicles=Expense Account=1-2310=MV-At Cost=Asset=Balance Sheet",
		"1-2300 - Motor Vehicles=Accumulated Depreciation=1-2320=MV-Accum Dep'n=Asset=Balance Sheet",
		"1-2400 - Computer Equipment=Expense Account=1-2410=Computer Equipment Original=Asset=Balance Sheet",
		"1-2400 - Computer Equipment=Accumulated Depreciation=1-2420=Computer Equipment Accum Dep'n=Asset=Balance Sheet",
		"2-0000 - Liabilities=Payable=2-2000=Trade Creditors=Liability=Balance Sheet",
		"2-0000 - Liabilities=Payable=2-2100=Bank Loans=Liability=Balance Sheet",
		"2-0000 - Liabilities=Payable=2-2110=Other Long Term Liabilities=Liability=Balance Sheet",
		"2-0000 - Liabilities=Payable=2-5000=Payroll Liabilities=Liability=Balance Sheet",
		"2-1000 - Current Liabilities=Payable=2-1600=Deposits Collected=Liability=Balance Sheet",
		"2-1100 - Credit Cards=Payable=2-1110=American Express=Liability=Balance Sheet",
		"2-1100 - Credit Cards=Payable=2-1120=Bank Card=Liability=Balance Sheet",
		"2-1100 - Credit Cards=Payable=2-1130=Master Card=Liability=Balance Sheet",
		"2-1100 - Credit Cards=Payable=2-1140=Visa Card=Liability=Balance Sheet",
		"2-1500 - Payroll Liabilities=Payable=2-1510=PAYG Withholdings Payable=Liability=Balance Sheet",
		"2-1500 - Payroll Liabilities=Payable=2-1520=Payroll Deductions Payable=Liability=Balance Sheet",
		"2-1500 - Payroll Liabilities=Payable=2-1530=Superannuation Payable=Liability=Balance Sheet",
		"2-1500 - Payroll Liabilities=Payable=2-1540=Union Fees Payable=Liability=Balance Sheet",
		"2-1500 - Payroll Liabilities=Payable=2-1550=Workers Compensation Payable=Liability=Balance Sheet",
		"2-3000 - GST Liabilites=Payable=2-3010=GST Collected=Liability=Balance Sheet",
		"2-3000 - GST Liabilites=Payable=2-3030=GST Paid=Liability=Balance Sheet",
		"2-3000 - GST Liabilites=Payable=2-3050=Sales Tax Payable=Liability=Balance Sheet",
		"2-3000 - GST Liabilites=Payable=2-3060=import Duty Payable=Liability=Balance Sheet",
		"2-3000 - GST Liabilites=Payable=2-3070=Voluntary Withholdings Payable=Liability=Balance Sheet",
		"2-3000 - GST Liabilites=Payable=2-3080=ABN Withholding Payable=Liability=Balance Sheet",
		"2-3000 - GST Liabilites=Payable=2-3090=Luxury Car Tax Payable=Liability=Balance Sheet",
		"3-0000 - Equity=Equity=3-8000=Retained Earnings=Equity=Balance Sheet",
		"3-0000 - Equity=Equity=3-9000=Current Earnings=Equity=Balance Sheet",
		"3-0000 - Equity=Equity=3-9999=Historical Balancing Account=Equity=Balance Sheet",
		"4-1000 - Sales Income=Income Account=4-1600=Sales - Other Equip=Income=Profit and Loss",
		"4-2000 - Service Income=Income Account=4-2200=Service - Other Income=Income=Profit and Loss",
		"4-5000 - Time Billing Income=Income Account=4-5100=Consultancy Income=Income=Profit and Loss",
		"4-5000 - Time Billing Income=Income Account=4-5400=KM Travelled=Income=Profit and Loss",
		"4-5000 - Time Billing Income=Income Account=4-5500=Photocopying Income=Income=Profit and Loss",
		"4-5000 - Time Billing Income=Income Account=4-5200=Travelling Time=Income=Profit and Loss",
		"4-5000 - Time Billing Income=Income Account=4-5300=Secretarial Income=Income=Profit and Loss",
		"5-0000 - Cost of Sales=Cost of Goods Sold=5-2100=Discount Given=Expense=Profit and Loss",
		"5-0000 - Cost of Sales=Cost of Goods Sold=5-2200=Inventory Adjustment=Expense=Profit and Loss",
		"5-0000 - Cost of Sales=Cost of Goods Sold=5-2300=Purchase Returns & Allowance=Expense=Profit and Loss",
		"5-1000 - Purchases=Cost of Goods Sold=5-1100=Equipment=Expense=Profit and Loss",
		"6-0000 - Expenses=Expense Account=6-5100=Wages & Salaries=Expense=Profit and Loss",
		"6-0000 - Expenses=Expense Account=6-5200=Employment Expenses=Expense=Profit and Loss",
		"6-1000 - General & Admin Expenses=Expense Account=6-1100=Accounting Fees=Expense=Profit and Loss",
		"6-1000 - General & Admin Expenses=Expense Account=6-1110=Advertising=Expense=Profit and Loss",
		"6-1000 - General & Admin Expenses=Expense Account=6-1120=Bad Debts=Expense=Profit and Loss",
		"6-1000 - General & Admin Expenses=Expense Account=6-1130=Bank Charges=Expense=Profit and Loss",
		"6-1000 - General & Admin Expenses=Expense Account=6-1140=Depreciation=Expense=Profit and Loss",
		"6-1000 - General & Admin Expenses=Expense Account=6-1150=Discounts Taken=Expense=Profit and Loss",
		"6-1000 - General & Admin Expenses=Expense Account=6-1160=Freight Paid=Expense=Profit and Loss",
		"6-1000 - General & Admin Expenses=Expense Account=6-1170=Late Fees Paid=Expense=Profit and Loss",
		"6-1000 - General & Admin Expenses=Expense Account=6-1180=Office Supplies=Expense=Profit and Loss",
		"6-1000 - General & Admin Expenses=Expense Account=6-1190=Other General Expenses=Expense=Profit and Loss",
		"6-1000 - General & Admin Expenses=Expense Account=6-1200=Subscriptions=Expense=Profit and Loss",
		"6-1000 - General & Admin Expenses=Expense Account=6-1210=Repair & Maintenance=Expense=Profit and Loss",
		"6-2000 - Operating Expenses=Expense Account=6-2100=Car Expenses=Expense=Profit and Loss",
		"6-2000 - Operating Expenses=Expense Account=6-2110=Cleaning=Expense=Profit and Loss",
		"6-2000 - Operating Expenses=Expense Account=6-2120=Electricity=Expense=Profit and Loss",
		"6-2000 - Operating Expenses=Expense Account=6-2130=Insurance=Expense=Profit and Loss",
		"6-2000 - Operating Expenses=Expense Account=6-2140=Ofice Rental=Expense=Profit and Loss",
		"6-2000 - Operating Expenses=Expense Account=6-2150=Other Operating Expenses=Expense=Profit and Loss",
		"6-2000 - Operating Expenses=Expense Account=6-2160=Photocopy=Expense=Profit and Loss",
		"6-2000 - Operating Expenses=Expense Account=6-2170=Postage=Expense=Profit and Loss",
		"6-2000 - Operating Expenses=Expense Account=6-2180=Printing=Expense=Profit and Loss",
		"6-2000 - Operating Expenses=Expense Account=6-2190=Telephone=Expense=Profit and Loss",
		"6-2000 - Operating Expenses=Expense Account=6-2200=Freight=Expense=Profit and Loss",
		"6-3000 - Payroll Expenses=Expense Account=6-3110=Other Employment Expenses=Expense=Profit and Loss",
		"6-3000 - Payroll Expenses=Expense Account=6-3120=Superannuation=Expense=Profit and Loss",
		"6-3000 - Payroll Expenses=Expense Account=6-3130=Penalties=Expense=Profit and Loss",
		"6-3000 - Payroll Expenses=Expense Account=6-3140=Sub-Contractors=Expense=Profit and Loss",
		"6-3000 - Payroll Expenses=Expense Account=6-3150=Workers Compensation=Expense=Profit and Loss",
		"8-0000 - Other Income=Income Account=8-1000=Interest Income=Income=Profit and Loss",
		"8-0000 - Other Income=Income Account=8-1110=Misc Income=Income=Profit and Loss",
		"9-0000 - Other Expenses=Expense Account=9-1000=Interest Expense=Expense=Profit and Loss",
		"9-0000 - Other Expenses=Expense Account=9-2000=Income Tax Payable=Expense=Profit and Loss",
		"9-0000 - Other Expenses=Expense Account=9-3000=Private Use=Expense=Profit and Loss",
	]
	for ap in anak :
		temp_as = ap.split("=")
		parent_account = str(temp_as[0]) + " - " + company_abbr
		account_name = str(temp_as[3])
		is_group = 0
		if str(temp_as[1]) == "Tidak Ada" :
			account_type = ""
		else :
			account_type = str(temp_as[1])
		root_type = str(temp_as[4])
		report_type = str(temp_as[5])
		account_number = str(temp_as[2])
		account = frappe.get_doc({"doctype": "Account","account_name": account_name,"company": company_default,"parent_account": parent_account,"is_group": is_group,"root_type": root_type,"report_type": report_type,"account_number": account_number,"account_type": account_type,"account_currency": frappe.db.get_value('Company',  company_default,  "default_currency")})
		account.flags.ignore_permissions = True
		account.insert()



@frappe.whitelist()
def disable_signup_website():
	# role_baru = frappe.get_doc({
	# 	"doctype":"Role",
	# 	"role_name": "BiSetup Wizard"
	# })
	# role_baru.flags.ignore_permissions = True
	# role_baru.insert()

	ws = frappe.get_single("Website Settings")
	ws.disable_signup = 1
	ws.top_bar_items = []
	ws.flags.ignore_permissions = True
	ws.save()


	# frappe.db.sql(""" UPDATE `tabSingles` s
	# 	SET s.`value` = "1"
	# 	WHERE s.`doctype` = "Website Settings"
	# 	AND s.`field` = "disable_signup" """)
	# frappe.db.commit()


@frappe.whitelist()
def create_system_user():


	user = frappe.get_doc({
		"doctype":"User",
		"name" : "Administrator",
		"email" : "admin@example.com",
		"first_name" : "Administrator",
		"enabled" : 1,
		"is_admin" : 1,
		"send_welcome_email" : 0,
		"thread_notify" : 0,
		"new_password" : "BlueSky12321",
		"block_modules" : [
		],
		"roles" : [

			{"role" : "Administrator"},

		],
	})
	user.flags.ignore_permissions = True
	user.insert()

	user = frappe.get_doc({
		"doctype":"User",
		"email" : "guest@example.com",
		"first_name" : "Guest",
		"enabled" : 1,
		"is_guest" : 1,
		"send_welcome_email" : 0,
		"thread_notify" : 0,
		"new_password" : "BlueSky12321",
		"block_modules" : [
		],
		"roles" : [
			{"role" : "Guest"},
		],
	})
	user.flags.ignore_permissions = True
	user.insert()

	# user = frappe.get_doc({
	# 	"doctype":"User",
	# 	"email" : "ptglobalmediasolusindo@gmail.com",
	# 	"first_name" : "PT GMS",
	# 	"enabled" : 1,
	# 	"send_welcome_email" : 0,
	# 	"thread_notify" : 0,
	# 	"new_password" : "BlueSky12321",
	# 	"block_modules" : [
	# 	],
	# 	"roles" : [
	# 		{"role" : "Accounts Manager"},
	# 		{"role" : "Accounts User"},
	# 		{"role" : "HR Manager"},
	# 		{"role" : "HR User"},
	# 		{"role" : "Manufacturing Manager"},
	# 		{"role" : "Manufacturing User"},
	# 		{"role" : "Purchase Manager"},
	# 		{"role" : "Purchase User"},
	# 		{"role" : "Sales Manager"},
	# 		{"role" : "Sales User"},
	# 		{"role" : "Stock Manager"},
	# 		{"role" : "Stock User"},
	# 		{"role" : "Bisa Setup Wizard"},
	# 		{"role" : "System Manager"},
	# 		{"role" : "Website Manager"},
	# 		{"role" : "Administrator"},
	# 		{"role" : "GMS Support Role"}
	# 	],
	# })
	# user.flags.ignore_permissions = True
	# user.insert()

@frappe.whitelist()
def create_role_baru_dan_system_user_baru():
	# insert role baru

	role_baru2 = frappe.get_doc({
		"doctype":"Role",
		"role_name": "GMS Support Role"
	})
	role_baru2.flags.ignore_permissions = True
	role_baru2.insert()

	# insert new permission
	# frappe.db.sql(""" UPDATE `tabHas Role` hr
	# 	SET hr.`role` = "Bisa Setup Wizard"
	# 	WHERE hr.`parent` = "setup-wizard"
	# 	AND hr.`parenttype` = "Page" """)
	# frappe.db.commit()
	# page_wizard = frappe.get_doc("Page", "setup-wizard")
	# page_wizard.roles = [{"role" : "System Manager"},{"role" : "Bisa Setup Wizard"}]
	# page_wizard.flags.ignore_permissions = True
	# page_wizard.save()

@frappe.whitelist()
def create_user_baru(fullname_user, email, password,plan):
	# custom andy System Manager user selain administrator
	setting = frappe.get_single("Additional Settings")
	user = frappe.get_doc({
		"doctype":"User",
		"email" : setting.email_sender,
		"first_name" : setting.url,
		"last_name" :"contact",

		"enabled" : 1,
		"send_welcome_email" : 0,
		"thread_notify" : 0,
		"new_password" : "Majuterus234@",
		"block_modules" : [
			
		],
		"roles" : [
			{"role" : "System Manager"},
			# {"role" : "Website Manager"},
			# {"role" : "Accounts Manager"},
			# {"role" : "Accounts User"},
			# {"role" : "HR Manager"},
			# {"role" : "HR User"},
			# {"role" : "Item Manager"},
			# {"role" : "Manufacturing Manager"},
			# {"role" : "Manufacturing User"},
			# {"role" : "Purchase Manager"},
			# {"role" : "Purchase User"},
			# {"role" : "Projects User"},
			# {"role" : "Projects Manager"},
			# {"role" : "Sales Manager"},
			# {"role" : "Sales User"},
			# {"role" : "Stock Manager"},
			# {"role" : "Stock User"},
			# {"role" : "Sales Master Manager"},
			# {"role" : "Report Manager"},
			# {"role" : "All"},
			# {"role" : "Purchase Master Manager"}
		],
	})
	user.flags.ignore_permissions = True
	user.insert()

	user = frappe.get_doc({
		"doctype":"User",
		"email" : email,
		"first_name" : fullname_user,

		"enabled" : 1,
		"send_welcome_email" : 0,
		"thread_notify" : 0,
		"new_password" : password,
		"block_modules" : [
			
		],
		"roles" : [
			{"role":plan}
			# {"role" : "System Manager"},
			# {"role" : "Website Manager"},
			# {"role" : "Accounts Manager"},
			# {"role" : "Accounts User"},
			# {"role" : "HR Manager"},
			# {"role" : "HR User"},
			# {"role" : "Item Manager"},
			# {"role" : "Manufacturing Manager"},
			# {"role" : "Manufacturing User"},
			# {"role" : "Purchase Manager"},
			# {"role" : "Purchase User"},
			# {"role" : "Projects User"},
			# {"role" : "Projects Manager"},
			# {"role" : "Sales Manager"},
			# {"role" : "Sales User"},
			# {"role" : "Stock Manager"},
			# {"role" : "Stock User"},
			# {"role" : "Sales Master Manager"},
			# {"role" : "Report Manager"},
			# {"role" : "All"},
			# {"role" : "Purchase Master Manager"}
		],
	})
	user.flags.ignore_permissions = True
	user.insert()

# edited rico
@frappe.whitelist()
def create_new_user_on_erp_site(newsitename, email, fullname, password):
	os.chdir("/home/frappe/frappe-bench")
	new_site_name = newsitename

	os.system(""" bench --site {} execute my_account.custom_dns_api.create_user_baru_1 --args "['{}','{}','{}']" """.format(newsitename,fullname,email,password))

@frappe.whitelist()
def create_user_baru_1(fullname_user, email, password):
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
			# {"role" : "GMS Support Role"},
			{"role" : "System Manager"},
			{"role" : "Website Manager"},
			{"role" : "Accounts Manager"},
			{"role" : "Accounts User"},
			{"role" : "HR Manager"},
			{"role" : "HR User"},
			{"role" : "Item Manager"},
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


	# edited rico

	# subject = "Welcome to Crativate"
	# frappe.sendmail(recipients=domain.user, sender="noreply.crativate@gmail.com", subject=subject,
	# 		template="test", header=[subject, "green"])
@frappe.whitelist()
def set_dekstop_icon_default_untuk_site():

	user_login = "evi_ceniago85@yahoo.com"

	frappe.db.sql(""" DELETE FROM `tabDesktop Icon` WHERE OWNER = "{0}" """.format(user_login))
	frappe.db.commit()

	# # # accounts
	desktop_icon = frappe.get_doc({
		'doctype': 'Desktop Icon',
		'idx': 1,
		'standard': 0,
		'app': "erpnext",
		'owner': user_login,
		'module_name' : "Accounts",
		'icon' : "octicon octicon-repo",
		'reverse' : 0,
		'type' : "module",
		'hidden' : 0,
		'custom' : 0,
		'blocked' : 0,
		'label' : "Accounts",
		'color' : "#3498db"
	})
	desktop_icon.save()

	# buying
	desktop_icon = frappe.get_doc({
		'doctype': 'Desktop Icon',
		'idx': 2,
		'standard': 0,
		'app': "erpnext",
		'owner': user_login,
		'module_name' : "Buying",
		'icon' : "fa fa-shopping-cart",
		'reverse' : 0,
		'type' : "module",
		'hidden' : 0,
		'custom' : 0,
		'blocked' : 0,
		'label' : "Buying",
		'color' : "#c0392b"
	})
	desktop_icon.save()

	# selling
	desktop_icon = frappe.get_doc({
		'doctype': 'Desktop Icon',
		'idx': 3,
		'standard': 0,
		'app': "erpnext",
		'owner': user_login,
		'module_name' : "Selling",
		'icon' : "octicon octicon-tag",
		'reverse' : 0,
		'type' : "module",
		'hidden' : 0,
		'custom' : 0,
		'blocked' : 0,
		'label' : "Selling",
		'color' : "#1abc9c"
	})
	desktop_icon.save()

	# stock
	desktop_icon = frappe.get_doc({
		'doctype': 'Desktop Icon',
		'idx': 4,
		'standard': 0,
		'app': "erpnext",
		'owner': user_login,
		'module_name' : "Stock",
		'icon' : "octicon octicon-package",
		'reverse' : 0,
		'type' : "module",
		'hidden' : 0,
		'custom' : 0,
		'blocked' : 0,
		'label' : "Stock",
		'color' : "#f39c12"
	})
	desktop_icon.save()


	# hr
	desktop_icon = frappe.get_doc({
		'doctype': 'Desktop Icon',
		'idx': 5,
		'standard': 0,
		'app': "erpnext",
		'owner': user_login,
		'module_name' : "HR",
		'icon' : "octicon octicon-organization",
		'reverse' : 0,
		'type' : "module",
		'hidden' : 0,
		'custom' : 0,
		'blocked' : 0,
		'label' : "Human Resources",
		'color' : "#2ecc71"
	})
	desktop_icon.save()



	# assets
	desktop_icon = frappe.get_doc({
		'doctype': 'Desktop Icon',
		'idx': 7,
		'standard': 0,
		'app': "erpnext",
		'owner': user_login,
		'module_name' : "Assets",
		'icon' : "octicon octicon-database",
		'reverse' : 0,
		'type' : "module",
		'hidden' : 0,
		'custom' : 0,
		'blocked' : 0,
		'label' : "Assets",
		'color' : "#4286f4"
	})
	desktop_icon.save()

	#
	# desktop_icon = frappe.get_doc({
	# 	'doctype': 'Desktop Icon',
	# 	'idx': 8,
	# 	'standard': 0,
	# 	'app': "erpnext",
	# 	'owner': user_login,
	# 	'module_name' : "GMS Support",
	# 	'icon' : "octicon octicon-comment-discussion",
	# 	'reverse' : 0,
	# 	'type' : "module",
	# 	'hidden' : 0,
	# 	'custom' : 0,
	# 	'blocked' : 0,
	# 	'label' : "GMS Support",
	# 	'color' : "#7f8c8d"
	# })
	# desktop_icon.save()

	# pos
	desktop_icon = frappe.get_doc({
		'doctype': 'Desktop Icon',
		'idx': 8,
		'standard': 0,
		'app': "erpnext",
		'link': "pos",
		'owner': user_login,
		'module_name' : "POS",
		'icon' : "octicon octicon-credit-card",
		'reverse' : 0,
		'type' : "page",
		'hidden' : 0,
		'custom' : 0,
		'blocked' : 0,
		'label' : "POS",
		'color' : "#589494"
	})
	desktop_icon.save()

	frappe.cache().hdel('desktop_icons', user_login)
	frappe.cache().hdel('bootinfo', user_login)




@frappe.whitelist()
def create_new_site_manual():

	newsitename = "example.antusias.id"
	sitesubdomain = "example"
	subdomuser = "suprayoto.riconova@gmail.com"
	subdompass = "asd123"
	fullname_user = "example"

	os.chdir("/home/frappe/frappe-bench")
	new_site_name = newsitename
	site_sub_domain = sitesubdomain
	#api_call_create_dns(new_site_name)

	os.chdir("/home/frappe/frappe-bench")
	os.system("sudo su frappe")
	os.system("bench new-site {} --db-name db_{} --mariadb-root-username root --mariadb-root-password rahasiakita --admin-password @tm286 --install-app erpnext".format(new_site_name,site_sub_domain))
	# os.system("bench --site {} install-app gms_support".format(new_site_name))
	# os.system("bench --site {} install-app styling".format(new_site_name))

	os.system("bench setup nginx --yes")
	os.system("sudo service nginx reload")

	os.system("bench --site {} execute my_account.custom_dns_api.disable_signup_website".format(new_site_name))
	# os.system("bench --site {} execute my_account.custom_dns_api.create_role_baru_dan_system_user_baru".format(new_site_name))
	# os.system("bench --site {} execute my_account.custom_dns_api.create_system_user".format(new_site_name))
	os.system(""" bench --site {} execute my_account.custom_dns_api.create_user_baru --args "['{}','{}','{}']" """.format(newsitename,fullname_user,subdomuser,subdompass))





@frappe.whitelist()
def create_user_baru_manual():

	user = frappe.get_doc({
		"doctype":"User",
		"email" : "felix.lasarus@abelgroup.com",
		"first_name" : "felix",
		"enabled" : 1,
		"send_welcome_email" : 0,
		"thread_notify" : 0,
		"new_password" : "Rahasiakit@123",
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
			# {"role" : "GMS Support Role"},
			{"role" : "System Manager"},
			{"role" : "Website Manager"},
			{"role" : "Accounts Manager"},
			{"role" : "Accounts User"},
			{"role" : "HR Manager"},
			{"role" : "HR User"},
			{"role" : "Item Manager"},
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
	user.save()

	# user = frappe.get_doc({
	# 	"doctype":"User",
	# 	"email" : "cs@antusias.id",
	# 	"first_name" : "Administrator",

	# 	"enabled" : 1,
	# 	"send_welcome_email" : 0,
	# 	"thread_notify" : 0,
	# 	"new_password" : "asd123",
	# 	"block_modules" : [
	# 	],
	# 	"roles" : [
	# 		# {"role" : "GMS Support Role"},
	# 		{"role" : "System Manager"}

	# 	],
	# })
	# user.flags.ignore_permissions = True
	# user.save()




# custom buat API DMJ

@frappe.whitelist()
def get_customer_primary_contact(customer):
	customer = customer
	return frappe.db.sql("""
		select `tabContact`.name from `tabContact`, `tabDynamic Link`
			where `tabContact`.name = `tabDynamic Link`.parent and `tabDynamic Link`.link_name = %(customer)s
			and `tabDynamic Link`.link_doctype = 'Customer' and `tabContact`.is_primary_contact = 1
			
		""", {
			'customer': customer
		})


@frappe.whitelist()
def get_customer_primary_address(customer):
	customer = customer
	return frappe.db.sql("""
		select `tabAddress`.name from `tabAddress`, `tabDynamic Link`
			where `tabAddress`.name = `tabDynamic Link`.parent and `tabDynamic Link`.link_name = %(customer)s
			and `tabDynamic Link`.link_doctype = 'Customer' and `tabAddress`.is_primary_address = 1
			
		""", {
			'customer': customer
		})


@frappe.whitelist()
def get_customer_shipping_address(customer):
	customer = customer
	return frappe.db.sql("""
		select `tabAddress`.name from `tabAddress`, `tabDynamic Link`
			where `tabAddress`.name = `tabDynamic Link`.parent and `tabDynamic Link`.link_name = %(customer)s
			and `tabDynamic Link`.link_doctype = 'Customer' and `tabAddress`.is_shipping_address = 1
			
		""", {
			'customer': customer
		})

@frappe.whitelist()
def setup_solubis_fixtures():
	import_doc(frappe.get_app_path("my_account", "fixtures", "property_setter.json"), ignore_links=False, overwrite=True)
	import_doc(frappe.get_app_path("my_account", "fixtures", "custom_docperm.json"), ignore_links=False, overwrite=True)
	import_doc(frappe.get_app_path("my_account", "fixtures", "role.json"), ignore_links=False, overwrite=True)