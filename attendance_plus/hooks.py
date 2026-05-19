app_name = "attendance_plus"
app_title = "Attendance Plus"
app_publisher = "Your Company"
app_description = "Unified biometric + app attendance management for ERPNext"
app_version = "0.0.1"
app_email = "admin@yourcompany.com"
app_license = "MIT"

# Install / Uninstall hooks
after_install = "attendance_plus.install.after_install"
before_uninstall = "attendance_plus.install.before_uninstall"

# Scheduled Tasks
scheduler_events = {
    "cron": {
        # Pull biometric punches every 5 minutes
        "*/5 * * * *": [
            "attendance_plus.biometric.sync.pull_biometric_logs"
        ],
        # Detect punch misses 30 min after each hour
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

# Custom fields added to existing doctypes
fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            ["module", "=", "Attendance Plus"]
        ]
    },
    {
        "doctype": "Workflow",
        "filters": [
            ["module", "=", "Attendance Plus"]
        ]
    }
]

# Web pages
website_route_rules = [
    {
        "from_route": "/attendance-portal",
        "to_route": "attendance_portal"
    }
]
