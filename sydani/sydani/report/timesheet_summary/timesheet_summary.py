import frappe
from frappe.utils import today, add_days, getdate
from datetime import datetime, timedelta


def execute(filters=None):
    columns = [
        {
            "label": "Employee",
            "fieldname": "employee",
            "fieldtype": "Link",
            "options": "Employee",
            "width": 220,
        },
        {"label": "Project", "fieldname": "project", "fieldtype": "Data", "width": 150},
        {"label": "FTE Percentage", "fieldname": "fte", "fieldtype": "Percentage", "width": 180},
        {"label": "Total Hours", "fieldname": "total_hours", "fieldtype": "Float", "width": 120},
        {
            "label": "Hourly Billing Rate",
            "fieldname": "billing_rate",
            "fieldtype": "Currency",
            "width": 170,
        },
        {
            "label": "Daily Billing Rate",
            "fieldname": "daily_billing_rate",
            "fieldtype": "Currency",
            "width": 170,
        },
        {
            "label": "Billing Amount",
            "fieldname": "billing_amount",
            "fieldtype": "Currency",
            "width": 200,
        },
    ]
    data = []

    # query = f"""
    #     SELECT ts.employee, ts.department, ts.company, ts.month, ts.fiscal_year, fte.project, fte.fte, fte.total_hours, fte.billing_rate, fte.daily_billing_rate, fte.billing_amount
    #     FROM `tabTimesheet` as ts
    #     JOIN `tabProject FTE Distribution` as fte ON ts.name = fte.parent
    # """

    # if filters:
    #     # Apply filter conditions
    #     if filters.get("employee"):
    #         query += f"AND employee = '{filters.get('employee')}' "
    #     if filters.get("department"):
    #         query += f"AND department = '{filters.get('department')}' "
    #     if filters.get("company"):
    #         query += f"AND company = '{filters.get('company')}' "
    #     if filters.get("project"):
    #         query += f"AND project = '{filters.get('project')}' "
    #     if filters.get("month"):
    #         query += f"AND month = '{filters.get('month')}' "
    #     if filters.get("year"):
    #         query += f"AND fiscal_year = '{filters.get('fiscal_year')}' "

    # for timesheet_summary in query:
    #     employee = timesheet_summary.employee
    #     department = timesheet_summary.department
    #     company = timesheet_summary.company
    #     month = timesheet_summary.month
    #     year = timesheet_summary.fiscal_year

    # data.append(
    #     {
    #         "employee": employee,
    #         "deparment": department,
    #         "company": company,
    #         "month": month,
    #         "year": year,
    #     }
    # )

    query = """
        SELECT ts.employee, ts.department, ts.company, ts.month, ts.fiscal_year, fte.project, fte.fte, fte.total_hours, fte.billing_rate, fte.daily_billing_rate, fte.billing_amount
        FROM `tabTimesheet` as ts
        JOIN `tabProject FTE Distribution` as fte ON ts.name = fte.parent
        WHERE 1=1
    """

    if filters:
        # Apply filter conditions
        if filters.get("employee"):
            query += f" AND ts.employee = '{filters.get('employee')}' "
        if filters.get("department"):
            query += f" AND ts.department = '{filters.get('department')}' "
        if filters.get("company"):
            query += f" AND ts.company = '{filters.get('company')}' "
        if filters.get("project"):
            query += f" AND fte.project = '{filters.get('project')}' "
        if filters.get("month"):
            query += f" AND ts.month = '{filters.get('month')}' "
        if filters.get("year"):
            query += f" AND ts.fiscal_year = '{filters.get('year')}' "

    # execute your query to get 'query_results', this depends on your database client
    query_results = frappe.db.sql(query, as_dict=True)

    data = []
    for timesheet_summary in query_results:
        data.append(
            {
                "employee": timesheet_summary.employee,
                "department": timesheet_summary.department,
                "company": timesheet_summary.company,
                "month": timesheet_summary.month,
                "year": timesheet_summary.fiscal_year,
                "project": timesheet_summary.project,
                "fte": timesheet_summary.fte,
                "total_hours": timesheet_summary.total_hours,
                "billing_rate": timesheet_summary.billing_rate,
                "daily_billing_rate": timesheet_summary.daily_billing_rate,
                "billing_amount": timesheet_summary.billing_amount,
            }
        )

    results = frappe.db.sql(query, as_dict=1)
    return columns, data
