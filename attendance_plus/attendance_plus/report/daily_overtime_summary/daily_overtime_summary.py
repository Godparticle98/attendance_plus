import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Employee", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 120},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
        {"label": "Department", "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 120},
        {"label": "Date", "fieldname": "attendance_date", "fieldtype": "Date", "width": 100},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": "Check-In", "fieldname": "in_time", "fieldtype": "Datetime", "width": 150},
        {"label": "Check-Out", "fieldname": "out_time", "fieldtype": "Datetime", "width": 150},
        {"label": "Overtime (Hrs)", "fieldname": "custom_overtime_hours", "fieldtype": "Float", "width": 120}
    ]

def get_data(filters):
    conditions = []
    values = {}
    
    if filters.get("from_date"):
        conditions.append("attendance_date >= %(from_date)s")
        values["from_date"] = filters.get("from_date")
    if filters.get("to_date"):
        conditions.append("attendance_date <= %(to_date)s")
        values["to_date"] = filters.get("to_date")
    if filters.get("employee"):
        conditions.append("employee = %(employee)s")
        values["employee"] = filters.get("employee")
    if filters.get("department"):
        conditions.append("department = %(department)s")
        values["department"] = filters.get("department")

    conditions.append("custom_overtime_hours > 0")

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    data = frappe.db.sql(f"""
        SELECT 
            employee, employee_name, department, attendance_date,
            status, in_time, out_time, custom_overtime_hours
        FROM `tabAttendance`
        WHERE {where_clause}
        ORDER BY attendance_date desc, employee asc
    """, values, as_dict=True)

    return data
