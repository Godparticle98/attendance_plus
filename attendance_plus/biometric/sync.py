"""
attendance_plus/biometric/sync.py

Pulls attendance logs from ZKTeco devices configured in Biometric Device doctype
and pushes them into ERPNext Employee Checkin.

Replaces the external biometric-attendance-sync-tool script.
Runs inside Frappe scheduler every 5 minutes.
"""

import frappe
from frappe.utils import now_datetime, get_datetime, cint
from datetime import datetime


def pull_biometric_logs():
    """
    Scheduled task: Pull logs from all active biometric devices
    and push to Employee Checkin.
    Called every 5 minutes via hooks.py scheduler_events.
    """
    devices = frappe.get_all(
        "Biometric Device",
        filters={"is_active": 1},
        fields=["name", "device_id", "ip_address", "port", "shift_type", "location"]
    )

    if not devices:
        return

    for device in devices:
        try:
            logs = _fetch_logs_from_device(device)
            if logs:
                pushed = _push_logs_to_erpnext(logs, device)
                frappe.db.set_value("Biometric Device", device.name, {
                    "last_sync_time": now_datetime(),
                    "sync_status": "Success",
                    "last_log_count": pushed
                })
            else:
                frappe.db.set_value("Biometric Device", device.name, {
                    "last_sync_time": now_datetime(),
                    "sync_status": "Success",
                    "last_log_count": 0
                })
        except Exception as e:
            frappe.log_error(
                title=f"Biometric Sync Failed: {device.name}",
                message=frappe.get_traceback()
            )
            frappe.db.set_value("Biometric Device", device.name, {
                "last_sync_time": now_datetime(),
                "sync_status": "Failed"
            })

    frappe.db.commit()


def _fetch_logs_from_device(device):
    """
    Connect to ZKTeco device via pyzk and fetch attendance logs.
    Returns list of dicts: {user_id, timestamp, punch_type}
    punch_type: 0 = IN, 1 = OUT (ZKTeco standard)
    """
    try:
        from zk import ZK
    except ImportError:
        frappe.log_error(
            title="pyzk not installed",
            message="Run: bench pip install pyzk"
        )
        return []

    zk = ZK(
        device.ip_address,
        port=cint(device.port) or 4370,
        timeout=10,
        password=0,
        force_udp=False,
        ommit_ping=False
    )

    conn = None
    logs = []

    try:
        conn = zk.connect()
        conn.disable_device()

        # Get last sync time to avoid re-importing old logs
        last_sync = frappe.db.get_value(
            "Biometric Device", device.name, "last_sync_time"
        )
        cutoff = get_datetime(last_sync) if last_sync else None

        attendances = conn.get_attendance()
        for att in attendances:
            # att.user_id, att.timestamp, att.punch (0=IN, 1=OUT, 4=OT IN, 5=OT OUT)
            ts = att.timestamp
            if cutoff and ts <= cutoff:
                continue

            punch_type = _map_punch_type(att.punch)
            logs.append({
                "user_id": str(att.user_id),
                "timestamp": ts,
                "punch_type": punch_type,
                "device_name": device.name
            })

        conn.enable_device()
    except Exception:
        raise
    finally:
        if conn:
            conn.disconnect()

    return logs


def _map_punch_type(punch_code):
    """Map ZKTeco punch codes to ERPNext log_type"""
    # 0 = Check In, 1 = Check Out, 4 = OT In, 5 = OT Out
    out_codes = [1, 5]
    return "OUT" if punch_code in out_codes else "IN"


def _push_logs_to_erpnext(logs, device):
    """
    Insert logs into Employee Checkin if not already present.
    Matches biometric user_id to Employee via attendance_device_id field.
    Returns count of new records pushed.
    """
    pushed = 0

    for log in logs:
        # Find employee by biometric/attendance device ID
        employee = frappe.db.get_value(
            "Employee",
            {"attendance_device_id": log["user_id"], "status": "Active"},
            ["name", "employee_name"],
            as_dict=True
        )

        if not employee:
            # Log unmapped biometric ID for HR to review
            _log_unmapped_id(log["user_id"], log["timestamp"], device.name)
            continue

        # Check for duplicate — same employee, same timestamp
        exists = frappe.db.exists("Employee Checkin", {
            "employee": employee.name,
            "time": log["timestamp"],
            "log_type": log["punch_type"]
        })

        if exists:
            continue

        try:
            checkin = frappe.get_doc({
                "doctype": "Employee Checkin",
                "employee": employee.name,
                "employee_name": employee.employee_name,
                "time": log["timestamp"],
                "log_type": log["punch_type"],
                "device_id": device.device_id,
                # Custom fields added via fixtures
                "custom_checkin_source": "Biometric",
                "custom_biometric_device": device.name,
                "custom_location": device.location or ""
            })
            checkin.insert(ignore_permissions=True)
            pushed += 1
        except Exception:
            frappe.log_error(
                title=f"Failed to insert checkin for {employee.name}",
                message=frappe.get_traceback()
            )

    return pushed


def _log_unmapped_id(user_id, timestamp, device_name):
    """
    Log biometric user IDs that don't match any ERPNext employee.
    HR can review and fix mappings from this log.
    """
    # Avoid duplicate unmapped logs for the same user
    existing = frappe.db.exists("Unmapped Biometric Log", {
        "biometric_user_id": user_id,
        "device": device_name
    })
    if not existing:
        try:
            frappe.get_doc({
                "doctype": "Unmapped Biometric Log",
                "biometric_user_id": user_id,
                "device": device_name,
                "first_seen": timestamp,
                "status": "Pending"
            }).insert(ignore_permissions=True)
        except Exception:
            pass  # Don't fail the whole sync for logging
