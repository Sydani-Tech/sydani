# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today, add_days, getdate
from datetime import datetime, timedelta


def execute(filters=None):
    columns = [
        {"label": "Manager", "fieldname": "principal", "fieldtype": "Link", "options": "Employee", "width": 280},
        {"label": "Aggregate Scores", "fieldname": "aggregate_scores", "fieldtype": "Float", "width": 150},  
        {"label": "Completion Rate", "fieldname": "completion_rate", "fieldtype": "Float", "width": 150},
        {"label": "Approval Rate", "fieldname": "approval_rate", "fieldtype": "Float", "width": 150},
        {"label": "Avg Early Approval %", "fieldname": "early_approval_percentage", "fieldtype": "Float", "width": 200},
        {"label": "Number of Work Plans", "fieldname": "num_work_plans", "fieldtype": "Int", "width": 200},
        # {"label": "Total Workplans", "fieldname": "total_work_plans", "fieldtype": "Int", "width": 150}
    ]

    data = []

    # Get the current date
    today_query = datetime.today()

    # Calculate the date of the Monday of the current week
    monday_of_current_week = today_query - timedelta(days=today_query.weekday())

    # Format the date to match the SQL format (YYYY-MM-DD)
    formatted_monday = monday_of_current_week.strftime('%Y-%m-%d')

    # Your SQL query
    query = f"""
        SELECT name, employee, completion_rate, present_cadre, department, company, work_week_begins_on, principal, approval, docstatus
        FROM `tabWork Plan`
        WHERE work_week_begins_on < '{formatted_monday}'
    """


    # query = """SELECT name, employee, completion_rate, present_cadre, department, company, work_week_begins_on, principal, approval, docstatus
    #         FROM `tabWork Plan` 
    #         WHERE 1=1"""

    if filters:
        # Apply filter conditions
        if filters.get("company"):
            query += f"AND company = '{filters.get('company')}' "
        if filters.get("principal"):
            query += f"AND principal = '{filters.get('principal')}' "
        

    # Apply date range filter
    if filters.get("date_range"):
        today_date = today()
        
        if filters.get("date_range") == "Last Week":
            start_date = getdate(add_days(today_date, -12))
        elif filters.get("date_range") == "Last 1 Month":
            start_date = getdate(add_days(today_date, -31))
        elif filters.get("date_range") == "Last 3 Months":
            start_date = getdate(add_days(today_date, -93))
        elif filters.get("date_range") == "Last 6 Months":
            start_date = getdate(add_days(today_date, -180))
        elif filters.get("date_range") == "Last 1 Year":
            start_date = getdate(add_days(today_date, -365))
        elif filters.get("date_range") == "All Time Record":
            start_date = getdate(add_days(today_date, -3650))
        
        # Assign end_date within the block
        end_date = getdate(today_date)
        
        query += f" AND work_week_begins_on >= '{start_date}' AND work_week_begins_on <= '{end_date}'"

    # ... (apply manager filter)
    

    # Initialize num_weeks_in_period
    num_weeks_in_period = 0

    work_plans = frappe.db.sql(query, as_dict=True)

    principal_completion_rates = {}
    principal_work_plan_count = {}
    principal_early_approval_count = {}
    total_work_plans = 0
    approved_work_plans = {}  # Counter for approved work plans

    # Collect completion rates, work plan count, early approval count, and calculate total work plans
    for plan in work_plans:
        principal = plan.principal
        completion_rate = plan.completion_rate or 0
        approval = plan.approval
        docstatus = plan.docstatus

        if principal not in principal_completion_rates:
            principal_completion_rates[principal] = []
            principal_work_plan_count[principal] = 0
            principal_early_approval_count[principal] = 0
            approved_work_plans[principal] = 0

        principal_completion_rates[principal].append(completion_rate)
        principal_work_plan_count[principal] += 1

        if approval == "Early":
            principal_early_approval_count[principal] += 1

        # Check if the work plan is approved
        if docstatus == 1:
            approved_work_plans[principal] += 1

        total_work_plans += 1

    # Calculate average completion rate, early approval percentage, and approval rate for each principal
    for principal, rates in principal_completion_rates.items():
        average_completion_rate = sum(rates) / len(rates) if len(rates) > 0 else 0
        early_approval_percentage = (
            # (principal_early_approval_count[principal] / principal_work_plan_count[principal]) * 100
            (principal_early_approval_count[principal] / len(rates) if len(rates) > 0 else 0) * 100
            # if principal_work_plan_count[principal] > 0
            # else 0
        )

        # Avoid division by zero for num_weeks_in_period
        num_weeks_in_period = (end_date - start_date).days // 7 if total_work_plans > 0 else 1

        # Calculate approval rate based on (approved_work_plans / total_work_plans) * 100
        approval_rate = (
            (approved_work_plans[principal]/ len(rates) if len(rates) > 0 else 0) * 100
            # if total_work_plans > 0
            # else 0
        )

        # Calculate Aggregate Scores with constants for weights
        aggregate_scores = (
            0.6 * average_completion_rate +
            0.3 * approval_rate +
            0.1 * early_approval_percentage
        )

        data.append({
            "principal": principal,
            "completion_rate": average_completion_rate,
            "approval_rate": approval_rate,
            "early_approval_percentage": early_approval_percentage,
            "aggregate_scores": aggregate_scores,
            "num_work_plans": principal_work_plan_count[principal],
            "total_work_plans": total_work_plans
        })

    # Sort data by Aggregate Scores (highest to lowest)
    sorted_data = sorted(data, key=lambda x: x["aggregate_scores"], reverse=True)

    return columns, sorted_data
