import frappe

@frappe.whitelist()
def get_pending_regularizations():
    return frappe.db.sql("""
        SELECT name, employee_name, date, regularization_type, reason, status
        FROM `tabAttendance Regularization`
        WHERE status = 'Pending Approval' AND docstatus = 1
        ORDER BY creation DESC
    """, as_dict=True)

@frappe.whitelist()
def approve_regularization(name):
    doc = frappe.get_doc("Attendance Regularization", name)
    doc.status = "Approved"
    doc.save(ignore_permissions=True)
    return "Approved"
