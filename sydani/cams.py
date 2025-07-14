import frappe
from frappe import _
from datetime import timedelta, datetime
from dateutil import parser
import requests
import json
import time

base_url = "https://robot.camsunit.com/external/api3.0/biometric?stgid="


def devices():
    # I skipped the first device on the main enterance
    return [
        # {
        #     "no": 1,
        #     "id": "ZXOL23807340",
        #     "name": "SlimBeast (i33)",
        #     "location": "",
        #     "auth": "qGwY4hb1f2DWA5YDPE7R5SwbGbSRPC9m",
        #     # error {'Status': 'API_RESPONSE_UNKNOWN_ERROR', 'OperationID': 'j95xfejt3vr11', 'StatusCode': 999}
        # },
        # {
        #     "no": 2,
        #     "id": "ZXOL23807307",
        #     "name": "SlimBeast (i33)",
        #     "location": "",
        #     "auth": "g58uaKkSfGGPJuy4wfqA2YtBTAj2iUXB",
        # },
        # {
        #     "no": 3,
        #     "id": "AIQF17804592",
        #     "name": "Ultron MultiFace (f34)",
        #     "location": "Main Exit",
        #     "auth": "pMxWWVPjPC73FBZ5dTxFNT1diDXKLyZA",
        # },
        {
            "no": 4,
            "id": "ZXQF20805360",
            "name": "SlimBeast (i33)",
            "location": "First Floor",
            "auth": "TAzltzl5qNkZskCtZ9Ff28I5Cy1fYvQF",
        },
        # {
        #     "no": 5,
        #     "id": "ZXQF20805344",
        #     "name": "SlimBeast (i33)",
        #     "location": "Fifth Floor",
        #     "auth": "2sKrXCGkTemBPyd7ApQ1ECstYWjPJqbu",
        # },
        # {
        #     "no": 6,
        #     "id": "ZXQF20805351",
        #     "name": "SlimBeast (i33)",
        #     "location": "Fourth Floor",
        #     "auth": "KOrrewgRPM8zYZEt94dEwnO2DRySdioL",
        # },
        # {
        #     "no": 7,
        #     "id": "ZXQF20805350",
        #     "name": "SlimBeast (i33)",
        #     "location": "Second Floor",
        #     "auth": "6ct2FnAzg5EDGHfZQRHpbzWTOq75GZC2",
        # },
        # {
        #     "no": 8,
        #     "id": "ZXQF20805346",
        #     "name": "SlimBeast (i33)",
        #     "location": "Third Floor",
        #     "auth": "iIka9fuMJv7x6kwaVcmw7BOkbAeSOQd2",
        # },
        # {
        #     "no": 9,
        #     "id": "AIPG29804894",
        #     "name": "Ultron MultiFaceFP (f34)",
        #     "location": "Main Entrance",
        #     "auth": "a7HSEjzJ2EFzJmkCRxknSWXagmYCA5oV",
        # }
    ]

def insert_device():

    for device in devices():
        dv = frappe.get_doc({
            "doctype": "Cams Devices",
            "device_id": device['id'],
            "device_name": device['name'],
            "device_location": device['location'],
            "device_auth_key": device['auth'],
        })
        dv.save()
        frappe.db.commit()

def get_log():
    last_eight_days = datetime.strftime(
        datetime.now() - timedelta(8), "%Y-%m-%d %H:%M:%S"
    )
    today = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    for device in devices():
        # Limit to one device - device no 2
        # if(device['no'] == 4):
        current_datetime = datetime.now()
        formatted_date = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
        post_data = {
            "Load": {
                "PunchLog": {"Filter": {"StartTime": last_eight_days, "EndTime": today}}
            },
            "OperationID": "j95xfejt3vr1" + str(device["no"]),
            "AuthToken": device["auth"],
            "Time": formatted_date,
        }
        url = f"{base_url}{device['id']}"
        request_data = requests.post(url, json=post_data).json()
        # employees = frappe.db.sql("SELECT * FROM `tabEmployee` LIMIT 1", as_dict=True)
        # print(employees)
        try:
            print(request_data)
            for log_data in request_data["PunchLog"]["Log"]:
                # employee = frappe.get_doc("Employee", {'attendance_device_id': log_data['UserID']})

                # print({'device_id': device['id'], 'user_id': user_id})
                # employee = frappe.db.sql(f"""SELECT name, attendance_device_id  FROM `tabEmployee`
                #   WHERE attendance_device_id = '{user_id}'""", as_dict=True)
                try:
                    user_id = log_data["UserID"]
                    log_time_obj = parser.parse(log_data["LogTime"])
                    log_time = datetime.strftime(log_time_obj, "%Y-%m-%d %H:%M:%S")

                    employee = frappe.db.sql(
                        f"""SELECT name from `tabEmployee` WHERE attendance_device_id = '{user_id}' """,
                        as_dict=True)

                    if employee:
                        checkin = frappe.db.sql(
                            f"""SELECT time 
                                    FROM `tabEmployee Checkin` 
                                        WHERE employee = '{employee[0]['name']}' 
                                            AND time = '{log_time}'""",
                            as_dict=True)

                        if len(checkin) == 0:
                            new_checkin = frappe.get_doc(
                                {
                                    "doctype": "Employee Checkin",
                                    "employee": employee[0]["name"],
                                    "time": log_time,
                                    "device_id": device["id"],
                                    "log_type": "IN",
                                    "shift": "Day Shift",
                                    "device_location": device["location"],
                                }
                            )

                            new_checkin.save()
                            frappe.db.commit()
                except Exception as e:
                    print(e)
                    pass
        except Exception as e:
            print(e)
            pass

                # log_exists = frappe.get_doc("Employee Checkin",
                # {"employee": log_data['employee'], 'attendance_date': attendance_date})


def parse_time(log_time):
    log_time_obj = parser.parse(log_time)
    return datetime.strftime(log_time_obj, "%Y-%m-%d %H:%M:%S")

def get_employee_by_device_id(user_id):
    return frappe.db.sql(f"""
        SELECT name from `tabEmployee` 
        WHERE attendance_device_id = '{user_id}' 
    """, as_dict=True)

def employee_checkin_exists(employee, log_time, device_id):
    checkin =  frappe.db.sql(f"""
            SELECT time 
            FROM `tabEmployee Checkin` 
            WHERE employee = '{employee}' 
            AND time = '{log_time}' 
            AND device_id = '{device_id}' 
        """, as_dict=True)
    if len(checkin) > 0:
        return True

    return False

def get_device(auth_key):
    return frappe.db.sql(f""" 
        SELECT device_id, device_location 
        FROM `tabCams Devices`
        WHERE device_auth_key = '{auth_key}' 
    """, as_dict=True)


@frappe.whitelist(allow_guest=True)
def cams_url():
    try:
        data = frappe.request.data.decode("utf-8")
        data_dict = json.loads(data)

        real_time_data = data_dict['RealTime']

        operation_id = real_time_data['OperationID']
        auth_token = real_time_data['AuthToken']
        user_id = real_time_data['PunchLog']['UserId']
        log_time = parse_time(real_time_data['PunchLog']['LogTime'])
        log_type = real_time_data['PunchLog']['Type']
        log_input_type = real_time_data['PunchLog']['InputType']

        device = get_device(auth_key=auth_token)
        if device:
            device = device[0]
        else:
            return

        employee = get_employee_by_device_id(user_id=user_id)

        if employee:
            employee_name = employee[0]['name']
        else:
            return

        checkin_exists = employee_checkin_exists(employee_name, log_time, device["device_id"])

        frappe.response.type = 'json'
        frappe.response.message = 'Done'
        frappe.response.status = 'Done'
        
        if not checkin_exists:
            new_checkin = frappe.get_doc({
                "doctype": "Employee Checkin",
                "employee": employee_name,
                "time": log_time,
                "device_id": device["device_id"],
                "log_type": "IN",
                "shift": "Day Shift",
                "device_location": device["device_location"],
            })

            new_checkin.save(ignore_permissions=True)
            frappe.db.commit()
            return frappe.response['message']
        else:
            return frappe.response['message']
        frappe.logger("camsunit.error").debug(f"CheckinExists - {data_dict}")
    except Exception as e:
        frappe.logger("camsunit.error").debug(e)


@frappe.whitelist(allow_guest=True)
def cams_url_s():
    
    data = frappe.request.data.decode("utf-8")
    frappe.logger("camsunit.error").debug(data)