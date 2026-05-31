"""
attendance_plus/tasks/attendance_processor.py

Daily task to process attendance for employees without shifts.
For employees with shifts, ERPNext's built-in auto-attendance handles it.
This handles the fallback case.
"""

import frappe
from frappe.utils import nowdate, get_datetime, add_days


def process_attendance():
    """
    Daily scheduled task.
    Processes attendance for employees without a shift assigned.
    Employees with shifts are handled by ERPNext's Shift Type auto-attendance.
    """
    today = nowdate()

    # Get employees without any shift
    employees_without_shift = frappe.db.sql("""
        SELECT e.name, e.employee_name, e.department
        FROM `tabEmployee` e
        WHERE e.status = 'Active'
        AND (e.default_shift IS NULL OR e.default_shift = '')
        AND NOT EXISTS (
            SELECT 1 FROM `tabShift Assignment` sa
            WHERE sa.employee = e.name
            AND sa.start_date <= %(today)s
            AND sa.docstatus = 1
            AND sa.status = 'Active'
        )
    """, {"today": today}, as_dict=True)

    for emp in employees_without_shift:
        try:
            _process_employee_attendance(emp, today)
        except Exception:
            frappe.log_error(
                title=f"Attendance Processing Failed: {emp.name}",
                message=frappe.get_traceback()
            )

    frappe.db.commit()


def _process_employee_attendance(emp, date):
    """Process attendance for a single employee on a given date"""

    # Skip if attendance already exists and is submitted
    existing = frappe.db.get_value("Attendance", {
        "employee": emp.name,
        "attendance_date": date,
        "docstatus": 1
    }, "name")
    if existing:
        return

    # Get checkins for the day
    checkins = frappe.get_all(
        "Employee Checkin",
        filters={
            "employee": emp.name,
            "time": ["between", [f"{date} 00:00:00", f"{date} 23:59:59"]]
        },
        fields=["log_type", "time"],
        order_by="time asc"
    )

    has_in = any(c.log_type == "IN" for c in checkins)
    has_out = any(c.log_type == "OUT" for c in checkins)

    in_time = next((c.time for c in checkins if c.log_type == "IN"), None)
    out_time = next((c.time for c in reversed(checkins) if c.log_type == "OUT"), None)

    # Check if on leave
    on_leave = frappe.db.exists("Leave Application", {
        "employee": emp.name,
        "from_date": ["<=", date],
        "to_date": [">=", date],
        "status": "Approved",
        "docstatus": 1
    })

    if on_leave:
        status = "On Leave"
    elif has_in and has_out:
        status = "Present"
    elif has_in or has_out:
        status = "Present"  # Punch miss — still mark present, regularization handles correction
    else:
        status = "Absent"

    # Don't create attendance for future dates or if no data at all and it's today
    if status == "Absent" and date == nowdate():
        return  # Wait till end of day — punch miss detector handles this

    # Create draft attendance
    att = frappe.get_doc({
        "doctype": "Attendance",
        "employee": emp.name,
        "employee_name": emp.employee_name,
        "attendance_date": date,
        "status": status,
        "in_time": in_time,
        "out_time": out_time,
        "company": frappe.db.get_value("Employee", emp.name, "company")
    })
    att.insert(ignore_permissions=True)
    att.submit()


def on_new_checkin(doc, method=None):
    """
    Triggered on every new Employee Checkin insert.
    Tags the source as 'App' if no source is set (came from Frappe HR mobile app).
    """
    if not doc.custom_checkin_source:
        frappe.db.set_value(
            "Employee Checkin", doc.name,
            "custom_checkin_source", "App"
        )
