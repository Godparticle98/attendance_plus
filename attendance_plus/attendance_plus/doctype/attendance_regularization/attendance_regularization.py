"""
attendance_plus/doctype/attendance_regularization/attendance_regularization.py
"""

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime


class AttendanceRegularization(Document):

    def validate(self):
        self._set_approver()
        self._validate_times()
        self._validate_no_duplicate()

    def on_submit(self):
        self.status = "Pending Approval"
        self.db_update()
        self._notify_approver()

    def _set_approver(self):
        if not self.approver:
            reports_to = frappe.db.get_value("Employee", self.employee, "reports_to")
            if reports_to:
                user = frappe.db.get_value("Employee", reports_to, "user_id")
                self.approver = user

    def _validate_times(self):
        rtype = self.regularization_type
        if rtype in ["Missing IN Punch", "Both Punches Missing"] and not self.in_time:
            frappe.throw("Check-In Time is required for this regularization type.")
        if rtype in ["Missing OUT Punch", "Both Punches Missing"] and not self.out_time:
            frappe.throw("Check-Out Time is required for this regularization type.")
        if self.in_time and self.out_time:
            if get_datetime(self.out_time) <= get_datetime(self.in_time):
                frappe.throw("Check-Out Time must be after Check-In Time.")

    def _validate_no_duplicate(self):
        existing = frappe.db.exists("Attendance Regularization", {
            "employee": self.employee,
            "date": self.date,
            "docstatus": ["!=", 2],
            "name": ["!=", self.name]
        })
        if existing:
            frappe.throw(
                f"A regularization request already exists for "
                f"{self.employee_name} on {self.date}."
            )

    def _notify_approver(self):
        if not self.approver:
            return
        frappe.sendmail(
            recipients=[self.approver],
            subject=f"Attendance Regularization Request from {self.employee_name}",
            message=f"""
                <p>Dear Manager,</p>
                <p><b>{self.employee_name}</b> has submitted an attendance regularization request.</p>
                <ul>
                    <li><b>Type:</b> {self.regularization_type}</li>
                    <li><b>Date:</b> {self.date}</li>
                    <li><b>Check-In:</b> {self.in_time or 'N/A'}</li>
                    <li><b>Check-Out:</b> {self.out_time or 'N/A'}</li>
                    <li><b>Reason:</b> {self.reason}</li>
                </ul>
                <p>
                    <a href="/app/attendance-regularization/{self.name}">
                        Click here to Approve or Reject
                    </a>
                </p>
            """,
            now=True
        )


@frappe.whitelist()
def approve_regularization(doc_name, remarks=""):
    doc = frappe.get_doc("Attendance Regularization", doc_name)

    if frappe.session.user != doc.approver:
        frappe.throw("Only the assigned approver can approve this request.")

    doc.status = "Approved"
    doc.manager_remarks = remarks
    doc.db_update()

    # Insert missing checkins
    _insert_missing_checkins(doc)

    # Reprocess attendance for this date
    _reprocess_attendance(doc.employee, doc.date)

    frappe.db.commit()

    employee_user = frappe.db.get_value("Employee", doc.employee, "user_id")
    if employee_user:
        frappe.sendmail(
            recipients=[employee_user],
            subject=f"Attendance Regularization Approved — {doc.date}",
            message=f"""
                <p>Your regularization request for <b>{doc.date}</b>
                has been <b>Approved</b>.</p>
                <p>Remarks: {remarks or 'None'}</p>
            """,
            now=True
        )

    return "Approved"


@frappe.whitelist()
def reject_regularization(doc_name, remarks=""):
    doc = frappe.get_doc("Attendance Regularization", doc_name)

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
            subject=f"Attendance Regularization Rejected — {doc.date}",
            message=f"""
                <p>Your regularization request for <b>{doc.date}</b>
                has been <b>Rejected</b>.</p>
                <p>Remarks: {remarks or 'None'}</p>
            """,
            now=True
        )

    return "Rejected"


def _insert_missing_checkins(doc):
    """Insert IN/OUT checkins based on regularization type"""
    entries = []
    if doc.in_time:
        entries.append(("IN", doc.in_time))
    if doc.out_time:
        entries.append(("OUT", doc.out_time))

    for log_type, ts in entries:
        exists = frappe.db.exists("Employee Checkin", {
            "employee": doc.employee,
            "time": get_datetime(ts),
            "log_type": log_type
        })
        if not exists:
            frappe.get_doc({
                "doctype": "Employee Checkin",
                "employee": doc.employee,
                "time": get_datetime(ts),
                "log_type": log_type,
                "custom_checkin_source": "Regularization",
                "custom_regularization_ref": doc.name
            }).insert(ignore_permissions=True)


def _reprocess_attendance(employee, date):
    """
    Cancel existing unprocessed attendance and trigger auto-attendance
    so ERPNext recalculates based on new checkins.
    """
    attendance_name = frappe.db.get_value("Attendance", {
        "employee": employee,
        "attendance_date": date,
        "docstatus": 0  # Draft only — don't touch submitted
    }, "name")

    if attendance_name:
        att = frappe.get_doc("Attendance", attendance_name)
        att.delete(ignore_permissions=True)

    # Trigger shift-based auto attendance for this employee+date
    try:
        from hrms.hr.doctype.shift_type.shift_type import process_auto_attendance_for_shifts
        process_auto_attendance_for_shifts()
    except Exception:
        pass  # Will be picked up by next scheduled auto-attendance run
