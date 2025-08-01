# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _


def execute(filters=None):
    columns, data = [], []

    # Define the basic columns
    columns = [
        {
            "fieldname": "employee",
            "label": _("Employee"),
            "fieldtype": "Link",
            "options": "Employee",
            "width": 250,
        },
    ]

    # Fetch employees with the employee_status_filter and conditional project filter applied
    employees = frappe.db.sql(
        """
        SELECT DISTINCT emp.name, emp.employee_name, emp.status, emp.company
        FROM `tabEmployee` emp
        WHERE 1=1
        
        {employee_filter}
        {company_filter}
        
        """.format(
            employee_filter=(
                f"AND emp.name = '{filters.get('employee')}'" if filters.get("employee") else ""
            ),
            company_filter=(
                f"AND emp.company = '{filters.get('company')}'" if filters.get("company") else ""
            ),
        )
    )

    # Build the data for each employee
    for emp in employees:
        row = {"employee": emp.name}

        data.append(row)
    return columns, data
