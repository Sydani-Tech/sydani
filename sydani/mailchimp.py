import frappe
import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError

def add_subscriber(doc, method=None):
    mailchimp = MailchimpMarketing.Client()
    mailchimp.set_config({
      "api_key": "ec7d6030916f81de32633e3cfd0073f0-us9",
      "server": "us9"
    })

    # list_id = "1037009" 
    list_id = "a251a2c28a"

    member_info = {
        "email_address": doc.email,
        "status": "subscribed",
        # "merge_fields": {
        #     "FNAME": f_name,
        #     "LNAME": l_name
        # }
    }

    try:
        response = mailchimp.lists.add_list_member(list_id, member_info)
        # print("response: {}".format(response))
        frappe.msgprint('Add to mailchimp')
    except ApiClientError as error:
        # frappe.msgprint("An exception occurred: {}".format(error.text))
