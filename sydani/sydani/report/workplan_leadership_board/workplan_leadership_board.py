# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today, add_days, getdate


def execute(filters=None):
    columns = [
        {
            "label": "Employee",
            "fieldname": "employee",
            "fieldtype": "Link",
            "options": "Employee",
            "width": 300,
        },
        {
            "label": "Aggregate Scores",
            "fieldname": "aggregate_scores",
            "fieldtype": "Float",
            "width": 150,
        },
        {
            "label": "Completion Rate",
            "fieldname": "completion_rate",
            "fieldtype": "Float",
            "width": 150,
        },
        {
            "label": "Submission Rate",
            "fieldname": "submission_rate",
            "fieldtype": "Float",
            "width": 150,
        },
        {
            "label": "Avg Early Submission %",
            "fieldname": "avg_early_submission",
            "fieldtype": "Float",
            "width": 200,
        },
        {
            "label": "Number of Work Plans",
            "fieldname": "num_work_plans",
            "fieldtype": "Int",
            "width": 200,
        },
    ]

    data = []

    # # Construct the base query
    query = f"""SELECT name, employee, completion_rate, present_cadre, department, company, work_week_begins_on, submission, work_quality_score
            FROM `tabWork Plan`
            WHERE 1 = 1 """

    # query = f"""SELECT name, employee, completion_rate, present_cadre, department, company, work_week_begins_on, submission, work_quality_score
    #         FROM `tabWork Plan`
    #         WHERE docstatus = 1 """

    if filters:
        # Apply filter conditions
        if filters.get("company"):
            query += f"AND company = '{filters.get('company')}' "
        if filters.get("present_cadre"):
            query += f"AND present_cadre = '{filters.get('present_cadre')}' "
        if filters.get("department"):
            query += f"AND department = '{filters.get('department')}' "

        # # Initialize end_date with a default value
        # end_date = getdate(today())

        # Apply date range filter
        # if filters.get("date_range"):
        #     today_date = today()

        #     if filters.get("date_range") == "Last Week":
        #         start_date = getdate(add_days(today_date, -12))
        #     elif filters.get("date_range") == "Last 1 Month":
        #         start_date = getdate(add_days(today_date, -31))
        #     elif filters.get("date_range") == "Last 3 Months":
        #         start_date = getdate(add_days(today_date, -93))
        #     elif filters.get("date_range") == "Last 6 Months":
        #         start_date = getdate(add_days(today_date, -180))
        #     elif filters.get("date_range") == "Last 1 Year":
        #         start_date = getdate(add_days(today_date, -365))
        #     elif filters.get("date_range") == "All Time Record":
        #         start_date = getdate(add_days(today_date, -3650))

        #     # Assign end_date within the block
        #     end_date = getdate(today_date)

        #     query += f"AND work_week_begins_on >= '{start_date}' AND work_week_begins_on <= '{end_date}'"

        if filters.get("start_date2") and filters.get("end_date2"):
            # start_date = filters["start_date2"]
            # end_date = filters["end_date2"]

            start_date = getdate(filters["start_date2"])
            end_date = getdate(filters["end_date2"])

            query += f"AND work_week_begins_on >= '{start_date}' AND work_week_begins_on <= '{end_date}'"

        else:
            filters.get("date_range")
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

            query += f"AND work_week_begins_on >= '{start_date}' AND work_week_begins_on <= '{end_date}'"

        # Apply employee filter
        if filters.get("employee"):
            query += f"AND employee = '{filters.get('employee')}'"

    work_plans = frappe.db.sql(query, as_dict=True)

    employee_completion_rates = {}
    employee_work_plan_count = {}
    employee_early_submission_count = {}
    total_work_plans = 0

    # Collect completion rates, work plan count, early submission count, and calculate total work plans
    for plan in work_plans:
        employee = plan.employee
        completion_rate = plan.completion_rate or 0
        submission = plan.submission

        if employee not in employee_completion_rates:
            employee_completion_rates[employee] = []
            employee_work_plan_count[employee] = 0
            employee_early_submission_count[employee] = 0

        employee_completion_rates[employee].append(completion_rate)
        employee_work_plan_count[employee] += 1

        if submission == "Early":
            employee_early_submission_count[employee] += 1

        total_work_plans += 1

    # Calculate average completion rate, early submission percentage, and submission rate for each employee
    for employee, rates in employee_completion_rates.items():
        average_completion_rate = sum(rates) / len(rates)
        early_submission_percentage = (
            (employee_early_submission_count[employee] / employee_work_plan_count[employee]) * 100
            if employee_work_plan_count[employee] > 0
            else 0
        )

        # Calculate the number of weeks in the selected time period
        # num_weeks_in_period = (end_date - start_date).days // 7

        # Calculate the number of weeks in the selected time period if start and end date is supplied
        if filters.get("start_date2") and filters.get("end_date2"):
            num_weeks_in_period = ((end_date - start_date).days + 6) // 7

        else:
            if filters.get("date_range") == "Last Week":
                num_weeks_in_period = 1
            elif filters.get("date_range") == "Last 1 Month":
                num_weeks_in_period = 4
            elif filters.get("date_range") == "Last 3 Months":
                num_weeks_in_period = 13
            elif filters.get("date_range") == "Last 6 Months":
                num_weeks_in_period = 26
            elif filters.get("date_range") == "Last 1 Year":
                num_weeks_in_period = 52
            elif filters.get("date_range") == "All Time Record":
                num_weeks_in_period = 52

        # Calculate the submission rate based on (employee_work_plan_count / num_weeks_in_period) * 100
        submission_rate = (
            (employee_work_plan_count[employee] / num_weeks_in_period) * 100
            if num_weeks_in_period > 0
            else 0
        )

        # Calculate Aggregate Scores
        aggregate_scores = (
            (0.6 * average_completion_rate)
            + (0.3 * submission_rate)
            + (0.1 * early_submission_percentage)
        )

        data.append(
            {
                "employee": employee,
                "completion_rate": average_completion_rate,
                "submission_rate": submission_rate,
                "avg_early_submission": early_submission_percentage,
                "aggregate_scores": aggregate_scores,
                "num_work_plans": employee_work_plan_count[employee],
            }
        )

    # Sort data by Aggregate Scores (highest to lowest)
    sorted_data = sorted(data, key=lambda x: x["aggregate_scores"], reverse=True)

    return columns, sorted_data
