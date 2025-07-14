import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, add_days, getdate, add_to_date, now
from datetime import date, timedelta, datetime
import requests
import traceback
import json
import os
import io

@frappe.whitelist(allow_guest=True)
def PunchLog(): 
  post_data = json.loads(frappe.request.data)
  
  path = f"plog.json"
  full_path = os.path.join(os.path.dirname(__file__), path)
  # if os.path.isfile(path) and os.access(PATH, os.R_OK):
  #   pass
  # else:
  with io.open(full_path, 'w') as log_data:
    log_data.write(str(post_data))


# def PunchLog(RealTime=None, employee_field_value=None, timestamp=None, device_id=None, log_type=None, skip_auto_attendance=0, employee_fieldname='attendance_device_id'):

# [{
#       "employee": employee_field_value,
#       "timestamp": timestamp,
#       "device": device_id,
#       "log": log_type,
#       "skip_auto": skip_auto_attendance,
#       "employee_field_name": employee_fieldname,
#       "punch": RealTime
#     }])