import frappe

@frappe.whitelist()
def get_overtime_summary(month_offset=0):
    from frappe.utils import add_months, get_first_day, get_last_day, today
    
    target_date = add_months(today(), int(month_offset))
    start_date = get_first_day(target_date)
    end_date = get_last_day(target_date)
    
    return frappe.db.sql("""
        SELECT 
            name, employee_name, attendance_date, in_time, out_time, 
            working_hours, custom_overtime_hours
        FROM `tabAttendance`
        WHERE 
            attendance_date >= %s 
            AND attendance_date <= %s 
            AND custom_overtime_hours > 0 
            AND docstatus = 1
        ORDER BY attendance_date DESC
    """, (start_date, end_date), as_dict=True)
