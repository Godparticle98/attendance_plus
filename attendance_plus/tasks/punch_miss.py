"""
attendance_plus/tasks/punch_miss.py

Detects employees with missing IN or OUT punches after their shift ends.
Runs every hour via scheduler. Creates auto Regularization Requests
and notifies employee + manager.
"""

import frappe
from frappe.utils import now_datetime, get_datetime, add_days, nowdate, getdate
from datetime import datetime, timedelta


def detect_punch_miss():
    """
    Main entry point. Called by scheduler every hour.
    Checks all active employees for punch miss on today's date.
    """
    today = nowdate()
    now = now_datetime()

    active_employees = frappe.get_all(
        "Employee",
        filters={"status": "Active"},
        fields=["name", "employee_name", "shift", "user_id", "reports_to"]
    )

    for emp in active_employees:
        try:
            _check_employee_punch(emp, today, now)
        except Exception:
            frappe.log_error(
                title=f"Punch Miss Check Failed: {emp.name}",
                message=frappe.get_traceback()
            )


def _check_employee_punch(emp, date, now):
    """Check a single employee for punch miss"""

    # Get shift end time to know when to check
    shift_end = _get_shift_end(emp, date)

    # Only check if shift has ended (with 30 min buffer)
    if shift_end:
        check_after = shift_end + timedelta(minutes=30)
        if now < check_after:
            return  # Shift not over yet, skip
    else:
        # No shift — check after 6 PM by default
        check_time = get_datetime(f"{date} 18:30:00")
        if now < check_time:
            return

    # Already has a regularization request for today? Skip
    existing_reg = frappe.db.exists("Attendance Regularization", {
        "employee": emp.name,
        "date": date,
        "docstatus": ["!=", 2]
    })
    if existing_reg:
        return

    # Get today's checkins for this employee
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

    # Determine miss type
    if not has_in and not has_out:
        miss_type = "Both Punches Missing"
    elif not has_in:
        miss_type = "Missing IN Punch"
    elif not has_out:
        miss_type = "Missing OUT Punch"
    else:
        return  # Both present, all good

    # Create auto regularization request
    _create_auto_regularization(emp, date, miss_type)

    # Notify employee and manager
    _notify_punch_miss(emp, date, miss_type)


def _get_shift_end(emp, date):
    """Get shift end datetime for employee on given date"""
    # Try employee's assigned shift first
    shift_name = emp.shift

    # If no shift on employee, check shift assignment
    if not shift_name:
        shift_assignment = frappe.db.get_value(
            "Shift Assignment",
            {
                "employee": emp.name,
                "start_date": ["<=", date],
                "docstatus": 1,
                "status": "Active"
            },
            "shift_type",
            order_by="start_date desc"
        )
        shift_name = shift_assignment

    if not shift_name:
        return None

    end_time = frappe.db.get_value("Shift Type", shift_name, "end_time")
    if not end_time:
        return None

    return get_datetime(f"{date} {end_time}")


def _create_auto_regularization(emp, date, miss_type):
    """Auto-create a regularization request for punch miss"""
    approver = _get_approver(emp)

    try:
        reg = frappe.get_doc({
            "doctype": "Attendance Regularization",
            "employee": emp.name,
            "date": date,
            "regularization_type": miss_type,
            "reason": f"Auto-detected: {miss_type} on {date}. Please provide correct punch times.",
            "approver": approver,
            "status": "Pending Approval"
        })
        reg.insert(ignore_permissions=True)
        reg.submit()
    except Exception:
        frappe.log_error(
            title=f"Auto Regularization Failed: {emp.name}",
            message=frappe.get_traceback()
        )


def _get_approver(emp):
    """Get approver user ID from reports_to"""
    if emp.reports_to:
        return frappe.db.get_value("Employee", emp.reports_to, "user_id")
    return None


def _notify_punch_miss(emp, date, miss_type):
    """Notify employee and manager about punch miss"""
    # Notify employee
    if emp.user_id:
        frappe.sendmail(
            recipients=[emp.user_id],
            subject=f"Attendance Alert: {miss_type} on {date}",
            message=f"""
                <p>Dear {emp.employee_name},</p>
                <p>We noticed a <b>{miss_type}</b> for your attendance on <b>{date}</b>.</p>
                <p>A regularization request has been automatically created.
                Please update it with the correct punch times and submit for approval.</p>
                <p>
                    <a href="/app/attendance-regularization?employee={emp.name}&date={date}">
                        View Regularization Request
                    </a>
                </p>
            """,
            now=False  # Queue it, don't block scheduler
        )

    # Notify manager
    approver = _get_approver(emp)
    if approver:
        frappe.sendmail(
            recipients=[approver],
            subject=f"Punch Miss Alert: {emp.employee_name} on {date}",
            message=f"""
                <p>FYI: <b>{emp.employee_name}</b> has a <b>{miss_type}</b>
                on <b>{date}</b>.</p>
                <p>A regularization request has been auto-created pending their action.</p>
            """,
            now=False
        )

def send_manager_summary_emails():
    """
    Daily scheduled task to send HR/Managers a summary of unresolved punch misses.
    """
    managers = frappe.db.sql("""
        SELECT DISTINCT approver 
        FROM `tabAttendance Regularization`
        WHERE status = 'Pending Approval'
        AND docstatus = 1
    """, as_dict=True)

    for row in managers:
        approver = row.approver
        if not approver: continue
        
        pending = frappe.get_all(
            "Attendance Regularization",
            filters={"approver": approver, "status": "Pending Approval", "docstatus": 1},
            fields=["employee_name", "date", "regularization_type"]
        )

        if not pending: continue

        rows_html = "".join([
            f"<tr><td>{p.employee_name}</td><td>{p.date}</td><td>{p.regularization_type}</td></tr>"
            for p in pending
        ])

        frappe.sendmail(
            recipients=[approver],
            subject="Daily Summary: Pending Attendance Regularizations",
            message=f"""
                <p>Dear Manager,</p>
                <p>You have <b>{len(pending)}</b> pending attendance regularizations requiring your action:</p>
                <table border="1" style="border-collapse: collapse; width: 100%; text-align: left;" cellpadding="5">
                    <tr><th>Employee</th><th>Date</th><th>Type</th></tr>
                    {rows_html}
                </table>
                <br>
                <p><a href="/app/attendance-regularization">Click here to view all</a></p>
            """,
            now=False
        )
