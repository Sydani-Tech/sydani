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
        {"fieldname": "total_fte", "label": _("Total FTE"), "fieldtype": "Float", "width": 170},
    ]

    # Fetch employees with the employee_status_filter and conditional project filter applied
    employees = frappe.db.sql(
        """
        SELECT DISTINCT emp.name, emp.employee_name, emp.status
        FROM `tabEmployee` emp
        WHERE 1=1
        {employee_status_filter}
        {employee_filter}
        {company_filter}
        {conditional_project_filter}
        """.format(
            employee_status_filter=(
                f"AND emp.status = 'Active'" if filters.get("employee_status") == "Active" else ""
            ),
            employee_filter=(
                f"AND emp.name = '{filters.get('employee')}'" if filters.get("employee") else ""
            ),
            company_filter=(
                f"AND emp.company = '{filters.get('company')}'" if filters.get("company") else ""
            ),
            conditional_project_filter=(
                """
                AND emp.name IN (
                    SELECT fte.employee 
                    FROM `tabProject FTE Assignment` fte
                    JOIN `tabProject` project ON fte.parent = project.name
                    WHERE fte.percentage_fte IS NOT NULL
                    {project_filter}
                )
                """.format(
                    project_filter=(
                        f"AND project.name = '{filters.get('project')}'"
                        if filters.get("project")
                        else ""
                    )
                )
                if filters.get("project")
                else ""
            ),
        ),
        as_dict=True,
    )

    # Fetch all projects with FTE assignments
    fte_assignments = frappe.db.sql(
        """
        SELECT
            fte.employee,
            fte.percentage_fte,
            project.name AS project_name,
            project.status,
            project.company
        FROM `tabProject FTE Assignment` fte
        JOIN `tabProject` project ON fte.parent = project.name
        WHERE fte.percentage_fte IS NOT NULL
        {employee_filter}
        {company_filter}
        {project_filter}
        {project_status_filter}
        """.format(
            employee_filter=(
                f"AND fte.employee = '{filters.get('employee')}'"
                if filters.get("employee")
                else ""
            ),
            company_filter=(
                f"AND project.company = '{filters.get('company')}'"
                if filters.get("company")
                else ""
            ),
            project_filter=(
                f"AND project.name = '{filters.get('project')}'" if filters.get("project") else ""
            ),
            project_status_filter=(
                f"AND project.status = '{filters.get('project_status')}'"
                if filters.get("project_status") and filters.get("project_status") != "All"
                else ""
            ),
        ),
        as_dict=True,
    )

    # Create dynamic columns for projects
    project_columns = list({d.project_name for d in fte_assignments})
    for project in project_columns:
        columns.append(
            {
                "fieldname": frappe.scrub(project),
                "label": _(project),
                "fieldtype": "Float",
                "width": 150,
            }
        )

    # Build the data for each employee
    for emp in employees:
        row = {"employee": emp.name, "total_fte": 0}

        # Initialize all project columns to 0
        for project in project_columns:
            project_field = frappe.scrub(project)
            row[project_field] = 0  # Default value

        # Populate project-specific FTE values
        for assignment in fte_assignments:
            if assignment.employee == emp.name:
                project_field = frappe.scrub(assignment.project_name)
                row[project_field] = assignment.percentage_fte
                row["total_fte"] += assignment.percentage_fte

        data.append(row)

    return columns, data
