"""
attendance_plus/api/dashboard.py

Whitelisted API methods for the Attendance Dashboard page.
"""

import frappe
from frappe.utils import nowdate, get_datetime, format_datetime


@frappe.whitelist()
def get_attendance_data(date=None, department=None, status_filter=None):
    """
    Returns attendance summary + per-employee rows for the given date.
    Combines data from Employee Checkin (live) and Attendance (processed).
    """
    if not date:
        date = nowdate()

    # Get all active employees (filtered by dept if provided)
    emp_filters = {"status": "Active"}
    if department:
        emp_filters["department"] = department

    employees = frappe.get_all(
        "Employee",
        filters=emp_filters,
        fields=["name", "employee_name", "department", "shift"]
    )

    rows = []
    summary = {"total": len(employees), "present": 0, "absent": 0, "late": 0, "punch_miss": 0}

    for emp in employees:
        row = _build_employee_row(emp, date)

        # Apply status filter
        if status_filter and row["status"] != status_filter:
            continue

        rows.append(row)

        # Update summary
        s = row["status"]
        if s in ["Present", "Half Day"]:
            summary["present"] += 1
        elif s == "Absent":
            summary["absent"] += 1
        elif s == "Late":
            summary["late"] += 1
            summary["present"] += 1
        elif s == "Punch Miss":
            summary["punch_miss"] += 1

    return {"summary": summary, "rows": rows}


def _build_employee_row(emp, date):
    """Build a single employee attendance row"""
    # Get checkins for this date
    checkins = frappe.get_all(
        "Employee Checkin",
        filters={
            "employee": emp.name,
            "time": ["between", [f"{date} 00:00:00", f"{date} 23:59:59"]]
        },
        fields=["log_type", "time", "custom_checkin_source"],
        order_by="time asc"
    )

    in_checkin = next((c for c in checkins if c.log_type == "IN"), None)
    out_checkin = next((c for c in reversed(checkins) if c.log_type == "OUT"), None)

    # Get processed attendance if exists
    attendance = frappe.db.get_value(
        "Attendance",
        {"employee": emp.name, "attendance_date": date, "docstatus": 1},
        ["status", "in_time", "out_time", "late_entry"],
        as_dict=True
    )

    # Determine display status
    if attendance:
        status = attendance.status
        if attendance.late_entry:
            status = "Late"
    elif in_checkin and out_checkin:
        status = "Present"
    elif in_checkin and not out_checkin:
        status = "Punch Miss"
    elif not in_checkin and not out_checkin:
        # Check if on leave
        on_leave = frappe.db.exists("Leave Application", {
            "employee": emp.name,
            "from_date": ["<=", date],
            "to_date": [">=", date],
            "status": "Approved",
            "docstatus": 1
        })
        status = "On Leave" if on_leave else "Absent"
    else:
        status = "Punch Miss"

    # Source label
    source = in_checkin.custom_checkin_source if in_checkin else None

    return {
        "employee": emp.name,
        "employee_name": emp.employee_name,
        "department": emp.department or "-",
        "date": date,
        "in_time": _fmt_time(in_checkin.time) if in_checkin else None,
        "out_time": _fmt_time(out_checkin.time) if out_checkin else None,
        "source": source,
        "status": status
    }


def _fmt_time(dt):
    if not dt:
        return None
    return get_datetime(dt).strftime("%H:%M")


@frappe.whitelist()
def get_pending_approvals():
    """
    Returns all pending Permission and Regularization requests
    where current user is the approver.
    """
    user = frappe.session.user
    pending = []

    # Attendance Permissions
    permissions = frappe.get_all(
        "Attendance Permission",
        filters={"approver": user, "status": "Pending Approval", "docstatus": 1},
        fields=["name", "employee", "employee_name", "date", "permission_type", "reason"]
    )
    for p in permissions:
        pending.append({
            "name": p.name,
            "doctype": "Attendance Permission",
            "doctype_label": "Permission",
            "employee": p.employee,
            "employee_name": p.employee_name,
            "date": p.date,
            "request_type": p.permission_type,
            "reason": p.reason
        })

    # Attendance Regularizations
    regularizations = frappe.get_all(
        "Attendance Regularization",
        filters={"approver": user, "status": "Pending Approval", "docstatus": 1},
        fields=["name", "employee", "employee_name", "date", "regularization_type", "reason"]
    )
    for r in regularizations:
        pending.append({
            "name": r.name,
            "doctype": "Attendance Regularization",
            "doctype_label": "Regularization",
            "employee": r.employee,
            "employee_name": r.employee_name,
            "date": r.date,
            "request_type": r.regularization_type,
            "reason": r.reason
        })

    return pending


def has_permission():
    """Used by add_to_apps_screen to control visibility"""
    return "HR Manager" in frappe.get_roles() or \
           "HR User" in frappe.get_roles() or \
           "System Manager" in frappe.get_roles()
