# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    # Define common columns
    columns = [
        {
            "label": "Employee",
            "fieldname": "employee",
            "fieldtype": "Link",
            "options": "Employee",
            "width": 170,
        },
    ]

    # Handle Summary Columns
    if filters and filters.get("reportss") == "Summary":
        columns.extend(
            [
                {
                    "label": "Employee No",
                    "fieldname": "employee_number",
                    "fieldtype": "Data",
                    "width": 115,
                },
                {
                    "label": "Present Cadre",
                    "fieldname": "designation",
                    "fieldtype": "Link",
                    "options": "Designation",
                    "width": 135,
                },
                {
                    "label": "Payroll Period",
                    "fieldname": "payroll_period",
                    "fieldtype": "Data",
                    "width": 110,
                },
                {
                    "label": "Working Days",
                    "fieldname": "total_working_days",
                    "fieldtype": "Data",
                    "width": 110,
                },
                {
                    "label": "Pay Days",
                    "fieldname": "payment_days",
                    "fieldtype": "Data",
                    "width": 120,
                },
                {
                    "label": "Currency",
                    "fieldname": "currency",
                    "fieldtype": "Link",
                    "options": "Currency",
                    "width": 85,
                },
                {
                    "label": "Gross Pay",
                    "fieldname": "gross_pay",
                    "fieldtype": "Float",
                    "width": 120,
                },
                {
                    "label": "Total Deduction",
                    "fieldname": "total_deduction",
                    "fieldtype": "Float",
                    "width": 125,
                },
                {
                    "label": "Net Pay",
                    "fieldname": "net_pay",
                    "fieldtype": "Float",
                    "width": 120,
                },
            ]
        )

    if filters and filters.get("reportss") == "Pension":
        columns.extend(
            [
                {
                    "label": "Employee No",
                    "fieldname": "employee_number",
                    "fieldtype": "Data",
                    "width": 115,
                },
                {
                    "label": "Pension Fund Administrator",
                    "fieldname": "pension_fund_administrator",
                    "fieldtype": "Data",
                    "width": 150,
                },
                {
                    "label": "Pension Fund Account",
                    "fieldname": "pension_fund_account",
                    "fieldtype": "Data",
                    "width": 150,
                },
                {
                    "label": "Currency",
                    "fieldname": "currency",
                    "fieldtype": "Link",
                    "options": "Currency",
                    "width": 85,
                },
                {
                    "label": "Employer Contribution",
                    "fieldname": "employer_contribution",
                    "fieldtype": "Float",
                    "width": 150,
                },
                {
                    "label": "Employee Contribution",
                    "fieldname": "employee_contribution",
                    "fieldtype": "Float",
                    "width": 150,
                },
                {
                    "label": "Employer Voluntary",
                    "fieldname": "employer_voluntary",
                    "fieldtype": "Float",
                    "width": 150,
                },
                {
                    "label": "Employee Voluntary",
                    "fieldname": "employee_voluntary",
                    "fieldtype": "Float",
                    "width": 150,
                },
                {
                    "label": "Total Contribution",
                    "fieldname": "total_contribution",
                    "fieldtype": "Float",
                    "width": 150,
                },
                {
                    "label": "Payroll Period",
                    "fieldname": "payroll_period",
                    "fieldtype": "Data",
                    "width": 150,
                },
            ]
        )

    if filters and filters.get("reportss") == "National Housing Fund":
        columns.extend(
            [
                {
                    "label": "NHF Accout Number",
                    "fieldname": "nhf_account_number",
                    "fieldtype": "Data",
                    "width": 160,
                },
                {
                    "label": "Currency",
                    "fieldname": "currency",
                    "fieldtype": "Data",
                    "width": 120,
                },
                {
                    "label": "Amount",
                    "fieldname": "national_housing_fund",
                    "fieldtype": "Float",
                    "width": 150,
                },
            ]
        )

    if filters and filters.get("reportss") == "Pay As You Earn":
        columns.extend(
            [
                {
                    "label": "Present Cadre",
                    "fieldname": "designation",
                    "fieldtype": "Link",
                    "options": "Designation",
                    "width": 145,
                },
                {
                    "label": "TIN",
                    "fieldname": "tax_identification_number",
                    "fieldtype": "Data",
                    "width": 140,
                },
                {
                    "label": "Currency",
                    "fieldname": "currency",
                    "fieldtype": "Data",
                    "width": 100,
                },
                {
                    "label": "Gross Pay",
                    "fieldname": "gross_pay",
                    "fieldtype": "Float",
                    "width": 120,
                },
                {
                    "label": "Total Deduction",
                    "fieldname": "total_deduction",
                    "fieldtype": "Float",
                    "width": 140,
                },
                {
                    "label": "Chargeable Income",
                    "fieldname": "chargeable_income",
                    "fieldtype": "Float",
                    "width": 150,
                },
                {
                    "label": "Tax Liability",
                    "fieldname": "tax_liability",
                    "fieldtype": "Float",
                    "width": 140,
                },
                {
                    "label": "Payroll Period",
                    "fieldname": "payroll_period",
                    "fieldtype": "Data",
                    "width": 120,
                },
            ]
        )

    # Handle Detailed Columns and Dynamic Components
    dynamic_components = []
    if filters and filters.get("reportss") == "Detailed":
        columns.extend(
            [
                {
                    "label": "Employee No",
                    "fieldname": "employee_number",
                    "fieldtype": "Data",
                    "width": 115,
                },
                {
                    "label": "Present Cadre",
                    "fieldname": "designation",
                    "fieldtype": "Link",
                    "options": "Designation",
                    "width": 135,
                },
                {
                    "label": "Payroll Period",
                    "fieldname": "payroll_period",
                    "fieldtype": "Data",
                    "width": 110,
                },
                {
                    "label": "Working Days",
                    "fieldname": "total_working_days",
                    "fieldtype": "Data",
                    "width": 110,
                },
                {
                    "label": "Pay Days",
                    "fieldname": "payment_days",
                    "fieldtype": "Data",
                    "width": 120,
                },
                {
                    "label": "Currency",
                    "fieldname": "currency",
                    "fieldtype": "Link",
                    "options": "Currency",
                    "width": 85,
                },
                {
                    "label": "Gross Pay",
                    "fieldname": "gross_pay",
                    "fieldtype": "Float",
                    "width": 120,
                },
                {
                    "label": "Net Pay",
                    "fieldname": "net_pay",
                    "fieldtype": "Float",
                    "width": 120,
                },
            ]
        )

        # Fetch dynamic components
        dynamic_components = frappe.db.sql(
            """
            SELECT sc.name, sc.type, sc.do_not_include_in_total
            FROM `tabSalary Component` sc
            INNER JOIN `tabSalary Component Account` sca ON sca.parent = sc.name
            WHERE sc.disabled = 0 AND sca.company = %s
            ORDER BY 
                CASE 
                    WHEN sc.type = 'Earning' THEN 1
                    WHEN sc.type = 'Deduction' THEN 2
                    ELSE 3 
                END
            """,
            (filters.get("company")),
            as_dict=True,
        )

        for component in dynamic_components:
            fieldname = component.name.lower().replace(" ", "_")
            column = {
                "label": component.name,
                "fieldname": fieldname,
                "fieldtype": "Float",
                "width": 120,
            }

            # Apply color formatting
            if component.type == "Earning" and component.do_not_include_in_total == 0:
                column["label"] = f"<span style='color:green'>{component.name}</span>"
            elif component.type == "Deduction" and component.do_not_include_in_total == 0:
                column["label"] = f"<span style='color:red'>{component.name}</span>"
            elif component.do_not_include_in_total == 1:
                column["label"] = f"<span style='color:black'>{component.name}</span>"

            columns.append(column)

        columns.extend(
            [
                {
                    "label": "Bank Name",
                    "fieldname": "bank_name",
                    "fieldtype": "Data",
                    "width": 150,
                },
                {
                    "label": "Bank Account Name",
                    "fieldname": "bank_account_name",
                    "fieldtype": "Data",
                    "width": 150,
                },
                {
                    "label": "Bank Code",
                    "fieldname": "bank_code",
                    "fieldtype": "Data",
                    "width": 120,
                },
                {
                    "label": "Bank Account No",
                    "fieldname": "bank_account_no",
                    "fieldtype": "Data",
                    "width": 150,
                },
                {
                    "label": "Pension Fund Administrator",
                    "fieldname": "pension_fund_administrator",
                    "fieldtype": "Data",
                    "width": 150,
                },
                {
                    "label": "Pension Fund Account",
                    "fieldname": "pension_fund_account",
                    "fieldtype": "Data",
                    "width": 150,
                },
                {
                    "label": "Tax Identification Number",
                    "fieldname": "tax_identification_number",
                    "fieldtype": "Data",
                    "width": 150,
                },
                {
                    "label": "NHF Account Number",
                    "fieldname": "nhf_account_number",
                    "fieldtype": "Data",
                    "width": 150,
                },
            ]
        )

    data = []

    # Base Query
    query = """
        SELECT name, employee, employee_number, designation, currency, payroll_period,
               total_working_days, payment_days, base_total_deduction, base_gross_pay, base_net_pay
    """
    if filters and filters.get("reportss") == "Pension":
        query += ", employee_number, currency, pension_fund_administrator, pension_fund_account, payroll_period"

    if filters and filters.get("reportss") == "Pay As You Earn":
        query += ", base_total_deduction, base_gross_pay, payroll_period, designation, currency, tax_identification_number"

    if filters and filters.get("reportss") == "National Housing Fund":
        query += ", nhf_account_number"

    if filters and filters.get("reportss") == "Detailed":
        query += ", employee_number, designation, currency, payroll_period, total_working_days, payment_days, base_total_deduction, base_gross_pay, base_net_pay, bank_name, bank_account_name, bank_code, bank_account_no, pension_fund_administrator, pension_fund_account, tax_identification_number, nhf_account_number"

    query += " FROM `tabSalary Slip` WHERE 1 = 1"

    # Apply Filters
    if filters:
        if filters.get("company"):
            query += f" AND company = '{filters.get('company')}'"
        if filters.get("designation"):
            query += f" AND designation = '{filters.get('designation')}'"
        if filters.get("department"):
            query += f" AND department = '{filters.get('department')}'"
        if filters.get("employee"):
            query += f" AND employee = '{filters.get('employee')}'"
        if filters.get("payroll_period"):
            query += f" AND payroll_period = '{filters.get('payroll_period')}'"

    salary_slips = frappe.db.sql(query, as_dict=True)

    for slips in salary_slips:
        # Initialize the row dictionary for each salary slip
        row = {
            "employee": slips.employee,
            # "employee_number": slips.employee_number,
            # "designation": slips.designation,
            # "currency": slips.currency,
            # "total_working_days": slips.total_working_days,
            # "payment_days": slips.payment_days,
            # "payroll_period": slips.payroll_period,
        }

        if filters and filters.get("reportss") == "Summary":
            row.update(
                {
                    "employee_number": slips.employee_number,
                    "designation": slips.designation,
                    "currency": slips.currency,
                    "total_working_days": slips.total_working_days,
                    "payment_days": slips.payment_days,
                    "payroll_period": slips.payroll_period,
                    "total_deduction": slips.base_total_deduction,
                    "gross_pay": slips.base_gross_pay,
                    "net_pay": slips.base_net_pay,
                }
            )
        if filters and filters.get("reportss") == "National Housing Fund":
            row.update(
                {
                    "nhf_account_number": slips.nhf_account_number,
                    "currency": slips.currency,
                    "national_housing_fund": 0,
                }
            )

            salary_details = frappe.get_all(
                "Salary Detail",
                filters={"parent": slips.name, "parentfield": ["in", ["earnings", "deductions"]]},
                fields=["salary_component", "amount", "parentfield"],
            )

            # Define mapping for salary components to the row keys
            field_mapping = {
                "National Housing Fund": "national_housing_fund",
            }

            for detail in salary_details:
                fieldname = field_mapping.get(detail.salary_component)
                if fieldname:
                    # Adjust the value based on the parent field (earnings or deductions)
                    row[fieldname] += detail.amount

        if filters and filters.get("reportss") == "Pay As You Earn":
            row.update(
                {
                    "gross_pay": slips.base_gross_pay,
                    "currency": slips.currency,
                    "total_deduction": slips.base_total_deduction,
                    "payroll_period": slips.payroll_period,
                    "designation": slips.designation,
                    "tax_identification_number": slips.tax_identification_number,
                    "chargeable_income": 0,
                    "tax_liability": 0,
                }
            )

            salary_details = frappe.get_all(
                "Salary Detail",
                filters={"parent": slips.name, "parentfield": ["in", ["earnings", "deductions"]]},
                fields=["salary_component", "amount", "parentfield"],
            )

            # Define mapping for salary components to the row keys
            field_mapping = {
                "Chargeable Income": "chargeable_income",
                "Tax Liability": "tax_liability",
            }

            for detail in salary_details:
                fieldname = field_mapping.get(detail.salary_component)
                if fieldname:
                    # Adjust the value based on the parent field (earnings or deductions)
                    row[fieldname] += detail.amount

        if filters and filters.get("reportss") == "Pension":
            row.update(
                {
                    "employee_number": slips.employee_number,
                    "pension_fund_administrator": slips.pension_fund_administrator,
                    "pension_fund_account": slips.pension_fund_account,
                    "payroll_period": slips.payroll_period,
                    "currency": slips.currency,
                    "employee_voluntary": 0,  # Default to 0
                    "employee_contribution": 0,  # Default to 0
                    "employer_contribution": 0,  # Default to 0
                    "employer_voluntary": 0,  # Default to 0
                    "total_contribution": 0,  # Default to 0 for total contribution
                }
            )

            salary_details = frappe.get_all(
                "Salary Detail",
                filters={"parent": slips.name, "parentfield": ["in", ["earnings", "deductions"]]},
                fields=["salary_component", "amount", "parentfield"],
            )

            # Define mapping for salary components to the row keys
            field_mapping = {
                "Employee Voluntary Pension Contribution": "employee_voluntary",
                "Employee Pension Contribution": "employee_contribution",
                "Employer Pension Contribution 10%": "employer_contribution",
                "Employer Voluntary Pension Contribution": "employer_voluntary",
            }

            for detail in salary_details:
                fieldname = field_mapping.get(detail.salary_component)
                if fieldname:
                    # Adjust the value based on the parent field (earnings or deductions)
                    row[fieldname] += detail.amount

            # Calculate total contribution
            row["total_contribution"] = (
                row["employee_voluntary"]
                + row["employee_contribution"]
                + row["employer_contribution"]
                + row["employer_voluntary"]
            )

        if filters and filters.get("reportss") == "Detailed":
            row.update(
                {
                    "employee_number": slips.employee_number,
                    "designation": slips.designation,
                    "currency": slips.currency,
                    "total_working_days": slips.total_working_days,
                    "payment_days": slips.payment_days,
                    "payroll_period": slips.payroll_period,
                    "gross_pay": slips.base_gross_pay,
                    "net_pay": slips.base_net_pay,
                    "bank_name": slips.bank_name,
                    "bank_account_name": slips.bank_account_name,
                    "bank_code": slips.bank_code,
                    "bank_account_no": slips.bank_account_no,
                    "pension_fund_administrator": slips.pension_fund_administrator,
                    "pension_fund_account": slips.pension_fund_account,
                    "tax_identification_number": slips.tax_identification_number,
                    "nhf_account_number": slips.nhf_account_number,
                }
            )

            # Initialize dynamic component fields to 0
            for component in dynamic_components:
                fieldname = component.name.lower().replace(" ", "_")
                row[fieldname] = 0

            # Fetch and set dynamic component values from earnings and deductions
            salary_details = frappe.get_all(
                "Salary Detail",
                filters={"parent": slips.name, "parentfield": ["in", ["earnings", "deductions"]]},
                fields=["salary_component", "amount", "parentfield"],
            )

            for detail in salary_details:
                fieldname = detail.salary_component.lower().replace(" ", "_")
                if fieldname in row:
                    # Adjust the value based on the parent field (earnings or deductions)
                    if detail.parentfield == "earnings":
                        row[fieldname] += detail.amount
                    elif detail.parentfield == "deductions":
                        row[fieldname] += detail.amount

        data.append(row)

    return columns, data
