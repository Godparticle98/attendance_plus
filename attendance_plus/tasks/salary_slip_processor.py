import frappe

def process_salary_slip_ot(doc, method=None):
    """
    Hooked to Salary Slip `before_validate` and `before_save`.
    Aggregates the total custom_overtime_hours from Attendance records
    for the payroll period and sets it to the Salary Slip.
    """
    if not doc.employee or not doc.start_date or not doc.end_date:
        return

    # Sum the custom_overtime_hours for the given period
    ot_hours = frappe.db.sql("""
        SELECT SUM(custom_overtime_hours)
        FROM `tabAttendance`
        WHERE employee = %s
        AND attendance_date >= %s
        AND attendance_date <= %s
        AND docstatus = 1
    """, (doc.employee, doc.start_date, doc.end_date))[0][0]

    doc.custom_ot_hours = ot_hours or 0.0
