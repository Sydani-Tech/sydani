# Copyright (c) 2023, ekomobong and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import hooks
from sydani.payment import flutterwave_transfer, create_transaction_log


class FlutterwaveTransaction(Document):
    def on_update(self):
        doc = self
        if (doc.status == "" or doc.status == None) and (
            doc.transaction_id == "" or doc.transaction_id == None
        ):
            pay = flutterwave_transfer(
                acc_no=doc.acc_no,
                bank=doc.bank,
                amount=doc.amount,
                debit_acc=doc.subaccount_reference,
                narration=doc.narration,
            )

            if pay["status"] == "success":
                doc.status = pay["status"].upper()
                doc.message = pay["message"]
                doc.transaction_id = pay["data"]["id"]
                create_transaction_log(data=pay, doc=doc, type="flutterwave")
                doc.save()
