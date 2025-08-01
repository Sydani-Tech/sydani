import frappe
from frappe import _
from frappe.utils import date_diff, now_datetime, add_days, getdate, add_to_date, now
from datetime import date, timedelta, datetime
from datetime import datetime
from sydani.payment import fetch_transfer, create_transaction_log
import requests
import json


def all():
    frappe.db.sql("DELETE FROM `tabGrievances and Complaints`")
    frappe.db.sql("DELETE FROM `tabWhistleblowing Form`")


def test_cams_punch_log():
    try:
        # AIPG29804894
        # AIQF17804592 -> pMxWWVPjPC73FBZ5dTxFNT1diDXKLyZA
        api_url = (
            "https://robot.camsunit.com/external/api3.0/biometric?stgid=AIPG29804894"
        )
        AuthToken = "pMxWWVPjPC73FBZ5dTxFNT1diDXKLyZA"
        operation_id = "j95xfejt3vr1"
        startTime = "2023-07-1 00:01:33"
        endTime = "2023-07-18 22:01:33"
        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")
        o_time = formatted_date

        data = {
            "Load": {
                "PunchLog": {"Filter": {"StartTime": startTime, "EndTime": endTime}}
            },
            "OperationID": operation_id,
            "AuthToken": AuthToken,
            "Time": o_time,
        }

        r = requests.post(api_url, json=data)
        print(r.content)
    except Exception as err:
        print(err)
        pass


# def add_user_with_photo():
#     user = {
#         "Add": {
#             "User": {
#                 "UserID": doc[3],
#                 "FirstName": doc[0],
#                 "LastName": doc[1],
#                 "UserType": "User"
#             }
#             "Template": [
#                {
#                     "Type": "Face",
#                     "UserID": "100",
#                     "Size": "25072",
#                     "Index": "0",
#                     "Data": "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAIBAQEBAQIBAQECAgICAgQDAgICAgUEBAMEBgUGBgYFBgYGBwkIBgcJBwYGCAsICQoKCgoKBggLDAsKDAkKCgr/2wBDAQICAgICAgUDAwU............scfxW8RRIo7KNUuQB+Qr5v1aRi3X/ADzXQ2dsI3RSnujknd1FQNckAl2PTOM1FdMRGx69Kgk4GQenSkka8jbsWzcgDcGpVuiR949exqkGZhuJ5JqNmLtk8fSkn2GoO5//2Q=="
#                },
#                {
#                     "Type": "Card",
#                     "UserID": "100",
#                     "Data": "102836"
#                },
#                 {
#                     "Type": "Fingerprint",
#                     "UserID": "100",
#                     "Index": "0",
#                     "Data": "TW9TUzIxAAAELC4ECAUHCc7QAAAcLWkBAAAAhNElqSxUAJIPOwCdAOojpgBqACMPrwCCLG0PDQCMAJQPPyyPAOYPGgBZANMjZACdAAkPXQClLJ0PygCiAGkPdiyqAGUPUQB2AFQjoQC+AKEPvADALE8OZwDKAI4NTSzOAEwOYgAfAM8hHQDeAFgP9QDbLE4PiAD6AOsPSSz8ADw..........jFifsBaMGPBRBPxDqMKhFbBjqQwsYQczEwwhsQ1yJnVFFdwMLBx8bEBW1T0ycGEEMnEPrABzyPKSfBBxCxLSOsXwkQKjX0OPtBTQQQIjoGwu0EFKM9Ho0GEC2AAPjuPAUQgU0XOsT6JBEuUAP+wAf+XS8RWl4MwVKHAA9vAAAAC0VS"
#                }
#           ]
#         },
#         "OperationID": "2jxpjfsasu8w3",
#         "AuthToken": AuthToken,
#         "Time": o_time
#     }


def cams_update_users():
    try:
        api_url = (
            "https://robot.camsunit.com/external/api3.0/biometric?stgid=AIQF17804592"
        )
        api_url_second_device = (
            "https://robot.camsunit.com/external/api3.0/biometric?stgid=ZXQF20805346"
        )
        # AuthToken = "iIka9fuMJv7x6kwaVcmw7BOkbAeSOQd2"
        AuthToken = "pMxWWVPjPC73FBZ5dTxFNT1diDXKLyZA"
        # TAzltzl5qNkZskCtZ9Ff28I5Cy1fYvQF
        tab = "tabEmployee"
        # operation_id = "2jxpjfsasu8w3"
        operation_id = "ZXQF20805346"
        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")
        o_time = formatted_date
        # Select documents from erp
        docs = frappe.db.sql(
            f'SELECT `first_name`, `last_name`, `status`, `attendance_device_id`, `user_id`, `access_card`, `attendance_device_manager` FROM `{tab}` WHERE `status` = "Active" AND `attendance_device_id` IS NOT NULL AND (DATE(`modified`) = CURDATE() OR DATE(`creation`) = CURDATE())'
        )
        # docs = frappe.db.sql(
        #     """
        #         SELECT `first_name`, `last_name`, `status`, `attendance_device_id`, `user_id`, `access_card`, `attendance_device_manager`
        #         FROM `tabEmployee`
        #         WHERE `status` = %s
        #         AND `attendance_device_id` IS NOT NULL
        #         AND `company` = %s
        #         """,
        #     values=("Active", "Sydani Institute for Research and Innovation"),
        #     # as_dict=True,  # Optional: returns results as a list of dicts
        # )

        if docs:
            print(docs)
            for doc in docs:
                user_type = "User" if doc[6] == 0 else "ADMIN"
                user = {
                    "Add": {
                        "User": {
                            "UserID": doc[3],
                            "FirstName": doc[0],
                            "LastName": doc[1],
                            "UserType": user_type,
                        }
                    },
                    # "OperationID": "2jxpjfsasu8w3",
                    "OperationID": "ZXQF20805346",
                    "AuthToken": AuthToken,
                    "Time": o_time,
                }

                if doc[5] != "null" and doc[5] != None:
                    user_type = "User" if doc[6] == 0 else "ADMIN"
                    user = {
                        "Add": {
                            "User": {
                                "UserID": doc[3],
                                "FirstName": doc[0],
                                "LastName": doc[1],
                                "UserType": user_type,
                            },
                            "Template": [
                                {"Type": "Card", "UserID": doc[3], "Data": doc[5]}
                            ],
                        },
                        # "OperationID": "2jxpjfsasu8w3",
                        "OperationID": "ZXQF20805346",
                        "AuthToken": AuthToken,
                        "Time": o_time,
                    }

                    update_user_card = {
                        "RealTime": {
                            "UserUpdated": {
                                "UserID": doc[3],
                                "OperationTime": o_time,
                                "Template": [
                                    {"Type": "Card", "UserID": doc[3], "Data": doc[5]}
                                ],
                            },
                            # "OperationID": "1vsyboxnuuorq",
                            "OperationID": "ZXQF20805346",
                            "AuthToken": AuthToken,
                            "Time": o_time,
                        }
                    }

                    # update_access_card = requests.post(api_url, json=update_user_card)
                # user["AuthToken"] = "a7HSEjzJ2EFzJmkCRxknSWXagmYCA5oV"
                user["AuthToken"] = "pMxWWVPjPC73FBZ5dTxFNT1diDXKLyZA"

                add_to_first_devices = requests.post(api_url, json=user)

                user["AuthToken"] = "iIka9fuMJv7x6kwaVcmw7BOkbAeSOQd2"

                add_to_second_devices = requests.post(api_url_second_device, json=user)

                print(f"{doc[0]} updated")
            # print(add_to_first_devices.content)
            # print(user_type)

        # get users that left from erp
        users_left = frappe.db.sql(
            f'SELECT `attendance_device_id`, `status`, `name`, `access_card` FROM {tab} WHERE `status` = "Left" AND `attendance_device_id` IS NOT NULL AND `access_card` IS NOT NULL AND (DATE(`modified`) = CURDATE())'
        )

        if users_left:

            # for each user that left as user object
            for user in users_left:
                delete_obj = {
                    "Delete": {"User": {"UserID": user[0]}},
                    # "OperationID": "1jxpjeoasu8wl",
                    "OperationID": "ZXQF20805346",
                    "AuthToken": AuthToken,
                    "Time": o_time,
                }
                # delete_obj["AuthToken"] = "a7HSEjzJ2EFzJmkCRxknSWXagmYCA5oV"
                delete_obj["AuthToken"] = "pMxWWVPjPC73FBZ5dTxFNT1diDXKLyZA"
                delete_from_first_device = requests.post(api_url, json=delete_obj)

                delete_obj["AuthToken"] = "iIka9fuMJv7x6kwaVcmw7BOkbAeSOQd2"
                delete_from_second_device = requests.post(
                    api_url_second_device, json=delete_obj
                )
                print(f"{user[2]} Deleted")

                # Update the employee record, set the field access_card to null
                frappe.db.set_value(tab, user[2], "access_card", None)

    except Exception as err:
        print(err)
        pass


def shift_22nd():
    try:
        # sync_time = add_to_date(now(), months=1)
        sync_time = datetime.now() - timedelta(days=2)  # Set time three days back
        stmt = f"UPDATE `tabShift Type` SET `last_sync_of_checkin` = '{sync_time}' WHERE `name` = 'Day Shift'"
        frappe.db.sql(stmt)
    except Exception as err:
        print(err)
        pass


def shift():
    try:
        sync_time = datetime.now() - timedelta(days=3)  # Set time three days back
        sync_time_formatted = sync_time.strftime("%Y-%m-%d %H:%M:%S")
        print(sync_time_formatted)
        stmt = f"UPDATE `tabShift Type` SET `last_sync_of_checkin` = '{sync_time_formatted}' WHERE `name` = 'Day Shift'"
        frappe.db.sql(stmt)
    except Exception as err:
        print(err)
        pass


# def delete_attendance():
#     try:
#         start_date = date.today().replace(day=1)
#         last_date = date.today().replace(day=24)

#         for att in frappe.get_list(
#             "Attendance",
#             filters={
#                 "attendance_date": ["between", (start_date, last_date)],
#                 "status": "Absent",
#             },
#         ):
#             att = frappe.get_doc("Attendance", att.name)

#             att.cancel()
#             att.delete()
#     except Exception as err:
#         print(err)
#         pass


# def delete_attendance_month_end():
#     start_date = date.today().replace(day=26)
#     last_date = (date.today().replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)

#     for att in frappe.get_list('Attendance', filters={'attendance_date': ['between', (start_date, last_date)], 'status': 'Absent'}):

#         att = frappe.get_doc('Attendance', att.name)

#         att.cancel()
#         att.delete()


def get_speedexam_auth_header(apiNameId):
    try:
        # Get aqccess token vars
        get_access_token_url = "https://apiv2.speedexam.net/api/Token/Get-Access-Token"
        get_access_token_data = {
            "customerId": "852-89228",
            "apiNameId": apiNameId,
            "apiKey": "65505293-567e-4c8a-9ab1-f1a57f161a87",
        }

        # Post request to get access token
        access_token_request = requests.post(
            get_access_token_url, json=get_access_token_data
        )
        access_token_request_json = access_token_request.json()

        return {"Authorization": "Bearer " + access_token_request_json["token"]}
    except Exception as err:
        print(err)
        pass


import random
import re


def generate_username(firstname, lastname):
    # Remove spaces from firstname and lastname
    # firstname = firstname.replace(" ", "")
    # lastname = lastname.replace(" ", "")

    firstname = re.sub(r"[^A-Za-z0-9]", "", firstname)
    lastname = re.sub(r"[^A-Za-z0-9]", "", lastname)

    # Generate 4 random characters excluding '0', '1', 'O', 'o', 'L', 'l', 'i', 'I'
    characters = "23456789ABCDEFGHJKMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz"
    random_chars = "".join(random.choices(characters, k=4))

    # Create the username
    return f"{firstname}{lastname}{random_chars}"


def add_speedexam_candidate():
    try:
        # Get authorization header
        # header = get_speedexam_auth_header("06")

        # Get Applicants that are wating for assessment
        applicants = frappe.db.sql(
            f"""
            SELECT * FROM `tabJob Applicant` WHERE status = 'Awaiting Assessment' """,
            as_dict=True,
        )

        if len(applicants) > 0:

            # Get authorization header
            header = get_speedexam_auth_header("06")

            # Loop through the applicants list
            for applicant in applicants:

                # Generate the username
                user_name = generate_username(applicant.firstname, applicant.lastname)

                # set var for canditate data
                candidate_data = {
                    "firstName": applicant.firstname,
                    "lastName": applicant.lastname,
                    "street": applicant.name,
                    "phone": applicant.phone_number,
                    "mobile": applicant.phone_number,
                    # "email": applicant.email,
                    "email": user_name,
                    # "userName": applicant.email,
                    "userName": user_name,
                    "password": applicant.assessment_password,
                    "groupsequenceId": 159,
                    "isActive": "True",
                }

                if applicant.job_title == "sydani-fellowship-program":
                    candidate_data["groupsequenceId"] = 138

                if applicant.job_title == "lga-technical-assistants":
                    candidate_data["groupsequenceId"] = 166

                # Add candidate url
                add_candidate_url = (
                    "https://apiv2.speedexam.net/api/Employee/Create a New Candidate"
                )
                # Create a candidate on speed speedexam
                add_candidate_request = requests.post(
                    add_candidate_url, json=candidate_data, headers=header
                )

                add_candidate_request_json = add_candidate_request.json()

                response_to_object = json.loads(add_candidate_request_json["result"])
                # response_description = response_to_object['Description']

                assessment_schedule_time = datetime.now().strftime(
                    "%Y, %m, %d, 8, 0, 0"
                )
                assessment_schedule_end = (datetime.now() + timedelta(days=3)).strftime(
                    "%Y,%m,%d 22:00:00"
                )

                doc = frappe.get_doc("Job Applicant", applicant.name)
                doc.speedexam_candidate_status = response_to_object["Description"]
                doc.username_2 = user_name
                if doc.speedexam_candidate_status == "Record Saved Successfully":
                    doc.status = "Assessment Scheduled"
                doc.save()

    except Exception as err:
        print(err)
        pass


def save_exam_result(result_objects, sfp=None):
    for result in result_objects:
        try:
            doc = frappe.get_doc("Job Applicant", {"username_2": result["username"]})
            if sfp:
                if result["percentage"] >= 60:
                    if (
                        doc.status == "Assessment Scheduled"
                        or doc.status == "Rejected - No Assessment"
                    ):
                        # if doc.status == "Rejected - No Assessment":
                        doc.assessment_score = result["percentage"]
                        doc.status = "Assessment Completed"
                        doc.save()
                elif result["percentage"] <= 39:
                    if (
                        doc.status == "Assessment Scheduled"
                        or doc.status == "Rejected - No Assessment"
                    ):
                        # if doc.status == "Rejected - No Assessment":
                        doc.assessment_score = result["percentage"]
                        doc.status = "Rejected - Assessment"
                        doc.save()
                elif (result["percentage"] > 39) and (result["percentage"] < 60):
                    if (
                        doc.status == "Assessment Scheduled"
                        or doc.status == "Rejected - No Assessment"
                    ):
                        # if doc.status == "Rejected - No Assessment":
                        doc.assessment_score = result["percentage"]
                        doc.status = "Assessment Imported"
                        doc.save()
            else:
                if result["percentage"] >= 50:
                    if (
                        doc.status == "Assessment Scheduled"
                        or doc.status == "Rejected - No Assessment"
                    ):
                        doc.assessment_score = result["percentage"]
                        doc.status = "Assessment Completed"
                        doc.save()
                elif result["percentage"] <= 34:
                    if (
                        doc.status == "Assessment Scheduled"
                        or doc.status == "Rejected - No Assessment"
                    ):
                        doc.assessment_score = result["percentage"]
                        doc.status = "Rejected - Assessment"
                        doc.save()
                elif (result["percentage"] > 34) and (result["percentage"] < 50):
                    if (
                        doc.status == "Assessment Scheduled"
                        or doc.status == "Rejected - No Assessment"
                    ):
                        doc.assessment_score = result["percentage"]
                        doc.status = "Assessment Imported"
                        doc.save()
            print(result)
            print(" ")
        except Exception as err:
            print(err)
            pass

def save_exam_result_spac(result_objects, sfp=None):
    for result in result_objects:
        try:
            doc = frappe.get_doc("Job Applicant", {"username_2": result["username"]})
            if sfp:
                if result["percentage"] >= 60:
                    if (
                        doc.status == "Assessment Scheduled"
                        or doc.status == "Rejected - No Assessment"
                    ):
                        # if doc.status == "Rejected - No Assessment":
                        doc.assessment_score = result["percentage"]
                        doc.status = "Assessment Completed"
                        doc.save()
                elif result["percentage"] <= 39:
                    if (
                        doc.status == "Assessment Scheduled"
                        or doc.status == "Rejected - No Assessment"
                    ):
                        # if doc.status == "Rejected - No Assessment":
                        doc.assessment_score = result["percentage"]
                        doc.status = "Rejected - Assessment"
                        doc.save()
                elif (result["percentage"] > 39) and (result["percentage"] < 60):
                    if (
                        doc.status == "Assessment Scheduled"
                        or doc.status == "Rejected - No Assessment"
                    ):
                        # if doc.status == "Rejected - No Assessment":
                        doc.assessment_score = result["percentage"]
                        doc.status = "Assessment Imported"
                        doc.save()
            else:
                if result["percentage"] >= 60:
                    if (
                        doc.status == "Assessment Scheduled"
                        or doc.status == "Rejected - No Assessment"
                    ):
                        doc.assessment_score = result["percentage"]
                        doc.status = "Assessment Completed"
                        doc.save()
                elif result["percentage"] < 60:
                    if (
                        doc.status == "Assessment Scheduled"
                        or doc.status == "Rejected - No Assessment"
                    ):
                        doc.assessment_score = result["percentage"]
                        doc.status = "Rejected - Assessment"
                        doc.save()
                
            print(result)
            print(" ")
        except Exception as err:
            print(err)
            pass




def get_speedexam_result():
    try:
        # Get authorization header
        header = get_speedexam_auth_header("02")
        today = datetime.now().strftime("%Y-%m-%d")
        # today = datetime.now() - timedelta(days=20)
        last_week = datetime.now() - timedelta(days=8)
        last_week = last_week.strftime("%Y-%m-%d")

        get_exam_result_url = f"""https://apiv2.speedexam.net/api/Exams/Get Results for an Exam?ExamSequnceId=102&Startdate={last_week}&Enddate={today}&PageNo=1&PageRows=100"""
        get_exam_result_url2 = f"""https://apiv2.speedexam.net/api/Exams/Get Results for an Exam?ExamSequnceId=102&Startdate={last_week}&Enddate={today}&PageNo=2&PageRows=100"""
        get_exam_result_url3 = f"""https://apiv2.speedexam.net/api/Exams/Get Results for an Exam?ExamSequnceId=102&Startdate={last_week}&Enddate={today}&PageNo=3&PageRows=100"""
        sfp_exam_result_url = f"""https://apiv2.speedexam.net/api/Exams/Get Results for an Exam?ExamSequnceId=109&Startdate={last_week}&Enddate={today}&PageNo=1&PageRows=100"""
        sfp_exam_result_url2 = f"""https://apiv2.speedexam.net/api/Exams/Get Results for an Exam?ExamSequnceId=109&Startdate={last_week}&Enddate={today}&PageNo=2&PageRows=100"""
        sfp_exam_result_url3 = f"""https://apiv2.speedexam.net/api/Exams/Get Results for an Exam?ExamSequnceId=109&Startdate={last_week}&Enddate={today}&PageNo=3&PageRows=100"""
        sfp_exam_result_url4 = f"""https://apiv2.speedexam.net/api/Exams/Get Results for an Exam?ExamSequnceId=109&Startdate={last_week}&Enddate={today}&PageNo=4&PageRows=100"""
        sfp_exam_result_url5 = f"""https://apiv2.speedexam.net/api/Exams/Get Results for an Exam?ExamSequnceId=109&Startdate={last_week}&Enddate={today}&PageNo=5&PageRows=100"""

        spac_exam_result_url = f"""https://apiv2.speedexam.net/api/Exams/Get Results for an Exam?ExamSequnceId=114&Startdate={last_week}&Enddate={today}&PageNo=1&PageRows=100"""
        spac_exam_result_url2 = f"""https://apiv2.speedexam.net/api/Exams/Get Results for an Exam?ExamSequnceId=114&Startdate={last_week}&Enddate={today}&PageNo=2&PageRows=100"""
        spac_exam_result_url3 = f"""https://apiv2.speedexam.net/api/Exams/Get Results for an Exam?ExamSequnceId=114&Startdate={last_week}&Enddate={today}&PageNo=3&PageRows=100"""

        exam_result_request = requests.get(get_exam_result_url, headers=header)
        exam_result_request2 = requests.get(get_exam_result_url2, headers=header)
        exam_result_request3 = requests.get(get_exam_result_url3, headers=header)
        sfp_exam_result = requests.get(sfp_exam_result_url, headers=header)
        sfp_exam_result2 = requests.get(sfp_exam_result_url2, headers=header)
        sfp_exam_result3 = requests.get(sfp_exam_result_url3, headers=header)
        sfp_exam_result4 = requests.get(sfp_exam_result_url4, headers=header)
        sfp_exam_result5 = requests.get(sfp_exam_result_url5, headers=header)

        spac_exam_result = requests.get(spac_exam_result_url, headers=header)
        spac_exam_result2 = requests.get(spac_exam_result_url2, headers=header)
        spac_exam_result3 = requests.get(spac_exam_result_url3, headers=header)

        exam_result_request_json = exam_result_request.json()
        exam_result_request_json2 = exam_result_request2.json()
        exam_result_request_json3 = exam_result_request3.json()
        sfp_result_request_json = sfp_exam_result.json()
        sfp_result_request_json2 = sfp_exam_result2.json()
        sfp_result_request_json3 = sfp_exam_result3.json()
        sfp_result_request_json4 = sfp_exam_result4.json()
        sfp_result_request_json5 = sfp_exam_result5.json()

        spac_result_request_json = spac_exam_result.json()
        spac_result_request_json2 = spac_exam_result2.json()
        spac_result_request_json3 = spac_exam_result3.json()

        if sfp_result_request_json["status"] == 200:
            sfp_result_to_object = json.loads(sfp_result_request_json["result"])
            save_exam_result(sfp_result_to_object, True)

        if sfp_result_request_json2["status"] == 200:
            sfp_result_to_object2 = json.loads(sfp_result_request_json2["result"])
            save_exam_result(sfp_result_to_object2, True)

        if sfp_result_request_json3["status"] == 200:
            sfp_result_to_object3 = json.loads(sfp_result_request_json3["result"])
            save_exam_result(sfp_result_to_object3, True)

        if sfp_result_request_json4["status"] == 200:
            sfp_result_to_object4 = json.loads(sfp_result_request_json4["result"])
            save_exam_result(sfp_result_to_object4, True)

        if sfp_result_request_json5["status"] == 200:
            sfp_result_to_object5 = json.loads(sfp_result_request_json5["result"])
            save_exam_result(sfp_result_to_object5, True)

        if exam_result_request_json["status"] == 200:
            result_to_object = json.loads(exam_result_request_json["result"])
            save_exam_result(result_to_object)

        if exam_result_request_json2["status"] == 200:
            result_to_object2 = json.loads(exam_result_request_json2["result"])
            save_exam_result(result_to_object2)

        if exam_result_request_json3["status"] == 200:
            result_to_object3 = json.loads(exam_result_request_json3["result"])
            save_exam_result(result_to_object3)

        if spac_result_request_json["status"] == 200:
            spac_result_to_object = json.loads(spac_result_request_json["result"])
            save_exam_result_spac(spac_result_to_object)

        if spac_result_request_json2["status"] == 200:
            spac_result_to_object2 = json.loads(spac_result_request_json2["result"])
            save_exam_result_spac(spac_result_to_object2)

        if spac_result_request_json3["status"] == 200:
            spac_result_to_object3 = json.loads(spac_result_request_json3["result"])
            save_exam_result_spac(spac_result_to_object3)

    except Exception as err:
        print(err)
        pass


# def get_speedexam_candidates():
#     # try:
#     # Get authorization header
#     base_url = 'https://apiv2.speedexam.net/'
#     header = get_speedexam_auth_header("07")

#     # get_candidates_url = f"""{base_url}api/Employee/Get Candidate List?Groupid=149&Page_no=1&Page_size=100"""
#     get_candidates_url = f"""{base_url}api/Employee/Get Candidate List?Page_no=1&Page_size=100"""
#     candidates_request = requests.get(get_candidates_url, headers=header)
#     candidates_request_json = candidates_request.json()

#     if candidates_request_json["status"] == 200:
#         candidates = json.loads(candidates_request_json["result"])
#         for candidate in candidates:
#             candidate_id = candidate['candidateid']
#             candiate_username = candidate['username']
#             # /api/Employee/Delete-Candidate -> use delete method -> CandidateID
#             # /api/Exams/Clear-Candidate-Exam-History -> use delete method -> CandidateID

#             # clear exam history
#             clear_exam = f"""{base_url}api/Exams/Clear-Candidate-Exam-History?CandidateID={candidate_id}"""
#             # delete candidate
#             delete_canditate = f"""{base_url}api/Employee/Delete-Candidate?CandidateID={candidate_id}"""

#             # {
#             #     'firstname': 'Adedayo',
#             #     'lastname': 'Adedoyin',
#             #     'email': 'dayoodupitan@gmail.com',
#             #     'username': 'dayoodupitan@gmail.com',
#             #     'group': 'API - Generic group',
#             #     'candidateid': 66777,
#             #     'totalrowcount': 49973,
#             #     'createby': 'Sydani Group',
#             #     'createdate': 'Jan  8 2024  5:15PM'
#             # }

#             # create candidate after deleting
#             # candidate_data = {
#             #     "firstName": applicant.firstname,
#             #     "lastName": applicant.lastname,
#             #     "street": applicant.name,
#             #     "phone": applicant.phone_number,
#             #     "mobile": applicant.phone_number,
#             #     "email": applicant.email,
#             #     "userName": applicant.email,
#             #     "password": applicant.assessment_password,
#             #     "groupsequenceId": 159,
#             #     "isActive": "True",
#             # }

#             # Add candidate url
#             add_candidate_url = "https://apiv2.speedexam.net/api/Employee/Create a New Candidate"

#             # Create a candidate on speed speedexam
#             add_candidate_request = requests.post(
#                 add_candidate_url, json=candidate_data, headers=header
#             )

#             add_candidate_request_json = add_candidate_request.json()

#             response_to_object = json.loads(add_candidate_request_json["result"])

#             print(candidate_id)
#             print('-----------')
#     # except Exception as e:
#     #     print(e)
#     #     pass


def get_dates_from_range(start_date, end_date):
    try:
        date_list = []
        for n in range(int((end_date - start_date).days) + 1):
            date_list.append(start_date + timedelta(n))
        return date_list
    except Exception as err:
        print(err)
        pass


def confirm_payment_transactions():
    try:
        transactions = frappe.db.sql(
            f""" SELECT name, transaction_id FROM `tabFlutterwave Transaction` 
            WHERE message = 'Transfer Queued Successfully' 
            OR message = 'Transfer retry attempt queued' """,
            as_dict=True,
        )

        for transaction in transactions:
            transfer = fetch_transfer(transaction.transaction_id)
            # print(transfer)
            if transfer["status"] == "success":
                transaction_doc = frappe.get_doc(
                    "Flutterwave Transaction", transaction.name
                )

                status = transfer["data"]["status"]
                complete_message = transfer["data"]["complete_message"]
                failed_message = "DISBURSE FAILED"

                transaction_doc.status = status

                if status == "FAILED":
                    transaction_doc.complete_message = complete_message
                    transaction_doc.message = failed_message
                else:
                    transaction_doc.message = complete_message

                transaction_doc.save()

                create_transaction_log(
                    data=transfer, doc=transaction_doc, type="flutterwave"
                )
                # create_transaction_log(transfer)
                # print(transfer)
    except Exception as err:
        print(err)
        pass


def delete_attendance_on_holidays():
    try:
        holidays_list = frappe.db.sql(
            f""" SELECT name, modified FROM `tabHoliday List` ORDER BY modified DESC LIMIT 1 """,
            as_dict=True,
        )[0]

        holidays = frappe.db.sql(
            f""" SELECT name, parent, holiday_date FROM `tabHoliday` 
            WHERE parent = '{holidays_list['name']}' """,
            as_dict=True,
        )

        today = datetime.today()
        today_minus_20_days = today - timedelta(days=30)

        attendance = frappe.db.sql(
            f""" SELECT name, attendance_date FROM `tabAttendance`
            WHERE attendance_date BETWEEN '{today_minus_20_days}' AND '{today}' """,
            as_dict=True,
        )

        for holiday in holidays:
            for att in attendance:
                if att["attendance_date"] == holiday["holiday_date"]:
                    h_att = frappe.get_doc("Attendance", att["name"])
                    h_att.cancel()
                    h_att.delete()
    except Exception as err:
        print(err)
        pass


def work_plan_create_work_from_home_attendance():
    docs = frappe.db.sql(
        f""" SELECT name, employee, work_from_home_date, general_work_from_home_date
        FROM `tabWork Plan` WHERE work_from_home_date IS NOT NULL AND workflow_state != "Draft" AND attendance_marked = 0 AND YEAR(creation) = YEAR(CURDATE())""",
        as_dict=True,
    )

    docs_general = frappe.db.sql(
        f""" SELECT name, employee, work_from_home_date, general_work_from_home_date
        FROM `tabWork Plan`
        WHERE general_work_from_home_date IS NOT NULL AND workflow_state != "Draft"
        AND general_wfh_marked = 0 AND YEAR(creation) = YEAR(CURDATE())  """,
        as_dict=True,
    )

    for doc in docs:

        att_exists = frappe.db.sql(
            f""" 
            SELECT name from `tabAttendance` 
                WHERE employee = '{doc['employee']}' 
                    AND attendance_date = '{doc['work_from_home_date']}' """,
            as_dict=True,
        )

        # att_exists_general = frappe.db.sql(
        #     f"""
        #     SELECT name from `tabAttendance`
        #         WHERE employee = '{doc['employee']}'
        #             AND attendance_date = '{doc['general_work_from_home_date']}' """,
        #     as_dict=True,
        # )

        if att_exists:
            update_att = frappe.get_doc("Attendance", att_exists[0]["name"])
            update_att.status = "Work From Home"
            update_att.workplan = doc.name
            update_att.save(ignore_permissions=True)
            update_att.submit()

        # if att_exists_general:
        #     update_att = frappe.get_doc("Attendance", att_exists[0]["name"])
        #     update_att.status = "Work From Home"
        #     update_att.workplan = doc.name
        #     update_att.save(ignore_permissions=True)
        #     update_att.submit()

        else:
            att = frappe.get_doc(
                {
                    "doctype": "Attendance",
                    "employee": doc["employee"],
                    "employee_name": doc["employee"],
                    "attendance_date": doc["work_from_home_date"],
                    "status": "Work From Home",
                    "work_plan": doc["name"],
                }
            )

            att.save(ignore_permissions=True)
            att.submit()

            # att_general = frappe.get_doc(
            #     {
            #         "doctype": "Attendance",
            #         "employee": doc["employee"],
            #         "employee_name": doc["employee"],
            #         "attendance_date": doc["general_work_from_home_date"],
            #         "status": "Work From Home",
            #         "work_plan": doc["name"],
            #     }
            # )

            # att_general.save(ignore_permissions=True)
            # att_general.submit()
        # Update attendance_marked to 1 for the current Work Plan
        frappe.db.set_value("Work Plan", doc["name"], "attendance_marked", 1)

    for doc_general in docs_general:
        att_exists_general = frappe.db.sql(
            f""" 
            SELECT name from `tabAttendance` 
                WHERE employee = '{doc_general['employee']}' 
                    AND attendance_date = '{doc_general['general_work_from_home_date']}' """,
            as_dict=True,
        )

        if att_exists_general:
            update_general_att = frappe.get_doc("Attendance", att_exists_general[0]["name"])
            update_general_att.status = "Work From Home"
            update_general_att.workplan = doc_general.name
            update_general_att.save(ignore_permissions=True)
            update_general_att.submit()
            frappe.db.set_value("Work Plan", doc_general["name"], "general_wfh_marked", 1)

        else:
            att_general = frappe.get_doc(
                {
                    "doctype": "Attendance",
                    "employee": doc_general["employee"],
                    "employee_name": doc_general["employee"],
                    "attendance_date": doc_general["general_work_from_home_date"],
                    "status": "Work From Home",
                    "work_plan": doc_general["name"],
                }
            )

            att_general.save(ignore_permissions=True)
            att_general.submit()
            frappe.db.set_value("Work Plan", doc_general["name"], "general_wfh_marked", 1)

        


def sorted_records():
    data = fetch_and_combine_records(
        employee="Ekomobong Akwaowo",
        project="",
        start_date="2023-06-01",
        end_date="2025-09-01",
        holiday_list="Sydani Holidays",
    )

    print(data)


@frappe.whitelist()
def fetch_and_combine_records(
    employee, start_date, end_date, holiday_list, project=None
):
    employee_project_records = frappe.db.sql(
        f"""SELECT name, percentage_fte, hourly_rate
            FROM `tabProject FTE Assignment`
            WHERE employee = '{employee}'
            AND parent = '{project}'""",
    )

    # Check if any records were returned before accessing the first element
    if employee_project_records:
        # Access the first element of the first tuple in the list
        percentage_fte = employee_project_records[0][1]
        hourly_rate = employee_project_records[0][2]
    else:
        # Handle the case where no records were returned
        percentage_fte = None
        hourly_rate = None

    combined_records = []  # List to store combined records

    # Fetching work plans based on employee
    work_plans = frappe.db.sql(
        f"""SELECT name, employee
            FROM `tabWork Plan`
            WHERE employee = '{employee}'""",
        as_dict=True,
    )

    for work_plan in work_plans:
        # Fetching additional activity records based on the parent work plan, status "Done," and date range
        additional_activity_records = frappe.db.sql(
            f"""SELECT name, activity, due_date, project, status, hours, '{percentage_fte}' as percentage_fte, '{hourly_rate}' as hourly_rate
                FROM `tabWork Plan Details Additional Activities`
                WHERE parent = '{work_plan['name']}'
                AND status = "Done"
                AND hours > 0
                {'AND project = %s' % repr(project) if project else ''}
                AND due_date BETWEEN '{start_date}' AND '{end_date}'""",
            as_dict=True,
        )
        combined_records.extend(additional_activity_records)

        # Fetching end of week records based on the parent work plan, status "Done," and date range
        end_of_week_records = frappe.db.sql(
            f"""SELECT name, activity, due_date, project, status, hours, '{percentage_fte}' as percentage_fte, '{hourly_rate}' as hourly_rate
                FROM `tabWork Plan Details End of Week`
                WHERE parent = '{work_plan['name']}'
                AND status = "Done"
                And hours > 0
                {'AND project = %s' % repr(project) if project else ''}
                AND due_date BETWEEN '{start_date}' AND '{end_date}'""",
            as_dict=True,
        )
        combined_records.extend(end_of_week_records)

    public_holidays = frappe.db.sql(
        f"""SELECT name, holiday_date, weekly_off
        From `tabHoliday`
        WHERE holiday_date BETWEEN '{start_date}' AND '{end_date}'
        AND parent = '{holiday_list}'
        AND weekly_off = 0""",
        as_dict=True,  # Convert the result to a list of dictionaries
    )

    # Matching columns and values
    matched_records = []

    for holiday in public_holidays:
        matched_record = {
            "activity": "Public Holiday",
            "due_date": holiday["holiday_date"],
            "project": project,
            "status": "Done",  # Assuming this is a constant value for public holidays
            "hours": 8 * percentage_fte / 100,
            "hourly_rate": hourly_rate,
        }
        matched_records.append(matched_record)

    combined_records.extend(matched_records)

    # Sort combined_records by due date
    sorted_records = sorted(combined_records, key=lambda x: x.get("due_date"))

    return sorted_records


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
        AND leave_nextweek = "No"
    """,
        as_dict=True,
    )

    for workplan in workplans:
        try:
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
            new_workplan.general_work_from_home_date = (
                workplan.next_work_week_begins_on + timedelta(days=4)
            )
            new_workplan.submission = workplan.next_weeks_submission
            new_workplan.approval = workplan.next_weeks_approval
            new_workplan.submission_time = workplan.next_weeks_submission_time
            new_workplan.approval_time = workplan.next_weeks_approval_time
            new_workplan.responsible_person = "Employee"
            new_workplan.copy_workplan = workplan.name
            new_workplan.work_from_home_date = ""
            new_workplan.docstatus = 0
            new_workplan.completion_rate = 0
            new_workplan.total_working_hours = 0
            new_workplan.workplan_created_from_previous = 1
            new_workplan.attendance_marked = 0
            new_workplan.general_wfh_marked = 0

            # Set the name of the Work Plan using employee and work_week_begins_on

            new_workplan.name = (
                f"{workplan.employee} - {workplan.next_work_week_begins_on}"
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

            existing_record = frappe.db.exists("Work Plan", new_workplan.name)
            if not existing_record:

                print(f"Work Plan {new_workplan.name} created successfully")
                new_workplan.save()
                updated_name = (
                    f"{new_workplan.employee} - {new_workplan.work_week_begins_date}"
                )
                frappe.rename_doc(
                    "Work Plan", f"{new_workplan.employee} -", updated_name
                )

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
        except Exception as e:
            pass
    frappe.db.commit()


def calculate_accumulated_depreciation():
    # Fetch all records from Asset Doctype where docstatus is 1, calculate_depreciation is 1, and name is specified
    assets = frappe.get_all(
        "Asset",
        filters={
            "docstatus": 1,
            "calculate_depreciation": 1,
        },
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
        # print(asset_current_value)
        # print(accumulated_depreciation_amount)
        # print(asset.gross_purchase_amount)
        # Update fields in the Asset document
        asset_doc.db_set(
            "accumulated_depreciation_amount", accumulated_depreciation_amount
        )
        asset_doc.db_set("asset_current_value", asset_current_value)

    frappe.db.commit()


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


@frappe.whitelist()
def create_or_update_vendor_evaluation_sheet(doc, method):
    # Ensure this function runs only when the Vendor Evaluation document is saved
    if method != "after_insert":
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
        # if vendor_evaluation_sheet_doc.docstatus == 0:
        #     vendor_evaluation_sheet_doc.evaluator = evaluator
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


def delete_old_records():
    # Calculate the cutoff date which is 3 weeks ago from today
    cutoff_date = add_days(now_datetime(), -21)

    # Fetch and delete old records from Email Queue
    email_queue_records = frappe.get_all(
        "Email Queue",
        filters={"creation": ["<", cutoff_date]},
        limit=1200,
        fields=["name"],
    )
    for record in email_queue_records:
        frappe.delete_doc("Email Queue", record["name"])

    # Fetch and delete old records from Error Log
    error_log_records = frappe.get_all(
        "Error Log",
        filters={"creation": ["<", cutoff_date]},
        limit=1200,
        fields=["name"],
    )
    for record in error_log_records:
        frappe.delete_doc("Error Log", record["name"])

    frappe.db.commit()


def mark_priority_employees_present():
    """
    Marks employees with priority status as present.
    """
    today = now_datetime().date()
    start_date = datetime.now() - timedelta(days=7)

    try:
        # Fetch all employees with priority status
        priority_employees = frappe.get_all(
            "Employee",
            filters={"always_mark_present": 1, "status": "Active"},
            fields=["name"]
        )

        if not priority_employees:
            return

        for employee in priority_employees:
            absent_attendance = frappe.get_all(
                "Attendance",
                filters={
                    "employee": employee.name,
                    "attendance_date": ["between", [start_date, today]],
                    "status": "Absent",
                },
                fields=["name"]
            )

            for attendance in absent_attendance:
                # Mark attendance as present
                attendance_doc = frappe.get_doc("Attendance", attendance.name)
                if attendance_doc.docstatus == 1:
                    attendance_doc.cancel()
                    attendance_doc.delete()

                    new_attendance = frappe.get_doc({
                        "doctype": "Attendance",
                        "employee": employee.name,
                        "attendance_date": attendance_doc.attendance_date,
                        "status": "Present",
                        "company": attendance_doc.company,
                        "shift": attendance_doc.shift,
                    })
                    new_attendance.insert()
                    new_attendance.submit()
                
                else:
                    attendance_doc.status = "Present"
                    attendance_doc.save()
                

        print("Priority employees marked as present successfully.")

    except Exception as e:
        print(f"Error: {str(e)}")