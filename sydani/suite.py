import frappe
from frappe import _
from frappe import utils
import os.path
import requests
import json
import base64
import re
import random


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@frappe.whitelist(allow_guest=True)
def demo(full_name, email, phone, company, website, position, message):
  if(not is_valid_email(email)):
    return;
    
  data = {
    'doctype': 'SydaSuite  Book Demo Requests',
    'full_name': full_name, 
    'email': email, 
    'phone': phone, 
    'company': company, 
    'website': website, 
    'position': position,
    'message': message
  }

  demo = frappe.get_doc(data)

  demo.save(ignore_permissions=True);
  frappe.db.commit()
  return {'status': 'Success'}


@frappe.whitelist(allow_guest=True)
def contact(first_name, last_name, email, phone, message):
  if(not is_valid_email(email)):
    return;
  data = {
    'doctype': 'SydaSuite  Contact Requests',
    'first_name': first_name, 
    'last_name': last_name, 
    'email': email, 
    'phone': phone, 
    'message': message
  }

  contact = frappe.get_doc(data)
  contact.save(ignore_permissions=True);
  frappe.db.commit()
  return {'status': 'Success'}
  