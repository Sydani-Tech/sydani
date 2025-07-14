import frappe
from frappe import _

# from frappe.model.document import Document
# from frappe.utils import date_diff, add_days, getdate, add_to_date, now
from datetime import date, timedelta, datetime

# import requests
# import json
# import uuid
# import hashlib


@frappe.whitelist(allow_guest=True)
def login(usr, pwd):
    # return frappe.generate_hash(length=15)
    try:
        login_manager = frappe.auth.LoginManager()
        login_manager.authenticate(user=usr, pwd=pwd)
        login_manager.post_login()
    except frappe.exceptions.AuthenticationError:
        frappe.clear_messages()
        frappe.local.response["message"] = {
            "success": 0,
            "message": "Authentication Error",
        }

        return

    user = generate_keys(frappe.session.user)
    # api_generate_key = generate_keys(user)

    frappe.response["message"] = {
        "success": 1,
        "message": "Authenticated",
        "sid": frappe.session.sid,
        "api_key": user.api_key,
        "api_secret": user.api_secret,
        "username": user.username,
        "email": user.email,
    }


def generate_keys(user):
    user_doc = frappe.get_doc("User", user)
    api_secret = frappe.generate_hash(length=15)

    if not user_doc.api_key:
        user_doc.api_key = frappe.generate_hash(length=15)

    user_doc.api_secret = api_secret
    user_doc.save(ignore_permissions=True)
    user_doc.api_secret = api_secret
    return user_doc


@frappe.whitelist()
def employees():
    employees = frappe.db.sql(
        f""" SELECT personal_email, prefered_email, access_card, ps_group, department,
            image, user_id  FROM `tabEmployee` WHERE status = 'Active' """,
        as_dict=True)
    return employees

@frappe.whitelist(allow_guest=True)
def email_group():
    emails = frappe.db.sql(f""" 
        SELECT email FROM `tabEmail Group Member`
    """)
    flattened_emails = [email for sublist in emails for email in sublist]

    return flattened_emails