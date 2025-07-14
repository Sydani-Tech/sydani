import frappe
from frappe import _
import json
from sydani.payment import verify_hash, create_transaction_log


@frappe.whitelist(allow_guest=True)
def flutterwave_trasaction_confirmation():
    if frappe.request.method == "POST":
        request_hash = frappe.request.headers.get("verif-hash")
        varified = verify_hash("@Sydani_Payment_System", request_hash)
        if varified:
            data = frappe.request.data.decode("utf-8")
            transfer_data = json.loads(data)
            
            frappe.get_doc(
                {
                    "doctype": "Flutterwave Webhook",
                    "json_data": str(transfer_data),
                }
            ).save(ignore_permissions=True)

            try:
                transaction = frappe.db.sql(
                    f""" SELECT name FROM `tabFlutterwave Transaction` 
                                                WHERE transaction_id = '{transfer_data['data']['id']}' """,
                    as_dict=True)[0]

                status = transfer_data["data"]["status"]
                complete_message = transfer_data["data"]["complete_message"]
                failed_message = "DISBURSE FAILED"

                if transaction:
                    transaction_doc = frappe.get_doc(
                        "Flutterwave Transaction", transaction["name"]
                    )

                    transaction_doc.status = status
                    transaction_doc.acc_name = transfer_data["data"]["fullname"]
                    transaction_doc.transfer_reference = transfer_data["data"]["reference"]

                    if status == "FAILED":
                        transaction_doc.complete_message = complete_message
                        transaction_doc.message = failed_message
                    else:
                        transaction_doc.message = complete_message
                        transaction_doc.complete_message = "Successfully completed"

                    transaction_doc.save(ignore_permissions=True)

                    create_transaction_log(
                        data=transfer_data, doc=transaction_doc, type="flutterwave"
                    )

                else:
                    transaction = frappe.get_doc(
                        {
                            "doctype": "Flutterwave Transaction",
                            "transaction_id": transfer_data["data"]["id"],
                            "status": status,
                            "acc_no": transfer_data["data"]["account_number"],
                            "bank": transfer_data["data"]["bank_code"],
                            "bank_name": transfer_data["data"]["bank_name"],
                            "acc_name": transfer_data["data"]["fullname"],
                            "amount": transfer_data["data"]["amount"],
                            "narration": transfer_data["data"]["narration"],
                            "transfer_reference": transfer_data["data"]["reference"]
                            # "subaccount_reference": doc.flutterwave_sub_account_reference,
                        }
                    )

                    if status == "FAILED":
                        transaction.complete_message = complete_message
                        transaction.message = failed_message
                    else:
                        transaction.message = complete_message
                        transaction.complete_message = "Successfully completed"

                    trx_ref = transfer_data["data"]["reference"].split("_")
                    if len(trx_ref) > 2:
                        trx_doc_type = trx_ref[1]
                        trx_doc_id = trx_ref[2]
                        trx_debit_acc = trx_ref[3]

                        transaction.document_type = trx_doc_type
                        transaction.document_id = trx_doc_id
                        transaction.subaccount_reference = trx_debit_acc

                    transaction.save(ignore_permissions=True)

                    create_transaction_log(
                        data=transfer_data, doc=transaction, type="flutterwave"
                    )

            except Exception as e:
                pass
        return {"status": 200}
    return "No data"
