import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, add_days, getdate, add_to_date, now
from datetime import date, timedelta, datetime
import requests
import traceback
import json
import random
import string
from collections import defaultdict

import frappe
from frappe.utils import getdate


def calculate_accumulated_depreciation():
    # Fetch all records from Asset Doctype where docstatus is 1, calculate_depreciation is 1, and name is specified
    assets = frappe.get_all(
        "Asset",
        filters={"docstatus": 1, "calculate_depreciation": 1},
        fields=["name", "gross_purchase_amount"],
    )

    for asset in assets:
        asset_doc = frappe.get_doc("Asset", asset.name)

        # Initialize accumulated_depreciation_amount for the asset
        accumulated_depreciation_amount = 0

        # Iterate through the "Depreciation Schedule" child table
        for schedule in asset_doc.schedules:
            # Check if journal_entry is not empty
            if schedule.journal_entry:
                # Update accumulated_depreciation_amount if the current row has a larger value
                accumulated_depreciation_amount = max(
                    accumulated_depreciation_amount,
                    schedule.accumulated_depreciation_amount,
                )

        # Calculate the current value of the asset
        asset_current_value = (
            asset.gross_purchase_amount - accumulated_depreciation_amount
        )

        # Update fields in the Asset document
        asset_doc.db_set(
            "accumulated_depreciation_amount", accumulated_depreciation_amount
        )
        asset_doc.db_set("asset_current_value", asset_current_value)

        # Print asset, accumulated_depreciation_amount, and asset_current_value for debugging
        print(
            f"Asset: {asset.name}, Accumulated Depreciation: {accumulated_depreciation_amount}, Current Value: {asset_current_value}"
        )

    frappe.db.commit()


def create_suppliers_from_employees():
    # Fetch active employees using frappe.db.sql
    employees = frappe.db.sql(
        """
        SELECT name, employee_name
        FROM `tabEmployee`
        WHERE status = 'Active'
    """,
        as_dict=True,
    )

    # Loop through each employee
    for employee in employees:
        employee_name = employee.get("employee_name")
        print(employee_name)

        # Check if a Supplier with a similar name already exists
        existing_supplier = frappe.get_all(
            "Supplier", filters={"supplier_name": ("like", f"%{employee_name}%")}
        )

        if not existing_supplier:
            # Create a new Supplier document
            supplier = frappe.new_doc("Supplier")
            supplier.supplier_name = employee_name
            supplier.is_approved = 1
            supplier.supplier_group = "Employees"
            supplier.supplier_type = "Individual"

            # Save the Supplier document
            supplier.insert(ignore_permissions=True)


@frappe.whitelist()
def get_employee_name(user):
    # Your logic to fetch Employee name based on the user
    employee_name = frappe.get_value("Employee", {"user_id": user}, "name")

    if employee_name:
        return employee_name
    else:
        frappe.throw(_("Employee not found for the given user."))


@frappe.whitelist()
def fetch_managers():
    # Set to store unique user names
    unique_user_names = set()

    # Fetch users with roles "Manager" where the 'enabled' field is 1
    managers = frappe.get_all(
        "User",
        filters={"enabled": 1, "role": ["in", ["Manager", "Managing Partner"]]},
        fields=["name", "full_name", "email"],
    )

    # Iterate through the fetched users and add unique names to the set
    for user in managers:
        unique_user_names.add(user.name)

    # Return a list of dictionaries with unique user names
    users_manager_role = [{"name": user_name} for user_name in unique_user_names]
    return users_manager_role


def process_employee_fte_allocation(doc, method):
    if doc.create_employee_fte_record:
        # create new Employee FTE Allocation record
        fte_allocation = frappe.new_doc("Employee FTE Allocation")

        # copy fields from Timesheet record
        fte_allocation.employee = doc.employee
        fte_allocation.month = doc.month
        fte_allocation.year = doc.fiscal_year
        fte_allocation.start_date = doc.month_start_date
        fte_allocation.end_date = doc.month_end_date
        fte_allocation.timesheet = doc.name
        fte_allocation.monthly_gross_pay = doc.monthly_gross_pay
        fte_allocation.total_allocation = 100

        # calculate and set difference in days
        difference_in_days = (
            getdate(fte_allocation.end_date) - getdate(fte_allocation.start_date)
        ).days + 1

        # Fetch the 'Sydani Holidays' list
        holiday_list = frappe.get_doc("Holiday List", "Sydani Holidays")

        # Count holidays that are between start_date and end_date
        num_holidays = sum(
            getdate(holiday.holiday_date) >= getdate(fte_allocation.start_date)
            and getdate(holiday.holiday_date) <= getdate(fte_allocation.end_date)
            for holiday in holiday_list.holidays
        )

        # Fetch attendances between the start_date and end_date which are not marked as 'Absent'
        attendances = frappe.get_all(
            "Attendance",
            filters={
                "employee": doc.employee,
                "attendance_date": [
                    "between",
                    [doc.month_start_date, doc.month_end_date],
                ],
                "status": ["!=", "Absent"],
            },
        )

        num_attendances = len(attendances)

        # Calculate the number of present days
        fte_allocation.number_of_days_present = num_attendances

        # Calculate number of working days
        fte_allocation.number_of_working_days = difference_in_days - num_holidays

        # Calculate Pay for the month
        fte_allocation.pay_for_the_month = (
            doc.monthly_gross_pay
            * num_attendances
            / fte_allocation.number_of_working_days
        )

        for timesheet_detail in doc.fte_distribution:
            # Append a new child record in Employee FTE Allocation and copy fields from Timesheet child record
            fte_allocation.append(
                "fte_distribution",
                {
                    "project": timesheet_detail.project,
                    "fte": timesheet_detail.fte,
                    "billing_hours": timesheet_detail.total_hours,
                    "billing_rate": timesheet_detail.billing_rate,
                    "cost_to_project": timesheet_detail.fte
                    * fte_allocation.pay_for_the_month
                    / 100,
                },
            )

        fte_allocation.insert()  # save Employee FTE Allocation record


@frappe.whitelist()
def fetch_records(month, year, company):
    allocations = frappe.get_all(
        "Employee FTE Allocation",
        filters={"month": month, "year": year, "company": company},
        fields=["name"],
    )

    result = defaultdict(float)
    total_personnel_cost = 0
    for allocation in allocations:
        doc = frappe.get_doc("Employee FTE Allocation", allocation.name)
        for fte in doc.fte_distribution:
            result[fte.project] += fte.cost_to_project
            total_personnel_cost += fte.cost_to_project

    final_result = [
        {
            "project": key,
            "cost_to_project": value,
            "total_personnel_cost": total_personnel_cost,
        }
        for key, value in result.items()
    ]

    return final_result


@frappe.whitelist()
def get_active_employees_without_allocation(month, year, company):
    employee_allocation = frappe.get_all(
        "Employee FTE Allocation",
        filters={"month": month, "year": year, "company": company},
        fields=["employee"],
    )

    active_employees = frappe.get_all(
        "Employee", filters={"status": "Active", "company": company}, fields=["name"]
    )

    employees_without_allocation = [
        employee["name"]
        for employee in active_employees
        if employee["name"]
        not in [allocation["employee"] for allocation in employee_allocation]
    ]

    return employees_without_allocation


def travel_request_attendance():
    # Fetch all Employee Travel Requests with workflow_state = "Approved by Manager"
    travel_requests = frappe.get_all(
        "Employee Travel Request",
        filters={
            "workflow_state": "Approved by Manager",
            # "workflow_state": "Change Request Approved",
            "approval_attendance": 0,
        },
        fields=["name"],
    )

    # Iterate through each travel request
    for request in travel_requests:
        travel_request_doc = frappe.get_doc("Employee Travel Request", request.name)

        # Iterate through each itinerary in the travel request
        for itinerary in travel_request_doc.travel_itinerary:
            return_date = (
                itinerary.return_date5
                or itinerary.return_date4
                or itinerary.return_date3
                or itinerary.return_date2
                or itinerary.return_date1
            )

            # Iterate through each day between departure_date1 and return_date
            current_date = itinerary.departure_date1
            print(return_date)
            print(current_date)
            while current_date <= return_date:
                # Check if attendance record exists for the current date and employee
                attendance_record = frappe.get_all(
                    "Attendance",
                    filters={
                        "employee": itinerary.employee,
                        "attendance_date": current_date,
                    },
                    fields=["name", "status"],
                )

                # If no record exists, create a new attendance record with status "Present" and submit it
                if not attendance_record:
                    new_attendance_doc = frappe.new_doc("Attendance")
                    new_attendance_doc.employee = itinerary.employee
                    new_attendance_doc.attendance_date = current_date
                    new_attendance_doc.status = "Present"
                    new_attendance_doc.insert()
                    new_attendance_doc.submit()

                # If record exists and status is "Absent", update it to "Present"
                elif attendance_record[0].status == "Absent":
                    attendance_doc = frappe.get_doc(
                        "Attendance", attendance_record[0].name
                    )
                    attendance_doc.status = "Present"
                    attendance_doc.save()

                # Move to the next day
                current_date = add_days(current_date, 1)

        # Update the approval_attendance field on the Employee Travel Request record to 1
        travel_request_doc.approval_attendance = 1
        travel_request_doc.save()


def travel_request_attendance_for_change():
    # Fetch all Employee Travel Requests with workflow_state = "Change Request Approved" and change_attendance = 0
    travel_requests = frappe.get_all(
        "Employee Travel Request",
        filters={
            "workflow_state": "Change Request Approved",
            "change_attendance": 0,
        },
        fields=["name"],
    )

    # Iterate through each travel request
    for request in travel_requests:
        travel_request_doc = frappe.get_doc("Employee Travel Request", request.name)

        # Iterate through each itinerary in the travel retirement
        for itinerary in travel_request_doc.travel_retirement:
            return_date = (
                itinerary.return_date5
                or itinerary.return_date4
                or itinerary.return_date3
                or itinerary.return_date2
                or itinerary.return_date1
            )

            # Iterate through each day between departure_date1 and return_date
            current_date = itinerary.departure_date1
            while current_date <= return_date:
                # Cancel and delete existing attendance records for the current date and employee
                attendance_records = frappe.get_all(
                    "Attendance",
                    filters={
                        "employee": itinerary.employee,
                        "attendance_date": current_date,
                    },
                    fields=["name"],
                )
                for record in attendance_records:
                    attendance_doc = frappe.get_doc("Attendance", record.name)
                    attendance_doc.cancel()
                    attendance_doc.delete()

                # Set skip_auto_attendance to 0 in Employee Checkin doctype for the employee and current date
                checkin_records = frappe.get_all(
                    "Employee Checkin",
                    filters={
                        "employee": itinerary.employee,
                        "time": current_date,
                        "skip_auto_attendance": 1,
                    },
                    fields=["name"],
                )
                for record in checkin_records:
                    checkin_doc = frappe.get_doc("Employee Checkin", record.name)
                    checkin_doc.skip_auto_attendance = 0
                    checkin_doc.save()

                # Move to the next day
                current_date = add_days(current_date, 1)

        # Iterate through each retirement in the travel retirement
        for retirement in travel_request_doc.travel_retirement:
            # Set return_date based on the retirement dates
            return_date = (
                retirement.return_date5
                or retirement.return_date4
                or retirement.return_date3
                or retirement.return_date2
                or retirement.return_date1
            )

            # Iterate through each day between departure_date1 and return_date
            current_date = retirement.departure_date1
            while current_date <= return_date:
                # Check if attendance record exists for the current date and employee
                attendance_record = frappe.get_all(
                    "Attendance",
                    filters={
                        "employee": retirement.employee,
                        "attendance_date": current_date,
                    },
                    fields=["name", "status"],
                )

                # If no record exists, create a new attendance record with status "Present" and submit it
                if not attendance_record:
                    new_attendance_doc = frappe.new_doc("Attendance")
                    new_attendance_doc.employee = retirement.employee
                    new_attendance_doc.attendance_date = current_date
                    new_attendance_doc.status = "Present"
                    new_attendance_doc.insert()
                    new_attendance_doc.submit()

                # If record exists and status is "Absent", update it to "Present"
                elif attendance_record[0].status == "Absent":
                    attendance_doc = frappe.get_doc(
                        "Attendance", attendance_record[0].name
                    )
                    attendance_doc.status = "Present"
                    attendance_doc.save()

                # Move to the next day
                current_date = add_days(current_date, 1)

        # Update the approval_attendance field on the Employee Travel Request record to 1
        travel_request_doc.change_attendance = 1
        travel_request_doc.save()


def copy_sales_invoice_items_to_sales_order(doc, method):
    # Fetch the Sales Order linked to the Sales Invoice
    sales_order = frappe.get_value("Sales Invoice", doc.name, "sales_order")

    # If a Sales Order is linked
    if sales_order:
        # Fetch the Sales Order document
        sales_order_doc = frappe.get_doc("Sales Order", sales_order)

        # Clear items table on Sales Order document
        sales_order_doc.items = []

        # Iterate over Sales Invoice items and copy them to Sales Order
        for item in doc.sales_order_item:
            sales_order_item = sales_order_doc.append(
                "items",
                {
                    "doctype": "Sales Order Item",
                    "parenttype": "Sales Order",  # Set parenttype
                    "parentfield": "items",  # Set parentfield to the name of the field in Sales Order
                    "item_code": item.item_code,
                    "deliverable": item.deliverable,
                    "deliverable_2": item.deliverable_2,
                    "delivery_date": item.delivery_date,
                    "qty": item.qty,
                    "rate": item.rate,
                    "amount": item.amount,
                    "status": item.status,
                    "item_name": item.item_name,
                    "description": item.description,
                    "uom": item.uom,
                },
            )

        # Save the Sales Order document
        sales_order_doc.save()


def check_due_dates_against_holidays(doc, method):
    # Get the employee's holiday list
    employee = frappe.get_doc("Employee", doc.employee)

    employee_holiday_list = employee.holiday_list

    # Fetch holidays for the employee's holiday list
    holidays = frappe.get_all(
        "Holiday", filters={"parent": employee_holiday_list}, fields=["holiday_date"]
    )

    # Extract holiday dates from the fetched records and convert them to strings
    holiday_dates = [str(holiday.holiday_date) for holiday in holidays]

    # Check due dates in next_week_workplan
    for row in doc.next_week_workplan:
        if row.due_date in holiday_dates:
            frappe.throw(
                "An activity has a due date that is a holiday in next week's activity table. Please assign the task to another day."
            )

    # Check due dates in end_of_the_week
    for row in doc.end_of_the_week:
        if row.due_date in holiday_dates:
            frappe.throw(
                "An activity has a due date that is a holiday in this week's activity table. Please assign the task to another day."
            )

    # Check due dates in additional_activities
    for row in doc.additional_activities:
        if row.due_date in holiday_dates:
            frappe.throw(
                "An activity has a due date that is a holiday in the additional activities' table. Please assign the task to another day."
            )

    # Prevent saving if any holiday is found
    if holiday_dates:
        error_message = "Holiday(s) found in the following tables of the Workplan:\n"
        holiday_found = False

        # Check due dates in next_week_workplan
        for row in doc.next_week_workplan:
            if row.due_date in holiday_dates:
                holiday_found = True
                error_message += f"- {row.due_date}: Next Week's Workplan\n"

        # Check due dates in end_of_the_week
        for row in doc.end_of_the_week:
            if row.due_date in holiday_dates:
                holiday_found = True
                error_message += f"- {row.due_date}: End of the Week\n"

        # Check due dates in additional_activities
        for row in doc.additional_activities:
            if row.due_date in holiday_dates:
                holiday_found = True
                error_message += f"- {row.due_date}: Additional Activities\n"

        if holiday_found:
            frappe.throw(error_message)


@frappe.whitelist()
def create_employee_exit_checklist(employee_name, relieving_date):
    # Check if any Employee Exit Checklist record exists for the employee
    exit_checklist_exists = frappe.db.exists(
        "Employee Exit Checklist", {"employee_name": employee_name}
    )

    if not exit_checklist_exists:
        # Create a new Employee Exit Checklist record
        employee_exit_checklist = frappe.new_doc("Employee Exit Checklist")
        employee_exit_checklist.employee_name = employee_name
        employee_exit_checklist.exit_date = relieving_date

        # Fetch and add records to hr_checklist_table
        hr_exit_activities = frappe.get_all(
            "Exit Activity",
            filters={"unit": "HR", "enable": 1},
            fields=["exit_activity"],
        )
        for activity in hr_exit_activities:
            employee_exit_checklist.append(
                "hr_checklist_table", {"activity": activity.exit_activity}
            )

        # Fetch and add records to it_checklist_table
        it_exit_activities = frappe.get_all(
            "Exit Activity",
            filters={"unit": "IT", "enable": 1},
            fields=["exit_activity"],
        )
        for activity in it_exit_activities:
            employee_exit_checklist.append(
                "it_checklist_table", {"activity": activity.exit_activity}
            )

        # Fetch and add records to finance_checklist_table
        finance_exit_activities = frappe.get_all(
            "Exit Activity",
            filters={"unit": "Finance", "enable": 1},
            fields=["exit_activity"],
        )
        for activity in finance_exit_activities:
            employee_exit_checklist.append(
                "finance_checklist_table", {"activity": activity.exit_activity}
            )

        # Fetch and add records to admin_checklist_table
        admin_exit_activities = frappe.get_all(
            "Exit Activity",
            filters={"unit": "Admin", "enable": 1},
            fields=["exit_activity"],
        )
        for activity in admin_exit_activities:
            employee_exit_checklist.append(
                "admin_checklist_table", {"activity": activity.exit_activity}
            )

        # Save the Employee Exit Checklist record
        employee_exit_checklist.save()

        # Print response
        frappe.msgprint("Employee Exit Checklist created successfully!")


def validate_if_applicant_has_applied(doc, method):
    # Calculate the date 3 months ago from today
    three_months_ago = add_to_date(now(), months=-3)
    email_id = doc.email_id

    # Fetch the job applicant with the given email_id created within the last 3 months
    job_applicant = frappe.db.sql(
        f"""
        SELECT name, applicant_name 
        FROM `tabJob Applicant` 
        WHERE email_id = %s
        AND creation >= '{three_months_ago}'
        """,
        (email_id,),
        as_dict=True,
    )

    # If a matching job applicant is found, raise an error with their applicant_name
    if job_applicant:
        frappe.throw(
            f"Hi {job_applicant[0]['applicant_name']}, you have applied for a job already in the past 3 months. Please note that you are only allowed to apply for 1 job opening in a 3-month period."
        )


def validate_if_a_vehicle_is_available(doc, method):
    # Get start and end times from the form
    current_doc_start_time = doc.start_time
    current_doc_end_time = doc.end_time

    # Fetch all vehicles that are currently "In Service"
    available_vehicles = frappe.db.sql(
        """
        SELECT name 
        FROM `tabVehicle` 
        WHERE status = 'In Service'
    """,
        as_dict=True,
    )

    if not available_vehicles:
        frappe.throw("There are no vehicles currently in service")

    # Prepare the list of available vehicles
    vehicle_names = [v["name"] for v in available_vehicles]

    if not vehicle_names:
        frappe.throw("No available vehicles found.")

    # Check if any of the available vehicles are booked during the selected time range
    vehicle_bookings = frappe.db.sql(
        """
        SELECT vehicle, start_time, end_time 
        FROM `tabVehicle Booking System` 
        WHERE vehicle IN ({})
        AND name != %s
        AND (
            (start_time <= %s AND end_time >= %s) OR
            (start_time <= %s AND end_time >= %s)
        )
    """.format(
            ",".join(["%s"] * len(vehicle_names))
        ),  # This generates placeholders for the vehicle names
        tuple(vehicle_names)
        + (
            doc.name,
            current_doc_start_time,
            current_doc_start_time,
            current_doc_end_time,
            current_doc_end_time,
        ),
        as_dict=True,
    )

    # If bookings are found, display an error with the booked vehicles and their times
    if vehicle_bookings:
        bookings_info = "<br>".join(
            [
                f"Vehicle: {b['vehicle']}, Start: {b['start_time']}, End: {b['end_time']}"
                for b in vehicle_bookings
            ]
        )
        frappe.throw(
            f"There are no vehicles available for your selected timeslot. <br><br>These are the current bookings for your timeslot:<br>{bookings_info}"
        )

    # If no conflicts exist, just pass
    pass


import frappe
from frappe.utils import today, getdate, get_first_day, get_last_day


def update_deliverable_expended_amounts():
    # Step 1: Fetch Budget Threshold records for the current fiscal year
    current_year = getdate(today()).year
    fiscal_start_date = get_first_day(f"{current_year}-01-01")
    fiscal_end_date = get_last_day(f"{current_year}-12-31")

    # Fetch all deliverable thresholds for the current fiscal year where budget_against is 'Project'
    deliverable_thresholds = frappe.db.sql(
        """
        SELECT bt.deliverable, bt.budget_threshold, bt.amount_expended, bt.parent, b.project
        FROM `tabBudget Threshold` bt
        JOIN `tabBudget` b ON bt.parent = b.name
        WHERE b.fiscal_year = %s
        AND b.budget_against = 'Project'
        AND b.docstatus = 1
    """,
        (current_year,),
        as_dict=True,
    )

    # Step 2: Fetch Purchase Invoice Items that match the criteria
    purchase_invoice_items = frappe.db.sql(
        """
        SELECT pii.deliverable, pii.base_amount, pii.parent
        FROM `tabPurchase Invoice Item` pii
        JOIN `tabPurchase Invoice` pi ON pii.parent = pi.name
        WHERE pi.posting_date BETWEEN %s AND %s
        AND pi.status IN ('Paid', 'Partly Paid')
        AND pi.docstatus = 1
        AND pii.deliverable IS NOT NULL

    """,
        (fiscal_start_date, fiscal_end_date),
        as_dict=True,
    )
    # print(purchase_invoice_items)

    # JOIN `tabBudget` b ON pi.project = b.project

    # Step 3: Sum up base_amounts for each deliverable and update the amount_expended on Deliverable Thresholds
    deliverable_expenses = {}

    for item in purchase_invoice_items:
        deliverable = item.deliverable
        if deliverable in deliverable_expenses:
            deliverable_expenses[deliverable] += item.base_amount
        else:
            deliverable_expenses[deliverable] = item.base_amount

    for threshold in deliverable_thresholds:
        deliverable = threshold.deliverable
        if deliverable in deliverable_expenses:
            # Step 4: Round the expended amount to 2 decimal places
            expended_amount = round(deliverable_expenses[deliverable], 2)
            # print(deliverable_expenses)

            # Update amount_expended for the matching deliverable
            frappe.db.set_value(
                "Budget Threshold",
                {"parent": threshold.parent, "deliverable": deliverable},
                "amount_expended",
                expended_amount,
            )

    frappe.db.commit()
