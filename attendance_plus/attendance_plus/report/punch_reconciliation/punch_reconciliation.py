import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Employee", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 120},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
        {"label": "Time", "fieldname": "time", "fieldtype": "Datetime", "width": 160},
        {"label": "Log Type", "fieldname": "log_type", "fieldtype": "Data", "width": 100},
        {"label": "Source", "fieldname": "custom_checkin_source", "fieldtype": "Data", "width": 120},
        {"label": "Biometric Device", "fieldname": "custom_biometric_device", "fieldtype": "Link", "options": "Biometric Device", "width": 150},
        {"label": "Location", "fieldname": "custom_location", "fieldtype": "Data", "width": 120},
        {"label": "Regularization Ref", "fieldname": "custom_regularization_ref", "fieldtype": "Link", "options": "Attendance Regularization", "width": 150}
    ]

def get_data(filters):
    conditions = []
    values = {}
    
    if filters.get("from_date"):
        conditions.append("DATE(time) >= %(from_date)s")
        values["from_date"] = filters.get("from_date")
    if filters.get("to_date"):
        conditions.append("DATE(time) <= %(to_date)s")
        values["to_date"] = filters.get("to_date")
    if filters.get("employee"):
        conditions.append("employee = %(employee)s")
        values["employee"] = filters.get("employee")
    if filters.get("source"):
        conditions.append("custom_checkin_source = %(source)s")
        values["source"] = filters.get("source")

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    data = frappe.db.sql(f"""
        SELECT 
            employee, employee_name, time, log_type,
            custom_checkin_source, custom_biometric_device, custom_location,
            custom_regularization_ref
        FROM `tabEmployee Checkin`
        WHERE {where_clause}
        ORDER BY time desc
    """, values, as_dict=True)

    return data
