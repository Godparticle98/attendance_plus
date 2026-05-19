"""
attendance_plus/install.py

Runs automatically after `bench install-app attendance_plus`.
Creates Workspace, Desktop Icon, and all custom fields.
Compatible with ERPNext 16 / Frappe v15+.
"""

import frappe


def after_install():
    print("\n=== Attendance Plus Setup ===")
    try:
        _create_workspace()
        _create_custom_fields()
        frappe.db.commit()
        print("=== Attendance Plus Setup Complete ===\n")
    except Exception:
        frappe.log_error(
            title="Attendance Plus Install Failed",
            message=frappe.get_traceback()
        )
        print("Setup encountered errors. Check error log.")


def _create_workspace():
    print("Setting up Workspace...")

    # Reload Number Cards
    number_cards = [
        "absent_today",
        "pending_regularizations",
        "present_today",
        "total_active_employees",
        "total_ot_hours_today"
    ]
    for card in number_cards:
        try:
            frappe.reload_doc("attendance_plus", "number_card", card, force=True)
            print(f"  Number Card reloaded: {card}")
        except Exception as e:
            print(f"  Failed to reload Number Card {card}: {e}")

    # Reload Reports
    reports = [
        "daily_overtime_summary",
        "punch_reconciliation"
    ]
    for report in reports:
        try:
            frappe.reload_doc("attendance_plus", "report", report, force=True)
            print(f"  Report reloaded: {report}")
        except Exception as e:
            print(f"  Failed to reload Report {report}: {e}")

    # Reload Workspace
    try:
        frappe.reload_doc("attendance_plus", "workspace", "attendance_plus", force=True)
        print("  Workspace reloaded from fixtures.")
    except Exception as e:
        print(f"  Failed to reload Workspace: {e}")



def _create_custom_fields():
    print("Creating custom fields...")

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

    created = 0
    skipped = 0
    failed = 0

    for doctype, fields in CUSTOM_FIELDS.items():
        for field in fields:

            if frappe.db.exists("Custom Field", {
                "dt": doctype,
                "fieldname": field["fieldname"]
            }):
                skipped += 1
                continue

            # For Link fields verify target DocType exists
            if field.get("fieldtype") == "Link":
                target = field.get("options", "")
                if target and not frappe.db.exists("DocType", target):
                    print(f"  SKIPPED (DocType '{target}' not found): {field['fieldname']}")
                    failed += 1
                    continue

            try:
                frappe.get_doc({
                    "doctype": "Custom Field",
                    "dt": doctype,
                    **field
                }).insert(ignore_permissions=True)
                created += 1
                print(f"  Created: {doctype}.{field['fieldname']}")
            except Exception as e:
                print(f"  ERROR ({doctype}.{field['fieldname']}): {e}")
                failed += 1

    print(f"  Custom fields — Created: {created}, Skipped: {skipped}, Failed: {failed}")


def before_uninstall():
    pass
