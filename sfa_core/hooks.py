app_name = "sfa_core"
app_title = "SFA Core"
app_publisher = "Hema Beverages"
app_description = "Sales Force Automation Platform for Hema Beverages"
app_email = "tech@hemabeverages.com"
app_license = "mit"
app_version = "0.0.1"




after_install = "sfa_core.field_sfa.install.after_install.after_install"
boot_session = "sfa_core.field_sfa.boot.boot_session"

# Redirect SFA users to the SFA app after login
on_session_creation = "sfa_core.api.auth.on_session_creation"

# Intercept /app requests and redirect SFA-only users to /sfa

doc_events = {
    "Customer": {
        "validate": "sfa_core.field_sfa.doc_events.customer.validate",
        "after_insert": "sfa_core.field_sfa.doc_events.customer.after_insert",
    },
    "Sales Order": {
        "validate": "sfa_core.field_sfa.doc_events.sales_order.validate",
        "on_submit": "sfa_core.field_sfa.doc_events.sales_order.on_submit",
        "on_cancel": "sfa_core.field_sfa.doc_events.sales_order.on_cancel",
    },
    "SFA Visit": {
        "validate": "sfa_core.field_sfa.doc_events.visit.validate",
        "on_update": "sfa_core.field_sfa.doc_events.visit.on_update",
        "on_submit": "sfa_core.field_sfa.doc_events.visit.on_submit",
    },
    "SFA Payment": {
        "validate": "sfa_core.field_sfa.doc_events.payment.validate",
        "on_submit": "sfa_core.field_sfa.doc_events.payment.on_submit",
    },
    "SFA Form Response": {
        "validate": "sfa_core.field_sfa.doc_events.form_response.validate",
        "on_submit": "sfa_core.field_sfa.doc_events.form_response.on_submit",
    },
    "SFA Field Activity": {
        "validate": "sfa_core.field_sfa.doc_events.field_activity.validate",
        "on_update": "sfa_core.field_sfa.doc_events.field_activity.on_update",
    },
    "SFA Beat Plan Amendment Request": {
        "validate": "sfa_core.field_sfa.doc_events.amendment.validate",
        "on_update": "sfa_core.field_sfa.doc_events.amendment.on_update",
    },
}

scheduler_events = {
    "daily": [
        "sfa_core.field_sfa.utils.scheduler.daily_end_of_day",
    ],
}

fixtures = [
    {"doctype": "Role", "filters": [["role_name", "in", ["SFA Manager", "SFA Supervisor", "SFA Rep", "SFA Viewer"]]]},
]

# Redirect plain /login to /login?redirect-to=/sfa for SFA users
# (handled via sfa.py — guests hitting /sfa get sent to login with redirect param)

website_route_rules = [
    {"from_route": "/sfa/<path:app_path>", "to_route": "sfa"},
]
