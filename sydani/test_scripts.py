import frappe
from datetime import date, timedelta, datetime
from sydani.tasks import get_speedexam_auth_header
from frappe.utils import date_diff, add_days, getdate, add_to_date, now
from datetime import date, timedelta, datetime
from sydani.payment import fetch_transfer, create_transaction_log
import requests
import json
import ast
from datetime import datetime
from textwrap import dedent


def create_new_workplan():
    import datetime

    today = datetime.date.today()
    workplans = frappe.db.sql(
        """
        SELECT * 
        FROM `tabWork Plan` 
        WHERE next_week_work_plan_created = 0 
        AND work_week_begins_on >= '23-10-2023' 
        AND docstatus = 1
        AND name LIKE "Ekomobong Akwaowo - 2023-10-23"
        AND leave_nextweek = "No"
    """,
        as_dict=True,
    )

    for workplan in workplans:

        existing_workplan = frappe.db.exists(
            "Work Plan",
            {
                "employee": workplan.employee,
                "work_week_begins_on": workplan.next_work_week_begins_on,
            },
        )
        if existing_workplan:
            print(
                f"Work Plan for {workplan.employee} on {workplan.next_work_week_begins_on} already exists. Skipping creation."
            )
            continue

        print(f"Processing Work Plan: {workplan.name}")
        new_workplan = frappe.new_doc("Work Plan")
        new_workplan.update(workplan)
        new_workplan.employee = workplan.employee
        new_workplan.workflow_state = "Draft"
        new_workplan.supervisor = workplan.supervisor
        new_workplan.supervisor_2 = workplan.supervisor_2
        new_workplan.principal = workplan.principal
        new_workplan.work_week_begins_on = workplan.next_work_week_begins_on
        new_workplan.work_week_begins_date = workplan.next_work_week_begins_on
        new_workplan.submission = workplan.next_weeks_submission
        new_workplan.approval = workplan.next_weeks_approval
        new_workplan.submission_time = workplan.next_weeks_submission_time
        new_workplan.approval_time = workplan.next_weeks_approval_time
        new_workplan.responsible_person = "Employee"
        new_workplan.copy_workplan = workplan.name
        new_workplan.work_from_home_date = ""
        new_workplan.docstatus = 0
        new_workplan.completion_rate = 0
        new_workplan.workplan_created_from_previous = 1

        # Set the name of the Work Plan using employee and work_week_begins_on

        new_workplan.name = f"{workplan.employee} - {workplan.next_work_week_begins_on}"

        for child_next_week in frappe.db.sql(
            """
                SELECT 
                    project, theme, activity, due_date, status, deliverable
                FROM `tabWork Plan Details Next Week`
                WHERE parent=%s
            """,
            (workplan.name,),
            as_dict=True,
        ):
            print(
                f"Copying Child: {child_next_week.name} from Work Plan: {workplan.name} to 'end_of_the_week' table"
            )
            new_child_end_of_week = new_workplan.append("end_of_the_week", {})
            new_child_end_of_week.update(
                {
                    "project": child_next_week.project,
                    "theme": child_next_week.theme,
                    "activity": child_next_week.activity,
                    "due_date": child_next_week.due_date,
                    "status": child_next_week.status,
                    "deliverable": child_next_week.deliverable,
                }
            )

        for child_next_week in frappe.db.sql(
            """
                SELECT 
                    project, theme, activity, due_date, status, deliverable
                FROM `tabWork Plan Details Next Week`
                WHERE parent=%s
            """,
            (workplan.name,),
            as_dict=True,
        ):
            print(
                f"Copying Child: {child_next_week.name} from Work Plan: {workplan.name} to 'beginning_of_the_week' table"
            )
            new_child_beginning_of_week = new_workplan.append(
                "beginning_of_the_week", {}
            )
            new_child_beginning_of_week.update(
                {
                    "project": child_next_week.project,
                    "theme": child_next_week.theme,
                    "activity": child_next_week.activity,
                    "due_date": child_next_week.due_date,
                    "status": child_next_week.status,
                    "deliverable": child_next_week.deliverable,
                }
            )

        # # Check if a record with the same name already exists
        # existing_record = frappe.db.exists("Work Plan", new_workplan.name)
        # if not existing_record:
        #     new_workplan.insert()
        #     frappe.db.commit()
        #     print(f"Work Plan {new_workplan.name} created successfully")

        # else:
        #     print(f"Work Plan with name {new_workplan.name} already exists. Skipped creating this record.")

        existing_record = frappe.db.exists("Work Plan", new_workplan.name)
        if not existing_record:
            # After the document is saved
            # # Rename the document

            # # Extracting the date components
            # work_week_begins_on = datetime.strptime(new_workplan.work_week_begins_on, '%d-%m-%Y').strftime('%Y-%m-%d')
            # new_workplan.name = f"{new_workplan.employee} - {new_workplan.work_week_begins_date}"
            # Change the workflow state based on the new state you desire
            # new_workplan.workflow_state = "Reviewed"
            print(f"Work Plan {new_workplan.name} created successfully")
            new_workplan.save()
            updated_name = (
                f"{new_workplan.employee} - {new_workplan.work_week_begins_date}"
            )
            frappe.rename_doc("Work Plan", f"{new_workplan.employee} -", updated_name)

            # frappe.db.commit()
            print(f"Work Plan {new_workplan.name} created successfully")
        else:
            print(
                f"Work Plan with name {new_workplan.name} already exists. Skipped creating this record."
            )

        # Assuming the next_week_work_plan_created field is a check field
        frappe.db.set_value(
            "Work Plan", workplan.name, "next_week_work_plan_created", 1
        )

    frappe.db.commit()


# create_new_workplan()


@frappe.whitelist()
def get_user_roles(user):
    user_roles = frappe.get_roles(user)
    return user_roles


# speed exam


def get_speedexam_candidates():
    # try:
    # Get authorization header
    base_url = "https://apiv2.speedexam.net/"
    get_candidates_header = get_speedexam_auth_header("07")
    # get_candidates_url = f"""{base_url}api/Employee/Get Candidate List?Groupid=149&Page_no=1&Page_size=100"""
    get_candidates_url = (
        f"""{base_url}api/Employee/Get Candidate List?Page_no=1&Page_size=100"""
    )
    candidates_request = requests.get(get_candidates_url, headers=get_candidates_header)
    candidates_request_json = candidates_request.json()

    if candidates_request_json["status"] == 200:
        candidates = json.loads(candidates_request_json["result"])
        for candidate in candidates:
            candidate_id = candidate["candidateid"]
            candidate_username = candidate["username"]
            candidate_email = candidate["email"]

            candidate_application = frappe.db.sql(
                f"""
                SELECT name, job_title, phone_number, assessment_password  
                FROM `tabJob Applicant` 
                WHERE email_id = '{candidate_email}' """,
                as_dict=True,
            )

            try:
                candidate_application = candidate_application[0]

                candidate_data = {
                    "firstName": candidate["firstname"],
                    "lastName": candidate["lastname"],
                    "street": candidate_application["name"],
                    "phone": candidate_application["phone_number"],
                    "mobile": candidate_application["phone_number"],
                    "email": candidate["email"],
                    "userName": candidate["email"],
                    "password": candidate_application["assessment_password"],
                    "isActive": "True",
                }

                if candidate_application.job_title == "sydani-fellowship-program":
                    candidate_data["groupsequenceId"] = 138
                else:
                    candidate_data["groupsequenceId"] = 159

                if candidate["email"] == "emmanuelezeh14@gmail.com":
                    delete_exam_url = f"""{base_url}api/Exams/Clear-Candidate-Exam-History?CandidateID={candidate_id}"""
                    # delete_exam_header = get_speedexam_auth_header("14")
                    delete_exam_request = requests.delete(delete_exam_url)
                    # emmanuelezeh14@gmail.com
                    print(delete_exam_request.json())
                    print(candidate_data)
                    break
                # /api/Employee/Delete-Candidate -> use delete method -> CandidateID
                # /api/Exams/Clear-Candidate-Exam-History -> use delete method -> CandidateID

                # clear exam history
                # delete_exam_url = f"""{base_url}api/Exams/Clear-Candidate-Exam-History?CandidateID={candidate_id}"""
                # delete_exam_header = get_speedexam_auth_header("14")
                # delete_exam_request = requests.delete(delete_exam_url, headers=delete_exam_header)

                #     # Add candidate url
                # delete_candidate_header = get_speedexam_auth_header("14")
                # delete_candidate_url = f"""{base_url}api/Employee/Delete-Candidate?CandidateID={candidate_id}"""
                # delete_candidate_request = requests.delete(delete_candidate_url, headers=delete_candidate_header)

                #     # Create a candidate on speed speedexam
                # add_candidate_header = get_speedexam_auth_header("06")
                # add_candidate_url = "https://apiv2.speedexam.net/api/Employee/Create a New Candidate"
                # add_candidate_request = requests.post(
                #     add_candidate_url, json=candidate_data, headers=add_candidate_header
                # )

                # add_candidate_request_json = add_candidate_request.json()

                # response_to_object = json.loads(add_candidate_request_json["result"])

                # print(response_to_object)
            except Exception as e:
                print(e)


# Define the method to fetch and create records
def fetch_and_create_email_group_members():
    # Fetch Job Applicants with subscription = 1
    job_applicants = frappe.get_list(
        "Job Applicant", filters={"subscription": 1}, fields=["name", "email"]
    )

    # Loop through the fetched records
    for applicant in job_applicants:
        # Check if the email is not empty
        if applicant.get("email"):
            # Check if the email already exists in Email Group Member
            email_exists = frappe.get_value(
                "Email Group Member", {"email": applicant.get("email")}
            )

            # If email does not exist, create Email Group Member record
            if not email_exists:
                # Create Email Group Member record
                email_group_member = frappe.new_doc("Email Group Member")
                email_group_member.email_group = "Job Applicants"
                email_group_member.email = applicant.get("email")

                # Save the Email Group Member record
                email_group_member.insert(ignore_permissions=True)

                # Set subscription to 0 after creating Email Group Member
            frappe.db.set_value("Job Applicant", applicant["name"], "subscription", 0)


# Define the method to fetch and create records
def fetch_and_create_email_group_members_vendors():
    # Fetch Suppliers with subscription = 1
    suppliers = frappe.get_list(
        "Supplier", filters={"subscription": 1}, fields=["name", "email"]
    )

    # Loop through the fetched records
    for supplier in suppliers:
        # Check if the email is not empty
        if supplier.get("email"):
            # Check if the email already exists in Email Group Member
            email_exists = frappe.get_value(
                "Email Group Member", {"email": supplier.get("email")}
            )

            # If email does not exist, create Email Group Member record
            if not email_exists:
                # Create Email Group Member record
                email_group_member = frappe.new_doc("Email Group Member")
                email_group_member.email_group = "Vendors"
                email_group_member.email = supplier.get("email")

                # Save the Email Group Member record
                email_group_member.insert(ignore_permissions=True)

                # Set subscription to 0 after creating Email Group Member
            frappe.db.set_value("Supplier", supplier["name"], "subscription", 0)


import frappe
from frappe.utils import getdate


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
def calculate_working_and_present_days(start_date, end_date, employee):

    # calculate and set difference in days
    difference_in_days = (getdate(end_date) - getdate(start_date)).days + 1

    # Fetch the 'Sydani Holidays' list
    holiday_list = frappe.get_doc("Holiday List", "Sydani Holidays")

    # Count holidays that are between start_date and end_date
    num_holidays = sum(
        getdate(holiday.holiday_date) >= getdate(start_date)
        and getdate(holiday.holiday_date) <= getdate(end_date)
        for holiday in holiday_list.holidays
    )

    # Fetch attendances between the start_date and end_date which are not marked as 'Absent'
    attendances = frappe.get_all(
        "Attendance",
        filters={
            "employee": employee,
            "attendance_date": ["between", [start_date, end_date]],
            "status": ["!=", "Absent"],
        },
    )

    num_attendances = len(attendances)

    # Calculate number of present days
    number_of_days_present = num_attendances

    # Calculate number of working days
    number_of_working_days = difference_in_days - num_holidays

    return number_of_working_days, number_of_days_present


import frappe


def get_employees_with_checkin_issues():
    # Get the current year
    current_year = datetime.now().year
    start_of_year = datetime(current_year, 1, 1)

    # Fetch employees and their hire dates for the current year
    employees = frappe.get_all(
        "Employee",
        filters={"date_of_joining": (">=", start_of_year)},
        fields=["name", "date_of_joining", "creation"],
    )

    # List to store employees with check-in issues
    employees_with_issues = []

    # Iterate through each employee
    for employee in employees:
        # Fetch check-in records for the employee where check-in time is earlier than hire date
        checkin_records = frappe.get_all(
            "Employee Checkin",
            filters={
                "employee": employee.name,
                "time": ("<", employee.date_of_joining),
            },
            fields=["name"],
        )

        # If there are any check-in records meeting the condition, add the employee to the list
        if checkin_records:
            employees_with_issues.append(employee)

    return employees_with_issues


# Call the function to get employees with check-in issues
# employees_with_issues = get_employees_with_checkin_issues()
# print(employees_with_issues)


import frappe
from collections import defaultdict


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


def process_attendance_records():
    start_date = "2024-11-07"
    end_date = "2024-12-31"
    # Fetch records from Attendance doctype between the given dates where status is Absent
    attendance_records = frappe.get_all(
        "Attendance",
        filters={
            "attendance_date": ["between", [start_date, end_date]],
            "status": "Absent",
        },
        fields=["name"],
    )

    # Cancel and delete the fetched attendance records
    for record in attendance_records:
        attendance_doc = frappe.get_doc("Attendance", record.name)
        attendance_doc.cancel()
        attendance_doc.delete()

    # Fetch records from Employee Checkin doctype between the given dates where skip_auto_attendace is 1
    checkin_records = frappe.get_all(
        "Employee Checkin",
        filters={
            "time": ["between", [start_date, end_date]],
            "skip_auto_attendance": 1,
        },
        fields=["name"],
    )

    # Update the skip_auto_attendance field for fetched records to 0
    for record in checkin_records:
        checkin_doc = frappe.get_doc("Employee Checkin", record.name)
        checkin_doc.skip_auto_attendance = 0
        checkin_doc.save()


def ai_test():
    # get `Job Opening -> name` from `Job Applicant -> job_title`

    job_applicants = frappe.db.sql(
        f""" 
        SELECT applicant_name, email_id, 
        status, job_title, 
        CONCAT('https://office.sydani.org', resume_attachment) AS cv_link 
        FROM `tabJob Applicant`
        WHERE status = 'Application Submitted' 
       
    """,
        as_dict=True,
    )

    if len(job_applicants) > 0:
        job_opening = job_applicants[0]["job_title"]

        required_qualifications = frappe.db.sql(
            f""" 
            SELECT required_qualifications 
            FROM `tabJob Opening` 
            WHERE name = '{job_opening}'
        """,
            as_dict=True,
        )[0]["required_qualifications"]

        for applicant in job_applicants:

            cv_url = applicant["cv_link"]

            data = {"cv_url": cv_url, "criteria": required_qualifications}

            request_data = requests.post(
                "http://127.0.0.1:8001/ai/api/screen", json=data
            ).json()

            print(request_data)

            break

    else:
        print("No applicants")


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


# @frappe.whitelist()
# def fetch_and_combine_records(
#     employee, start_date, end_date, holiday_list, project=None
# ):
#     employee_project_records = frappe.db.sql(
#         f"""SELECT name, percentage_fte, hourly_rate
#             FROM `tabProject FTE Assignment`
#             WHERE employee = '{employee}'
#             AND parent = '{project}'""",
#     )

#     # Check if any records were returned before accessing the first element
#     if employee_project_records:
#         # Access the first element of the first tuple in the list
#         percentage_fte = employee_project_records[0][1]
#         hourly_rate = employee_project_records[0][2]
#     else:
#         # Handle the case where no records were returned
#         percentage_fte = None
#         hourly_rate = None

#     combined_records = []  # List to store combined records

#     # Fetching work plans based on employee
#     work_plans = frappe.db.sql(
#         f"""SELECT name, employee
#             FROM `tabWork Plan`
#             WHERE employee = '{employee}'""",
#         as_dict=True,
#     )

#     for work_plan in work_plans:
#         # Fetching additional activity records based on the parent work plan, status "Done," and date range
#         additional_activity_records = frappe.db.sql(
#             f"""SELECT name, activity, due_date, project, status, hours, '{percentage_fte}' as percentage_fte, '{hourly_rate}' as hourly_rate
#                 FROM `tabWork Plan Details Additional Activities`
#                 WHERE parent = '{work_plan['name']}'
#                 AND status = "Done"
#                 AND hours > 0
#                 {'AND project = %s' % repr(project) if project else ''}
#                 AND due_date BETWEEN '{start_date}' AND '{end_date}'""",
#             as_dict=True,
#         )
#         combined_records.extend(additional_activity_records)

#         # Fetching end of week records based on the parent work plan, status "Done," and date range
#         end_of_week_records = frappe.db.sql(
#             f"""SELECT name, activity, due_date, project, status, hours, '{percentage_fte}' as percentage_fte, '{hourly_rate}' as hourly_rate
#                 FROM `tabWork Plan Details End of Week`
#                 WHERE parent = '{work_plan['name']}'
#                 AND status = "Done"
#                 AND hours > 0
#                 {'AND project = %s' % repr(project) if project else ''}
#                 AND due_date BETWEEN '{start_date}' AND '{end_date}'""",
#             as_dict=True,
#         )
#         combined_records.extend(end_of_week_records)

#     public_holidays = frappe.db.sql(
#         f"""SELECT name, holiday_date, weekly_off
#         From `tabHoliday`
#         WHERE holiday_date BETWEEN '{start_date}' AND '{end_date}'
#         AND parent = '{holiday_list}'
#         AND weekly_off = 0""",
#         as_dict=True,  # Convert the result to a list of dictionaries
#     )

#     # Matching columns and values
#     matched_records = []

#     for holiday in public_holidays:
#         matched_record = {
#             # "name": holiday["name"],  # Assuming the name column exists in both tables
#             "activity": "Public Holiday",
#             "due_date": holiday["holiday_date"],
#             "project": project,
#             "status": "Done",  # Assuming this is a constant value for public holidays
#             "hours": 8 * percentage_fte / 100,
#             "hourly_rate": hourly_rate,
#         }
#         matched_records.append(matched_record)

#     combined_records.extend(matched_records)

#     # Sort combined_records by due date
#     sorted_records = sorted(combined_records, key=lambda x: x.get("due_date"))

#     return sorted_records


# def sorted_records():
#     data = fetch_and_combine_records(
#         employee="Raheenat Sunmisola Mohammed",
#         project="Dial-a-Doc",
#         start_date="2024-01-02",
#         end_date="2024-06-15",
#         holiday_list="Sydani Holidays",
#     )

#     print(data)


import frappe


@frappe.whitelist()
def create_or_update_vendor_evaluation_sheet(doc, method):
    # Ensure this function runs only when the Vendor Evaluation document is saved
    if method != "on_update":
        return

    # Check each evaluator role individually and create/update Vendor Evaluation Sheet accordingly
    if doc.hr_evaluator and doc.docstatus == 0:
        create_or_update_sheet_for_evaluator(doc, "HR", doc.hr_evaluator)

    if doc.admin_evaluator and doc.docstatus == 0:
        create_or_update_sheet_for_evaluator(doc, "Admin", doc.admin_evaluator)

    if doc.operations_evaluator and doc.docstatus == 0:
        create_or_update_sheet_for_evaluator(
            doc, "Operations", doc.operations_evaluator
        )

    if doc.programs_evaluator and doc.docstatus == 0:
        create_or_update_sheet_for_evaluator(doc, "Programs", doc.programs_evaluator)


def create_or_update_sheet_for_evaluator(doc, evaluator_role, evaluator):
    # Check if Vendor Evaluation Sheet exists for this evaluator role
    vendor_evaluation_sheet = frappe.get_list(
        "Vendor Evaluation Sheet",
        filters={"vendor_evaluation": doc.name, "evaluators_role": evaluator_role},
        fields=["name"],
    )

    if vendor_evaluation_sheet:
        # Get existing Vendor Evaluation Sheet document
        vendor_evaluation_sheet_doc = frappe.get_doc(
            "Vendor Evaluation Sheet", vendor_evaluation_sheet[0].name
        )

        # Only update if docstatus is 0 (draft)
        if vendor_evaluation_sheet_doc.docstatus == 0:
            vendor_evaluation_sheet_doc.evaluator = evaluator
    else:
        # Create new Vendor Evaluation Sheet
        vendor_evaluation_sheet_doc = frappe.new_doc("Vendor Evaluation Sheet")
        vendor_evaluation_sheet_doc.vendor_evaluation = doc.name
        vendor_evaluation_sheet_doc.rating_guide_link = "f89273916e"  # Example link
        vendor_evaluation_sheet_doc.vendor = doc.vendor
        vendor_evaluation_sheet_doc.vendor_type = doc.vendor_type
        vendor_evaluation_sheet_doc.vendor_evaluation_period = (
            doc.vendor_evaluation_period
        )
        vendor_evaluation_sheet_doc.evaluators_role = evaluator_role
        vendor_evaluation_sheet_doc.evaluator = evaluator

    # Fetch Vendor Competencies for the specified evaluator role and enabled status
    competencies = frappe.get_list(
        "Vendor Competencies",
        filters={"enabled": 1, "evaluator": evaluator_role},
        fields=[
            "name",
            "broad_competency",
            "specific_competency",
            "description",
            "weight_factor",
        ],
    )

    # Clear existing competencies and add new ones
    vendor_evaluation_sheet_doc.set("competencies", [])

    for competency in competencies:
        vendor_evaluation_sheet_doc.append(
            "competencies",
            {
                "competency": competency.name,
                "broad_competency": competency.broad_competency,
                "specific_competency": competency.specific_competency,
                "description": competency.description,
                "weight_factor": competency.weight_factor,
            },
        )

    vendor_evaluation_sheet_doc.save()


import frappe
from frappe.utils import now_datetime, add_days


def delete_old_records():
    # Calculate the cutoff date which is 2 weeks ago from today
    cutoff_date = add_days(now_datetime(), -21)

    # Fetch and delete old records from Email Queue
    email_queue_records = frappe.get_all(
        "Email Queue",
        filters={"creation": ["<", cutoff_date]},
        limit=500,
        fields=["name"],
    )
    for record in email_queue_records:
        frappe.delete_doc("Email Queue", record["name"])

    # Fetch and delete old records from Error Log
    error_log_records = frappe.get_all(
        "Error Log",
        filters={"creation": ["<", cutoff_date]},
        limit=500,
        fields=["name"],
    )
    for record in error_log_records:
        frappe.delete_doc("Error Log", record["name"])

    frappe.db.commit()


def reset_cv_review():
    cvs = frappe.get_all(
        "Job Applicant", filters={"status": ["in", ["Awaiting Review", "Rejected ATS"]]}
    )
    for cv in cvs:
        cv_doc = frappe.get_doc("Job Applicant", cv.name)
        cv_doc.cv_review_date = None
        cv_doc.cv_score = None
        cv_doc.ai_response = None
        cv_doc.recommended_role = None
        cv_doc.status = "Application Submited"
        cv_doc.score_on_recommended_role = None
        cv_doc.feedback_on_recommended_role = None
        cv_doc.save()


def get_doctypes():
    expense_claim = frappe.get_doc("Expense Claim", "PV_NO:202407220002")
    # Dictionary to store all fields and their values
    result = {}

    # Fetch specific fields from the main Expense Claim document
    main_fields = ["name", "purpose", "used_by", "project_2"]
    result["doctype_fields"] = {
        field: expense_claim.get(field) for field in main_fields
    }

    # Fetch all fields from the child table 'expenses'
    result["expenses"] = []

    for expense in expense_claim.expenses:
        result["expenses"].append(
            {fieldname: value for fieldname, value in expense.as_dict().items()}
        )

    # Print the result to the console
    print(result)


import frappe
import json
from frappe.utils import now_datetime


def fetch_expense_claim_details():
    expense_claim_name = "PV_NO:202407220002"

    # Fetch the main doctype fields
    expense_claim = frappe.get_doc("Expense Claim", expense_claim_name)
    expense_claim_fields = {
        "name": expense_claim.name,
        "purpose": expense_claim.purpose,
        "used_by": expense_claim.used_by,
        "project_2": expense_claim.project_2,
    }

    # Fetch the child table records from 'expenses'
    expenses = []
    for expense in expense_claim.expenses:
        expenses.append(
            {
                "name": expense.name,
                "owner": expense.owner,
                "creation": expense.creation.isoformat(),
                "modified": expense.modified.isoformat(),
                "modified_by": expense.modified_by,
                "parent": expense.parent,
                "parentfield": expense.parentfield,
                "parenttype": expense.parenttype,
                "idx": expense.idx,
                "docstatus": expense.docstatus,
                "expense_date": expense.expense_date.isoformat(),
                "deliverable": expense.deliverable,
                "expense_type": expense.expense_type,
                "default_account": expense.default_account,
                "description": expense.description,
                "description_2": expense.description_2,
                "frequency": expense.frequency,
                "quantity": expense.quantity,
                "unit_cost": expense.unit_cost,
                "amount": expense.amount,
                "sanctioned_amount": expense.sanctioned_amount,
                "cost_center": expense.cost_center,
                "doctype": "Expense Claim Detail",
            }
        )

    # Combine the main doctype and child table data
    result = {"expense_claim_fields": expense_claim_fields, "expenses": expenses}

    print(result)
    return result


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
from datetime import timedelta


@frappe.whitelist()
def fetch_and_reconcile_entries(from_date, to_date, company, bank_account):
    try:
        # Fetch bank transactions from the Bank Transactions doctype based on the provided filters
        query = """
            SELECT name, date, withdrawal, deposit, status, bank_account, company, reference_number, description
            FROM `tabBank Transaction`
            WHERE company = %s
            AND bank_account = %s
            AND status IN ("Pending", "Unreconciled")
            AND date BETWEEN %s AND %s
            AND (currency != 'NGN' OR (currency = 'NGN' AND withdrawal > 55))
        """
        bank_transactions = frappe.db.sql(
            query, (company, bank_account, from_date, to_date), as_dict=True
        )
        # AND name = "ACC-BTN-2024-00134"
        # Process each bank transaction
        for bank_transaction in bank_transactions:
            company = bank_transaction["company"]
            bank_account = bank_transaction["bank_account"]
            bank_transaction_date = bank_transaction["date"]
            reference_number = bank_transaction.get("reference_number")
            description = bank_transaction.get("description")

            # Calculate the date range (a day before and after the bank transaction date)
            date_lower_bound = bank_transaction_date - timedelta(days=1)
            date_upper_bound = bank_transaction_date + timedelta(days=1)

            # Query the Payment Entry table for matching records
            payment_entry_query = """
                SELECT name, reference_no, reference_date, payment_narration
                FROM `tabPayment Entry`
                WHERE company = %s
                AND bank_account = %s
                AND reference_date BETWEEN %s AND %s
                AND docstatus = 1
            """
            payment_entries = frappe.db.sql(
                payment_entry_query,
                (company, bank_account, date_lower_bound, date_upper_bound),
                as_dict=True,
            )

            # Find matching payment entry
            matching_entry = None
            for payment_entry in payment_entries:
                if (
                    reference_number
                    and payment_entry["reference_no"] == reference_number
                ):
                    matching_entry = payment_entry
                    break

                # Check for 30-character match in description and payment_narration
                if description and payment_entry["payment_narration"]:
                    for i in range(len(description) - 29):
                        desc_substring = description[i : i + 30]
                        if desc_substring in payment_entry["payment_narration"]:
                            matching_entry = payment_entry
                            break

            if matching_entry:
                # Perform reconciliation
                pe_doc = frappe.get_doc("Payment Entry", matching_entry["name"])
                bt_doc = frappe.get_doc("Bank Transaction", bank_transaction["name"])

                allocated_amount = (
                    bt_doc.deposit if bt_doc.deposit > 0 else bt_doc.withdrawal
                )

                if (pe_doc.allocated_amount_bt + allocated_amount) > pe_doc.paid_amount:
                    continue  # Skip reconciliation if allocated amount exceeds paid amount

                bt_row = bt_doc.append("payment_entries", {})
                bt_row.payment_document = "Payment Entry"
                bt_row.payment_entry = matching_entry["name"]
                bt_row.allocated_amount = allocated_amount

                pe_row = pe_doc.append("bank_transactions", {})
                pe_row.bank_transaction = bank_transaction["name"]

                pe_doc.allocated_amount_bt += allocated_amount
                pe_doc.unallocated_amount_bt = (
                    pe_doc.paid_amount - pe_doc.allocated_amount_bt
                )

                if pe_doc.allocated_amount_bt < pe_doc.paid_amount:
                    pe_doc.bank_reconciliation_status = "Partly Reconciled"
                elif pe_doc.allocated_amount_bt == pe_doc.paid_amount:
                    pe_doc.bank_reconciliation_status = "Reconciled"

                pe_doc.save()
                bt_doc.payment_entry_updated = 1
                bt_doc.save()

                frappe.db.commit()
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Reconciliation Error")
        return {"status": "error", "message": str(e)}

    return {"status": "success", "message": "Reconciliation completed successfully."}


def test_reconciliation_process():
    """
    Test the bank transaction reconciliation process by fetching bank transactions,
    finding matching payment entries, and updating the records. This function
    can be executed using `bench execute`.
    """
    from_date = "2024-05-01"
    to_date = "2024-10-31"
    company = "Sydani Technologies"
    bank_account = "1500615136 - Sydani Tech - Access Bank"

    print(
        f"Starting reconciliation process for company: {company}, bank account: {bank_account}, from date: {from_date} to date: {to_date}"
    )

    # Call the function to fetch and reconcile entries
    fetch_and_reconcile_entries(from_date, to_date, company, bank_account)

    print("\nReconciliation process completed.")


@frappe.whitelist()
def fetch_and_create_journal_entry(from_date, to_date, company, bank_account):
    try:
        # Fetch bank transactions from the Bank Transaction doctype based on the provided filters
        query = """
            SELECT name, date, withdrawal, deposit, status, bank_account, company, reference_number, description, currency
            FROM `tabBank Transaction`
            WHERE company = %s
            AND bank_account = %s
            AND status IN ("Pending", "Unreconciled")
            AND date BETWEEN %s AND %s
            AND withdrawal > 0  
            AND withdrawal < 55
            AND currency = 'NGN'
        """
        bank_transactions = frappe.db.sql(
            query, (company, bank_account, from_date, to_date), as_dict=True
        )
        # AND name IN ("ACC-BTN-2024-00162", "ACC-BTN-2024-00161", "ACC-BTN-2024-00160")
        if not bank_transactions:
            frappe.throw("No matching bank charges found.")

        # Log fetched transactions for debugging
        frappe.logger().debug(f"Fetched bank transactions: {bank_transactions}")

        # Fetch bank account's account
        ledger_account = frappe.db.get_value("Bank Account", bank_account, "account")
        # Fetch the bank charges account from the Company linked to the bank account
        bank_charges_account = frappe.db.get_value(
            "Company", company, "bank_charges_account"
        )

        if not bank_charges_account:
            frappe.throw(f"Bank charges account for {company} not found.")

        # Sum all withdrawals for the final debit entry
        total_withdrawals = sum(bt["withdrawal"] for bt in bank_transactions)
        # print(company)
        # print(bank_account)

        # Prepare the Journal Entry document
        journal_entry = frappe.get_doc(
            {
                "doctype": "Journal Entry",
                "voucher_type": "Bank Entry",
                "company": company,
                "posting_date": to_date,  # Set to the to_date
                "cheque_date": to_date,  # Set cheque_date as to_date
                "cheque_no": f"Bank Charges from {from_date} to {to_date}",
                "user_remark": f"Being total bank charges between {from_date} to {to_date} for {bank_account}",
                "title": f"Being total bank charges between {from_date} to {to_date} for {bank_account}",
                "accounts": [],  # Account table entries will be added here
            }
        )

        # Add a row for each bank transaction to the accounts table
        for bank_transaction in bank_transactions:
            # Log transaction details before appending to the journal entry
            frappe.logger().debug(f"Processing bank transaction: {bank_transaction}")

            # Validate fields to avoid the NoneType issue
            bt_bank_account = bank_transaction.get("bank_account", "")
            account = ledger_account
            account_currency = bank_transaction.get("currency", "")
            credit_amount = bank_transaction.get("withdrawal", 0)
            reference_number = bank_transaction.get("description", "N/A")

            if not account or not account_currency or credit_amount is None:
                frappe.logger().error(
                    f"Missing required data in bank transaction: {bank_transaction}"
                )
                frappe.throw(
                    f"Missing required data for transaction {bank_transaction['name']}"
                )

            journal_entry.append(
                "accounts",
                {
                    "account": ledger_account,
                    "bank_account": bt_bank_account,  # Set bank account on bank transaction
                    "account_currency": account_currency,  # Set currency
                    "credit_in_account_currency": credit_amount,  # Set withdrawal as credit
                    "user_remark": reference_number,  # Set reference_number as user_remark
                    "is_advance": "No",
                    "exchange_rate": 1,
                },
            )

        # Add the final row for bank charges with the specific remark
        journal_entry.append(
            "accounts",
            {
                "account": bank_charges_account,  # Set the bank charges account
                "debit_in_account_currency": total_withdrawals,  # Set the total withdrawal sum as debit
                "user_remark": f"Being total bank charges between {from_date} to {to_date} for {bank_account}",
                "is_advance": "No",
                "exchange_rate": 1,
            },
        )

        for bk in journal_entry.accounts:
            print(bk.account)

        # Insert and submit the Journal Entry
        # journal_entry.insert()
        journal_entry.save()
        # Uncomment to submit after testing
        # journal_entry.submit()

        # Fetch and update each bank transaction with the created journal entry
        for bank_transaction in bank_transactions:
            # Fetch the Bank Transaction document
            bt_doc = frappe.get_doc("Bank Transaction", bank_transaction["name"])

            # Append a row to the payment_entries table on the Bank Transaction
            # bt_row = bt_doc.append("payment_entries", {})

            bt_row = {
                "payment_document": "Journal Entry",
                "payment_entry": journal_entry.name,
                "allocated_amount": bank_transaction["withdrawal"],
            }

            bt_doc.append("payment_entries", bt_row)

            # Save the updated Bank Transaction document

            bt_doc.save()

        frappe.db.commit()

        # Return a message with a link to the newly created journal entry
        journal_entry_link = frappe.utils.get_url_to_form(
            "Journal Entry", journal_entry.name
        )
        return {
            "message": f"Journal entry <a href='{journal_entry_link}'>{journal_entry.name}</a> created and bank transactions reconciled successfully."
        }

    except Exception as e:
        # Log the full traceback for debugging
        frappe.log_error(frappe.get_traceback(), "fetch_and_create_journal_entry")
        frappe.logger().error(f"Error occurred: {str(e)}")
        return {"error": str(e)}


def test_bank_charges_reconciliation_process():
    """
    Test the bank transaction reconciliation process by fetching bank transactions,
    creating journal entries, and updating the records. This function can be executed
    using `bench execute`.
    """
    from_date = "2024-05-01"
    to_date = "2024-10-31"
    company = "Sydani Technologies"
    bank_account = "1500615136 - Sydani Tech - Access Bank"

    print(
        f"Starting reconciliation process for company: {company}, bank account: {bank_account}, from date: {from_date} to date: {to_date}"
    )

    try:
        # Call the function to fetch and create journal entry for bank charges reconciliation
        result = fetch_and_create_journal_entry(
            from_date, to_date, company, bank_account
        )

        # Print the result of the reconciliation process (success message or link)
        if "error" in result:
            print(f"An error occurred: {result['error']}")
        else:
            print(f"Success: {result['message']}")

    except Exception as e:
        # If there's an unhandled exception, print the traceback and the error message
        print("An unexpected error occurred during the reconciliation process:")
        frappe.log_error(
            frappe.get_traceback(), "test_bank_charges_reconciliation_process"
        )
        print(frappe.get_traceback())

    print("\nReconciliation process completed.")


@frappe.whitelist()
def return_budget_thresholds(project):
    fields = frappe.db.sql(
        """
        SELECT deliverable, budget_threshold, amount_expended
        FROM `tabBudget Threshold` bt
        JOIN `tabBudget` b ON bt.parent = b.name
        WHERE b.budget_against = 'Project'
        AND b.project = %s
        """,
        (project,),
        as_dict=True,
    )

    return fields


def test_return_budget_thresholds():
    # Supply a test project for which budget thresholds need to be fetched
    test_project = "Collaborative Action Strategy for Health Campaign Effectiveness (CAS)"  # Replace with an actual project ID if needed

    # Call the function to fetch budget thresholds for the test project
    budget_thresholds = return_budget_thresholds(test_project)

    # Check if any budget thresholds were returned
    if not budget_thresholds:
        frappe.msgprint(f"No budget thresholds found for the project: {test_project}")
    else:
        frappe.msgprint(f"Budget thresholds found for the project: {test_project}")
        # for threshold in budget_thresholds:
        #     print(
        #         f"Deliverable: {threshold['deliverable']}, Budget Threshold: {threshold['budget_threshold']}, Amount Expended: {threshold['amount_expended']}"
        #     )

    return budget_thresholds


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


import frappe


def find_employees_without_salary_structure():
    # Fetch all active employees
    active_employees = frappe.get_all(
        "Employee", filters={"status": "Active"}, fields=["name"]
    )

    # Fetch all salary structure assignments
    salary_structure_assignments = frappe.get_all(
        "Salary Structure Assignment",
        filters={"from_date": [">=", "2024-12-20"]},
        fields=["employee"],
    )

    # Extract employee names from salary structure assignments
    assigned_employees = {
        assignment["employee"] for assignment in salary_structure_assignments
    }

    # Find employees without salary structure assignment
    employees_without_salary_structure = [
        employee["name"]
        for employee in active_employees
        if employee["name"] not in assigned_employees
    ]

    # Return or log the result
    if employees_without_salary_structure:
        print(
            f"The following employees do not have a salary structure assignment: {', '.join(employees_without_salary_structure)}"
        )
    else:
        print("All active employees have a salary structure assignment.")


import frappe
from frappe.utils import today, getdate


def fetch_and_save_sydani_group_attendance_records():
    # Set the date range
    start_date = "2024-10-24"
    # end_date = today()
    end_date = "2024-12-12"

    # Step 1: Fetch all active employees from Sydani Group
    active_employees = frappe.get_all(
        "Employee",
        filters={"status": "Active", "company": "Sydani Group"},
        fields=["name", "employee_name"],
    )

    # Step 2: For each employee, fetch their Attendance records between start and end date
    for employee in active_employees:
        attendance_records = frappe.get_all(
            "Attendance",
            filters={
                "employee": employee["name"],
                "attendance_date": ["between", [start_date, end_date]],
                "docstatus": 1,
            },
            fields=["name", "attendance_date", "status"],
        )

        # # Step 3: Save the fetched attendance records (custom logic or further processing)

        for record in attendance_records:
            # Fetch the attendance document
            attendance_doc = frappe.get_doc("Attendance", record["name"])

            # Update the company to "Sydani Group" if not already set
            # if attendance_doc.company != "Sydani Group":
            attendance_doc.company = "Sydani Group"
            attendance_doc.random_check = 1

            # Save the updated document
            attendance_doc.save()
            frappe.db.commit()  # Commit the changes to the database

            # You can add further custom logic or logging here if needed
            print(
                f"Updated attendance for {employee['employee_name']} on {record['attendance_date']}"
            )


import frappe
from datetime import datetime


@frappe.whitelist()
def get_gl_entries_balance(bank_account, from_date, to_date):
    # Fetch account linked to bank_account
    account = frappe.db.get_value("Bank Account", bank_account, "account")

    if not account:
        return {"error": "Account not found for the specified bank account."}

    # Fetch Bank Account values
    bank_account_doc = frappe.get_doc("Bank Account", bank_account)
    total_deposits = bank_account_doc.total_deposits or 0
    total_withdrawals = bank_account_doc.total_withdrawals or 0
    balance_date = bank_account_doc.balance_date

    # Initialize sums for opening and closing bank balances
    opening_balance_bank = 0
    closing_balance_bank = 0

    # If balance_date is on or earlier than from_date, add total_deposits and total_withdrawals
    from_date_obj = datetime.strptime(from_date, "%Y-%m-%d").date()
    to_date_obj = datetime.strptime(to_date, "%Y-%m-%d").date()

    # if balance_date and balance_date <= from_date:
    if balance_date and balance_date <= from_date_obj:
        opening_total_deposit_adjustment = total_deposits
        opening_total_withdrawal_adjustment = total_withdrawals
    else:
        opening_total_deposit_adjustment = 0
        opening_total_withdrawal_adjustment = 0

    # If balance_date is on or after to_date, add total_deposits and total_withdrawals
    # if balance_date and balance_date <= to_date:
    if balance_date and balance_date <= to_date_obj:
        closing_total_deposit_adjustment = total_deposits
        closing_total_withdrawal_adjustment = total_withdrawals
    else:
        closing_total_deposit_adjustment = 0
        closing_total_withdrawal_adjustment = 0

    # Fetch bank transactions before or on from_date
    opening_transactions = frappe.get_all(
        "Bank Transaction",
        filters={
            "bank_account": bank_account,
            "date": ["<=", from_date],
            "docstatus": 1,
        },
        fields=["deposit", "withdrawal"],
    )
    opening_deposit_sum = sum(tx.deposit for tx in opening_transactions)
    opening_withdrawal_sum = sum(tx.withdrawal for tx in opening_transactions)
    opening_balance_bank = (
        opening_deposit_sum
        + opening_total_deposit_adjustment
        - opening_withdrawal_sum
        - opening_total_withdrawal_adjustment
    )

    # Fetch bank transactions before or on to_date
    closing_transactions = frappe.get_all(
        "Bank Transaction",
        filters={
            "bank_account": bank_account,
            "date": ["<=", to_date],
            "docstatus": 1,
        },
        fields=["deposit", "withdrawal"],
    )
    closing_deposit_sum = sum(tx.deposit for tx in closing_transactions)
    closing_withdrawal_sum = sum(tx.withdrawal for tx in closing_transactions)
    closing_balance_bank = (
        closing_deposit_sum
        + closing_total_deposit_adjustment
        - closing_withdrawal_sum
        - closing_total_withdrawal_adjustment
    )

    # Get GL Entries on and before from_date (Opening Balance)
    opening_entries = frappe.get_all(
        "GL Entry",
        filters={
            "account": account,
            "posting_date": ["<=", from_date],
            "is_cancelled": 0,
        },
        fields=["debit_in_account_currency", "credit_in_account_currency"],
    )
    opening_debit = sum(entry.debit_in_account_currency for entry in opening_entries)
    opening_credit = sum(entry.credit_in_account_currency for entry in opening_entries)
    opening_balance = opening_debit - opening_credit

    # Get GL Entries on and before to_date (Closing Balance)
    closing_entries = frappe.get_all(
        "GL Entry",
        filters={
            "account": account,
            "posting_date": ["<=", to_date],
            "is_cancelled": 0,
        },
        fields=["debit_in_account_currency", "credit_in_account_currency"],
    )
    closing_debit = sum(entry.debit_in_account_currency for entry in closing_entries)
    closing_credit = sum(entry.credit_in_account_currency for entry in closing_entries)
    closing_balance = closing_debit - closing_credit

    # Get GL Entries between from_date and to_date, sorted by oldest to newest
    gl_entries = frappe.get_all(
        "GL Entry",
        filters={
            "account": account,
            "posting_date": ["between", [from_date, to_date]],
            "is_cancelled": 0,
        },
        fields=["name", "debit_in_account_currency", "credit_in_account_currency"],
        order_by="posting_date asc",
    )

    # Calculate total debits and credits between from_date and to_date
    period_debit = sum(entry.debit_in_account_currency for entry in gl_entries)
    period_credit = sum(entry.credit_in_account_currency for entry in gl_entries)

    # Fetch Bank Transactions between from_date and to_date
    bank_transactions = frappe.get_all(
        "Bank Transaction",
        filters={
            "bank_account": bank_account,
            "date": ["between", [from_date, to_date]],
            "docstatus": 1,
        },
        fields=["name", "deposit", "withdrawal", "status"],
    )

    # Add the opening balances to the period balance if it is between from and to date
    if balance_date and balance_date >= from_date_obj and balance_date <= to_date_obj:
        deposit_opening_balance = total_deposits
        withdrawal_opening_balance = total_withdrawals
    else:
        deposit_opening_balance = 0
        withdrawal_opening_balance = 0

    # Sum deposits and withdrawals within the period for Bank Transactions
    total_deposit_period = (
        sum(tx.deposit for tx in bank_transactions) + deposit_opening_balance
    )
    total_withdrawal_period = (
        sum(tx.withdrawal for tx in bank_transactions) + withdrawal_opening_balance
    )

    # Prepare the response with entry names, balances, sums of debits/credits, and bank transaction data and number of unreconciled transactions
    entry_names = [entry.name for entry in gl_entries]
    bank_transaction_for_period = [
        bank_transaction.name for bank_transaction in bank_transactions
    ]
    unreconciled_transactions = len(
        [
            transaction
            for transaction in bank_transactions
            if transaction.status != "Reconciled"
        ]
    )

    entry_details = {
        "entry_names": entry_names,
        "bank_transaction_for_period": bank_transaction_for_period,
        "opening_balance": opening_balance,
        "closing_balance": closing_balance,
        "period_debit": period_debit,
        "period_credit": period_credit,
        "opening_balance_bank": opening_balance_bank,
        "closing_balance_bank": closing_balance_bank,
        "total_deposit_period": total_deposit_period,
        "total_withdrawal_period": total_withdrawal_period,
        "unreconciled_transactions": unreconciled_transactions,
    }

    return entry_details


def test_gl_entries():
    bank_account = "1477855025 - Sydani Farms - Access Bank"  # Replace with the actual bank account
    from_date = "2024-07-01"
    to_date = "2024-11-01"

    try:
        # Call the function to fetch GL entry balances
        result = get_gl_entries_balance(bank_account, from_date, to_date)

        # Check for the result and print relevant information
        if "error" in result:
            print(f"An error occurred: {result['error']}")
        else:
            # Extract entry names, opening balance, and closing balance from result
            entry_names = result.get("entry_names", [])
            bank_transaction_for_period = result.get("bank_transaction_for_period", [])
            opening_balance = result.get("opening_balance", 0)
            closing_balance = result.get("closing_balance", 0)
            period_debit = result.get("period_debit", 0)
            period_credit = result.get("period_credit", 0)
            opening_balance_bank = result.get("opening_balance_bank", 0)
            closing_balance_bank = result.get("closing_balance_bank", 0)
            total_deposit_period = result.get("total_deposit_period", 0)
            total_withdrawal_period = result.get("total_withdrawal_period", 0)
            unreconciled_transactions = result.get("unreconciled_transactions", 0)

            # Print the success message with details
            print("GL Entry Names:", entry_names)
            print("Bank Transactions:", bank_transaction_for_period)
            print("Opening Balance:", opening_balance)
            print("Closing Balance:", closing_balance)
            print("Period Debit:", period_debit)
            print("Period Credit:", period_credit)
            print("Opening Bank Balance:", opening_balance_bank)
            print("Closing Bank Balance:", closing_balance_bank)
            print("Period Deposit:", total_deposit_period)
            print("Period Withdrawal:", total_withdrawal_period)
            print("Number of Unreconciled Transactions:", unreconciled_transactions)

    except Exception as e:
        # Print an error message and log the exception traceback if any error occurs
        # print("The system could not obtain the GL entry balances")
        # Uncomment to log error in Frappe's error log if needed
        # frappe.log_error(frappe.get_traceback(), "test_gl_entries_error")
        print(frappe.get_traceback())


import frappe


def rename_user():
    old_email = "esther.iyiegbu@sydani.org"
    new_email = "esther.sydney@sydani.org"

    # Check if the old email exists
    if frappe.db.exists("User", old_email):
        try:
            # Rename the user record
            frappe.rename_doc("User", old_email, new_email)
            frappe.db.commit()
            print(f"User '{old_email}' renamed to '{new_email}' successfully.")
        except Exception as e:
            print(f"Error renaming user: {e}")
    else:
        print(f"User '{old_email}' not found.")


import frappe
from frappe.utils import getdate, add_days


@frappe.whitelist()
def get_leave_and_holiday_days(employee, work_week_begins_on):
    try:
        # Convert the work_week_begins_on to a date object
        work_week_begins_on = getdate(work_week_begins_on)

        # Calculate the end of the work week (4 days after work_week_begins_on)
        work_week_end = add_days(work_week_begins_on, 4)

        # Fetch the holiday list for the employee from the Employee doctype
        holiday_list = frappe.db.get_value("Employee", employee, "holiday_list")

        # Fetch all holidays for the given holiday list within the specified date range
        holidays = frappe.get_all(
            "Holiday",
            filters={
                "parent": holiday_list,
                "holiday_date": ["between", [work_week_begins_on, work_week_end]],
            },
            fields=["holiday_date"],
        )

        # # Extract holiday dates into a list
        # holiday_days = [getdate(holiday["holiday_date"]) for holiday in holidays]
        holiday_days = [
            getdate(holiday["holiday_date"]).strftime("%Y-%m-%d")
            for holiday in holidays
        ]

        # Fetch leave days for the employee within the specified date range
        # Calculate the date range
        # work_week_end = add_days(work_week_begins_on, 4)

        # Query the Attendance doctype
        attendance_records = frappe.get_all(
            "Attendance",
            filters={
                "employee": employee,
                "status": "On Leave",
                "attendance_date": ["between", [work_week_begins_on, work_week_end]],
            },
            fields=["attendance_date"],
        )

        # Extract the attendance dates
        # leave_days = [record["attendance_date"] for record in attendance_records]
        leave_days = [
            getdate(record["attendance_date"]).strftime("%Y-%m-%d")
            for record in attendance_records
        ]

        # Return both leave days and holiday days
        return {"leave_days": leave_days, "holiday_days": holiday_days}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in get_leave_and_holiday_days")
        return {"error": str(e)}


def test_leave_days():
    employee = "Morenike Olubunmi Oni"  # Replace with the actual employee
    work_week_begins_on = "2024-11-11"

    try:
        # Call the function to fetch leave days (or attendance days)
        result = get_leave_and_holiday_days(employee, work_week_begins_on)

        # Check the result and print relevant information
        if isinstance(result, list):  # Assuming result is a list of leave days
            if result:
                # Convert datetime.date objects to strings before joining
                leave_days_str = ", ".join([str(day) for day in result])
                print(f"Leave days for employee {employee}: {leave_days_str}")
            else:
                print(
                    f"No leave days found for employee {employee} within the given range."
                )
        else:
            print(f"Unexpected result format: {result}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print(frappe.get_traceback())


import frappe


def get_doc_fields():
    fields = frappe.db.sql(
        """
    SELECT *
    FROM `tabUser`
    
""",
        # WHERE `parent` = 'User'
        as_dict=True,
    )
    print(fields)


import frappe
from datetime import datetime, time


@frappe.whitelist()
def print_attendance_table():
    # Define the date range
    start_date = datetime(2024, 1, 4)
    end_date = datetime(2024, 11, 30)

    # Define the early threshold and the cutoff time
    early_threshold = time(9, 0)  # Early arrivals before 9:00 AM
    cutoff_time = time(9, 15)  # Filter out records after 9:15 AM

    # Fetch attendance records within the date range and with in_time populated
    attendance_records = frappe.db.get_all(
        "Attendance",
        filters={
            "attendance_date": ["between", (start_date, end_date)],
            "in_time": ["is", "set"],
        },
        fields=["employee", "in_time"],
    )

    if not attendance_records:
        print("No attendance records found within the specified date range.")
        return

    # Group data by employee
    employee_data = {}

    for record in attendance_records:
        employee = record["employee"]
        in_time = record["in_time"]  # Already a datetime object
        arrival_time = in_time.time()  # Extract the time part

        # Filter out records after the cutoff time
        if arrival_time > cutoff_time:
            continue

        if employee not in employee_data:
            employee_data[employee] = {"arrival_times": [], "early_arrivals": 0}

        # Track arrival times
        employee_data[employee]["arrival_times"].append(arrival_time)

        # Count early arrivals
        if arrival_time < early_threshold:
            employee_data[employee]["early_arrivals"] += 1

    # Process data for output
    table = []
    for employee, data in employee_data.items():
        # Calculate average arrival time
        total_seconds = sum(
            [t.hour * 3600 + t.minute * 60 + t.second for t in data["arrival_times"]]
        )
        avg_seconds = (
            total_seconds // len(data["arrival_times"]) if data["arrival_times"] else 0
        )
        avg_time = time(
            avg_seconds // 3600, (avg_seconds % 3600) // 60, avg_seconds % 60
        )

        # Append data to the table
        table.append(
            {
                "Employee": employee,
                "Average Arrival Time": avg_time.strftime("%H:%M:%S"),
                "No of Early Arrivals": data["early_arrivals"],
            }
        )

    # Sort the table by the most early arrivals
    table.sort(key=lambda x: x["No of Early Arrivals"], reverse=True)

    # Print the table
    print("\nAttendance Summary (Sorted by Most Early Arrivals):")
    print(f"{'Employee':<60}{'Average Arrival Time':<40}{'No of Early Arrivals':<20}")
    print("-" * 60)
    for row in table:
        print(
            f"{row['Employee']:<60}{row['Average Arrival Time']:<40}{row['No of Early Arrivals']:<20}"
        )


def test_fields():
    fields = frappe.db.sql(
        f""" 
    SELECT *
    FROM `tabAsset Finance Book`
    WHERE parent = 'SGP/furniture_and_fittings/office_table/collapsible_meeting_table/44857'""",
        as_dict=True,
    )

    return fields


def test_fieldss():
    fields = frappe.db.sql(
        f""" 
    SELECT opening_accumulated_depreciation
    FROM `tabAsset`
    WHERE name = 'SGP/furniture_and_fittings/office_table/collapsible_meeting_table/44857'""",
        as_dict=True,
    )

    return fields


# @frappe.whitelist()
# def fetch_and_combine_records(employee, start_date, end_date, holiday_list):
#     """
#     Fetches and combines work plan details, end-of-week records, and public holidays
#     for an employee within a given date range, and sorts them by due date.
#     """
#     combined_records = []

#     # Calculate one week before start_date
#     one_week_before_start_date = (
#         frappe.utils.getdate(start_date) - timedelta(days=6)
#     ).strftime("%Y-%m-%d")

#     # Fetching work plans based on employee and work_week_begins_on condition
#     work_plans = frappe.db.sql(
#         f"""SELECT name
#             FROM `tabWork Plan`
#             WHERE employee = %s
#             AND work_week_begins_on BETWEEN %s AND %s""",
#         (employee, one_week_before_start_date, end_date),
#         as_dict=True,
#     )

#     # Fetching additional activities and end-of-week records for all work plans
#     project_hours = {}
#     for work_plan in work_plans:
#         # Fetching additional activity records
#         additional_activity_records = frappe.db.sql(
#             f"""SELECT name, activity, due_date, status, hours, project
#                 FROM `tabWork Plan Details Additional Activities`
#                 WHERE parent = %s
#                 AND status = "Done"
#                 AND hours > 0
#                 AND due_date BETWEEN %s AND %s""",
#             (work_plan["name"], start_date, end_date),
#             as_dict=True,
#         )
#         combined_records.extend(additional_activity_records)

#         # Fetching end-of-week records
#         end_of_week_records = frappe.db.sql(
#             f"""SELECT name, activity, due_date, status, hours, project
#                 FROM `tabWork Plan Details End of Week`
#                 WHERE parent = %s
#                 AND status = "Done"
#                 AND hours > 0
#                 AND due_date BETWEEN %s AND %s""",
#             (work_plan["name"], start_date, end_date),
#             as_dict=True,
#         )
#         combined_records.extend(end_of_week_records)

#         # Aggregate hours by project
#         for record in additional_activity_records + end_of_week_records:
#             project = record["project"]
#             hours = record["hours"]
#             project_hours[project] = project_hours.get(project, 0) + hours

#     # Calculate the total hours across all projects
#     total_hours = sum(project_hours.values())

#     # Calculate the percentage for each project
#     project_percentages = {
#         project: (hours / total_hours if total_hours > 0 else 0)
#         for project, hours in project_hours.items()
#     }

#     # Fetch attendance that are leave days
#     leave_days = frappe.db.sql(
#         f"""SELECT name, employee, attendance_date, status, leave_type
#             FROM `tabAttendance`
#             WHERE employee = %s
#             AND attendance_date BETWEEN %s AND %s""",
#         (employee, start_date, end_date),
#         as_dict=True,
#     )
#     for leave_day in leave_days:
#         for project, percentage in project_percentages.items():
#             combined_records.append(
#                 {
#                     "activity": leave_day["leave_type"],
#                     "due_date": leave_day["attendance_date"],
#                     "status": "Done",  # Assuming this is a constant value for leave days
#                     "hours": 8 * percentage,  # Split hours by project percentage
#                     "project": project,
#                 }
#             )

#     # Fetching public holidays within the given date range
#     public_holidays = frappe.db.sql(
#         f"""SELECT name, holiday_date, weekly_off
#             FROM `tabHoliday`
#             WHERE holiday_date BETWEEN %s AND %s
#             AND parent = %s
#             AND weekly_off = 0""",
#         (start_date, end_date, holiday_list),
#         as_dict=True,
#     )

#     # Adding public holidays to the combined records
#     for holiday in public_holidays:
#         for project, percentage in project_percentages.items():
#             combined_records.append(
#                 {
#                     "activity": "Public Holiday",
#                     "due_date": holiday["holiday_date"],
#                     "status": "Done",  # Assuming this is a constant value for public holidays
#                     "hours": 8 * percentage,  # Split hours by project percentage
#                     "project": project,
#                 }
#             )

#     # Sorting combined records by due date
#     sorted_records = sorted(combined_records, key=lambda x: x.get("due_date"))

#     return sorted_records

from datetime import timedelta
import frappe


@frappe.whitelist()
def fetch_and_combine_records(employee, start_date, end_date, holiday_list):
    """
    Fetches and combines work plan details, end-of-week records, and public holidays
    for an employee within a given date range, and sorts them by due date.
    """
    combined_records = []

    # Calculate one week before start_date
    one_week_before_start_date = (
        frappe.utils.getdate(start_date) - timedelta(days=7)
    ).strftime("%Y-%m-%d")

    # Fetching work plans based on employee and work_week_begins_on condition
    work_plans = frappe.db.sql(
        f"""SELECT name
            FROM `tabWork Plan`
            WHERE employee = %s
            AND work_week_begins_on BETWEEN %s AND %s""",
        (employee, one_week_before_start_date, end_date),
        as_dict=True,
    )

    # Aggregate project hours across Additional Activities and End of Week
    project_hours = {}
    for work_plan in work_plans:
        # Additional Activities
        additional_activity_records = frappe.db.sql(
            f"""SELECT project, SUM(hours) AS hours
                FROM `tabWork Plan Details Additional Activities`
                WHERE parent = %s
                AND status = 'Done'
                AND due_date BETWEEN %s AND %s
                GROUP BY project""",
            (work_plan["name"], start_date, end_date),
            as_dict=True,
        )
        for record in additional_activity_records:
            project_hours[record["project"]] = (
                project_hours.get(record["project"], 0) + record["hours"]
            )

        # End of Week
        end_of_week_records = frappe.db.sql(
            f"""SELECT project, SUM(hours) AS hours
                FROM `tabWork Plan Details End of Week`
                WHERE parent = %s
                AND status = 'Done'
                AND due_date BETWEEN %s AND %s
                GROUP BY project""",
            (work_plan["name"], start_date, end_date),
            as_dict=True,
        )
        for record in end_of_week_records:
            project_hours[record["project"]] = (
                project_hours.get(record["project"], 0) + record["hours"]
            )

        # Fetch individual activities for combined records
        additional_activities = frappe.db.sql(
            f"""SELECT name, activity, due_date, status, hours, project
                FROM `tabWork Plan Details Additional Activities`
                WHERE parent = %s
                AND status = 'Done'
                AND due_date BETWEEN %s AND %s""",
            (work_plan["name"], start_date, end_date),
            as_dict=True,
        )
        combined_records.extend(additional_activities)

        end_of_week_activities = frappe.db.sql(
            f"""SELECT name, activity, due_date, status, hours, project
                FROM `tabWork Plan Details End of Week`
                WHERE parent = %s
                AND status = 'Done'
                AND due_date BETWEEN %s AND %s""",
            (work_plan["name"], start_date, end_date),
            as_dict=True,
        )
        combined_records.extend(end_of_week_activities)

    # Fetch attendance records for leave days
    leave_days = frappe.db.sql(
        f"""SELECT attendance_date, leave_type
            FROM `tabAttendance`
            WHERE employee = %s
            AND attendance_date BETWEEN %s AND %s""",
        (employee, start_date, end_date),
        as_dict=True,
    )
    for leave_day in leave_days:
        for project, hours in project_hours.items():
            combined_records.append(
                {
                    "activity": leave_day["leave_type"],
                    "due_date": leave_day["attendance_date"],
                    "status": "Done",
                    "hours": (
                        (8 * hours / sum(project_hours.values()))
                        if project_hours
                        else 0
                    ),
                    "project": project,
                }
            )

    # Fetch public holidays
    public_holidays = frappe.db.sql(
        f"""SELECT holiday_date
            FROM `tabHoliday`
            WHERE holiday_date BETWEEN %s AND %s
            AND parent = %s
            AND weekly_off = 0""",
        (start_date, end_date, holiday_list),
        as_dict=True,
    )
    for holiday in public_holidays:
        for project, hours in project_hours.items():
            combined_records.append(
                {
                    "activity": "Public Holiday",
                    "due_date": holiday["holiday_date"],
                    "status": "Done",
                    "hours": (
                        (8 * hours / sum(project_hours.values()))
                        if project_hours
                        else 0
                    ),
                    "project": project,
                }
            )

    # Remove records for regular days with activity=None
    combined_records = [
        record
        for record in combined_records
        if record["activity"] is not None  # Include records with a valid activity
        # or (
        #     record["activity"] is None
        #     and (
        #         record["due_date"]
        #         in [d["attendance_date"] for d in leave_days]  # Leave days
        #         or record["due_date"]
        #         in [h["holiday_date"] for h in public_holidays]  # Public holidays
        #     )
        # )
    ]

    # Sorting combined records by due date
    sorted_records = sorted(combined_records, key=lambda x: x.get("due_date"))

    return sorted_records


def sorted_records():
    data = fetch_and_combine_records(
        employee="Ekomobong Akwaowo",
        start_date="2024-12-10",
        end_date="2024-12-18",
        holiday_list="Sydani Holidays",
    )

    print(data)


# def sorted_records():
#     data = fetch_and_combine_records(
#         employee="David Soluchukwu Katchy",
#         start_date="2024-12-10",
#         end_date="2025-12-20",
#         holiday_list="Sydani Holidays",
#     )

#     print(data)


def test_fields2():
    # Fetch parent record from Expense Claim
    parent_records = frappe.db.sql(
        f"""
        SELECT *
        FROM `tabExpense Claim`
        WHERE name = 'PV_NO:202411270004'
        """,
        as_dict=True,
    )

    # Fetch child records from Expense Claim Detail
    child_records = frappe.db.sql(
        f"""
        SELECT 
            ec.name AS parent_name, 
            ecd.*
        FROM `tabExpense Claim` ec
        JOIN `tabExpense Claim Detail` ecd
        ON ec.name = ecd.parent
        WHERE ec.name = 'PV_NO:202411270004'
        """,
        as_dict=True,
    )

    # Combine parent and child records
    result = {
        "parent_record": parent_records,
        "child_records": child_records,
    }

    return result


# Server Script Type: Document Event
# Trigger: After Submit
import frappe


def creat_ps_attendance(doc, method):
    """
    Handles the workflow for creating or updating PS Attendance and PS Report documents
    triggered by the PS Attendance Request doctype.

    :param doc: The document triggering the workflow.
    :param method: The method triggering the workflow (e.g., 'on_submit').
    """
    ps_session = f"{doc.ps_group} - {doc.date}"

    # Check if PS Attendance already exists
    att_exists = frappe.db.sql(
        """
        SELECT name 
        FROM `tabPS Attendance` 
        WHERE employee = %s AND ps_session = %s
    """,
        (doc.employee, ps_session),
        as_dict=True,
    )

    # Check if PS Report already exists
    ps_report = frappe.db.sql(
        """
        SELECT name 
        FROM `tabPS Report` 
        WHERE ps_date = %s AND ps_group = %s
    """,
        (doc.date, doc.ps_group),
        as_dict=True,
    )

    # Create a new PS Report if it doesn't exist
    if not ps_report:
        new_ps_report = frappe.get_doc(
            {
                "doctype": "PS Report",
                "ps_date": doc.date,
                "ps_group": doc.ps_group,
                "start_time": "",
                "end_time": "",
            }
        )
        new_ps_report.save()

        # Rename the PS Report
        updated_name = f"{new_ps_report.ps_group} - {new_ps_report.ps_date}"
        frappe.rename_doc("PS Report", new_ps_report.name, updated_name)

    # Delete existing attendance if found
    if att_exists:
        existing_attendance = frappe.get_doc("PS Attendance", att_exists[0].name)
        existing_attendance.delete()

    # Create a new PS Attendance
    attendance = frappe.get_doc(
        {
            "doctype": "PS Attendance",
            "ps_group": doc.ps_group,
            "employee": doc.employee,
            "ps_session": ps_session,
            "ps_date": doc.date,
            "start_time": "",
            "end_time": "",
            "entry_time": "",
            "exit_time": "",
            "status": "Out On Permission",
        }
    )
    attendance.save()


# @frappe.whitelist()
# def fetch_and_create_journal_entry_from_payroll_entry(
#     payroll_entry,
#     payroll_period,
#     company,
#     currency,
#     posting_date,
#     payroll_payable_account,
#     cost_center,
#     payment_account,
# ):

#     # Fetch Salary Slips in draft state
#     all_salary_slips = frappe.get_all(
#         "Salary Slip",
#         filters={
#             "payroll_entry": payroll_entry,
#             "payroll_period": payroll_period,
#             "company": company,
#             "currency": currency,
#             "docstatus": 0,
#         },
#         fields=["name", "docstatus"],
#     )
#     for slip in all_salary_slips:
#         slip_doc = frappe.get_doc("Salary Slip", slip["name"])
#         slip_doc.submit()

#     try:
#         # Fetch Salary Slips
#         salary_slips = frappe.get_all(
#             "Salary Slip",
#             filters={
#                 "payroll_entry": payroll_entry,
#                 "payroll_period": payroll_period,
#                 "company": company,
#                 "currency": currency,
#             },
#             fields=["name", "docstatus"],
#         )

#         if not salary_slips:
#             frappe.throw("No Salary Slips found for the given criteria.")

#         for slip in salary_slips:
#             if slip["docstatus"] == 0:
#                 frappe.throw(f"Salary Slip {slip['name']} must be submitted first.")

#         # Initialize component account mappings
#         earnings_map = {}
#         deductions_map = {}
#         pension_contribution = 0

#         # Process Salary Slips
#         for slip in salary_slips:
#             salary_slip = frappe.get_doc("Salary Slip", slip["name"])

#             total_statistical_earnings = 0
#             total_excluded_earnings = 0
#             total_statistical_deductions = 0
#             total_excluded_deductions = 0

#             for earning in salary_slip.earnings:
#                 account = frappe.db.get_value(
#                     "Salary Component Account",
#                     {"parent": earning.salary_component, "company": company},
#                     "account",
#                 )

#                 is_statistical = frappe.db.get_value(
#                     "Salary Component",
#                     earning.salary_component,
#                     "statistical_component",
#                 )
#                 is_excluded = frappe.db.get_value(
#                     "Salary Component",
#                     earning.salary_component,
#                     "do_not_include_in_total",
#                 )

#                 if is_statistical:
#                     total_statistical_earnings += earning.amount
#                 if is_excluded:
#                     total_excluded_earnings += earning.amount

#                 if account:
#                     earnings_map[account] = (
#                         earnings_map.get(account, 0) + earning.amount
#                     )

#                 if earning.salary_component == "Employer Pension Contribution 10%":
#                     pension_contribution += earning.amount

#             for deduction in salary_slip.deductions:
#                 account = frappe.db.get_value(
#                     "Salary Component Account",
#                     {"parent": deduction.salary_component, "company": company},
#                     "account",
#                 )

#                 is_statistical = frappe.db.get_value(
#                     "Salary Component",
#                     deduction.salary_component,
#                     "statistical_component",
#                 )
#                 is_excluded = frappe.db.get_value(
#                     "Salary Component",
#                     deduction.salary_component,
#                     "do_not_include_in_total",
#                 )

#                 if is_statistical:
#                     total_statistical_deductions += deduction.amount
#                 if is_excluded:
#                     total_excluded_deductions += deduction.amount

#                 if account:
#                     deductions_map[account] = (
#                         deductions_map.get(account, 0) + deduction.amount
#                     )

#         # Deduct the excluded earnings and statistical earnings from total
#         total_earnings = sum(earnings_map.values()) - (
#             # total_statistical_earnings + total_excluded_earnings
#             pension_contribution
#         )
#         total_deductions = sum(deductions_map.values()) - (
#             total_statistical_deductions + total_excluded_deductions
#         )
#         net_payable = total_earnings - total_deductions

#         # print("Total Earnings:", total_earnings)
#         # print("total_statistical_earnings:", total_statistical_earnings)
#         # print("total_excluded_earnings:", total_excluded_earnings)
#         # print("Total Deductions:", total_deductions)
#         # print("pension_contribution:", pension_contribution)
#         # print("Net Payable:", net_payable)

#         # Prepare Journal Entry
#         journal_entry = frappe.get_doc(
#             {
#                 "doctype": "Journal Entry",
#                 "voucher_type": "Journal Entry",
#                 "company": company,
#                 "posting_date": posting_date,
#                 "user_remark": f"Payroll Journal Entry for {payroll_period}",
#                 "accounts": [],
#             }
#         )

#         # Add Earnings Entries
#         for account, amount in earnings_map.items():
#             journal_entry.append(
#                 "accounts",
#                 {
#                     "account": account,
#                     "debit_in_account_currency": total_earnings,
#                     "credit_in_account_currency": 0,
#                     "user_remark": f"Being Salary journal for {payroll_period}",
#                 },
#             )

#         # Add Employer Pension Contribution
#         if pension_contribution > 0:
#             pension_account = frappe.db.get_value(
#                 "Salary Component Account",
#                 {"parent": "Employer Pension Contribution 10%", "company": company},
#                 "account",
#             )
#             if pension_account:
#                 journal_entry.append(
#                     "accounts",
#                     {
#                         "account": pension_account,
#                         "debit_in_account_currency": pension_contribution,
#                         "credit_in_account_currency": 0,
#                         "user_remark": f"Employer Pension Contribution for {payroll_period}",
#                     },
#                 )

#         # Add Deductions Entries
#         for account, amount in deductions_map.items():
#             journal_entry.append(
#                 "accounts",
#                 {
#                     "account": account,
#                     "debit_in_account_currency": 0,
#                     "credit_in_account_currency": amount,
#                     "user_remark": f"Deductions for {payroll_period}",
#                     "reference_type": "Payroll Entry",
#                     "reference_name": payroll_entry,
#                 },
#             )

#         # Add Employer Pension Contribution in credit
#         if pension_contribution > 0:
#             pension_account = frappe.db.get_value(
#                 "Salary Component Account",
#                 {"parent": "Employee Pension Contribution", "company": company},
#                 "account",
#             )
#             if pension_account:
#                 journal_entry.append(
#                     "accounts",
#                     {
#                         "account": pension_account,
#                         "debit_in_account_currency": 0,
#                         "credit_in_account_currency": pension_contribution,
#                         "user_remark": f"Employer Pension Contribution for {payroll_period}",
#                         "reference_type": "Payroll Entry",
#                         "reference_name": payroll_entry,
#                     },
#                 )

#         # Add Payroll Payable Account as balancing entry
#         journal_entry.append(
#             "accounts",
#             {
#                 "account": payroll_payable_account,
#                 "debit_in_account_currency": 0,
#                 "credit_in_account_currency": net_payable,
#                 "user_remark": f"Net salaries payable for {payroll_period}",
#                 "reference_type": "Payroll Entry",
#                 "reference_name": payroll_entry,
#             },
#         )

#         # # Insert and Submit Journal Entry
#         journal_entry.insert()
#         # # journal_entry.submit()
#         # # frappe.db.commit()

#         frappe.msgprint(
#             f"Journal entry {journal_entry.name} created successfully.",
#             alert=True,
#         )
#         # # return {
#         # #     "message": f"Journal entry {journal_entry.name} created successfully.",
#         # #     "journal_entry": journal_entry.name,
#         # # }

#         bank_entry = frappe.get_doc(
#             {
#                 "doctype": "Journal Entry",
#                 "voucher_type": "Bank Entry",
#                 "company": company,
#                 "posting_date": posting_date,
#                 "cheque_no": "XXXXXXXXXX",
#                 "cheque_date": posting_date,
#                 "user_remark": f"Payroll Bank Entry for {payroll_period}",
#                 "accounts": [],
#             }
#         )

#         # Add Earnings Entries
#         for account, amount in earnings_map.items():
#             bank_entry.append(
#                 "accounts",
#                 {
#                     "account": payment_account,
#                     "debit_in_account_currency": 0,
#                     "credit_in_account_currency": total_earnings,
#                     "user_remark": f"Being Salary bank entry for {payroll_period}",
#                 },
#             )

#         # Add Employer Pension Contribution
#         if pension_contribution > 0:
#             pension_account = frappe.db.get_value(
#                 "Salary Component Account",
#                 {"parent": "Employer Pension Contribution 10%", "company": company},
#                 "account",
#             )

#             if pension_account:
#                 bank_entry.append(
#                     "accounts",
#                     {
#                         "account": payment_account,
#                         "debit_in_account_currency": 0,
#                         "credit_in_account_currency": pension_contribution,
#                         "user_remark": f"Employer Pension Contribution for {payroll_period}",
#                     },
#                 )

#         # Add Deductions Entries
#         for account, amount in deductions_map.items():
#             bank_entry.append(
#                 "accounts",
#                 {
#                     "account": account,
#                     "debit_in_account_currency": amount,
#                     "credit_in_account_currency": 0,
#                     "user_remark": f"Deductions for {payroll_period}",
#                     "reference_type": "Payroll Entry",
#                     "reference_name": payroll_entry,
#                 },
#             )

#         # Add Employer Pension Contribution in credit
#         if pension_contribution > 0:
#             pension_account = frappe.db.get_value(
#                 "Salary Component Account",
#                 {"parent": "Employee Pension Contribution", "company": company},
#                 "account",
#             )

#             if pension_account:
#                 bank_entry.append(
#                     "accounts",
#                     {
#                         "account": pension_account,
#                         "debit_in_account_currency": pension_contribution,
#                         "credit_in_account_currency": 0,
#                         "user_remark": f"Employer Pension Contribution for {payroll_period}",
#                         "reference_type": "Payroll Entry",
#                         "reference_name": payroll_entry,
#                     },
#                 )

#         # Add Payroll Payable Account as balancing entry
#         bank_entry.append(
#             "accounts",
#             {
#                 "account": payroll_payable_account,
#                 "debit_in_account_currency": net_payable,
#                 "credit_in_account_currency": 0,
#                 "user_remark": f"Net salaries payable for {payroll_period}",
#                 "reference_type": "Payroll Entry",
#                 "reference_name": payroll_entry,
#             },
#         )

#         # Insert and Submit Bank Entry
#         bank_entry.insert()
#         # journal_entry.submit()
#         # frappe.db.commit()

#         frappe.msgprint(
#             f"Bank entry {bank_entry.name} created successfully.", alert=True
#         ),

#         return {
#             "message": f"Journal entry {journal_entry.name} created successfully.",
#             # "journal_entry": journal_entry.name,
#             "message": f"Bank entry {bank_entry.name} created successfully.",
#             # "bank_entry": bank_entry.name,
#             "status": "success",
#         }

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "fetch_and_create_journal_entry")
#         return {"error": str(e)}


@frappe.whitelist()
def fetch_and_create_journal_entry_from_payroll_entry(
    payroll_entry,
    payroll_period,
    company,
    currency,
    posting_date,
    payroll_payable_account,
    cost_center,
    payment_account,
):

    # Fetch Salary Slips in draft state
    all_salary_slips = frappe.get_all(
        "Salary Slip",
        filters={
            "payroll_entry": payroll_entry,
            "payroll_period": payroll_period,
            "company": company,
            "currency": currency,
            "docstatus": 0,
        },
        fields=["name", "docstatus"],
    )
    for slip in all_salary_slips:
        slip_doc = frappe.get_doc("Salary Slip", slip["name"])
        slip_doc.submit()

    try:
        # Fetch Salary Slips
        salary_slips = frappe.get_all(
            "Salary Slip",
            filters={
                "payroll_entry": payroll_entry,
                "payroll_period": payroll_period,
                "company": company,
                "currency": currency
            },
            fields=["name", "docstatus"],
        )

        if not salary_slips:
            frappe.throw("No Salary Slips found for the given criteria.")

        for slip in salary_slips:
            if slip["docstatus"] == 0:
                frappe.throw(f"Salary Slip {slip['name']} must be submitted first.")

        # Initialize component account mappings
        earnings_map = {}
        deductions_map = {}
        pension_contribution = 0
        total_fringe_benefits = 0

        # Process Salary Slips
        for slip in salary_slips:
            salary_slip = frappe.get_doc("Salary Slip", slip["name"])

            total_statistical_earnings = 0
            total_excluded_earnings = 0
            total_statistical_deductions = 0
            total_excluded_deductions = 0

            slip_pension_contribution = 0

            

            # for earning in salary_slip.earnings:
            #     account = frappe.db.get_value(
            #         "Salary Component Account",
            #         {"parent": earning.salary_component, "company": company},
            #         "account",
            #     )

            #     is_statistical = frappe.db.get_value(
            #         "Salary Component",
            #         earning.salary_component,
            #         "statistical_component",
            #     )
            #     is_excluded = frappe.db.get_value(
            #         "Salary Component",
            #         earning.salary_component,
            #         "do_not_include_in_total",
            #     )

            #     if is_statistical:
            #         total_statistical_earnings += earning.amount
            #     if is_excluded:
            #         total_excluded_earnings += earning.amount

            #     if account:
            #         earnings_map[account] = (
            #             earnings_map.get(account, 0) + earning.amount
            #         )

            #     if earning.salary_component == "Employer Pension Contribution 10%":
            #         pension_contribution += earning.amount

            for earning in salary_slip.earnings:
                is_statistical = frappe.db.get_value(
                    "Salary Component",
                    earning.salary_component,
                    "statistical_component",
                )
                is_excluded = frappe.db.get_value(
                    "Salary Component",
                    earning.salary_component,
                    "do_not_include_in_total",
                )

                if earning.salary_component == "Employer Pension Contribution 10%":
                    pension_contribution += earning.amount

                    slip_pension_contribution += earning.amount

                if is_excluded:
                    total_excluded_earnings += earning.amount
                    continue  # Skip this component entirely

                if is_statistical:
                    total_statistical_earnings += earning.amount

                account = frappe.db.get_value(
                    "Salary Component Account",
                    {"parent": earning.salary_component, "company": company},
                    "account",
                )

                if account:
                    earnings_map[account] = earnings_map.get(account, 0) + earning.amount

            # Calculate and sum fringe benefits
            fringe_benefit = total_excluded_earnings - slip_pension_contribution
            total_fringe_benefits += fringe_benefit

                


            for deduction in salary_slip.deductions:
                account = frappe.db.get_value(
                    "Salary Component Account",
                    {"parent": deduction.salary_component, "company": company},
                    "account",
                )

                is_statistical = frappe.db.get_value(
                    "Salary Component",
                    deduction.salary_component,
                    "statistical_component",
                )
                is_excluded = frappe.db.get_value(
                    "Salary Component",
                    deduction.salary_component,
                    "do_not_include_in_total",
                )

                if is_statistical:
                    total_statistical_deductions += deduction.amount
                if is_excluded:
                    total_excluded_deductions += deduction.amount

                if account:
                    deductions_map[account] = (
                        deductions_map.get(account, 0) + deduction.amount
                    )
        # #Calculate Fringe Benefits
        # fringe_benefits = total_excluded_earnings - pension_contribution

        # Deduct the excluded earnings and statistical earnings from total
        total_earnings = sum(earnings_map.values()) - (
            # total_statistical_earnings + total_excluded_earnings
            # pension_contribution + fringe_benefits
            0
        )
        total_deductions = sum(deductions_map.values()) - (
            total_statistical_deductions + total_excluded_deductions
        )
        # net_payable = total_earnings - total_deductions
        net_payable = total_earnings - total_deductions
        
        print("Earnings Map:", earnings_map)
        print("Deductions Map:", deductions_map)
        print("Total Earnings:", total_earnings)
        print("Total Statistical Earnings:", total_statistical_earnings)
        print("Total Excluded Earnings:", total_excluded_earnings)
        print("Total Deductions:", total_deductions)
        print("Pension Contribution:", pension_contribution)
        print("Net Payable:", net_payable)
        print("Total Fringe Benefits:", total_fringe_benefits)

        # Prepare Journal Entry
        journal_entry = frappe.get_doc(
            {
                "doctype": "Journal Entry",
                "voucher_type": "Journal Entry",
                "company": company,
                "posting_date": posting_date,
                "user_remark": f"Payroll Journal Entry for {payroll_period}",
                "accounts": [],
            }
        )

        # Add Earnings Entries
        for account, amount in earnings_map.items():
            journal_entry.append(
                "accounts",
                {
                    "account": account,
                    "debit_in_account_currency": total_earnings,
                    "credit_in_account_currency": 0,
                    "user_remark": f"Being Salary journal for {payroll_period}",
                },
            )

        # Get the main earnings account
        main_earnings_account = frappe.db.get_value(
            "Salary Component Account",
            {"parent": "Basic Compensation", "company": company},
            "account",
        )
        # Add Employer Pension Contribution
        if pension_contribution > 0:
            pension_account = frappe.db.get_value(
                "Salary Component Account",
                {"parent": "Basic Compensation", "company": company},
                "account",
            )
            if pension_account:
                journal_entry.append(
                    "accounts",
                    {
                        "account": main_earnings_account,
                        "debit_in_account_currency": pension_contribution,
                        "credit_in_account_currency": 0,
                        "user_remark": f"Employer Pension Contribution for {payroll_period}",
                    },
                )

        # Add Fringe Benefits in debit
        if total_fringe_benefits > 0:
            journal_entry.append(
                "accounts",
                {
                    "account": main_earnings_account,
                    "debit_in_account_currency": total_fringe_benefits,
                    "credit_in_account_currency": 0,
                    "user_remark": f"Other fringe Benefits for {payroll_period}",
                },
            )

        # Add Deductions Entries
        for account, amount in deductions_map.items():
            journal_entry.append(
                "accounts",
                {
                    "account": account,
                    "debit_in_account_currency": 0,
                    "credit_in_account_currency": amount,
                    "user_remark": f"Deductions for {payroll_period}",
                    "reference_type": "Payroll Entry",
                    "reference_name": payroll_entry,
                },
            )

        # Add Employer Pension Contribution in credit
        if pension_contribution > 0:
            pension_account = frappe.db.get_value(
                "Salary Component Account",
                {"parent": "Employee Pension Contribution", "company": company},
                "account",
            )
            if pension_account:
                journal_entry.append(
                    "accounts",
                    {
                        "account": pension_account,
                        "debit_in_account_currency": 0,
                        "credit_in_account_currency": pension_contribution,
                        "user_remark": f"Employer Pension Contribution for {payroll_period}",
                        "reference_type": "Payroll Entry",
                        "reference_name": payroll_entry,
                    },
                )

        #Add Fringe Benefits in credit        
        if total_fringe_benefits > 0:
            fringe_account = frappe.db.get_value(
                "Salary Component Account",
                {"parent": "Annual Bonus", "company": company},
                "account",
            )
            if fringe_account:
                journal_entry.append(
                    "accounts",
                    {
                        "account": fringe_account,
                        "debit_in_account_currency": 0,
                        "credit_in_account_currency": total_fringe_benefits,
                        "user_remark": f"Other fringe Benefits for {payroll_period}",
                        "reference_type": "Payroll Entry",
                        "reference_name": payroll_entry,
                    },
                )

        # Add Payroll Payable Account as balancing entry
        journal_entry.append(
            "accounts",
            {
                "account": payroll_payable_account,
                "debit_in_account_currency": 0,
                "credit_in_account_currency": net_payable,
                "user_remark": f"Net salaries payable for {payroll_period}",
                "reference_type": "Payroll Entry",
                "reference_name": payroll_entry,
            },
        )

        # # Insert and Submit Journal Entry
        journal_entry.insert()
        # # journal_entry.submit()
        # # frappe.db.commit()

        frappe.msgprint(
            f"Journal entry {journal_entry.name} created successfully.",
            alert=True,
        )
        # return {
        #     "message": f"Journal entry {journal_entry.name} created successfully.",
        #     "journal_entry": journal_entry.name,
        # }

        bank_entry = frappe.get_doc(
            {
                "doctype": "Journal Entry",
                "voucher_type": "Bank Entry",
                "company": company,
                "posting_date": posting_date,
                "cheque_no": "XXXXXXXXXX",
                "cheque_date": posting_date,
                "user_remark": f"Payroll Bank Entry for {payroll_period}",
                "accounts": [],
            }
        )

        # Add Earnings Entries
        for account, amount in earnings_map.items():
            bank_entry.append(
                "accounts",
                {
                    "account": payment_account,
                    "debit_in_account_currency": 0,
                    "credit_in_account_currency": total_earnings,
                    "user_remark": f"Being Salary bank entry for {payroll_period}",
                },
            )

        # Add Employer Pension Contribution
        if pension_contribution > 0:
            pension_account = frappe.db.get_value(
                "Salary Component Account",
                {"parent": "Employer Pension Contribution 10%", "company": company},
                "account",
            )

            if pension_account:
                bank_entry.append(
                    "accounts",
                    {
                        "account": payment_account,
                        "debit_in_account_currency": 0,
                        "credit_in_account_currency": pension_contribution,
                        "user_remark": f"Employer Pension Contribution for {payroll_period}",
                    },
                )

        # Add Fringe Benefits in payment account
        if total_fringe_benefits > 0:
            bank_entry.append(
                "accounts",
                {
                    "account": payment_account,
                    "debit_in_account_currency": 0,
                    "credit_in_account_currency": total_fringe_benefits,
                    "user_remark": f"Other fringe Benefits for {payroll_period}",
                },
            )

        # Add Deductions Entries
        for account, amount in deductions_map.items():
            bank_entry.append(
                "accounts",
                {
                    "account": account,
                    "debit_in_account_currency": amount,
                    "credit_in_account_currency": 0,
                    "user_remark": f"Deductions for {payroll_period}",
                    "reference_type": "Payroll Entry",
                    "reference_name": payroll_entry,
                },
            )

        # Add Employer Pension Contribution in credit
        if pension_contribution > 0:
            pension_account = frappe.db.get_value(
                "Salary Component Account",
                {"parent": "Employee Pension Contribution", "company": company},
                "account",
            )

            if pension_account:
                bank_entry.append(
                    "accounts",
                    {
                        "account": pension_account,
                        "debit_in_account_currency": pension_contribution,
                        "credit_in_account_currency": 0,
                        "user_remark": f"Employer Pension Contribution for {payroll_period}",
                        "reference_type": "Payroll Entry",
                        "reference_name": payroll_entry,
                    },
                )

        # Add Fringe Benefits in credit
        if total_fringe_benefits > 0:
            fringe_account = frappe.db.get_value(
                "Salary Component Account",
                {"parent": "Annual Bonus", "company": company},
                "account",
            )
            if fringe_account:
                bank_entry.append(
                    "accounts",
                    {
                        "account": fringe_account,
                        "debit_in_account_currency": total_fringe_benefits,
                        "credit_in_account_currency": 0,
                        "user_remark": f"Other fringe Benefits for {payroll_period}",
                        "reference_type": "Payroll Entry",
                        "reference_name": payroll_entry,
                    },
                )

        # Add Payroll Payable Account as balancing entry
        bank_entry.append(
            "accounts",
            {
                "account": payroll_payable_account,
                "debit_in_account_currency": net_payable,
                "credit_in_account_currency": 0,
                "user_remark": f"Net salaries payable for {payroll_period}",
                "reference_type": "Payroll Entry",
                "reference_name": payroll_entry,
            },
        )

        # Insert and Submit Bank Entry
        bank_entry.insert()
        # journal_entry.submit()
        # frappe.db.commit()

        frappe.msgprint(
            f"Bank entry {bank_entry.name} created successfully.", alert=True
        ),

        return {
            "message": f"Journal entry {journal_entry.name} created successfully.",
            # "journal_entry": journal_entry.name,
            "message": f"Bank entry {bank_entry.name} created successfully.",
            # "bank_entry": bank_entry.name,
            "status": "success",
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "fetch_and_create_journal_entry")
        return {"error": str(e)}


def test_fetch_and_create_journal_entry_from_payroll_entry():
    payroll_entry = "HR-PRUN-2025-00042"  # Replace with an actual Payroll Entry
    payroll_period = "May 2025"  # Replace with the actual payroll period
    company = "Sydani Technologies"  # Replace with the actual company
    currency = "NGN"  # Replace with the actual currency
    posting_date = "2025-05-23"  # Replace with an actual posting date
    payroll_payable_account = (
        "2108 - Payroll Payable - ST"  # Replace with the actual account
    )
    cost_center = "Main - ST"  # Replace with the actual cost center
    payment_account = (
        "1500615136 - Operations - ST"  # Replace with the actual payment account
    )

    try:
        # Call the function to fetch and create the journal entry
        result = fetch_and_create_journal_entry_from_payroll_entry(
            payroll_entry,
            payroll_period,
            company,
            currency,
            posting_date,
            payroll_payable_account,
            cost_center,
            payment_account,
        )

        # Check the result and print relevant information
        if isinstance(result, dict) and "message" in result:
            print(f"Success: {result['message']}")
        elif isinstance(result, dict) and "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Unexpected result format: {result}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print(frappe.get_traceback())



import frappe
from frappe.utils import now_datetime, add_days, formatdate

@frappe.whitelist()
def send_rfq_emails(docname):
    doc = frappe.get_doc("Procurement Request", docname)

    for row in doc.vendors_being_considered:
        email = row.email
        vendor = row.vendor

        if not email:
            continue

        subject = f"Request for Quotation (RFQ) - Sydani Group"
        due_date = formatdate(add_days(now_datetime(), 2), "dd-MM-yyyy")

        context = {
            "doc": doc,
            "vendor_column": vendor,
            "due_date": due_date
        }

        message = frappe.render_template("""
        <p><strong>RFQ ID:</strong> {{ doc.name }}</p>
        <p><strong>Response Due Date & Time:</strong> {{ due_date }} / 15:00pm</p>
        <hr>
        <h3>1.0 Background to Sydani Group</h3>
        <p>Sydani Group is a management consulting firm founded by seasoned international development professionals...</p>

        <h3>2.0 Subject of Procurement</h3>
        <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead><tr>
        <th style="padding: 8px;">Item</th>
        <th style="padding: 8px;">Description</th>
        <th style="padding: 8px;">Quantity</th>
        </tr></thead>
        <tbody>
        {% for item in doc.items %}
        <tr>
        <td style="padding: 8px;">{{ item.item }}</td>
        <td style="padding: 8px;">{{ item.description }}</td>
        <td style="padding: 8px;">{{ item.quantity }}</td>
        </tr>
        {% endfor %}
        </tbody></table>

        <p>Click the link below to send your RFQ:</p>
        <p><a href="https://office.sydani.org/request-for-quotation-response?new=1&procurement_request={{ doc.name }}&vendor={{ vendor_column }}">
        Submit Quotation
        </a></p>

        <p>Yours sincerely,<br><strong>Marcus Sule</strong></p>
                """, context)

        frappe.sendmail(
            recipients=[email],
            subject=subject,
            message=message
        )

    return "Emails sent successfully"

