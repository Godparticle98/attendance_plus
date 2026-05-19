import frappe

def get_context(context):
    if "HR Manager" not in frappe.get_roles() and \
       "HR User" not in frappe.get_roles() and \
       "System Manager" not in frappe.get_roles():
        frappe.throw("Not permitted", frappe.PermissionError)
    context.no_cache = 1