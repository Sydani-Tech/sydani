
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr, formatdate, get_datetime, getdate, nowdate
from erpnext.hr.doctype.attendance.attendance import Attendance
from erpnext.hr.utils import validate_active_employee


class CustomAttendance(Document):
        def validate(self):
                from erpnext.controllers.status_updater import validate_status
                validate_status(self.status, ["Present", "Absent", "On Leave", "Half Day", "Work From Home"])
                validate_active_employee(self.employee)
                self.validate_attendance_date()
                self.validate_duplicate_record()
                self.validate_employee_status()
                self.check_leave_record()

        def validate_attendance_date(self):
                date_of_joining = frappe.db.get_value("Employee", self.employee, "date_of_joining")

                # leaves can be marked for future dates
                #if self.status != 'On Leave' and not self.leave_application and getdate(self.attendance_date) > getdate(nowdate()):
                #        frappe.throw(_("Attendance can not be marked for future dates"))
                if date_of_joining and getdate(self.attendance_date) < getdate(date_of_joining):
                        frappe.throw(_("Attendance date can not be less than employee's joining date"))

        def validate_duplicate_record(self):
                res = frappe.db.sql("""
                        select name from `tabAttendance`
                        where employee = %s
                                and attendance_date = %s
                                and name != %s
                                and docstatus != 2
                """, (self.employee, getdate(self.attendance_date), self.name))
                if res:
                        frappe.throw(_("Attendance for employee {0} is already marked for the date {1}").format(
                                frappe.bold(self.employee), frappe.bold(self.attendance_date)))

        def validate_employee_status(self):
                if frappe.db.get_value("Employee", self.employee, "status") == "Inactive":
                        frappe.throw(_("Cannot mark attendance for an Inactive employee {0}").format(self.employee))

        def check_leave_record(self):
                leave_record = frappe.db.sql("""
                        select leave_type, half_day, half_day_date
                        from `tabLeave Application`
                        where employee = %s
                                and %s between from_date and to_date
                                and status = 'Approved'
                                and docstatus = 1
                """, (self.employee, self.attendance_date), as_dict=True)
                if leave_record:
                        for d in leave_record:
                                self.leave_type = d.leave_type
                                if d.half_day_date == getdate(self.attendance_date):
                                        self.status = 'Half Day'
                                        frappe.msgprint(_("Employee {0} on Half day on {1}")
                                                .format(self.employee, formatdate(self.attendance_date)))
                                else:
                                        self.status = 'On Leave'
                                        frappe.msgprint(_("Employee {0} is on Leave on {1}")
                                                .format(self.employee, formatdate(self.attendance_date)))

                if self.status in ("On Leave", "Half Day"):
                        if not leave_record:
                                frappe.msgprint(_("No leave record found for employee {0} on {1}")
                                        .format(self.employee, formatdate(self.attendance_date)), alert=1)
                elif self.leave_type:
                        self.leave_type = None
                        self.leave_application = None

        def validate_employee(self):
                emp = frappe.db.sql("select name from `tabEmployee` where name = %s and status = 'Active'",
                        self.employee)
                if not emp:
                        frappe.throw(_("Employee {0} is not active or does not exist").format(self.employee))

