app_name = "attendance_plus"
app_title = "Attendance Plus"
app_publisher = "Your Company"
app_description = "Unified biometric + app attendance management for ERPNext"
app_version = "0.0.1"
app_email = "admin@yourcompany.com"
app_license = "MIT"

# Install / Uninstall
after_install = "attendance_plus.install.after_install"
before_uninstall = "attendance_plus.install.before_uninstall"

# Frappe v16 desktop icon
add_to_apps_screen = [
    {
        "name": "attendance_plus",
        "logo": "/assets/attendance_plus/images/logo.svg",
        "title": "Attendance Plus",
        "route": "/app/attendance-dashboard",
        "has_permission": "attendance_plus.api.dashboard.has_permission"
    }
]

# Scheduled Tasks
scheduler_events = {
    "cron": {
        "*/5 * * * *": [
            "attendance_plus.biometric.sync.pull_biometric_logs"
        ],
        "30 * * * *": [
            "attendance_plus.tasks.punch_miss.detect_punch_miss"
        ],
    },
    "daily": [
        "attendance_plus.tasks.attendance_processor.process_attendance"
    ],
}

# Document Events
doc_events = {
    "Employee Checkin": {
        "after_insert": "attendance_plus.tasks.attendance_processor.on_new_checkin",
    }
}

# Fixtures — synced on migrate, never deleted as orphan
fixtures = [
    {
        "doctype": "Workspace",
        "filters": [["name", "=", "Attendance Plus"]]
    }
]
