# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe.utils import getdate, nowdate

def execute(filters=None):
    columns = [
        
        {"label": "Request Type", "fieldname": "request_type", "fieldtype": "Data", "width": 150},
        {"label": "Request", "fieldname": "request", "fieldtype": "Dynamic Link", "options": "request_type", "width": 190},
        {"label": "Date", "fieldname": "request_date", "fieldtype": "Date", "width": 115},
        {"label": "Responsible Party", "fieldname": "responsible_party", "fieldtype": "Data", "width": 150},
        {"label": "Delay", "fieldname": "delay", "fieldtype": "Data", "width": 250},
        {"label": "Approver", "fieldname": "approver", "fieldtype": "Data", "width": 200},
		{"label": "Currency", "fieldname": "currency", "fieldtype": "Link", "options": "Currency", "width": 100},
        {"label": "Amount Requested", "fieldname": "total", "fieldtype": "Float", "width": 150},     
        {"label": "Purpose", "fieldname": "purpose", "fieldtype": "Data", "width": 300},
        {"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 200},
        {"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 200},
    ]

    data = []
    fiscal_year = filters.get("fiscal_year") if filters else None
    from_date = filters.get("from_date") if filters else None
    to_date = filters.get("to_date") if filters else None
    project = filters.get("project") if filters else None
    company = filters.get("company") if filters else None
    request_type = filters.get("request_type") if filters else None
    max_percentage_paid = filters.get("max_percentage_paid") if filters else 100

    if from_date and to_date:
        try:
            from_date = getdate(from_date)  # Convert to date if necessary
            to_date = getdate(to_date)      # Convert to date if necessary
            date_filter = ["between", [from_date, to_date]]
        except Exception as e:
            frappe.throw(_("Invalid date format provided for from_date or to_date. Please use YYYY-MM-DD."))
    else:
        date_filter = ["between", get_fiscal_year_dates(fiscal_year)]

    # Fetch Expense Claims
    if request_type == "All" or request_type == "Expense Claim":
        expense_claims = frappe.get_all(
            "Expense Claim",
            filters={
                "responsible_party": ["in", ["Finance", "Manager", "Internal Audit", "Managing Partner"]],
                "date_created": date_filter,
                "suspend_payment": 0,
                **({"project": project} if project else {}),
                **({"company": company} if company else {}),
            },
            fields=["name", "creation", "modified","purpose", "responsible_party", "expense_approver", "manager_name", "project", "payment_total", "payment_total_advance", "currency", "company"],
            order_by="creation desc"
        )
        for claim in expense_claims:
            # Calculate total paid for each claim
            total_paid = frappe.db.sql("""
                SELECT SUM(paid_amount)
                FROM `tabPayment Entry`
                WHERE payment_request = %s AND docstatus = 1 AND workflow_state != "Cancelled"
            """, (claim.name))[0][0] or 0
            claim.total_paid = total_paid

            # Calculate total raised for each claim
            total_raised = frappe.db.sql("""
                SELECT SUM(paid_amount)
                FROM `tabPayment Entry`
                WHERE payment_request = %s AND ((docstatus = 0) or (docstatus = 1)) AND workflow_state != "Cancelled"
            """, (claim.name))[0][0] or 0
            claim.total_raised = total_raised

            data.append({
                "request_type": "Expense Claim",
                "request": claim.name,
                "request_date": claim.creation.date(),
                "delay": format_delay(claim.modified),
                "responsible_party": claim.responsible_party,
                "approver": "Sidney Sampson" if claim.responsible_party == "Managing Partner" else claim.manager_name,
                "total": claim.payment_total if claim.payment_total > 0.1 else claim.payment_total_advance,
                "total_paid": total_paid,
                "percentage_paid": (total_paid / claim.payment_total * 100) if claim.payment_total > 0.1 else (total_paid / claim.payment_total_advance * 100) if claim.payment_total_advance > 0.1 else 0,
                "total_raised": total_raised,
                "percentage_raised": (total_raised / claim.payment_total * 100) if claim.payment_total > 0.1 else (total_raised / claim.payment_total_advance * 100) if claim.payment_total_advance > 0.1 else 0,
                "purpose": claim.purpose,
                "project": claim.project,
                "currency": claim.currency,
                "company": claim.company,
            })

    # Fetch Employee Travel Requests
    if request_type == "All" or request_type == "Employee Travel Request":
        travel_requests = frappe.get_all(
            "Employee Travel Request",
            filters={
                "responsible_person": ["in", ["Admin", "Audit and Finance", "Manager"]],
                # "trip_start_date": ["between", date_filter],
                "trip_start_date": date_filter,
                **({"project_name": project} if project else {}),
                **({"company": company} if company else {}),
            },
            fields=["name", "creation", "modified","responsible_person", "project_manager", "purpose_of_the_trip", "project_name", "total", "currency", "company"]
        )
        for request in travel_requests:

            # Calculate total paid for each travel request
            total_paid = frappe.db.sql("""
                SELECT SUM(paid_amount)
                FROM `tabPayment Entry`
                WHERE employee_travel_request = %s AND docstatus = 1 AND workflow_state != "Cancelled"
            """, (request.name))[0][0] or 0
            request.total_paid = total_paid

            # Calculate total raised for each travel request
            total_raised = frappe.db.sql("""
                SELECT SUM(paid_amount)
                FROM `tabPayment Entry`
                WHERE employee_travel_request = %s AND ((docstatus = 0) OR (docstatus = 1)) AND workflow_state != "Cancelled"
            """, (request.name))[0][0] or 0
            request.total_raised = total_raised

            data.append({
                "request_type": "Employee Travel Request",
                "request": request.name,
                "request_date": request.creation.date(),
                "delay": format_delay(request.modified),
                "responsible_party": request.responsible_person,
                "approver": request.project_manager,
                "total": request.total,
                "total_paid": request.total_paid,
                "percentage_paid": (request.total_paid / request.total * 100) if request.total > 0 else 0,
                "total_raised": total_raised,
                "percentage_raised": (total_raised / request.total * 100) if request.total > 0 else 0,
                "purpose": request.purpose_of_the_trip,
                "project": request.project_name,
                "currency": request.currency,
                "company": request.company,
            })

    # Fetch Procurement Requests
    if request_type == "All" or request_type == "Procurement Request":
        procurement_requests = frappe.get_all(
            "Procurement Request",
            filters={
                "responsible_party": ["in", ["Procurement", "Manager"]],
                # "request_date": ["between", date_filter],
                "request_date": date_filter,
                **({"project": project} if project else {}),
                **({"company": company} if company else {}),
            },
            fields=["name", "creation", "modified","responsible_party", "approving_managers_email","purpose", "project", "total", "currency", "company"]
        )
        for request in procurement_requests:

            # Calculate total paid for each procurement request
            total_paid = frappe.db.sql("""
                SELECT SUM(paid_amount)
                FROM `tabPayment Entry`
                WHERE procurement_request = %s AND docstatus = 1 AND workflow_state != "Cancelled"
            """, (request.name))[0][0] or 0
            request.total_paid = total_paid

             # Calculate total raised for each travel request
            total_raised = frappe.db.sql("""
                SELECT SUM(paid_amount)
                FROM `tabPayment Entry`
                WHERE procurement_request = %s AND ((docstatus = 0) or (docstatus = 1)) AND workflow_state != "Cancelled"
            """, (request.name))[0][0] or 0
            request.total_raised = total_raised

            data.append({
                "request_type": "Procurement Request",
                "request": request.name,
                "request_date": request.creation.date(),
                "delay": format_delay(request.modified),
                "responsible_party": request.responsible_party,
                "approver": request.approving_managers_email,
                "total": request.total,
                "total_paid": request.total_paid,
                "percentage_paid": (request.total_paid / request.total * 100) if request.total > 0 else 0,
                "total_raised": total_raised,
                "percentage_raised": (total_raised / request.total * 100) if request.total > 0 else 0,
                "purpose": request.purpose,
                "project": request.project,
                "currency": request.currency,
                "company": request.company,
            })

    # Fetch Procurement Requests
    if request_type == "All" or request_type == "Procurement Evaluation Sheet":
        procurement_purchase_orders = frappe.get_all(
            "Procurement Evaluation Sheet",
            filters={
                "responsible_party": ["in", ["Procurement", "Audit", "Audit and Finance", "Manager"]],
                "creation": date_filter,
                **({"project": project} if project else {}),
                **({"company": company} if company else {}),
            },
            fields=["name", "creation", "modified","responsible_party", "approvers_name","purpose", "project", "grand_total", "currency", "company"]
        )
        for request in procurement_purchase_orders:

            # Calculate total paid for each procurement request
            total_paid = frappe.db.sql("""
                SELECT SUM(paid_amount)
                FROM `tabPayment Entry`
                WHERE procurement_purchase_order = %s AND docstatus = 1 AND workflow_state != "Cancelled"
            """, (request.name))[0][0] or 0
            request.total_paid = total_paid

             # Calculate total raised for each travel request
            total_raised = frappe.db.sql("""
                SELECT SUM(paid_amount)
                FROM `tabPayment Entry`
                WHERE procurement_purchase_order = %s AND ((docstatus = 0) or (docstatus = 1)) AND workflow_state != "Cancelled"
            """, (request.name))[0][0] or 0
            request.total_raised = total_raised

            data.append({
                "request_type": "Procurement Evaluation Sheet",
                "request": request.name,
                "request_date": request.creation,
                "delay": format_delay(request.modified),
                "responsible_party": request.responsible_party,
                "approver": request.approvers_name,
                "total": request.grand_total,
                "total_paid": request.total_paid,
                "percentage_paid": (request.total_paid / request.grand_total * 100) if request.grand_total > 0 else 0,
                "total_raised": total_raised,
                "percentage_raised": (total_raised / request.grand_total * 100) if request.grand_total > 0 else 0,
                "purpose": request.purpose,
                "project": request.project,
                "currency": request.currency,
                "company": request.company,
            })

    # Fetch Capacity Building Fund Requests
    if request_type == "All" or request_type == "Capacity Building Fund Request":
        capacity_building_requests = frappe.get_all(
            "Capacity Building Fund Request",
            filters={
                "workflow_state": ["in", ["Submitted", "Validated"]],
                "creation": date_filter,
                **({"project": project} if project else {}),
                **({"company": company} if company else {}),
            },
            fields=["name", "creation", "modified","status", "employee","approver_name", "coursetraining_title", "institution", "cost", "currency", "company", "workflow_state"]
        )
        for request in capacity_building_requests:

            # Calculate total paid for each capacity building request
            total_paid = frappe.db.sql("""
                SELECT SUM(paid_amount)
                FROM `tabPayment Entry`
                WHERE capacity_building_fund_request = %s AND docstatus = 1 AND workflow_state != "Cancelled"
            """, (request.name))[0][0] or 0
            request.total_paid = total_paid

             # Calculate total raised for each travel request
            total_raised = frappe.db.sql("""
                SELECT SUM(paid_amount)
                FROM `tabPayment Entry`
                WHERE capacity_building_fund_request = %s AND ((docstatus = 0) or (docstatus = 1)) AND workflow_state != "Cancelled"
            """, (request.name))[0][0] or 0
            request.total_raised = total_raised

            
            # Merge fields to get purpose
            request.purpose = f"Capacity Building Fund Request for {request.employee} to obtain {request.coursetraining_title} at {request.institution}"

            #Manually set project if not available
            request.project = "Sydani Capacity Building Program" if request.company == "Sydani Initiative for International Development" else "Capacity Building (ST)" if request.company == "Sydani Technologies" else "Capacity Building (SG)" if request.company == "Sydani Group" else "Capacity Building (SC)" if request.company == "Sydani Consulting" else "Capacity building (SyRI)"

            #Manually set responsible party if not available
            request.responsible_party = "HR" if request.workflow_state in ["Submitted"] else "Approver"

            data.append({
                "request_type": "Capacity Building Fund Request",
                "request": request.name,
                "request_date": request.creation.date(),
                "delay": format_delay(request.modified),
                "responsible_party": request.responsible_party,
                "approver": request.approver_name,  #
                "total": request.cost,
                "total_paid": request.total_paid,
                "percentage_paid": (request.total_paid / request.cost * 100) if request.cost > 0 else 0,
                "total_raised": total_raised,
                "percentage_raised": (total_raised / request.cost * 100) if request.cost > 0 else 0,
                "purpose": f"Capacity Building Fund Request for {request.employee} to obtain {request.coursetraining_title} at {request.institution}",
                "project": request.project, 
                "currency": request.currency,
                "company": request.company,
            })

    # Filter data based on max_percentage_paid
    if max_percentage_paid:
        data = [d for d in data if d.get("percentage_paid", 0) <= max_percentage_paid]
        
    # Sort data by request type and name
    # data.sort(key=lambda x: (x["request_type"], x["request"]))
    
    return columns, data

def get_fiscal_year_dates(fiscal_year):
    if not fiscal_year:
        fiscal_year = frappe.defaults.get_defaults().get("fiscal_year")
    fiscal_year_doc = frappe.get_doc("Fiscal Year", fiscal_year)
    return [fiscal_year_doc.year_start_date, fiscal_year_doc.year_end_date]

from datetime import datetime
from dateutil.relativedelta import relativedelta

def format_delay(modified_time):
    now = datetime.now()
    delta = relativedelta(now, modified_time)
    parts = []
    if delta.years: parts.append(f"{delta.years} year{'s' if delta.years > 1 else ''}")
    if delta.months: parts.append(f"{delta.months} month{'s' if delta.months > 1 else ''}")
    if delta.days: parts.append(f"{delta.days} day{'s' if delta.days > 1 else ''}")
    if delta.hours: parts.append(f"{delta.hours} hour{'s' if delta.hours > 1 else ''}")
    if not parts: parts.append("Just Now")
    return ", ".join(parts)
