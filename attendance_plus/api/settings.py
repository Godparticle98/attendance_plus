import frappe
import json

@frappe.whitelist()
def get_settings():
    doc = frappe.get_doc("Attendance Plus Settings")
    return {
        "default_break_time": doc.default_break_time,
        "default_work_hours": doc.default_work_hours
    }

@frappe.whitelist()
def save_settings(data):
    if isinstance(data, str):
        data = json.loads(data)
        
    doc = frappe.get_doc("Attendance Plus Settings")
    doc.default_break_time = data.get("default_break_time", doc.default_break_time)
    doc.default_work_hours = data.get("default_work_hours", doc.default_work_hours)
    doc.save(ignore_permissions=True)
    return "Saved"
