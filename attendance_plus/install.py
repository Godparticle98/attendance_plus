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

    if frappe.db.exists("Workspace", "Attendance Plus"):
        print("  Workspace already exists, skipping.")
        return

    ws = frappe.new_doc("Workspace")
    ws.title = "Attendance Plus"
    ws.name = "Attendance Plus"
    ws.label = "Attendance Plus"
    ws.module = "Attendance Plus"
    ws.is_standard = 1
    ws.app = "attendance_plus"
    ws.public = 1
    ws.icon = "fa fa-clock-o"
    ws.color = "#2490EF"
    ws.category = "Modules"

    # ERPNext 16 uses a JSON content field for workspace layout
    ws.content = """[
        {
            "id": "section_1",
            "type": "header",
            "data": {
                "text": "Attendance Plus",
                "level": 3,
                "col": 12
            }
        },
        {
            "id": "section_2",
            "type": "spacer",
            "data": {"col": 12}
        }
    ]"""

    ws.insert(ignore_permissions=True)
    print("  Workspace created.")

    # Add shortcuts
    shortcuts = [
        {
            "label": "Attendance Dashboard",
            "type": "URL",
            "url": "/attendance_dashboard",
            "color": "#2490EF",
            "icon": "fa fa-bar-chart"
        },
        {
            "label": "Biometric Device",
            "type": "DocType",
            "link_to": "Biometric Device",
            "color": "#36414C",
            "icon": "fa fa-microchip"
        },
        {
            "label": "Attendance Permission",
            "type": "DocType",
            "link_to": "Attendance Permission",
            "color": "#F8814F",
            "icon": "fa fa-check-circle"
        },
        {
            "label": "Attendance Regularization",
            "type": "DocType",
            "link_to": "Attendance Regularization",
            "color": "#A9E6A0",
            "icon": "fa fa-pencil-square-o"
        },
        {
            "label": "Unmapped Biometric Log",
            "type": "DocType",
            "link_to": "Unmapped Biometric Log",
            "color": "#FFC4C4",
            "icon": "fa fa-exclamation-triangle"
        },
        {
            "label": "Employee Checkin",
            "type": "DocType",
            "link_to": "Employee Checkin",
            "color": "#98D85B",
            "icon": "fa fa-sign-in"
        },
    ]

    for i, sc in enumerate(shortcuts):
        try:
            shortcut = frappe.new_doc("Workspace Shortcut")
            shortcut.parenttype = "Workspace"
            shortcut.parentfield = "shortcuts"
            shortcut.parent = "Attendance Plus"
            shortcut.label = sc["label"]
            shortcut.type = sc["type"]
            shortcut.color = sc.get("color", "#2490EF")
            shortcut.icon = sc.get("icon", "")
            shortcut.idx = i + 1

            if sc["type"] == "DocType":
                shortcut.link_to = sc["link_to"]
            elif sc["type"] == "URL":
                shortcut.url = sc["url"]

            shortcut.insert(ignore_permissions=True)
            print(f"  Shortcut added: {sc['label']}")
        except Exception as e:
            print(f"  Shortcut skipped ({sc['label']}): {e}")

    print("  Workspace setup done.")


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
    """Clean up on uninstall"""
    print("\n=== Attendance Plus Cleanup ===")

    # Remove workspace
    if frappe.db.exists("Workspace", "Attendance Plus"):
        frappe.delete_doc("Workspace", "Attendance Plus", ignore_permissions=True)
        print("  Workspace removed.")

    # Remove custom fields
    custom_fields = frappe.get_all("Custom Field", filters={"module": "Attendance Plus"})
    for cf in custom_fields:
        try:
            frappe.delete_doc("Custom Field", cf.name, ignore_permissions=True)
            print(f"  Removed custom field: {cf.name}")
        except Exception:
            pass

    frappe.db.commit()
    print("=== Cleanup Complete ===\n")
