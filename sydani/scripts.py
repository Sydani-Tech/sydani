import frappe
from frappe import _
from datetime import date, timedelta, datetime
import requests


def auto_submit_ps_report():
    reports = frappe.db.sql(
        f""" SELECT name FROM `tabPS Report` WHERE docstatus = 0 AND start_time IS NOT NULL AND end_time IS NOT NULL 
  AND facilitator IS NOT NULL AND co_facilitator IS NOT NULL AND star_performer IS NOT NULL""",
        as_dict=True,
    )

    for report in reports:
        doc = frappe.get_doc("PS Report", report.name)
        doc.submit()


@frappe.whitelist()
def auto_share(doc, users):
    pass


def document_shared_with_user(doctype, name, user):
    shares = frappe.db.sql(
        f"""SELECT name FROM `tabDocShare` WHERE share_doctype = '{doctype}' 
                          	AND share_name = '{name}' AND user = '{user}' LIMIT 1""",
        as_dict=True,
    )

    return len(shares) > 0


def get_employee_by_name(employee_name):
    name = employee_name.split(" ")

    stmt = f"""SELECT user_id FROM `tabEmployee` 
        WHERE employee_name LIKE '%{name[0]}%{name[1]}%' LIMIT 1"""

    employee = frappe.db.sql(stmt, as_dict=True)
    if len(employee) > 0:
        return employee[0]
    else:
        stmt = f"""SELECT user_id FROM `tabEmployee` 
        WHERE employee_name LIKE '%{name[1]}%{name[0]}%' LIMIT 1"""
        employee = frappe.db.sql(stmt, as_dict=True)
        return employee[0]


def share_doc(doc, user_email, write=1, share=1, submit=1):
    is_shared = document_shared_with_user(doc.doctype, doc.name, user_email)
    if is_shared:
        return False

    frappe.share.add(
        doc.doctype,
        doc.name,
        user_email,
        notify=0,
        write=write,
        share=share,
        submit=submit,
        flags={"ignore_share_permission": True},
    )
    return True


def share_transport_reinsbursement(doc, method=None):

    manager = get_employee_by_name(doc.manager)
    shared = share_doc(doc, manager["user_id"])
    if shared:
        frappe.msgprint(
            _("Shared with the manager {0}").format(
                frappe.bold(doc.manager), alert=True
            )
        )


def share_employee_travel_request(doc, method=None):

    # project_lead = get_employee_by_name(doc.project_lead)

    # shared = share_doc(doc, project_lead['user_id'])
    # if shared:
    #      frappe.msgprint(_("Shared with the project lead {0}").format(
    # 					frappe.bold(doc.project_lead), alert=True))

    share_with_manager = share_doc(doc, doc.managers_email)

    doc_dict = doc.as_dict()
    for itinerary in doc_dict.travel_itinerary:
        share_doc(
            doc=doc, user_email=itinerary.employees_email, write=1, share=1, submit=0
        )

    for retirement in doc_dict.travel_retirement:
        share_doc(
            doc=doc, user_email=itinerary.employees_email, write=1, share=1, submit=0
        )


def share_time_sheet(doc, method=None):

    supervisor = get_employee_by_name(doc.supervisor)
    shared = share_doc(doc, supervisor["user_id"])
    if shared:
        frappe.msgprint(
            _("Shared with the supervisor {0}").format(
                frappe.bold(doc.supervisor), alert=True
            )
        )


def share_attendance_request(doc, method=None):
    try:
        share_doc(doc=doc, user_email=doc.approver, write=1, share=1, submit=0)
        # doc_dict = doc.as_dict()
        # for approve in doc_dict.approver:
        #     share_doc(doc=doc,user_email=approve.email,write=1,share=1,submit=0)
    except:
        pass

def share_project_requirement_form(doc, method=None):
    try:
        share_doc(doc=doc, user_email=doc.managers_email, write=1, share=1, submit=0)
        # doc_dict = doc.as_dict()
        # for approve in doc_dict.approver:
        #     share_doc(doc=doc,user_email=approve.email,write=1,share=1,submit=0)
    except:
        pass

def share_trip_report(doc, method=None):
    try:
        share_doc(doc=doc, user_email=doc.managers_email, write=1, share=1, submit=1)
        # doc_dict = doc.as_dict()
        # for approve in doc_dict.approver:
        #     share_doc(doc=doc,user_email=approve.email,write=1,share=1,submit=0)
    except:
        pass


@frappe.whitelist()
def get_user_roles(user):
    user_roles = frappe.get_roles(user)
    return user_roles

@frappe.whitelist()
def return_budget_thresholds(project):
    # Get the current fiscal year
    current_fiscal_year = frappe.db.get_value(
        "Fiscal Year", {"year_start_date": ["<=", frappe.utils.today()]}, "name"
    )

    if not current_fiscal_year:
        frappe.throw("Current Fiscal Year not found.")

    fields = frappe.db.sql(
        """
        SELECT bt.deliverable, bt.budget_threshold, bt.amount_expended
        FROM `tabBudget Threshold` bt
        JOIN `tabBudget` b ON bt.parent = b.name
        WHERE b.budget_against = 'Project'
        AND b.project = %s
        AND b.fiscal_year = %s
        """,
        (project, current_fiscal_year),
        as_dict=True,
    )

    return fields


def test_return_budget_thresholds():
    print(
        return_budget_thresholds(
            "Collaborative Action Strategy for Health Campaign Effectiveness (CAS)"
        )
    )


# AND YEAR(b.fiscal_year) = %s
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


@frappe.whitelist()
def fetch_ongoing_projects(company, user):
    """
    Fetch all ongoing projects where the company matches the argument
    and also projects where the user is listed in the Project User child table.

    :param company: The company to filter projects.
    :param user: The user to check in the Project User child table (defaults to frappe.session.user).
    :return: List of unique matching project names.
    """

    # Fetch projects where status is "Ongoing" and company matches
    ongoing_projects = frappe.get_all(
        "Project", filters={"status": "Ongoing", "company": company}, fields=["name"]
    )

    # ongoing_projects = frappe.db.sql(
    #     """        SELECT name FROM `tabProject`
    #     WHERE status = 'Ongoing' AND company = %s
    #     """,
    #     (company,),
    #     as_dict=True,
    # )

    # Fetch parent project names from the Project User child table for the given user
    user_project_parents = frappe.get_all(
        "Project User", filters={"user": user}, fields=["parent"]
    )

    # user_project_parents = frappe.db.sql(
    #     """SELECT parent FROM `tabProject User`
    #     WHERE user = %s""",
    #     (user,),
    #     as_dict=True,
    # )

    # Extract project names from the child table query
    user_project_names = [proj["parent"] for proj in user_project_parents]

    # Filter projects from user_project_parents where status is "Ongoing"
    ongoing_user_projects = frappe.get_all(
        "Project",
        filters={"status": "Ongoing", "name": ["in", user_project_names]},
        fields=["name"],
    )

    # ongoing_user_projects = frappe.db.sql(
    #     """SELECT name FROM `tabProject`
    #     WHERE status = 'Ongoing' AND name IN %s""",
    #     (tuple(user_project_names),),
    #     as_dict=True,
    # )

    # Combine and deduplicate project names
    all_projects = list(
        {proj["name"] for proj in ongoing_projects + ongoing_user_projects}
    )

    return all_projects


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
    # from_date_str = from_date_obj.strftime("%Y-%m-%d") 

    from_date_minus_1 = from_date_obj - timedelta(days=1)
    from_date_str = from_date_minus_1.strftime("%Y-%m-%d")

    to_date_obj = datetime.strptime(to_date, "%Y-%m-%d").date()
    to_date_str = from_date_obj.strftime("%Y-%m-%d") 

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
            "date": ["<=", from_date_str],
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
            "posting_date": ["<=", from_date_str],
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
            # frappe.logger().debug(f"Processing bank transaction: {bank_transaction}")

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


def validate_expense_claim_approvers_limits(doc, method):
    
    if doc.workflow_state not in ["Draft", "Returned To Employee"]:
        return

    # Determine correct amount
    base_amount = (
        doc.payment_total
        if doc.requisition_type in ["Retirement", "Petty Cash"]
        else doc.payment_total_advance
        if doc.requisition_type == "Advance Request"
        else 0
    )
    amount = (
        base_amount
        if (doc.denomination == doc.base_currency and doc.denomination == "NGN")
        else base_amount * (doc.exchange_rate or 1)
    ) or 0

    # Fetch user roles
    user_roles = frappe.get_roles(doc.expense_approver)

    if amount >= 5000000:
        return  # No restriction for 5M and above

    if "Engagement Manager" in user_roles and amount > 2000000:
        frappe.throw(f"{doc.manager_name} can only approve amounts up to NGN 2,000,000 or its forex equivalent autonomously. Please select an approver with a higher approval limit.")

    if "Senior Engagement Manager" in user_roles and amount > 2000000:
        frappe.throw(f"{doc.manager_name} can only approve amounts up to NGN 2,000,000 or its forex equivalent autonomously. Please select an approver with a higher approval limit")

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


        
        message2 = frappe.render_template("""
                                         <p>Dear {{doc.vendor}},</p>
                                            <br/>
                                            <p>We hope this mail finds you well.</p>
                                            <br/>
                                            <p>Kindly share your most competitive quote for the supply and delivery of the list items.</p>
                                            <br/>

                                            <table border="1" style="border-collapse: collapse; width: 100%;">
                                                <thead>
                                                    <tr>
                                                        <th style="padding: 8px; text-align: left;">Item </th>
                                                        <th style="padding: 8px; text-align: left;">Description</th>
                                                        <th style="padding: 8px; text-align: left;">Quantity</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {% for item in doc.items %}
                                                    <tr>
                                                        <td style="padding: 8px;">{{ item.item }}</td>
                                                        <td style="padding: 8px;">{{ item.description }}</td>
                                                        <td style="padding: 8px;">{{ item.quantity }}</td>
                                                    </tr>
                                                    {% endfor %}
                                                </tbody>
                                            </table>

                                            <p>We will be glad to receive your quote on or before 2 pm tomorrow.</p>
                                            <br/>
                                            <p>Please let us know if you have any questions or if you require further information to prepare a quote.</p>
                                            <br/>
                                            <p>Thank you for your time and consideration.</p>
                                            <br/>
                                            <p>Best Regards,</p>
                                            <p>Sydani Group</p>
                                         """, context)

        frappe.sendmail(
            recipients=[email],
            subject=subject,
            message=message
        )

    return "Emails sent successfully"

def calculate_rfq_doc(doc, method):
    total_quote_price = 0

    # Loop through each item in the quote table
    for row in doc.quote:
        # 1. Calculate amount = unit_price * quantity
        row.amount = (row.unit_price or 0) * (row.quantity or 0)
        row.currency = doc.quote_currency
        total_quote_price += row.amount

    doc.quote_price = total_quote_price
    doc.grand_total = (doc.quote_price or 0) + (doc.tax or 0) - (doc.discount or 0)
   
import frappe
from frappe.utils import nowdate, getdate

@frappe.whitelist()
def get_available_capacity_building_funds(employee):
    # Step 1: Fetch base salary from Salary Structure Assignment
    salary_structure_assignment = frappe.get_all(
        "Salary Structure Assignment",
        filters={"employee": employee},
        fields=["base", "currency"],
        order_by="from_date desc",
        limit=1,
        ignore_permissions=True
    )

    if not salary_structure_assignment:
        frappe.throw("No Salary Structure Assignment found for this employee.")

    base = salary_structure_assignment[0].base
    currency = salary_structure_assignment[0].currency

    salary_slip = frappe.get_all(
        "Salary Slip",
        filters={"employee": employee},
        fields=["end_date", "net_pay"],
        order_by="end_date desc",
        limit=1,
        ignore_permissions=True
    )
    monthly_net = salary_slip[0].net_pay or 0


    # Step 2: Get current fiscal year start and end
    fiscal_year = frappe.get_value("Fiscal Year", {"disabled": 0, "year_start_date": ["<=", nowdate()], "year_end_date": [">=", nowdate()]}, ["name", "year_start_date", "year_end_date"], as_dict=True)
    
    if not fiscal_year:
        frappe.throw("Current fiscal year not found.")

    start_date = fiscal_year.year_start_date
    end_date = fiscal_year.year_end_date

   
    used_funds = frappe.db.sql("""
    SELECT SUM(cost) FROM `tabCapacity Building Fund Request`
    WHERE workflow_state IN ('Approved', 'Draft', 'Submitted', 'Validated')
    AND creation BETWEEN %s AND %s
    AND created_by = %s
    """, (start_date, end_date, employee))[0][0] or 0


    # Step 4: Calculate available funds
    available_funds = base * 12 * 0.05 - used_funds

    return {
        "currency": currency,
        "used_funds": used_funds,
        "available_funds": available_funds,
        "monthly_net": monthly_net
    }