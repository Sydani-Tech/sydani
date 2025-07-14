import frappe
from frappe import auth
import json
from datetime import date


def get_todays_votes(team):

    todays_date = date.today()
    event_name = "vote_updated"

    stmt = f"""SELECT employee, ps_team_id, COUNT(votes) as votes_today
                FROM `tabPS Vote`
                WHERE `created` = '{todays_date}' """


    # working on updating combine ps regardless of team ->   
    # combine_stmt = stmt + "GROUP BY employee ORDER BY COUNT(votes) DESC LIMIT 5 "

    total_votes_stmt = f"""SELECT COUNT(votes) as total_votes FROM `tabPS Vote` WHERE `created` = '{todays_date}' """

    if team == "#latitude":
        add_filter = "AND `ps_team_id` = 'Latitude' "
        event_name = "vote_updated_latitude"
        stmt += add_filter
        total_votes_stmt += add_filter
    elif team == "#longitude":
        add_filter = "AND `ps_team_id` = 'Longitude' "
        event_name = "vote_updated_longitude"
        stmt += add_filter
        total_votes_stmt += add_filter

    stmt += "GROUP BY employee ORDER BY COUNT(votes) DESC LIMIT 5 "

    # stmt = f"""SELECT employee, ps_team_id, COUNT(votes) as votes_today
    #             FROM `tabPS Vote`
    #             WHERE `created` = '{todays_date}'
    #             GROUP BY employee
    #             ORDER BY COUNT(votes) DESC LIMIT 5 """

    votes = frappe.db.sql(stmt, as_dict=True)
    total_votes = frappe.db.sql(total_votes_stmt, as_dict=True)

    frappe.publish_realtime(event_name, {'vote_count': votes, 'total_votes': total_votes})

    # frappe.publish_realtime(event_name, {'vote_count': votes, 'total_votes': total_votes})


@frappe.whitelist(allow_guest=True)
def get_employee_list(team):
    if frappe.session.user == 'Guest':
        return frappe.session.user

    stmt = "SELECT `employee_name` as name, `email`, `ps_team` FROM `tabEmployee` "

    if team == "#latitude":
        stmt += " WHERE `ps_team` = 'Latitude' "
    elif team == "#longitude":
        stmt += " WHERE `ps_team` = 'Longitude' "

    list = frappe.db.sql(stmt, as_dict=True)

    frappe.response['message'] = {
        "success_key": 1,
        "user": frappe.session.user,
        "employees": list
    }

    get_todays_votes(team)

    return


@frappe.whitelist(allow_guest=True)
def login(usr, pwd):
    try:
        login_manager = auth.LoginManager()
        login_manager.authenticate(user=usr, pwd=pwd)
        login_manager.post_login()

        frappe.response['message'] = {
            "success_key": 1,
            "user": frappe.session.user
        }

    except frappe.AuthenticationError:
        frappe.response['message'] = {
            "success_key": 0,
            "message": "Authentication Error"
        }

        return


@frappe.whitelist(allow_guest=True)
def cast_vote(employee_voted, ps_team, user_email):

    employee_voted_dic = json.loads(employee_voted)
    # get todays date
    todays_date = date.today()

    # get day of the week Mon=0 and Sun=6
    todays_day = todays_date.weekday()

    todays_user_vote = frappe.db.sql(
        f"SELECT votes FROM `tabPS Vote` WHERE `user_email` = '{user_email}' AND `created` = '{todays_date}'", as_list=True)
    # len(todays_user_vote) == 0 and todays_day = 3
    
    if (len(todays_user_vote) == 0 and todays_day = 3):
        # Filter whwere ps team = ps_team -> should add the feature
        ps_vote = frappe.get_doc({
            'doctype': 'PS Vote',
            'user_email': user_email,
            'employee': employee_voted_dic['name'],
            'employee_email': employee_voted_dic['email'],
            'ps_team_id': employee_voted_dic['ps_team'],
            'votes': 1,
            'created': todays_date
        })

        ps_vote.insert()

        frappe.response['message'] = {
            "success_key": 1,
            "message": 'Vote Submited Successfully'
        }

        get_todays_votes(ps_team)

    else:

        frappe.response['message'] = {
            "success_key": 0,
            "message": 'You Reach Max No of Votes Today'
        }

    return

    # frappe.msgprint(str(employee_vote['name']))
    # frappe.msgprint(str(todays_day))
    # return frappe.db.sql("SELECT * FROM `tabPS Vote`", as_dict=True)
