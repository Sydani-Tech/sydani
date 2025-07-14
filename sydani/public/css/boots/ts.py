import frappe
from frappe import _
from datetime import date, timedelta, datetime

tester = frappe.conf.dev_tester


def test():
    
    t = frappe.db.sql(
        f"select name from `tabEmployee` where user_id = '{tester}'", as_dict=True)[0]

    d = datetime.today().replace(day=1)

    at = frappe.db.sql(
        f"select name, attendance_date, status from `tabAttendance` where employee = '{t['name']}' and attendance_date >= '{d}'",
        as_dict=True)

    print(at)
