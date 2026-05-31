import frappe
from frappe.utils import nowdate, add_days

def send_daily_attendance_digest():
    """
    Sends a daily summary of yesterday's attendance, overtime, and missing punches
    to users with 'HR Manager' or 'System Manager' roles.
    """
    yesterday = add_days(nowdate(), -1)

    # Get stats
    total_employees = frappe.db.count("Employee", {"status": "Active"})
    present = frappe.db.count("Attendance", {"attendance_date": yesterday, "status": ["in", ["Present", "Half Day"]], "docstatus": 1})
    absent = frappe.db.count("Attendance", {"attendance_date": yesterday, "status": "Absent", "docstatus": 1})
    
    # Get overtime sum
    ot_data = frappe.db.sql("""
        SELECT IFNULL(SUM(custom_overtime_hours), 0)
        FROM `tabAttendance`
        WHERE attendance_date = %s
        AND docstatus = 1
    """, (yesterday,))
    total_ot = ot_data[0][0] if ot_data else 0.0

    # Get pending regularizations
    pending_regs = frappe.db.count("Attendance Regularization", {"date": yesterday, "status": "Pending Approval", "docstatus": 1})

    # Prepare HTML
    html_content = f"""
    <h3>Daily Attendance Digest - {yesterday}</h3>
    <table border="1" style="border-collapse: collapse; text-align: left;" cellpadding="8">
        <tr><th>Metric</th><th>Count</th></tr>
        <tr><td>Total Active Employees</td><td>{total_employees}</td></tr>
        <tr><td>Present / Half Day</td><td>{present}</td></tr>
        <tr><td>Absent</td><td>{absent}</td></tr>
        <tr><td>Total OT Hours</td><td>{total_ot} hrs</td></tr>
        <tr><td>Pending Regularizations (From Yesterday)</td><td>{pending_regs}</td></tr>
    </table>
    <br>
    <p>Please review pending attendance regularizations in the system.</p>
    """

    # Get recipients (HR Managers and System Managers)
    users = frappe.db.sql("""
        SELECT DISTINCT parent as user 
        FROM `tabHas Role` 
        WHERE role IN ('HR Manager', 'System Manager')
        AND parenttype = 'User'
    """, as_dict=True)

    recipients = [u.user for u in users if u.user and u.user != "Administrator"]

    if not recipients:
        return

    frappe.sendmail(
        recipients=recipients,
        subject=f"Attendance Digest - {yesterday}",
        message=html_content,
        now=False
    )
