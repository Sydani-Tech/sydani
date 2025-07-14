from . import __version__ as app_version

app_name = "sydani"
app_title = "Sydani"
app_publisher = "ekomobong"
app_description = "For Sydani custom apps"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "erp@sydani.org"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/sydani/css/sydani.css"
# app_include_js = "/assets/sydani/js/sydani.js"

# include js, css files in header of web template
# web_include_css = "/assets/sydani/css/sydani.css"
# web_include_js = "/assets/sydani/js/sydani.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "sydani/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "sydani.install.before_install"
# after_install = "sydani.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "sydani.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    # "*": {
    # 	"before_save": "sydani.sms.send"
    # 	# "on_update": "",
    # 	# "on_cancel": "method",
    # 	# "on_trash": "method"
    # }
    "Expense Claim": {
        "before_save": "sydani.payment.expense_claim_create_trasaction",
        "validate": "sydani.scripts.validate_expense_claim_approvers_limits",
        },
    "Transport Reimbursement": {
        "on_update": "sydani.scripts.share_transport_reinsbursement"
    },
    "Employee Travel Request": {
        "on_update": "sydani.scripts.share_employee_travel_request"
    },
    "Timesheet": {"on_update": "sydani.scripts.share_time_sheet"},
    # "Timesheet": {"on_update": "sydani.custom_scripts.process_employee_fte_allocation"},
    "Trip Report": {"on_update": "sydani.scripts.share_trip_report"},
    "Attendance Request": {"on_update": "sydani.scripts.share_attendance_request"},
    "Work Plan": {
        "on_update": "sydani.custom_scripts.check_due_dates_against_holidays"
    },
    "Email Group Member": {"on_update": "sydani.mailchimp.add_subscriber"},
    "Sales Invoice": {
        "on_update": "sydani.custom_scripts.copy_sales_invoice_items_to_sales_order"
    },
    "Vendor Evaluation": {
        "after_insert": "sydani.tasks.create_or_update_vendor_evaluation_sheet"
    },
    "Job Applicant": {
        "before_insert": "sydani.custom_scripts.validate_if_applicant_has_applied"
    },
    "Vehicle Booking System": {
        "on_update": "sydani.custom_scripts.validate_if_a_vehicle_is_available"
    },
    "PS Attendance Request": {
        "on_submit": "sydani.test_scripts.creat_ps_attendance"
    },
    "RFQ Response": {""
        "validate": "sydani.scripts.calculate_rfq_doc"
    },
    "Project Requirement Form": {
        "on_update": "sydani.scripts.share_project_requirement_form"
    },
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    # "cron": {
    # 	"45 21 * * *": [
    # 		"sydani.tasks.shift"
    # ]
    # },
    "all": ["sydani.tasks.all"],
    "cron": {
        "30 11 * * *": ["sydani.tasks.mark_priority_employees_present"], 
        "30 11 * * *": ["sydani.tasks.add_speedexam_candidate"],
        "0 16 * * *": ["sydani.tasks.add_speedexam_candidate"],
        "30 22 * * *": ["sydani.tasks.add_speedexam_candidate"],
        "*/5 * * * *": ["sydani.tasks.create_new_workplan"],
        "45 22 * * *": ["sydani.tasks.shift"],
        "45 22 * * *": ["sydani.tasks.shift_22nd"],
        "30 12 * * *": ["sydani.tasks.get_speedexam_result"],
        "0 17 * * *": ["sydani.tasks.get_speedexam_result"],
        "30 23 * * *": ["sydani.tasks.get_speedexam_result"],
        "*/10 * * * *": ["sydani.cams.get_log"],
        "*/45 * * * *": ["sydani.ats_api.auto_screen"],
        "0 23 * * *": ["sydani.scripts.auto_submit_ps_report"],
        "0 23 * * *": ["sydani.tasks.delete_attendance_on_holidays"],
        "0 * * * *": ["sydani.tasks.work_plan_create_work_from_home_attendance"],
        # "*/30 * * * *": ["sydani.tasks.delete_old_records"],
        "0 3 * * *": ["sydani.tasks.calculate_accumulated_depreciation"],
        "0 22 * * *": ["sydani.custom_scripts.create_suppliers_from_employees"],
        "0 20 * * *": ["sydani.custom_scripts.travel_request_attendance"],
        "30 20 * * *": ["sydani.custom_scripts.travel_request_attendance_for_change"],
        "0 2 * * *": ["sydani.tasks.fetch_and_create_email_group_members_vendors"],
        "0 2 * * *": ["sydani.tasks.fetch_and_create_email_group_members"],
        "0 3 * * *": ["sydani.payment.fetch_and_save_exchange_rates"],
        "30 8 * * *": ["sydani.custom_scripts.update_deliverable_expended_amounts"],
        "30 13 * * *": ["sydani.custom_scripts.update_deliverable_expended_amounts"],
        "30 20 * * *": ["sydani.custom_scripts.update_deliverable_expended_amounts"],
        # "0 22 * * *": [
        # 	"sydani.tasks.confirm_payment_transactions"
        # ]
    },
    # 0 */2 * * 1-5
    # 	"daily": [
    # 		"sydani.tasks.daily"
    # 	],
    "hourly": ["sydani.tasks.cams_update_users"],
    # "hourly": [
    # 	"sydani.tasks.get_speedexam_result"
    # ],
    # 	"weekly": [
    # 		"sydani.tasks.weekly"
    # 	]
    # 	"monthly": [
    # 		"sydani.tasks.monthly"
    # 	]
}

# Testing
# -------

# before_tests = "sydani.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "sydani.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "sydani.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
    {
        "doctype": "{doctype_1}",
        "filter_by": "{filter_by}",
        "redact_fields": ["{field_1}", "{field_2}"],
        "partial": 1,
    },
    {
        "doctype": "{doctype_2}",
        "filter_by": "{filter_by}",
        "partial": 1,
    },
    {
        "doctype": "{doctype_3}",
        "strict": False,
    },
    {"doctype": "{doctype_4}"},
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"sydani.auth.validate"
# ]
