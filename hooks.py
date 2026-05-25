app_name = "sfa_core"
app_title = "SFA Core"
app_publisher = "Hema Beverages"
app_description = "Sales Force Automation Platform for Hema Beverages"
app_email = "tech@hemabeverages.com"
app_license = "mit"

required_apps = ["erpnext"]
app_version = "0.0.1"

# Assets are built via Vite, not Frappe esbuild
# Run: cd apps/sfa_core && npm install && npm run build
# app_include_css = "/assets/sfa_core/dist/sfa_core.bundle.css"
# app_include_js = "/assets/sfa_core/dist/sfa_desk.bundle.js"

after_install = "sfa_core.install.after_install.after_install"
boot_session = "sfa_core.boot.boot_session"

doc_events = {
    "Customer": {
        "validate": "sfa_core.doc_events.customer.validate",
        "after_insert": "sfa_core.doc_events.customer.after_insert",
    },
    "Sales Order": {
        "validate": "sfa_core.doc_events.sales_order.validate",
        "on_submit": "sfa_core.doc_events.sales_order.on_submit",
    },
    "SFA Visit": {
        "validate": "sfa_core.doc_events.visit.validate",
        "on_update": "sfa_core.doc_events.visit.on_update",
        "on_submit": "sfa_core.doc_events.visit.on_submit",
    },
    "SFA Payment": {
        "validate": "sfa_core.doc_events.payment.validate",
        "on_submit": "sfa_core.doc_events.payment.on_submit",
    },
    "SFA Form Response": {
        "validate": "sfa_core.doc_events.form_response.validate",
        "on_submit": "sfa_core.doc_events.form_response.on_submit",
    },
    "SFA Field Activity": {
        "validate": "sfa_core.doc_events.field_activity.validate",
        "on_update": "sfa_core.doc_events.field_activity.on_update",
    },
    "SFA Beat Plan Amendment Request": {
        "validate": "sfa_core.doc_events.amendment.validate",
        "on_update": "sfa_core.doc_events.amendment.on_update",
    },
}

scheduler_events = {
    "daily": [
        "sfa_core.utils.scheduler.daily_end_of_day",
        "sfa_core.utils.scheduler.daily_share_threshold",
    ],
    "hourly": [
        "sfa_core.utils.scheduler.hourly_compliance",
    ],
    "cron": {
        "*/5 * * * *": [
            "sfa_core.utils.scheduler.five_minute_gps",
        ],
        "0 2 * * *": [
            "sfa_core.utils.scheduler.nightly_badge",
        ],
        "0 7 * * *": [
            "sfa_core.utils.scheduler.morning_beat",
        ],
    },
}

fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "SFA Core"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "SFA Core"]]},
    {"dt": "Workspace", "filters": [["module", "=", "SFA Core"]]},
    {"dt": "SFA Points Config"},
    {"dt": "SFA Badge"},
]
