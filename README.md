# attendance_plus — Setup Guide

Unified biometric + app attendance management for ERPNext.

---

## 1. Create & Install the App

```bash
cd /home/frappe/frappe-bench

bench new-app attendance_plus
# App Title: Attendance Plus
# App Description: Unified attendance management
# Leave rest as defaults

bench --site your-site.com install-app attendance_plus
```

---

## 2. Copy App Files

Copy the generated files into:
```
frappe-bench/apps/attendance_plus/attendance_plus/
```

Folder structure:
```
attendance_plus/
├── hooks.py
├── biometric/
│   ├── __init__.py
│   └── sync.py
├── doctype/
│   ├── biometric_device/
│   │   ├── biometric_device.json
│   │   └── biometric_device.py  (empty controller ok)
│   ├── attendance_permission/
│   │   ├── attendance_permission.json
│   │   └── attendance_permission.py
│   └── attendance_regularization/
│       ├── attendance_regularization.json
│       └── attendance_regularization.py
├── tasks/
│   ├── __init__.py
│   └── punch_miss.py
├── api/
│   ├── __init__.py
│   └── dashboard.py
├── fixtures/
│   ├── __init__.py
│   └── custom_fields.py
└── pages/
    └── attendance_dashboard/
        └── attendance_dashboard.html
```

---

## 3. Install Python Dependency (pyzk)

```bash
cd /home/frappe/frappe-bench
bench pip install pyzk
```

---

## 4. Run Migrations & Create Custom Fields

```bash
bench --site your-site.com migrate

# Create custom fields on Employee Checkin and Attendance
bench --site your-site.com execute attendance_plus.fixtures.custom_fields.create_custom_fields
```

---

## 5. Configure Biometric Devices

1. Go to **Attendance Plus > Biometric Device > New**
2. Fill in:
   - **Device Name**: e.g. "Main Gate"
   - **Device ID**: Must match the ID set in ZKTeco device network settings
   - **IP Address**: Device's LAN IP (e.g. 192.168.1.201)
   - **Port**: 4370 (default for ZKTeco)
   - **Location**: Optional — links to ERPNext Location
   - **Default Shift Type**: For employees without a specific shift
3. Save and set **Is Active = Yes**

---

## 6. Map Employees to Biometric IDs

Each employee must have their biometric user ID set in ERPNext:

1. Open **Employee** record
2. Go to **Attendance and Leave Details** section
3. Set **Attendance Device ID** = the User ID in the biometric machine

This is how the sync tool matches punches to employees.

---

## 7. Disable Geo-Attendance (Important)

Since we're handling location validation ourselves:

1. Go to **HR Settings**
2. Uncheck **Enable Geolocation Tracking**
3. Save

The biometric sync will now push to Employee Checkin without geo conflicts.

---

## 8. Enable Auto Attendance on Shift Types

For employees with shifts:
1. Go to **Shift Type** > open each shift
2. Enable **Enable Auto Attendance**
3. Set **Process Attendance After** (e.g. 2 hours after shift end)

For employees without shifts — attendance is processed daily by our custom task.

---

## 9. Restart & Test

```bash
bench restart

# Test biometric sync manually
bench --site your-site.com execute attendance_plus.biometric.sync.pull_biometric_logs

# Test punch miss detection
bench --site your-site.com execute attendance_plus.tasks.punch_miss.detect_punch_miss
```

---

## 10. Dashboard Access

The manager dashboard is available at:
```
https://your-site.com/attendance-dashboard
```

Accessible to: HR Manager, HR User roles (configurable in page permissions).

---

## Workflow Summary

| Scenario | What Happens |
|---|---|
| Employee punches biometric | Sync pulls every 5 min → Employee Checkin (Source: Biometric) |
| Employee uses Frappe HR app | Standard checkin → Employee Checkin (Source: App) |
| Employee misses punch | Detected after shift end → Auto Regularization created → Notified |
| Employee submits Permission | Routes to direct manager → Approve/Reject → Checkins auto-created |
| Employee submits Regularization | Routes to direct manager → Approve → Missing checkins inserted |
| Manager opens Dashboard | Live view of all employee statuses + pending approvals |

---

## Troubleshooting

**Biometric sync not working?**
```bash
# Check logs
bench --site your-site.com show-logs
# Test device connectivity
ping 192.168.1.201  # your device IP
```

**pyzk not found?**
```bash
bench pip install pyzk
bench restart
```

**Custom fields not appearing?**
```bash
bench --site your-site.com execute attendance_plus.fixtures.custom_fields.create_custom_fields
bench --site your-site.com clear-cache
```
