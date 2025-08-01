import frappe
from frappe.utils import getdate, date_diff, random_string
from datetime import timedelta
import random


def execute(filters=None):
    # Get start date and end date from filters
    start_date = getdate(filters.get("start_date"))
    end_date = getdate(filters.get("end_date"))

    # Generate dynamic columns for each date between start date and end date
    columns = [
        {"label": "Employee", "fieldname": "employee", "fieldtype": "Link", "options": "Employee"},
        {"label": "FTE %", "fieldname": "fte", "fieldtype": "Float"},
        {"label": "Total Hours", "fieldname": "total_hours", "fieldtype": "Float"},
        {"label": "Hourly Rate", "fieldname": "hourly_rate", "fieldtype": "Currency"},
        {"label": "Billing Amount", "fieldname": "billing_amount", "fieldtype": "Currency"},
    ]
    data = []  # Initialize data to ensure it's always defined
 

    # dynamic_columns = []
    # current_date = start_date
    # while current_date <= end_date:
    #     dynamic_columns.append(
    #         {"label": str(current_date), "fieldname": random_string(10), "fieldtype": "Float"}
    #     )
    #     current_date += timedelta(days=1)
    # columns.extend(dynamic_columns)

    project = filters.get("project")
    employee = filters.get("employee")

    # Fetch project document based on the filter
    if project:
        project_doc = frappe.get_doc("Project", project)
        currency = project_doc.currency
        holiday_list_name = project_doc.holiday_list_2

        holiday_list = frappe.get_doc("Holiday List", holiday_list_name)
        excluded_dates = [
            holiday.holiday_date for holiday in holiday_list.holidays if holiday.weekly_off
        ]
        timesheet_excluded_dates = [
            date for date in excluded_dates if start_date <= date <= end_date
        ]

        # Remove excluded dates from dynamic column generation
        dynamic_columns = []
        current_date = start_date
        while current_date <= end_date:
            if current_date not in timesheet_excluded_dates:
                dynamic_columns.append(
                    {
                        "label": str(current_date),
                        "fieldname": random_string(10),
                        "fieldtype": "Float",
                    }
                )
            current_date += timedelta(days=1)
        columns.extend(dynamic_columns)

        # Prepare data for the selected project
        # data = []
        total_billing_amount = 0  # Initialize total billing amount
        for fte_assignment in project_doc.get("fte_assignment"):
            employee = fte_assignment.employee
            percentage_fte = fte_assignment.percentage_fte

            # # Calculate Total Hours based on FTE percentage
            # total_hours = (date_diff(end_date, start_date) + 1) * (percentage_fte / 100) * 8

            # Calculate Total Hours based on FTE percentage and adjusted working days
            total_working_days = (end_date - start_date).days + 1 - len(timesheet_excluded_dates)
            total_hours = total_working_days * (percentage_fte / 100) * 8

            # Distribute total hours randomly across dynamic columns
            distributed_hours = distribute_hours(total_hours, len(dynamic_columns), percentage_fte)

            # Get Hourly Rate (Assuming hourly_rate is a field in FTE Assignment)
            hourly_rate = fte_assignment.hourly_rate

            # Calculate Billing Amount
            billing_amount = total_hours * hourly_rate
            total_billing_amount += billing_amount  # Add to total billing amount

            # Prepare row data with dynamic column values
            row_data = {
                "employee": employee,
                "fte": percentage_fte,
                "total_hours": total_hours,
                "hourly_rate": hourly_rate,
                "billing_amount": billing_amount,
                "currency": currency,
            }
            for index, column in enumerate(dynamic_columns):
                row_data[column["fieldname"]] = distributed_hours[index]

            data.append(row_data)

        # Add total row to data
        total_row = {
            "employee": "Total",
            "fte": "",
            "total_hours": "",
            # "hourly_rate": "",
            "billing_amount": total_billing_amount,
            "currency": currency,
        }
        for column in dynamic_columns:
            total_row[column["fieldname"]] = sum(row[column["fieldname"]] for row in data)
        data.append(total_row)

        # Add style for total_billing_amount to make it bold
        # for key in total_row:
        #     if key == "billing_amount":
        #         total_row[key] = "<b>" + str(total_row[key]) + "</b>"

    # Fetch employee document based on the filter
    elif employee:
        # Fetch data for the selected employee
        pass
    else:
        # Fetch data without any filters
        pass

    return columns, data


def distribute_hours(total_hours, num_columns, fte_percentage):
    """Distribute total hours randomly across dynamic columns"""
    # Initialize list to hold distributed hours
    distributed_hours = []

    # Calculate the maximum allowed hours for each column
    max_hours = 8

    # Calculate the minimum allowed hours for each column
    min_hours = max(0.98 * max_hours, 0.01 * fte_percentage * max_hours)

    # Calculate the total minimum hours for all columns
    total_min_hours = min_hours * num_columns

    # Adjust dynamic hours to fit the total hours calculated based on FTE percentage
    scaling_factor = total_hours / total_min_hours if total_min_hours > 0 else 1
    for _ in range(num_columns):
        # Generate a random hour within the allowed range and scale it
        random_hour = min(random.uniform(min_hours, max_hours) * scaling_factor, total_hours)

        # Round the distributed hour to two decimal places
        rounded_hour = round(random_hour, 2)

        distributed_hours.append(rounded_hour)
        total_hours -= rounded_hour

    return distributed_hours



# import frappe
# from frappe.utils import getdate, date_diff, random_string
# from datetime import timedelta
# import random

# def execute(filters=None):
#     if not filters:
#         filters = {}

#     start_date = getdate(filters.get("start_date"))
#     end_date = getdate(filters.get("end_date"))

#     columns = [
#         {"label": "Employee", "fieldname": "employee", "fieldtype": "Link", "options": "Employee"},
#         {"label": "FTE %", "fieldname": "fte", "fieldtype": "Float"},
#         {"label": "Total Hours", "fieldname": "total_hours", "fieldtype": "Float"},
#         {"label": "Hourly Rate", "fieldname": "hourly_rate", "fieldtype": "Currency"},
#         {"label": "Billing Amount", "fieldname": "billing_amount", "fieldtype": "Currency"},
#     ]

#     data = []  # ✅ Ensures it's always initialized
#     project = filters.get("project")
#     employee = filters.get("employee")

#     # Handle project logic
#     if project:
#         project_doc = frappe.get_doc("Project", project)
#         currency = project_doc.currency
#         holiday_list_name = project_doc.holiday_list_2

#         holiday_list = frappe.get_doc("Holiday List", holiday_list_name)
#         excluded_dates = [
#             holiday.holiday_date for holiday in holiday_list.holidays if holiday.weekly_off
#         ]
#         timesheet_excluded_dates = [
#             date for date in excluded_dates if start_date <= date <= end_date
#         ]

#         # Generate dynamic columns excluding holidays
#         dynamic_columns = []
#         current_date = start_date
#         while current_date <= end_date:
#             if current_date not in timesheet_excluded_dates:
#                 dynamic_columns.append({
#                     "label": str(current_date),
#                     "fieldname": random_string(10),
#                     "fieldtype": "Float",
#                 })
#             current_date += timedelta(days=1)

#         columns.extend(dynamic_columns)

#         total_billing_amount = 0

#         for fte_assignment in project_doc.get("fte_assignment"):
#             employee = fte_assignment.employee
#             percentage_fte = fte_assignment.percentage_fte
#             total_working_days = (end_date - start_date).days + 1 - len(timesheet_excluded_dates)
#             total_hours = total_working_days * (percentage_fte / 100) * 8
#             distributed_hours = distribute_hours(total_hours, len(dynamic_columns), percentage_fte)

#             hourly_rate = fte_assignment.hourly_rate
#             billing_amount = total_hours * hourly_rate
#             total_billing_amount += billing_amount

#             row_data = {
#                 "employee": employee,
#                 "fte": percentage_fte,
#                 "total_hours": total_hours,
#                 "hourly_rate": hourly_rate,
#                 "billing_amount": billing_amount,
#                 "currency": currency,
#             }

#             for index, column in enumerate(dynamic_columns):
#                 row_data[column["fieldname"]] = distributed_hours[index]

#             data.append(row_data)

#         # Add total row
#         total_row = {
#             "employee": "Total",
#             "fte": "",
#             "total_hours": "",
#             "billing_amount": total_billing_amount,
#             "currency": currency,
#         }
#         for column in dynamic_columns:
#             total_row[column["fieldname"]] = sum(row[column["fieldname"]] for row in data)
#         data.append(total_row)

#     elif employee:
#         # You can implement similar logic here if needed for individual employee reporting
#         pass

#     else:
#         # If no filters, return empty data or raise a warning depending on your use case
#         pass

#     return columns, data

# def distribute_hours(total_hours, num_columns, fte_percentage):
#     """Distribute total hours randomly across dynamic columns"""
#     distributed_hours = []
#     max_hours = 8
#     min_hours = max(0.98 * max_hours, 0.01 * fte_percentage * max_hours)
#     total_min_hours = min_hours * num_columns
#     scaling_factor = total_hours / total_min_hours if total_min_hours > 0 else 1

#     for _ in range(num_columns):
#         random_hour = min(random.uniform(min_hours, max_hours) * scaling_factor, total_hours)
#         rounded_hour = round(random_hour, 2)
#         distributed_hours.append(rounded_hour)
#         total_hours -= rounded_hour

#     return distributed_hours
