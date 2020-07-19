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
def rebuild_tree_error():
	rebuild_tree("Account", "parent_account")

@frappe.whitelist()
def api_call_create_dns(new_site_name):

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
	    'X-Auth-Email': "bobby@solubis.id",
	    # api key crativate / rectios : 7eb0d91566ac6409d1957961abac095ec405c
	    # antusias : 2a7fc7cab52ed7d244db75641d75ca8bf4b93
	    'X-Auth-Key': "2a7fc7cab52ed7d244db75641d75ca8bf4b93",
	    'Cache-Control': "no-cache",
	    'Postman-Token': "b8f18408-ab53-00b4-3931-90536b6d5371"
	    }

	response = requests.request("POST", url, data=json.dumps(payload), headers=headers)

	print(response.text)

	
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


	frappe.db.sql("""update `tabMaster Subdomain` set is_created = 1 where name = '{}' """.format(sitesubdomain))
	frappe.db.commit()
	os.chdir("/home/frappe/frappe-bench")
	os.system("sudo su frappe")
	os.system("bench new-site {} --db-name db_{} --mariadb-root-username root --mariadb-root-password majuterus234@ --admin-password majuterus234@ --install-app erpnext --install-app solubis_brand".format(new_site_name,site_sub_domain))
	
	#os.system("bench setup nginx --yes")
	#os.system("sudo service nginx reload")

	#os.system("bench --site {} execute solubis_brand.custom_function.disable_signup_website".format(new_site_name))
	#os.system("bench --site {} execute solubis_brand.custom_function.import_fixtures".format(new_site_name))
	#os.system(""" bench --site {} execute solubis_brand.custom_function.disable_other_roles --args "['{}']" """.format(plan))
	#os.system("""bench --site {} execute solubis_brand.custom_function.create_user_baru --args "['{}','{}','{}','{}']" 
	#	""".format(newsitename,fullname_user,subdomuser,subdompass,plan))


@frappe.whitelist(allow_guest=True)
def send_mail_site_created(subdomuser, fullname, newsitename):
	setting = frappe.get_single("Additional Settings")
	subject = "Welcome to {}".format(setting.url)
	args = {"full_name":fullname,"site_link":newsitename}
	frappe.sendmail(recipients=subdomuser, sender=setting.email_sender, subject=subject,
			template="site_created", header=[subject, "green"], args=args,delayed=False)
