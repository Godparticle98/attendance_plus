"""
attendance_plus/fixtures/custom_fields.py

Run this once after app install to create all required custom fields.
Usage: bench execute attendance_plus.fixtures.custom_fields.create_custom_fields
"""

import frappe


CUSTOM_FIELDS = {
    "Employee Checkin": [
        {
            "fieldname": "custom_checkin_source",
            "label": "Check-in Source",
            "fieldtype": "Select",
            "options": "\nBiometric\nApp\nManual\nPermission\nRegularization",
            "insert_after": "log_type",
            "in_list_view": 1,
            "in_filter": 1,
            "module": "Attendance Plus"
        },
        {
            "fieldname": "custom_biometric_device",
            "label": "Biometric Device",
            "fieldtype": "Link",
            "options": "Biometric Device",
            "insert_after": "custom_checkin_source",
            "module": "Attendance Plus"
        },
        {
            "fieldname": "custom_location",
            "label": "Location",
            "fieldtype": "Data",
            "insert_after": "custom_biometric_device",
            "module": "Attendance Plus"
        },
        {
            "fieldname": "custom_permission_ref",
            "label": "Permission Reference",
            "fieldtype": "Link",
            "options": "Attendance Permission",
            "insert_after": "custom_location",
            "read_only": 1,
            "module": "Attendance Plus"
        },
        {
            "fieldname": "custom_regularization_ref",
            "label": "Regularization Reference",
            "fieldtype": "Link",
            "options": "Attendance Regularization",
            "insert_after": "custom_permission_ref",
            "read_only": 1,
            "module": "Attendance Plus"
        }
    ],
    "Attendance": [
        {
            "fieldname": "custom_permission_type",
            "label": "Permission Type",
            "fieldtype": "Data",
            "insert_after": "late_entry",
            "read_only": 1,
            "module": "Attendance Plus"
        },
        {
            "fieldname": "custom_permission_ref",
            "label": "Permission Reference",
            "fieldtype": "Link",
            "options": "Attendance Permission",
            "insert_after": "custom_permission_type",
            "read_only": 1,
            "module": "Attendance Plus"
        }
    ]
}


def create_custom_fields():
    """Create all custom fields for attendance_plus"""
    for doctype, fields in CUSTOM_FIELDS.items():
        for field in fields:
            if frappe.db.exists("Custom Field", {
                "dt": doctype,
                "fieldname": field["fieldname"]
            }):
                print(f"  Skipping (exists): {doctype}.{field['fieldname']}")
                continue

            cf = frappe.get_doc({
                "doctype": "Custom Field",
                "dt": doctype,
                **field
            })
            cf.insert(ignore_permissions=True)
            print(f"  Created: {doctype}.{field['fieldname']}")

    frappe.db.commit()
    print("All custom fields created.")
