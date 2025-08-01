
import frappe
from frappe import _
from dateutil.relativedelta import relativedelta
from datetime import datetime

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_employees(filters)
    processed_data = process_data(data, filters)  # Calculate Years column

    return columns, processed_data

def get_columns():
    return [
        _("Name") + ":Link/Employee:250",
        _("Date of Joining") + ":Date:120",
        _("Years") + ":Int:80",  # New column for number of years
        _("Department") + ":Link/Branch:150",
        _("Designation") + ":Link/Designation:150", _("Gender") + "::100",
        _("Company") + ":Link/Company:240"
    ]

def get_employees(filters):
    conditions = get_conditions(filters)
    return frappe.db.sql("""
        select name, employee_name, date_of_joining,
            branch, department, designation,
            gender, company
        from tabEmployee where status = 'Active' %s
    """ % conditions, as_dict=True)

def get_conditions(filters):
    conditions = ""
    if filters.get("month"):
        month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
                 "Dec"].index(filters["month"]) + 1
        conditions += " and month(date_of_joining) = '%s'" % month

    # Exclude employees hired this calendar year
    conditions += " and year(date_of_joining) < %s" % frappe.utils.nowdate().split('-')[0]

    if filters.get("company"):
        conditions += " and company = '%s'" % filters["company"]

    return conditions

from calendar import monthrange

def get_last_day_of_month(date_obj):
    last_day = monthrange(date_obj.year, date_obj.month)[1]
    return date_obj.replace(day=last_day)

def process_data(data, filters):
    processed_data = []
    today = datetime.now().date()

    for row in data:
        doj = row.get('date_of_joining')

        # Adjust DOJ to last day of its month
        doj_adjusted = get_last_day_of_month(doj) if doj else None

        # Adjust today's date
        today_adjusted = get_last_day_of_month(today)

        # Calculate years of service
        years_of_service = relativedelta(today_adjusted, doj).years if doj else 0

        processed_data.append([
            row.get("name"),
            row.get("date_of_joining"),
            years_of_service,
            row.get("department"),
            row.get("designation"),
            row.get("gender"),
            row.get("company"),
        ])

    return processed_data
