"""
attendance_plus/doctype/attendance_permission/attendance_permission.py
"""

import frappe
from frappe.model.document import Document
from frappe.utils import time_diff_in_hours, get_datetime, nowdate


class AttendancePermission(Document):

    def validate(self):
        self._set_total_hours()
        self._set_approver()
        self._validate_no_duplicate()

    def on_submit(self):
        self.status = "Pending Approval"
        self.db_update()
        self._notify_approver()

    def _set_total_hours(self):
        if self.from_time and self.to_time:
            from_dt = get_datetime(f"{self.date} {self.from_time}")
            to_dt = get_datetime(f"{self.date} {self.to_time}")
            self.total_hours = round(time_diff_in_hours(to_dt, from_dt), 2)

    def _set_approver(self):
        if not self.approver:
            reports_to = frappe.db.get_value("Employee", self.employee, "reports_to")
            if reports_to:
                user = frappe.db.get_value("Employee", reports_to, "user_id")
                self.approver = user

    def _validate_no_duplicate(self):
        existing = frappe.db.exists("Attendance Permission", {
            "employee": self.employee,
            "date": self.date,
            "permission_type": self.permission_type,
            "docstatus": ["!=", 2],
            "name": ["!=", self.name]
        })
        if existing:
            frappe.throw(
                f"An {self.permission_type} permission already exists for "
                f"{self.employee_name} on {self.date}."
            )

    def _notify_approver(self):
        if not self.approver:
            return
        frappe.sendmail(
            recipients=[self.approver],
            subject=f"Attendance Permission Request from {self.employee_name}",
            message=f"""
                <p>Dear Manager,</p>
                <p><b>{self.employee_name}</b> has submitted an attendance permission request.</p>
                <ul>
                    <li><b>Type:</b> {self.permission_type}</li>
                    <li><b>Date:</b> {self.date}</li>
                    <li><b>Time:</b> {self.from_time} to {self.to_time}</li>
                    <li><b>Reason:</b> {self.reason}</li>
                </ul>
                <p>
                    <a href="/app/attendance-permission/{self.name}">
                        Click here to Approve or Reject
                    </a>
                </p>
            """,
            now=True
        )


@frappe.whitelist()
def approve_permission(doc_name, remarks=""):
    """Called by manager from the form to approve"""
    doc = frappe.get_doc("Attendance Permission", doc_name)

    if frappe.session.user != doc.approver:
        frappe.throw("Only the assigned approver can approve this request.")

    doc.status = "Approved"
    doc.manager_remarks = remarks
    doc.db_update()

    # Create Employee Checkin entries based on permission type
    _create_checkins_for_permission(doc)

    # Patch attendance record if it exists
    _patch_attendance_for_permission(doc)

    frappe.db.commit()

    # Notify employee
    employee_user = frappe.db.get_value("Employee", doc.employee, "user_id")
    if employee_user:
        frappe.sendmail(
            recipients=[employee_user],
            subject=f"Attendance Permission Approved — {doc.date}",
            message=f"""
                <p>Your {doc.permission_type} permission for <b>{doc.date}</b>
                has been <b>Approved</b>.</p>
                <p>Remarks: {remarks or 'None'}</p>
            """,
            now=True
        )

    return "Approved"


@frappe.whitelist()
def reject_permission(doc_name, remarks=""):
    """Called by manager from the form to reject"""
    doc = frappe.get_doc("Attendance Permission", doc_name)

    if frappe.session.user != doc.approver:
        frappe.throw("Only the assigned approver can reject this request.")

    doc.status = "Rejected"
    doc.manager_remarks = remarks
    doc.db_update()
    frappe.db.commit()

    employee_user = frappe.db.get_value("Employee", doc.employee, "user_id")
    if employee_user:
        frappe.sendmail(
            recipients=[employee_user],
            subject=f"Attendance Permission Rejected — {doc.date}",
            message=f"""
                <p>Your {doc.permission_type} permission for <b>{doc.date}</b>
                has been <b>Rejected</b>.</p>
                <p>Remarks: {remarks or 'None'}</p>
            """,
            now=True
        )

    return "Rejected"


def _create_checkins_for_permission(doc):
    """
    For Onsite / Outdoor Duty — create IN/OUT checkins
    so auto-attendance marks them Present
    """
    if doc.permission_type not in ["Onsite Work", "Outdoor Duty"]:
        return

    for log_type, punch_time in [("IN", doc.from_time), ("OUT", doc.to_time)]:
        ts = get_datetime(f"{doc.date} {punch_time}")
        exists = frappe.db.exists("Employee Checkin", {
            "employee": doc.employee,
            "time": ts,
            "log_type": log_type
        })
        if not exists:
            frappe.get_doc({
                "doctype": "Employee Checkin",
                "employee": doc.employee,
                "time": ts,
                "log_type": log_type,
                "custom_checkin_source": "Permission",
                "custom_permission_ref": doc.name
            }).insert(ignore_permissions=True)


def _patch_attendance_for_permission(doc):
    """
    If attendance already exists for this date, update status to Present
    and note the permission type
    """
    attendance = frappe.db.get_value("Attendance", {
        "employee": doc.employee,
        "attendance_date": doc.date,
        "docstatus": 1
    }, "name")

    if attendance:
        frappe.db.set_value("Attendance", attendance, {
            "custom_permission_type": doc.permission_type,
            "custom_permission_ref": doc.name
        })
