import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, add_days, getdate, add_to_date, now
from datetime import date, timedelta, datetime
import requests
from rave_python import Rave
import uuid
import hashlib

tester = frappe.conf.dev_tester
flutter_wave_public_key = frappe.conf.flutter_wave_public_key
flutter_wave_secret_key = frappe.conf.flutter_wave_secret_key
flutter_wave_production_secret_key = frappe.conf.flutter_wave_production_secret_key
flutter_wave_encryption_key = frappe.conf.flutter_wave_encryption_key

rave = Rave(
    flutter_wave_public_key, flutter_wave_secret_key, usingEnv=False, production=False
)
# rave = Rave('FLWPUBK_TEST-57ca0e624762234ac133621354da1d2b-X', 'FLWSECK_TEST-280eae5fd4503a54421e2401ce186bff-X', usingEnv=False, production=False)

paystack_base_url = "https://api.paystack.co/"
flutterwave_base_url = "https://api.flutterwave.com/v3/"
content_type = "application/json"

# flutter_wave_production_public_key

# flutter_wave_production_encryption_key

flutterwave_headers = {
    "Authorization": flutter_wave_production_secret_key,
    "Content-Type": content_type,
}

paystack_headers = {
    "Authorization": "Bearer sk_test_95a5dbf54e6f0242bbcc4f2abbe69f754aca25d8",
    "Content-Type": content_type,
}


# sk_test_caf864689258c5f0794c0343485816aa43f14291


def generate_uuid():
    uid = uuid.uuid4()
    return str(uid)


def generate_hash(secret_data):
    # create the hash object
    hash_object = hashlib.sha256()
    # update the hash object with the secret data
    hash_object.update(secret_data.encode())
    # get the hexadecimal representation of the hash
    secret_hash = hash_object.hexdigest()
    return secret_hash


def verify_hash(secret_data, stored_hash):
    # create the hash object and update with the secret data
    hash_object = hashlib.sha256()
    hash_object.update(secret_data.encode())
    # get the hexadecimal representation of the hash
    computed_hash = hash_object.hexdigest()
    # compare the stored hash with the computed hash
    if stored_hash == computed_hash:
        return 1
    else:
        return 0


def paystack_list_of_banks():
    url = f"{paystack_base_url}bank?country=nigeria&currency=NGN"
    response = requests.get(url, headers=paystack_headers)
    response = response.json()
    no = 1
    for bank in response["data"]:
        new_bank = frappe.get_doc(
            {
                "doctype": "Paystack Nigerian Banks",
                "bank_name": bank["name"],
                "slug": bank["slug"],
                "code": bank["code"],
                "long_code": bank["longcode"],
                "type": bank["type"],
                "gateway": bank["gateway"],
                "pay_with_bank": bank["pay_with_bank"],
                "active": bank["active"],
                "currency": bank["currency"],
            }
        )
        print(bank)
        new_bank.save()
        # print('.')
        no += 1


def paystack_create_recipient(name, bank, acc_no):
    url = f"{paystack_base_url}transferrecipient"
    get_bank = frappe.get_doc("Paystack Nigerian Banks", bank)
    if get_bank:
        data = {
            "type": "nuban",
            "name": name,
            "account_number": acc_no,
            "bank_code": get_bank.code,
            "currency": "NGN",
        }

        response = requests.post(url, headers=paystack_headers, json=data)
        return response.json()
    else:
        return "Bank not found"

    # Transfer Recipient response:
    # {
    #   "status": true,
    #   "message": "Transfer recipient created successfully",
    #   "data": {
    #     "active": true,
    #     "createdAt": "2020-05-13T13:59:07.741Z",
    #     "currency": "NGN",
    #     "domain": "test",
    #     "id": 6788170,
    #     "integration": 428626,
    #     "name": "John Doe",
    #     "recipient_code": "RCP_t0ya41mp35flk40",
    #     "type": "nuban",
    #     "updatedAt": "2020-05-13T13:59:07.741Z",
    #     "is_deleted": false,
    #     "details": {
    #       "authorization_code": null,
    #       "account_number": "0001234567",
    #       "account_name": null,
    #       "bank_code": "058",
    #       "bank_name": "Guaranty Trust Bank"
    #     }
    #   }
    # }


def paystack_create_subaccount():
    url = f"{paystack_base_url}subaccount"

    data = {
        "business_name": "Sunshine Studios",
        "settlement_bank": "044",
        "account_number": "0193274682",
        "percentage_charge": 18.2,
    }

    response = requests.post(url, headers=paystack_headers, json=data)
    print(response.json())

    # response
    # {
    # "status": true,
    # "message": "Subaccount created",
    # "data": {
    #       "integration": 100973,
    #       "domain": "test",
    #       "subaccount_code": "ACCT_4hl4xenwpjy5wb",
    #       "business_name": "Sunshine Studios",
    #       "description": null,
    #       "primary_contact_name": null,
    #       "primary_contact_email": null,
    #       "primary_contact_phone": null,
    #       "metadata": null,
    #       "percentage_charge": 18.2,
    #       "is_verified": false,
    #       "settlement_bank": "Access Bank",
    #       "account_number": "0193274682",
    #       "settlement_schedule": "AUTO",
    #       "active": true,
    #       "migrate": false,
    #       "id": 55,
    #       "createdAt": "2016-10-05T13:22:04.000Z",
    #       "updatedAt": "2016-10-21T02:19:47.000Z"
    #     }
    #   }


def paystack_list_sub_account():
    url = f"{paystack_base_url}subaccount"
    response = requests.get(url, headers=paystack_headers)
    print(response.json())


def paystack_transfer(recipient, amount, source="balance"):
    url = f"{paystack_base_url}transfer"
    reason = "Salary payment for April"
    reference = f"{generate_uuid()}-{recipient}"
    data = {
        "source": source,
        "amount": amount,
        "reference": reference,
        "recipient": recipient,
        "reason": reason,
    }
    response = requests.post(url, headers=paystack_headers, json=data)
    return response.json()


def paystack_fetch_transfer(transfer_id):
    url = f"{paystack_base_url}{transfer_id}"
    response = requests.get(url, headers=paystack_headers)
    return response.json()


def paystack_bulk_transfer():
    # url = f'{paystack_base_url}transfer'
    url = f"{paystack_base_url}transfer/bulk"
    recipients = [
        {
            "account_number": "1234567890",
            "bank_code": "044",  # Bank code for Access Bank Nigeria
            "amount": 500000,  # Transfer amount in kobo (NGN 5,000)
            "currency": "NGN",  # Currency code (Nigerian Naira)
            "description": "Payment for goods",
            "reference": "REF123456789",  # Unique reference for the transfer
        },
        {
            "account_number": "0987654321",
            "bank_code": "057",  # Bank code for Zenith Bank Nigeria
            "amount": 1000000,  # Transfer amount in kobo (NGN 10,000)
            "currency": "NGN",  # Currency code (Nigerian Naira)
            "description": "Payment for services",
            "reference": "REF987654321",  # Unique reference for the transfer
        },
    ]

    # Set the transfer batch parameters
    transfer_batch = {
        "currency": "NGN",  # Currency code (Nigerian Naira)
        "source": "balance",  # Funding source (balance or bank)
        "transfers": recipients,  # List of transfer recipients
    }

    response = response = requests.post(
        url, headers=paystack_headers, json=transfer_batch
    )
    print(response.json())

    # transfer response
    # {
    #   "status": true,
    #   "message": "Transfer has been queued",
    #   "data": {
    #     "reference": "your-unique-reference",
    #     "integration": 428626,
    #     "domain": "test",
    #     "amount": 37800,
    #     "currency": "NGN",
    #     "source": "balance",
    #     "reason": "Holiday Flexing",
    #     "recipient": 6788170,
    #     "status": "success",
    #     "transfer_code": "TRF_fiyxvgkh71e717b",
    #     "id": 23070321,
    #     "createdAt": "2020-05-13T14:22:49.687Z",
    #     "updatedAt": "2020-05-13T14:22:49.687Z"
    #   }
    # }


def flutterwave_list_of_banks():
    url = f"{flutterwave_base_url}banks/ng"
    response = requests.get(url, headers=flutterwave_headers).json()
    no = 1
    for bank in response["data"]:
        bank_name = bank["name"]
        bank_id = bank["id"]
        bank_code = bank["code"]

        bank_exists = frappe.db.sql(
            f"""
            SELECT name FROM `tabFlutterwave Nigerian Banks` 
            WHERE bank_name = '{bank_name}' 
        """,
            as_dict=True,
        )

        if bank_exists:
            existing_bank = frappe.get_doc(
                "Flutterwave Nigerian Banks", bank_exists[0]["name"]
            )
            existing_bank.id = bank_id
            existing_bank.code = bank_code
            existing_bank.save()
            frappe.db.commit()
            print(bank_name, " --updated")
        else:
            new_bank = frappe.get_doc(
                {
                    "doctype": "Flutterwave Nigerian Banks",
                    "bank_name": bank_name,
                    "id": bank_id,
                    "code": bank_code,
                }
            )
            print(bank_name, "saved new")
            new_bank.save()


def flutterwave_transfer(bank, acc_no, amount, debit_acc=None, narration=None):
    url = f"{flutterwave_base_url}transfers"
    transfer_data = {
        "account_bank": bank,
        "account_number": acc_no,
        "amount": amount,
        "narration": narration,
        "currency": "NGN",
        "reference": f"{generate_uuid()}_{bank}",
        "debit_currency": "NGN",
        "requires_approval": 1,
    }

    if debit_acc:
        transfer_data["debit_subaccount"] = debit_acc
    if narration:
        transfer_data["narration"] = narration

    transfer = requests.post(url, headers=flutterwave_headers, json=transfer_data)
    return transfer.json()


def flutterwave_transfer_bulk(title, bulk_data):
    url = f"{flutterwave_base_url}bulk-transfers"

    transfer_data = {"title": title, "bulk_data": bulk_data}
    bulk_transfer = requests.post(url, headers=flutterwave_headers, json=transfer_data)

    trns = frappe.get_doc(
        {
            "doctype": "Flutterwave Webhook",
            "json_data": str(bulk_transfer.json()),
        }
    )

    trns.save(ignore_permissions=True)

    tdata = frappe.get_doc(
        {
            "doctype": "Flutterwave Webhook",
            "json_data": str(transfer_data),
        }
    )
    tdata.save(ignore_permissions=True)

    return bulk_transfer.json()


def flutterwave_create_sub_account(acc_name, email, phone):
    url = f"{flutterwave_base_url}payout-subaccounts"
    data = {
        "account_name": acc_name,
        "email": email,
        "mobilenumber": phone,
        "country": "NG",
    }

    create = requests.post(url, headers=flutterwave_headers, json=data)
    return create.json()


@frappe.whitelist()
def flutterwave_fetch_transactions1():
    account_reference = "PSA5382B6C7535461668"
    url = f"{flutterwave_base_url}payout-subaccounts/PSA5382B6C7535461668/transactions?from=2021-01-01&to=2025-02-10&currency=NGN"
    get = requests.get(url, headers=flutterwave_headers)
    return get.json()


@frappe.whitelist()
def flutterwave_fetch_transactions(account_reference, from_date, to_date, currency):
    url = f"{flutterwave_base_url}payout-subaccounts/{account_reference}/transactions?from={from_date}&to={to_date}&currency={currency}"
    get = requests.get(url, headers=flutterwave_headers)
    return get.json()


@frappe.whitelist()
def flutterwave_sub_account_balance(account_reference):
    url = f"{flutterwave_base_url}payout-subaccounts/{account_reference}/balances"
    get = requests.get(url, headers=flutterwave_headers)
    return get.json()


def flutterwave_get_sub_account(account_reference):
    url = f"{flutterwave_base_url}payout-subaccounts/{account_reference}"
    get = requests.get(url, headers=flutterwave_headers)
    return get.json()


def flutterwave_update_sub_account(account_reference, name, email, phone):
    url = f"{flutterwave_base_url}payout-subaccounts/{account_reference}"
    data = {"account_name": name, "mobilenumber": phone, "email": email}
    update = requests.put(url, headers=flutterwave_headers, json=data)
    return update.json()


def flutterwave_get_all_sub_account():
    url = f"{flutterwave_base_url}payout-subaccounts"
    get = requests.get(url, headers=flutterwave_headers)
    return get.json()


def create_transaction_log(data, doc, type="flutterwave"):
    if "status" in data:
        status = data["status"].upper()
        complete_message = data["data"]["complete_message"].upper()
        message = data["message"]
        full_name = data["data"]["full_name"]
    else:
        status = data["data"]["status"]
        complete_message = data["data"]["complete_message"]
        failed_message = "DISBURSE FAILED"
        full_name = data["data"]["fullname"]
        if status == "FAILED":
            message = failed_message
        else:
            message = complete_message

    log = frappe.get_doc(
        {
            "doctype": "Payment Transaction Logs",
            "id": data["data"]["id"],
            "status": status,
            "message": message,
            "acc_no": data["data"]["account_number"],
            "bank_code": data["data"]["bank_code"],
            "bank_name": data["data"]["bank_name"],
            "acc_name": full_name,
            "currency": data["data"]["currency"],
            "amount": data["data"]["amount"],
            "fee": data["data"]["fee"],
            "reference": data["data"]["reference"],
            # 'meta': data['data']['meta'],
            "flutterwave_transaction": doc.name,
            "narration": data["data"]["narration"],
            "complete_message": complete_message,
            "requires_approval": data["data"]["requires_approval"],
            "is_approved": data["data"]["is_approved"],
        }
    )

    log.save(ignore_permissions=True)


@frappe.whitelist()
def confirm_acc_no(acc_no, code):
    url = f"{flutterwave_base_url}accounts/resolve"
    acc_details = {"account_number": acc_no, "account_bank": code}
    confirm = requests.post(url, headers=flutterwave_headers, json=acc_details)
    if confirm.json()["status"] == "success":
        return confirm.json()["data"]["account_name"]
    return "Failed to confirm"


def fetch_all_transfers():
    url = f"{flutterwave_base_url}transfers"
    get = requests.get(url, headers=flutterwave_headers)
    print(get.json())


@frappe.whitelist()
def retry_transfer(transfer_id):
    url = f"{flutterwave_base_url}transfers/{transfer_id}/retries"

    transaction = frappe.db.sql(
        f""" SELECT name FROM `tabFlutterwave Transaction` 
    WHERE transaction_id = '{transfer_id}' """,
        as_dict=True,
    )[0]

    if transaction:
        get = requests.post(url, headers=flutterwave_headers)
        response = get.json()

        transaction_doc = frappe.get_doc("Flutterwave Transaction", transaction["name"])
        transaction_doc.message = response["message"].replace(".", "")
        transaction_doc.status = response["status"].upper()
        transaction_doc.complete_message = response["data"]["complete_message"]
        transaction_doc.save()

    frappe.msgprint(response["message"])


def fetch_transfer(transfer_id):
    url = f"{flutterwave_base_url}transfers/{transfer_id}"
    get = requests.get(url, headers=flutterwave_headers)
    return get.json()


@frappe.whitelist()
def get_employee_acc(employee_name):
    employee_name = employee_name.lower().strip().split()
    first_name = employee_name[0]
    last_name = employee_name[-1]
    employee_id = f"{first_name}.{last_name}@sydani.org"
    employee = frappe.db.sql(
        f"""SELECT bank_ac_no, 
    bank_account_name, bank_code, bank_name, bank_name_flutterwave 
    FROM `tabEmployee` 
    WHERE user_id = "{employee_id}" """,
        as_dict=True,
    )[0]
    return employee


# Expence claim checks
def is_completed(doc):
    return True if doc.payment_completed == 1 else False


def is_sub_acc(doc):
    return True if doc.flutterwave_sub_account_reference else False


def is_single(doc):
    return True if doc.pay_to == "Single Recipient" else False


def is_retirement(doc):
    return True if doc.requisition_type == "Retirement" else False


def is_petty(doc):
    return True if doc.requisition_type == "Petty Cash" else False


def is_advance_request(doc):
    return True if doc.requisition_type == "Advance Request" else False


def is_ngn(doc):
    return True if doc.denomination == "NGN" else False


def is_approved(doc):
    return True if doc.workflow_state == "Approved" else False


def is_approved_advance(doc):
    return True if doc.workflow_state == "Advance Retirement Approved" else False


def is_retirment_completed(doc):
    return True if doc.retirement_completed == 1 else False


def expense_claim_create_trasaction(doc, method=None):
    document_type = "Expense Claim"
    # "document_type": document_type,
    # "document_id": doc.name,
    # Expense Claim Retirement/single
    if (
        is_approved(doc)
        and is_completed(doc)
        and is_sub_acc(doc)
        and is_single(doc)
        and (is_retirement(doc) or is_petty(doc))
        and is_ngn(doc)
    ):
        trx = frappe.get_doc(
            {
                "doctype": "Flutterwave Transaction",
                "document_type": document_type,
                "acc_no": doc.bank_account,
                "bank": doc.bank_name,
                "bank_name": doc.bank_name_flutterwave,
                "acc_name": doc.bank_account_name,
                "amount": doc.payment_total,
                "subaccount_reference": doc.flutterwave_sub_account_reference,
                "narration": doc.payment_narration,
            }
        )
        trx.document_id = doc.name
        trx.save()
        return True

    # Advance Request Approved - is for the first leg, the advance leg. payment_total_advance will be sent to recipients on the child table "erpnext_table_advance". The trigger for this is doc.payment_completed
    # Advance Retirement Approved  if (doc.payment_total > doc.payment_total_advance:)- is for the second leg, amount_due_employee_advance will be sent out to recipients on the child table "multiple_recipients". The trigger for this is retirement_completed
    # Also include Flutterwave Subaccount in Flutterwave Transaction Doctype (copy from doc.mode_of_payment)
    # retirement_completed
    # Retirement Multiple ------------------------------------------------
    if (
        is_approved(doc)
        and is_completed(doc)
        and is_sub_acc(doc)
        and is_single(doc) == False
        and (is_retirement(doc) or is_petty(doc))
        and is_ngn(doc)
    ):
        bulk_transfer_data = []

        for rcp in doc.multiple_recipients:
            # bulk_transfer_data.append(
            #     {
            #         "bank_code": rcp.bank_name,
            #         "account_number": rcp.account_number,
            #         "amount": rcp.amount,
            #         "narration": doc.payment_narration,
            #         "currency": doc.denomination,
            #         "reference": f"{generate_uuid()}_{document_type}_{doc.name}_{doc.flutterwave_sub_account_reference}",
            #         "debit_subaccount": doc.flutterwave_sub_account_reference,
            #         "debit_currency": doc.denomination,
            #     }
            # )
            trx = frappe.get_doc(
                {
                    "doctype": "Flutterwave Transaction",
                    "document_type": document_type,
                    "acc_no": rcp.account_number,
                    "bank": rcp.bank_name,
                    # "bank_name": doc.bank_name_flutterwave,
                    # "acc_name": doc.bank_account_name,
                    "amount": rcp.amount,
                    "subaccount_reference": doc.flutterwave_sub_account_reference,
                    "narration": doc.payment_narration,
                }
            )

            trx.document_id = doc.name
            trx.save()

        # flutterwave_transfer_bulk(doc.purpose, bulk_transfer_data)
        return True

    # Advance/single
    if (
        is_approved_advance(doc)
        and is_retirment_completed(doc)
        and is_sub_acc(doc)
        and is_single(doc)
        and is_advance_request(doc)
        and is_ngn(doc)
    ):
        # Advance Retirement/single
        if doc.payment_total > doc.payment_total_advance:
            amount = doc.amount_due_employee_advance
        else:
            amount = doc.payment_total_advance

        trx = frappe.get_doc(
            {
                "doctype": "Flutterwave Transaction",
                "document_type": document_type,
                "acc_no": doc.bank_account,
                "bank": doc.bank_name,
                "bank_name": doc.bank_name_flutterwave,
                "acc_name": doc.bank_account_name,
                "amount": amount,
                "subaccount_reference": doc.flutterwave_sub_account_reference,
                "narration": doc.payment_narration,
            }
        )

        trx.document_id = doc.name
        trx.save()
        return True

    # Advance/Multiple
    if (
        is_approved_advance(doc)
        and is_retirment_completed(doc)
        and is_sub_acc(doc)
        and is_single(doc) == False
        and is_advance_request(doc)
        and is_ngn(doc)
    ):
        # Advance Retirement/Multiple
        if doc.payment_total > doc.payment_total_advance:
            recipients = doc.multiple_recipients
        else:
            recipients = doc.erpnext_table_advance

        bulk_transfer_data = []

        for rcp in recipients:
            # bulk_transfer_data.append(
            #     {
            #         "bank_code": rcp.bank_name,
            #         "account_number": rcp.account_number,
            #         "amount": rcp.amount,
            #         "narration": doc.payment_narration,
            #         "currency": doc.denomination,
            #         "reference": f"{generate_uuid()}_{document_type}_{doc.name}_{doc.flutterwave_sub_account_reference}",
            #         "debit_subaccount": doc.flutterwave_sub_account_reference,
            #         "debit_currency": doc.denomination,
            #     }
            # )
            trx = frappe.get_doc(
                {
                    "doctype": "Flutterwave Transaction",
                    "document_type": document_type,
                    "acc_no": rcp.account_number,
                    "bank": rcp.bank_name,
                    # "bank_name": doc.bank_name_flutterwave,
                    # "acc_name": doc.bank_account_name,
                    "amount": rcp.amount,
                    "subaccount_reference": doc.flutterwave_sub_account_reference,
                    "narration": doc.payment_narration,
                }
            )

            trx.document_id = doc.name
            trx.save()

        # flutterwave_transfer_bulk(doc.purpose, bulk_transfer_data)
        return True


def fluttwave_billers():
    url = f"{flutterwave_base_url}billers"
    response = requests.get(url, headers=flutterwave_headers)
    print(response.json())


def flutterwave_billers_category():
    url = f"{flutterwave_base_url}bill-categories"
    response = requests.get(url, headers=flutterwave_headers)
    print(response.json())


def flutterwave_subaccounts():
    url = f"{flutterwave_base_url}subaccounts"
    response = requests.get(url, headers=flutterwave_headers)
    print(response.json())


def flutterwave_subaccount(acc_id):
    url = f"{flutterwave_base_url}subaccounts/{acc_id}"
    response = requests.get(url, headers=flutterwave_headers)
    print(response.json())


def flutterwave_transactions(acc_ref, from_date, to_date):
    # flutterwave_base_url = "https://api.flutterwave.com/v3/"
    url = f"{flutterwave_base_url}/payout-subaccounts/{acc_ref}/transactions?from={from_date}&to={to_date}"
    response = requests.get(url, headers=flutterwave_headers)
    return response.json()


@frappe.whitelist()
def flutterwave_exchange_rate(amount, dest_cur, src_cur):
    # Amount in destination/foreign currency
    url = f"{flutterwave_base_url}transfers/rates?amount={amount}&destination_currency={dest_cur}&source_currency={src_cur}"
    response = requests.get(url, headers=flutterwave_headers)
    return response.json()


import frappe
import requests
from datetime import datetime


@frappe.whitelist()
def fetch_and_save_exchange_rates():
    # Define the currency pairs to fetch exchange rates for
    currency_pairs = [
        {"from_currency": "USD", "to_currency": "NGN"},
        {"from_currency": "EUR", "to_currency": "NGN"},
        {"from_currency": "GBP", "to_currency": "NGN"},
        {"from_currency": "NGN", "to_currency": "KES"},
        {"from_currency": "KES", "to_currency": "NGN"},
        {"from_currency": "USD", "to_currency": "KES"},
        {"from_currency": "EUR", "to_currency": "KES"},
        {"from_currency": "GBP", "to_currency": "KES"},
    ]

    # Loop through each currency pair and fetch the exchange rate
    for pair in currency_pairs:
        from_currency = pair["from_currency"]
        to_currency = pair["to_currency"]

        # Fetch the exchange rate
        # url = f"{flutterwave_base_url}transfers/rates?amount=1&destination_currency=GBP&source_currency=NGN"
        url = f"{flutterwave_base_url}transfers/rates?amount=1&destination_currency={from_currency}&source_currency={to_currency}"
        response = requests.get(url, headers=flutterwave_headers)

        # Parse the response
        if response.status_code == 200:
            exchange_rate_data = response.json()
            if exchange_rate_data.get("status") == "success":
                exchange_rate = exchange_rate_data["data"]["rate"]

                # Create a new record in the Exchange Rate doctype
                exchange_rate_record = frappe.get_doc(
                    {
                        "doctype": "Currency Exchange",
                        "date": datetime.today().date(),
                        "from_currency": from_currency,
                        "to_currency": to_currency,
                        "exchange_rate": exchange_rate,
                    }
                )
                exchange_rate_record.insert(ignore_permissions=True)
        else:
            frappe.log_error(
                f"Failed to fetch exchange rate for {from_currency}/{to_currency}: {response.text}",
                "Exchange Rate Fetch Error",
            )


def test(doc, method=None):
    frappe.msgprint(str(doc))
    # stmt = flutterwave_transactions("PSA067E3A09FF6274811", "2023-05-01", "2023-06-25")
    # print(stmt)
    # {{base_url}}/v3/payout-subaccounts/:account_reference/transactions?from=2021-02-10&to=2021-04-20


def get_bulk_trans():
    # "https://api.flutterwave.com/v3/transfers?batch_id=9145"
    url = f"{flutterwave_base_url}/transfers?batch_id=370151"
    response = requests.get(url, headers=flutterwave_headers)
    print(response.json())


def test_hash():
    # psw = '@Sydani_Payment_System'
    # hashed_psw = generate_hash(psw)

    # # verify = verify_hash(psw, hashed_psw)
    # # if(verify):
    # #   print('pass')
    # # else:
    # #   print('failed')

    # print(hashed_psw)
    # print(verify)

    # # CONFirm ACC
    # c = confirm_acc_no('0043097472', '044')
    # print(c)
    print(fetch_transfer("50620046"))


# {
#     'title': 'Flutterwave test',
#     'bulk_data': [
#         {
#             'account_bank': '070',
#             'account_number': '6173309589',
#             'amount': 100,
#             'narration': 'Test for multiple',
#             'currency': 'NGN',
#             'reference': '7e142b64-8a53-43f7-a5ff-9b89fe6970e9_Expense Claim_PV_NO:202307050003_PSA067E3A09FF6274811',
#             'debit_subaccount': 'PSA067E3A09FF6274811',
#             'debit_currency': 'NGN'
#         },
#         {
#             'account_bank': '100004', 'account_number': '8082299660', 'amount': 100, 'narration': 'Test for multiple', 'currency': 'NGN', 'reference': '5aa7cf11-8112-4ef4-a32b-a9fff8a9a96f_Expense Claim_PV_NO:202307050003_PSA067E3A09FF6274811', 'debit_subaccount': 'PSA067E3A09FF6274811', 'debit_currency': 'NGN'}]}


def test_exchange():
    res = flutterwave_exchange_rate(amount=1)
    print(res)
