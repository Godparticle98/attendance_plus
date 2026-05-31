import frappe
from frappe.utils import nowdate, get_datetime

@frappe.whitelist()
def get_dashboard_data():
    today = nowdate()
    
    # 1. Total Active Employees
    total_employees = frappe.db.count("Employee", {"status": "Active"})
    
    # 2. Get today's check-ins to compute real-time presence (since Attendance records might not be generated yet)
    checkins = frappe.db.sql("""
        SELECT employee, log_type, time, employee_name
        FROM `tabEmployee Checkin`
        WHERE time >= %s AND time <= %s
        ORDER BY time ASC
    """, (f"{today} 00:00:00", f"{today} 23:59:59"), as_dict=True)
    
    present_employees = set()
    employee_times = {}
    
    for c in checkins:
        present_employees.add(c.employee)
        if c.employee not in employee_times:
            employee_times[c.employee] = {"name": c.employee_name, "in": None, "out": None}
        
        if c.log_type == "IN" and not employee_times[c.employee]["in"]:
            employee_times[c.employee]["in"] = c.time.strftime("%H:%M")
        elif c.log_type == "OUT":
            employee_times[c.employee]["out"] = c.time.strftime("%H:%M")
            
    present_today = len(present_employees)
    
    # Employees who are on leave today
    on_leave = frappe.db.sql("""
        SELECT employee FROM `tabLeave Application`
        WHERE from_date <= %s AND to_date >= %s AND status = 'Approved' AND docstatus = 1
    """, (today, today))
    on_leave_set = {r[0] for r in on_leave}
    
    absent_today = total_employees - present_today - len(on_leave_set)
    if absent_today < 0: absent_today = 0
    
    # Pending Regularizations
    pending_regs = frappe.db.count("Attendance Regularization", {"status": "Pending Approval", "docstatus": 1})
    
    # Today's Attendance Table Data (Live from check-ins)
    live_attendance = []
    for emp, times in employee_times.items():
        status = "Present" if times["in"] and times["out"] else "Punched IN" if times["in"] else "Punched OUT"
        live_attendance.append({
            "employee_name": times["name"],
            "status": status,
            "in_time": times["in"] or "-",
            "out_time": times["out"] or "-"
        })
        
    return {
        "total_employees": total_employees,
        "present_today": present_today,
        "absent_today": absent_today,
        "pending_regs": pending_regs,
        "live_attendance": live_attendance
    }

@frappe.whitelist()
def trigger_sync():
    """
    Manually triggers the biometric sync and processes the attendance
    to immediately reflect manual check-ins.
    """
    from attendance_plus.biometric.sync import pull_biometric_logs
    from attendance_plus.tasks.attendance_processor import process_attendance
    
    try:
        # Pull biometric if pyzk exists, ignore if not
        pull_biometric_logs()
    except Exception:
        pass
        
    process_attendance()
    return "Synced successfully"
