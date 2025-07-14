# Copyright (c) 2023, ekomobong and contributors
# For license information, please see license.txt

import frappe
from sydani.payment import flutterwave_create_sub_account
from frappe.model.document import Document

class FlutterwaveSubaccount(Document):

	def on_update(self):
		doc = self
		
		if doc.status is None or doc.status == '':
			acc = flutterwave_create_sub_account(acc_name=doc.account_name, email=doc.email, phone=doc.phone_number)
			frappe.msgprint(str(acc))
			if acc['status'] == 'success':

				doc.status = acc['data']['status']
				doc.account_reference = acc['data']['account_reference']
				doc.account_id = acc['data']['id']
				doc.country = acc['data']['country']
				doc.account_number = acc['data']['nuban']
				doc.bank_name = acc['data']['bank_name']
				doc.bank_code = acc['data']['bank_code']
				doc.barter_id = acc['data']['barter_id']

				doc.save()

