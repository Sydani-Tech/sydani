import frappe
import requests
import ast
import json
import time
from textwrap import dedent
from frappe.utils import today


@frappe.whitelist()
def screen(applicant):
    try:
        job_applicant = frappe.db.sql(
            f""" 
            SELECT applicant_name, gender, email_id, 
            status, job_title, 
            CONCAT('https://office.sydani.org', resume_attachment) AS cv_link 
            FROM `tabJob Applicant`
            WHERE email_id = '{applicant}'  
        """,
            as_dict=True,
        )

        # AND status = 'Application Submitted'

        if len(job_applicant) > 0:
            applicant = job_applicant[0]
            job_opening = applicant["job_title"]

            required_qualifications = frappe.db.sql(
                f""" 
                SELECT required_qualifications 
                FROM `tabJob Opening` 
                WHERE name = '{job_opening}'
            """,
                as_dict=True,
            )[0]["required_qualifications"]

            cv_url = applicant["cv_link"]

            additional_info = dedent(
                f""" 
                applicant_name: {job_applicant[0]['applicant_name']}
                applicant_gender: {job_applicant[0]['gender']}
            """
            )

            data = {
                "cv_url": cv_url,
                "criteria": required_qualifications,
                "additional_info": additional_info.replace("\n", ""),
            }

            frappe.logger("gtp.error").debug(data)

            request_data = requests.post(
                "http://127.0.0.1:8001/ai/api/screen", json=data
            ).json()

            result_dict = ast.literal_eval(request_data)
            reason = result_dict["reason"].split("->")
            result_dict["reason_list"] = reason

            return result_dict
    except Exception as e:
        frappe.logger("gtp.error").debug(e)
        return {"name": "Can not review", "status": "", "reason": "Invalid input"}


def get_other_openings():
    return frappe.db.sql(
        f""" 
        SELECT name, required_qualifications FROM `tabJob Opening` 
        WHERE status = 'Open' 
    """,
        as_dict=True,
    )


def ai_request(applicant):
    
    additional_info = f""" 
        applicant_name: {applicant.applicant_name}
        applicant_gender: {applicant.gender}
    """

    data = {
        "cv_url": applicant.cv_link,
        "criteria": applicant.required_qualifications,
        "additional_info": additional_info.replace("\n", ""),
    }

    if data["criteria"]:

        request_data = requests.post("http://127.0.0.1:8001/ai/api/screen", json=data)
        # print('res -> ', request_data.text)
        # print(" ---------- ")
        # print('json -> ', request_data.json())
        # return None
        if request_data.status_code == 200:
            try:
                return ast.literal_eval(request_data.json())
            except:
                return None
        else:
            frappe.logger("gtp.error").debug(request_data.text)
            return None
    else:
        frappe.logger("gtp.error").debug("no criteria found")
        return None


def auto_screen():
    unqualified_candidates = []
    qualified_for_other_openings = []

    job_applicants = frappe.db.sql(
        f"""
        SELECT apc.name, apc.applicant_name, apc.gender, email_id, 
        apc.status, apc.job_title, apc.designation, 
        job.required_qualifications, job.status,
        CONCAT('https://office.sydani.org', apc.resume_attachment) AS cv_link 
        FROM `tabJob Applicant` AS apc 
        LEFT JOIN `tabJob Opening` AS job ON apc.job_title = job.name
        WHERE apc.status = 'Application Submitted' AND
        job.status = 'Open' ORDER BY RAND() ASC LIMIT 10
        """,
        as_dict=True,
    )
    # ORDER BY RAND()
    # ORDER BY apc.creation ASC
    # AND job.status = 'Open' ORDER BY apc.creation ASC LIMIT 1
    # AND job.status = 'Open' AND job.name = 'finance-lead, communication-' ORDER BY apc.creation ASC LIMIT 15
    # print(job_applicants)
    for job_applicant in job_applicants:
        print(job_applicant)
        
        # frappe.logger("gtp.error").debug(data)
        
        assm_result = ai_request(job_applicant)
        
        if assm_result == None:
            continue

        app_doctype = frappe.get_doc("Job Applicant", job_applicant.name)

        if assm_result["status"] == "qualified":

            app_doctype.cv_score = assm_result["score"]
            app_doctype.ai_response = assm_result["reason"]
            app_doctype.status = "Awaiting Review"
            app_doctype.cv_review_date = today()
            app_doctype.save()
            frappe.db.commit()
            # app_doctype.status = 'Awaiting Assessment'

            qfy = {
                "name": assm_result["name"],
                "status": assm_result["status"],
                "score": assm_result["score"],
                "reason": assm_result["reason"],
            }

            print(qfy)
            print("------------------")
            # print(" ")
        elif assm_result["status"] == "unqualified":
            app_doctype.cv_score = assm_result["score"]
            app_doctype.ai_response = assm_result["reason"]
            app_doctype.cv_review_date = today()
            app_doctype.save()
            frappe.db.commit()
            unqualified_candidates.append(
                {"applicant": job_applicant, "unq_result": assm_result}
            )

    for applicant_obj in unqualified_candidates:
        applicant = applicant_obj["applicant"]
        unq_result = applicant_obj["unq_result"]

        app_doctype = frappe.get_doc("Job Applicant", applicant.name)
        other_openings = get_other_openings()

        unqualified = 0
        openings_checked = ""

        if applicant.name in qualified_for_other_openings:
            continue

        for opening in other_openings:
            # if applicant.name in qualified_for_other_openings:
            #     break
            applicant["required_qualifications"] = opening.required_qualifications

            time.sleep(5)
            assm_result = ai_request(applicant)

            if assm_result == None:
                continue

            openings_checked += f" {opening.name},"

            if assm_result["status"] == "qualified":
                qualified_for_other_openings.append(applicant.name)

                app_doctype.cv_score = unq_result["score"]
                app_doctype.score_on_recommended_role = assm_result["score"]
                app_doctype.ai_response = unq_result["reason"]
                app_doctype.feedback_on_recommended_role = assm_result["reason"]
                app_doctype.recommended_role = opening["name"]
                app_doctype.job_title = opening["name"]
                app_doctype.status = "Awaiting Review"
                # app_doctype.status = 'Awaiting Assessment'
                app_doctype.save()
                # frappe.db.commit()
                unqualified = 0

                qfy = {
                    "name": assm_result["name"],
                    "status": assm_result["status"],
                    "score": assm_result["score"],
                    # "reason": assm_result["reason"],
                    "opening": opening["name"],
                }

                print(qfy)
                print("------------------")
                # print(" ")
                break
            elif assm_result["status"] == "unqualified":
                unqualified = 1

        if unqualified == 1:
            msg = f"The applicant fails to meet the criteria for these positions: {openings_checked}"
            app_doctype.score_on_recommended_role = assm_result["score"]
            app_doctype.feedback_on_recommended_role = msg
            app_doctype.status = "Rejected - ATS"
            app_doctype.save()
            frappe.db.commit()
            print(applicant.name, msg)
            print("------------------")
            print(" ")
