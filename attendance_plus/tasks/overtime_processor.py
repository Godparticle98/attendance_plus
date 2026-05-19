"""
attendance_plus/tasks/overtime_processor.py

Calculates overtime based on rules defined in Attendance Plus Settings.
Hooked to Attendance before_submit.
"""

import frappe
from frappe.utils import time_diff_in_seconds, get_datetime
import math

def calculate_overtime(doc, method=None):
    """
    Hooked to Attendance before_submit.
    Calculates custom_overtime_hours based on OT Configuration.
    """
    if doc.status not in ["Present", "Half Day"]:
        doc.custom_overtime_hours = 0.0
        return

    # Check if employee has an employment type mapped for OT
    employee_type = frappe.db.get_value("Employee", doc.employee, "employment_type")
    if not employee_type:
        return

    # Load settings
    settings = frappe.get_single("Attendance Plus Settings")
    if not settings.ot_configuration:
        return

    # Find OT config for this employee type
    ot_config = next((row for row in settings.ot_configuration if row.employee_type == employee_type), None)
    
    if not ot_config or ot_config.ot_type != "Daily Basis":
        return

    # Calculate Total Time from First IN and Last OUT
    checkins = frappe.get_all(
        "Employee Checkin",
        filters={
            "employee": doc.employee,
            "time": ["between", [f"{doc.attendance_date} 00:00:00", f"{doc.attendance_date} 23:59:59"]]
        },
        fields=["log_type", "time"],
        order_by="time asc"
    )

    first_in = next((c.time for c in checkins if c.log_type == "IN"), None)
    last_out = next((c.time for c in reversed(checkins) if c.log_type == "OUT"), None)

    if not first_in or not last_out:
        # Cannot calculate reliable OT without both punches
        doc.custom_overtime_hours = 0.0
        return

    # If in_time / out_time are set on Attendance, use those, else use checkins
    in_time = get_datetime(doc.in_time or first_in)
    out_time = get_datetime(doc.out_time or last_out)

    if out_time <= in_time:
        doc.custom_overtime_hours = 0.0
        return

    total_seconds = time_diff_in_seconds(out_time, in_time)
    total_hours = total_seconds / 3600.0

    break_time = settings.default_break_time or 1.5
    work_hours = settings.default_work_hours or 8.0

    net_hours = total_hours - break_time

    if net_hours > work_hours:
        ot_raw = net_hours - work_hours
        # Floor to nearest 0.5 (e.g. 4.3 -> 4.0, 4.6 -> 4.5)
        ot_floored = math.floor(ot_raw * 2) / 2.0
        doc.custom_overtime_hours = ot_floored
    else:
        doc.custom_overtime_hours = 0.0
