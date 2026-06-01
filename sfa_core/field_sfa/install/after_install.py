import frappe
from frappe import _


def after_install():
    """Post-install setup for SFA Core"""
    setup_attendance_fields()
    setup_gps_capture_fields()
    setup_sync_fields()
    setup_lead_fields()
    setup_location_types()
    setup_security_defaults()
    create_sfa_roles()
    frappe.db.commit()
    setup_sfa_module()
    frappe.db.commit()
    setup_sfa_workspace()
    setup_custom_fields()
    frappe.db.commit()
    seed_customer_groups()
    frappe.db.commit()
    seed_brand_defaults()
    frappe.db.commit()
    seed_gamification_defaults()
    frappe.db.commit()
    frappe.msgprint(_("SFA Core installed successfully. Please run bench migrate if DocTypes are not visible."))


PRODUCT_DEFAULTS = {
    "product_name": "FieldPro",
    "login_tagline": "Know your field.",
    "primary_color": "#1A1A2E",
    "accent_color": "#378ADD",
    "logo_login": "/assets/sfa_core/images/fieldpro-logo.svg",
    "logo_navbar": "/assets/sfa_core/images/fieldpro-mark.svg",
    "favicon": "/assets/sfa_core/images/fieldpro-favicon.svg",
}


def seed_brand_defaults():
    """Seed the PRODUCT (FieldPro) brand defaults if unset, then sync to Frappe.

    Only fills blank fields, so a tenant's saved overrides (e.g. Hema's logo,
    loaded via fixture) are never clobbered. Idempotent — safe on every run.

    Skips gracefully if the DocType isn't synced/importable yet (e.g. during an
    early migrate pass) so it can never abort the migration."""
    if not frappe.db.exists("DocType", "SFA Brand Settings"):
        return
    try:
        from sfa_core.field_sfa.doctype.sfa_brand_settings.sfa_brand_settings import (
            sync_brand_to_frappe,
        )
    except Exception:
        # Controller not importable yet — defer to the next migrate/the patch.
        return

    bs = frappe.get_single("SFA Brand Settings")
    changed = False
    for key, val in PRODUCT_DEFAULTS.items():
        if not bs.get(key):
            bs.set(key, val)
            changed = True
    if changed:
        bs.save(ignore_permissions=True)  # on_update triggers sync_brand_to_frappe
    else:
        sync_brand_to_frappe()


def create_sfa_roles():
    """Create SFA-specific roles"""
    roles = [
        {"role_name": "SFA Manager", "desk_access": 1},
        {"role_name": "SFA Supervisor", "desk_access": 1},
        {"role_name": "SFA Rep", "desk_access": 0},
        {"role_name": "SFA Field Helper", "desk_access": 0},
        {"role_name": "SFA Viewer", "desk_access": 1},
    ]
    for role in roles:
        if not frappe.db.exists("Role", role["role_name"]):
            doc = frappe.get_doc({"doctype": "Role", **role})
            doc.insert(ignore_permissions=True)


def setup_sfa_module():
    """Create SFA Core module"""
    if not frappe.db.exists("Module Def", "SFA Core"):
        module = frappe.get_doc({
            "doctype": "Module Def",
            "module_name": "SFA Core",
            "app_name": "sfa_core",
            "custom": 0,
        })
        module.insert(ignore_permissions=True)
        frappe.db.commit()


def setup_sfa_workspace():
    """Create SFA workspace with shortcuts and document links"""
    if frappe.db.exists("Workspace", "SFA"):
        # Update existing workspace with proper content
        ws = frappe.get_doc("Workspace", "SFA")
    else:
        ws = frappe.new_doc("Workspace")
        ws.name = "SFA"

    ws.update({
        "label": "SFA",
        "title": "SFA",
        "icon": "target",
        "module": "SFA Core",
        "is_standard": 1,
        "public": 1,
        "for_user": "",
        "sequence_id": 99,
        "shortcuts": [
            {
                "type": "Page",
                "label": "SFA Dashboard",
                "link_to": "sfa-dashboard",
                "color": "#2563EB",
                "icon": "dashboard",
            },
            {
                "type": "Page",
                "label": "Visits",
                "link_to": "sfa-visits",
                "color": "#16A34A",
                "icon": "map-marker",
            },
            {
                "type": "Page",
                "label": "Form Templates",
                "link_to": "sfa-form-templates",
                "color": "#7C3AED",
                "icon": "form",
            },
            {
                "type": "DocType",
                "label": "Beat Plans",
                "link_to": "SFA Beat Plan",
                "color": "#D97706",
                "icon": "calendar",
            },
            {
                "type": "DocType",
                "label": "SFA Payments",
                "link_to": "SFA Payment",
                "color": "#E11D48",
                "icon": "currency",
            },
        ],
        "links": [
            {
                "type": "Card Break",
                "label": "Field Operations",
                "is_query_report": 0,
            },
            {
                "type": "Link",
                "label": "SFA Visit",
                "link_type": "DocType",
                "link_to": "SFA Visit",
                "is_query_report": 0,
            },
            {
                "type": "Link",
                "label": "SFA Beat Plan",
                "link_type": "DocType",
                "link_to": "SFA Beat Plan",
                "is_query_report": 0,
            },
            {
                "type": "Link",
                "label": "SFA Payment",
                "link_type": "DocType",
                "link_to": "SFA Payment",
                "is_query_report": 0,
            },
            {
                "type": "Link",
                "label": "SFA Field Activity",
                "link_type": "DocType",
                "link_to": "SFA Field Activity",
                "is_query_report": 0,
            },
            {
                "type": "Card Break",
                "label": "Customers & Territory",
                "is_query_report": 0,
            },
            {
                "type": "Link",
                "label": "Customer",
                "link_type": "DocType",
                "link_to": "Customer",
                "is_query_report": 0,
            },
            {
                "type": "Link",
                "label": "SFA Saved Location",
                "link_type": "DocType",
                "link_to": "SFA Saved Location",
                "is_query_report": 0,
            },
            {
                "type": "Card Break",
                "label": "Forms & Intelligence",
                "is_query_report": 0,
            },
            {
                "type": "Link",
                "label": "SFA Form Template",
                "link_type": "DocType",
                "link_to": "SFA Form Template",
                "is_query_report": 0,
            },
            {
                "type": "Link",
                "label": "SFA Form Response",
                "link_type": "DocType",
                "link_to": "SFA Form Response",
                "is_query_report": 0,
            },
            {
                "type": "Card Break",
                "label": "Gamification",
                "is_query_report": 0,
            },
            {
                "type": "Link",
                "label": "SFA Points Config",
                "link_type": "DocType",
                "link_to": "SFA Points Config",
                "is_query_report": 0,
            },
            {
                "type": "Link",
                "label": "SFA Badge",
                "link_type": "DocType",
                "link_to": "SFA Badge",
                "is_query_report": 0,
            },
            {
                "type": "Link",
                "label": "SFA Rep Points Ledger",
                "link_type": "DocType",
                "link_to": "SFA Rep Points Ledger",
                "is_query_report": 0,
            },
            {
                "type": "Card Break",
                "label": "Reports",
                "is_query_report": 0,
            },
            {
                "type": "Link",
                "label": "Visit Compliance",
                "link_type": "Report",
                "link_to": "visit_compliance",
                "is_query_report": 1,
            },
            {
                "type": "Link",
                "label": "Rep Productivity",
                "link_type": "Report",
                "link_to": "rep_productivity",
                "is_query_report": 1,
            },
            {
                "type": "Link",
                "label": "Sales Performance",
                "link_type": "Report",
                "link_to": "sales_performance",
                "is_query_report": 1,
            },
            {
                "type": "Link",
                "label": "Leaderboard",
                "link_type": "Report",
                "link_to": "leaderboard",
                "is_query_report": 1,
            },
            {
                "type": "Card Break",
                "label": "Settings",
                "is_query_report": 0,
            },
            {
                "type": "Link",
                "label": "SFA Target Period",
                "link_type": "DocType",
                "link_to": "SFA Target Period",
                "is_query_report": 0,
            },
            {
                "type": "Link",
                "label": "SFA SKU Points Multiplier",
                "link_type": "DocType",
                "link_to": "SFA SKU Points Multiplier",
                "is_query_report": 0,
            },
        ],
    })

    if ws.is_new():
        ws.insert(ignore_permissions=True)
    else:
        ws.save(ignore_permissions=True)

    frappe.db.commit()


def setup_custom_fields():
    """Ensure custom fields exist on standard doctypes"""
    from frappe.custom.doctype.custom_field.custom_field import create_custom_field

    fields = [
        {
            "dt": "Customer",
            "fieldname": "custom_sfa_status",
            "label": "SFA Status",
            "fieldtype": "Select",
            "options": "Active\nInactive\nProspect\nDormant",
            "insert_after": "customer_group",
        },
        {
            "dt": "Customer",
            "fieldname": "custom_last_visit_date",
            "label": "Last Visit Date",
            "fieldtype": "Date",
            "insert_after": "custom_sfa_status",
            "read_only": 1,
        },
        {
            "dt": "Customer",
            "fieldname": "custom_mobile_no",
            "label": "Mobile No",
            "fieldtype": "Data",
            "options": "Phone",
            "insert_after": "custom_last_visit_date",
            "description": "Outlet contact phone (SFA).",
        },
        {
            "dt": "Sales Order",
            "fieldname": "custom_sfa_visit",
            "label": "Linked SFA Visit",
            "fieldtype": "Link",
            "options": "SFA Visit",
            "insert_after": "customer",
        },
        {
            "dt": "Sales Order",
            "fieldname": "custom_sfa_rep",
            "label": "SFA Rep",
            "fieldtype": "Link",
            "options": "Sales Person",
            "insert_after": "custom_sfa_visit",
            "description": "Sales Person (rep) who placed this order via SFA.",
        },
        {
            "dt": "Sales Order Item",
            "fieldname": "custom_carton_qty",
            "label": "Carton Qty",
            "fieldtype": "Float",
            "insert_after": "qty",
            "description": "Paid carton quantity (SFA free-carton pricing model).",
        },
        {
            "dt": "Sales Order Item",
            "fieldname": "custom_free_qty",
            "label": "Free Qty",
            "fieldtype": "Float",
            "insert_after": "custom_carton_qty",
            "description": "Free carton quantity (margin embedded as free stock).",
        },
        {
            "dt": "Sales Order Item",
            "fieldname": "custom_unpaid_qty",
            "label": "Unpaid Qty",
            "fieldtype": "Float",
            "insert_after": "custom_free_qty",
            "description": "Unpaid/credit carton quantity.",
        },
        {
            "dt": "Item",
            "fieldname": "custom_sfa_company",
            "label": "SFA Company",
            "fieldtype": "Link",
            "options": "SFA Company",
            "insert_after": "item_group",
        },
        {
            "dt": "Item",
            "fieldname": "custom_size",
            "label": "Size",
            "fieldtype": "Data",
            "insert_after": "custom_sfa_company",
        },
        {
            "dt": "Item",
            "fieldname": "custom_packaging",
            "label": "Packaging",
            "fieldtype": "Data",
            "insert_after": "custom_size",
        },
        {
            "dt": "Item",
            "fieldname": "custom_pack_config",
            "label": "Pack Config",
            "fieldtype": "Data",
            "insert_after": "custom_packaging",
        },
        {
            "dt": "Sales Person",
            "fieldname": "custom_sfa_companies",
            "label": "SFA Companies",
            "fieldtype": "Table",
            "options": "SFA Sales Person Company",
            "insert_after": "custom_territory",
        },
        {
            "dt": "User",
            "fieldname": "custom_can_export_reports",
            "label": "Can Export SFA Reports",
            "fieldtype": "Check",
            "insert_after": "username",
            "default": 0,
            "description": "Allow this user to download/export SFA reports (CSV/Excel). Admins can always export.",
        },
        {
            "dt": "Sales Order",
            "fieldname": "custom_sfa_order_type",
            "label": "Order Type",
            "fieldtype": "Select",
            "options": "Booking\nVan Sale",
            "default": "Booking",
            "insert_after": "custom_sfa_rep",
        },
        {
            "dt": "Sales Order",
            "fieldname": "custom_sfa_delivery_status",
            "label": "Delivery Status",
            "fieldtype": "Select",
            "options": "Pending\nDelivered",
            "default": "Pending",
            "insert_after": "custom_sfa_order_type",
            "read_only": 1,
            "allow_on_submit": 1,
        },
        {
            "dt": "Sales Order",
            "fieldname": "custom_sfa_delivered_on",
            "label": "Delivered On",
            "fieldtype": "Datetime",
            "insert_after": "custom_sfa_delivery_status",
            "read_only": 1,
            "allow_on_submit": 1,
        },
        {
            "dt": "Sales Order",
            "fieldname": "custom_sfa_delivered_by",
            "label": "Delivered By",
            "fieldtype": "Link",
            "options": "User",
            "insert_after": "custom_sfa_delivered_on",
            "read_only": 1,
            "allow_on_submit": 1,
        },
        {
            "dt": "Item Group",
            "fieldname": "custom_sfa_enabled",
            "label": "Enabled for SFA",
            "fieldtype": "Check",
            "default": "1",
            "insert_after": "is_group",
        },
        {
            "dt": "Sales Order",
            "fieldname": "custom_sfa_confirmed_on",
            "label": "Confirmed On",
            "fieldtype": "Datetime",
            "insert_after": "custom_sfa_order_type",
            "read_only": 1,
            "allow_on_submit": 1,
        },
        {
            "dt": "Sales Order",
            "fieldname": "custom_sfa_confirmed_by",
            "label": "Confirmed By",
            "fieldtype": "Link",
            "options": "User",
            "insert_after": "custom_sfa_confirmed_on",
            "read_only": 1,
            "allow_on_submit": 1,
        },
        {
            "dt": "SFA Payment",
            "fieldname": "custom_payment_mode",
            "label": "Payment Mode",
            "fieldtype": "Select",
            "options": "\nCash\nCartons",
            "default": "Cash",
            "insert_after": "payment_type",
            "in_list_view": 1,
            "description": "Cash = enter amount directly. Cartons = calculate from items \u00d7 rate.",
        },
        {
            "dt": "SFA Payment",
            "fieldname": "custom_carton_section",
            "label": "Carton Details",
            "fieldtype": "Section Break",
            "insert_after": "custom_payment_mode",
            "depends_on": "eval:doc.custom_payment_mode == 'Cartons'",
        },
        {
            "dt": "SFA Payment",
            "fieldname": "custom_carton_items",
            "label": "Carton Items",
            "fieldtype": "Table",
            "options": "SFA Payment Carton Item",
            "insert_after": "custom_carton_section",
            "depends_on": "eval:doc.custom_payment_mode == 'Cartons'",
        },
        {
            "dt": "SFA Payment",
            "fieldname": "custom_carton_total",
            "label": "Carton Total",
            "fieldtype": "Currency",
            "insert_after": "custom_carton_items",
            "read_only": 1,
            "depends_on": "eval:doc.custom_payment_mode == 'Cartons'",
            "description": "Auto-calculated from carton items \u00d7 rate per carton",
        },
        {
            "dt": "SFA Payment",
            "fieldname": "custom_sales_order",
            "label": "Against Order",
            "fieldtype": "Link",
            "options": "Sales Order",
            "insert_after": "visit",
        },
    ]

    for field in fields:
        try:
            dt = field.pop("dt")
            create_custom_field(dt, field)
        except Exception as e:
            frappe.log_error(f"SFA Core: Failed to create custom field {field.get('fieldname')}: {str(e)}")


# Canonical SFA outlet-type taxonomy (leaf Customer Groups under the root).
SFA_CUSTOMER_GROUPS = [
    "Distributor",
    "Dealer",
    "Sub-Dealer",
    "Wholesaler / Stockist",
    "Retailer",
    "Kiosk / Duka",
    "Convenience Store",
    "Supermarket",
    "Bar / Club",
    "Restaurant / Café",
    "Hotel / Lodge",
    "Petrol Forecourt",
    "Hospital / Clinic",
    "School / Campus",
    "Government / NGO",
]


def seed_customer_groups():
    """Create the SFA outlet-type Customer Groups as leaf nodes under the root.
    Idempotent — skips any that already exist."""
    root = frappe.db.get_value("Customer Group", {"is_group": 1, "parent_customer_group": ""}, "name") \
        or "All Customer Groups"
    for name in SFA_CUSTOMER_GROUPS:
        if frappe.db.exists("Customer Group", name):
            continue
        try:
            doc = frappe.new_doc("Customer Group")
            doc.customer_group_name = name
            doc.parent_customer_group = root
            doc.is_group = 0
            doc.insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"SFA Core: failed to create Customer Group {name}: {e}")


# --- Gamification defaults ---------------------------------------------------

# Default points per activity. Read by the award engine via SFA Points Config;
# these rows make the system work out-of-the-box and are editable in-app.
SFA_POINTS_CONFIG = [
    {"activity_type": "Visit Complete",      "points": 10, "multiplier_field": "None",          "description": "Points per completed visit"},
    {"activity_type": "Order Placed",        "points": 20, "multiplier_field": "Carton Qty",    "description": "Points per carton ordered (x SKU multiplier)"},
    {"activity_type": "Payment Collected",   "points": 15, "multiplier_field": "Payment Amount", "description": "Points per UGX 100,000 collected"},
    {"activity_type": "Form Submitted",      "points": 5,  "multiplier_field": "None",          "description": "Points per form submitted"},
    {"activity_type": "Beat Plan Completed", "points": 25, "multiplier_field": "None",          "description": "Points for completing a full beat plan"},
    {"activity_type": "GPS Track Uploaded",  "points": 5,  "multiplier_field": "None",          "description": "Points for uploading a GPS track"},
]

# Default badge set spanning the available criteria types.
SFA_BADGES = [
    {"badge_name": "First Steps",       "criteria_type": "Visit Count",      "threshold_value": 10,      "period_days": 0,  "points_bonus": 50,  "icon": "award",  "description": "Complete 10 visits"},
    {"badge_name": "Road Warrior",      "criteria_type": "Visit Count",      "threshold_value": 100,     "period_days": 30, "points_bonus": 200, "icon": "truck",  "description": "100 visits in 30 days"},
    {"badge_name": "Deal Maker",        "criteria_type": "Order Value",      "threshold_value": 5000000, "period_days": 30, "points_bonus": 300, "icon": "trending-up", "description": "UGX 5M in orders in 30 days"},
    {"badge_name": "Closer",            "criteria_type": "Order Value",      "threshold_value": 20000000,"period_days": 30, "points_bonus": 750, "icon": "star",   "description": "UGX 20M in orders in 30 days"},
    {"badge_name": "Cash Collector",    "criteria_type": "Payment Amount",   "threshold_value": 3000000, "period_days": 30, "points_bonus": 250, "icon": "dollar-sign", "description": "UGX 3M collected in 30 days"},
    {"badge_name": "Century Club",      "criteria_type": "Points Threshold", "threshold_value": 1000,    "period_days": 0,  "points_bonus": 100, "icon": "zap",    "description": "Earn 1,000 lifetime points"},
    {"badge_name": "Elite Performer",   "criteria_type": "Points Threshold", "threshold_value": 5000,    "period_days": 0,  "points_bonus": 500, "icon": "shield", "description": "Earn 5,000 lifetime points"},
]


def seed_gamification_defaults():
    """Seed SFA Points Config rows and default Badges. Idempotent — skips existing."""
    for cfg in SFA_POINTS_CONFIG:
        if frappe.db.exists("SFA Points Config", cfg["activity_type"]):
            continue
        try:
            doc = frappe.new_doc("SFA Points Config")
            doc.update(cfg)
            doc.is_active = 1
            doc.insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"SFA Core: failed to seed points config {cfg['activity_type']}: {e}")

    for badge in SFA_BADGES:
        if frappe.db.exists("SFA Badge", badge["badge_name"]):
            continue
        try:
            doc = frappe.new_doc("SFA Badge")
            doc.update(badge)
            doc.is_active = 1
            doc.insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"SFA Core: failed to seed badge {badge['badge_name']}: {e}")


SECURITY_DEFAULTS = {
    "session_expiry": "336:00:00",        # 14-day sliding idle window
    "deny_multiple_sessions": 1,          # one active session per user
    "logout_on_password_reset": 1,        # a reset logs out all sessions
    "disable_user_pass_login": 0,         # keep email/password login on
}


DEFAULT_LOCATION_TYPES = [
    ("Customer", "A customer / outlet location"),
    ("Warehouse", "A storage or distribution point"),
    ("Office", "A company office"),
    ("Competitor", "A competitor outlet"),
    ("Other", "Any other saved place"),
]


def setup_location_types():
    """Seed the configurable saved-location type list. Idempotent."""
    for option_name, description in DEFAULT_LOCATION_TYPES:
        if not frappe.db.exists("SFA Location Type", option_name):
            frappe.get_doc({
                "doctype": "SFA Location Type",
                "option_name": option_name,
                "description": description,
                "is_active": 1,
            }).insert(ignore_permissions=True)


LEAD_FIELDS = {
    "Lead": [
        {"fieldname": "custom_sfa_rep", "label": "SFA Rep", "fieldtype": "Link", "options": "Sales Person", "insert_after": "territory"},
        {"fieldname": "custom_sfa_status", "label": "SFA Status", "fieldtype": "Select", "options": "New\nContacted\nQualified\nConverted\nDropped", "default": "New", "insert_after": "custom_sfa_rep"},
        {"fieldname": "custom_sfa_latitude", "label": "Capture Latitude", "fieldtype": "Float", "precision": "6", "insert_after": "custom_sfa_status", "read_only": 1},
        {"fieldname": "custom_sfa_longitude", "label": "Capture Longitude", "fieldtype": "Float", "precision": "6", "insert_after": "custom_sfa_latitude", "read_only": 1},
        {"fieldname": "custom_sfa_gps_accuracy", "label": "Capture GPS Accuracy (m)", "fieldtype": "Float", "insert_after": "custom_sfa_longitude", "read_only": 1},
        {"fieldname": "custom_sfa_captured_at", "label": "Captured At", "fieldtype": "Datetime", "insert_after": "custom_sfa_gps_accuracy", "read_only": 1},
        {"fieldname": "custom_client_uuid", "label": "Client UUID", "fieldtype": "Data", "read_only": 1, "no_copy": 1, "search_index": 1, "insert_after": "custom_sfa_captured_at"},
    ],
}


def setup_lead_fields():
    """SFA fields on the ERPNext Lead: assigned rep, SFA lifecycle status,
    GPS capture quad, and the offline-sync client uuid. Idempotent."""
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
    create_custom_fields(LEAD_FIELDS, ignore_validate=True)
    frappe.db.commit()


def setup_security_defaults():
    """Apply Field SFA session-security System Settings.

    Baked into install so every new tenant site gets the same security posture
    without manual DB edits. Idempotent — safe to run on every install/migrate.
    """
    for field, value in SECURITY_DEFAULTS.items():
        frappe.db.set_single_value("System Settings", field, value)
    frappe.db.commit()


GPS_CAPTURE_FIELDS = {
    "Sales Order": [
        {"fieldname": "custom_sfa_latitude", "label": "Capture Latitude", "fieldtype": "Float", "precision": "6", "insert_after": "custom_sfa_rep", "read_only": 1},
        {"fieldname": "custom_sfa_longitude", "label": "Capture Longitude", "fieldtype": "Float", "precision": "6", "insert_after": "custom_sfa_latitude", "read_only": 1},
        {"fieldname": "custom_sfa_gps_accuracy", "label": "Capture GPS Accuracy (m)", "fieldtype": "Float", "insert_after": "custom_sfa_longitude", "read_only": 1},
        {"fieldname": "custom_sfa_captured_at", "label": "Captured At", "fieldtype": "Datetime", "insert_after": "custom_sfa_gps_accuracy", "read_only": 1},
    ],
    "SFA Payment": [
        {"fieldname": "custom_sfa_latitude", "label": "Capture Latitude", "fieldtype": "Float", "precision": "6", "insert_after": "sales_person", "read_only": 1},
        {"fieldname": "custom_sfa_longitude", "label": "Capture Longitude", "fieldtype": "Float", "precision": "6", "insert_after": "custom_sfa_latitude", "read_only": 1},
        {"fieldname": "custom_sfa_gps_accuracy", "label": "Capture GPS Accuracy (m)", "fieldtype": "Float", "insert_after": "custom_sfa_longitude", "read_only": 1},
        {"fieldname": "custom_sfa_captured_at", "label": "Captured At", "fieldtype": "Datetime", "insert_after": "custom_sfa_gps_accuracy", "read_only": 1},
    ],
    "Customer": [
        {"fieldname": "custom_sfa_gps_accuracy", "label": "Capture GPS Accuracy (m)", "fieldtype": "Float", "insert_after": "custom_longitude", "read_only": 1},
        {"fieldname": "custom_sfa_captured_at", "label": "Captured At", "fieldtype": "Datetime", "insert_after": "custom_sfa_gps_accuracy", "read_only": 1},
    ],
    "SFA Form Response": [
        {"fieldname": "custom_sfa_gps_accuracy", "label": "Capture GPS Accuracy (m)", "fieldtype": "Float", "insert_after": "longitude", "read_only": 1},
        {"fieldname": "custom_sfa_captured_at", "label": "Captured At", "fieldtype": "Datetime", "insert_after": "custom_sfa_gps_accuracy", "read_only": 1},
    ],
}


def setup_gps_capture_fields():
    """Capture-GPS custom fields on the records reps create in the field
    (where/when each capture happened). Baked into install so new tenant sites
    get them; a patch applies them to existing sites. Idempotent."""
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
    create_custom_fields(GPS_CAPTURE_FIELDS, ignore_validate=True)
    frappe.db.commit()


ATTENDANCE_FIELDS = {
    "Employee Checkin": [
        {"fieldname": "custom_sfa_day_priorities", "label": "Day Priorities", "fieldtype": "Small Text", "insert_after": "device_id"},
        {"fieldname": "custom_sfa_day_focus", "label": "Day Focus Areas", "fieldtype": "Small Text", "insert_after": "custom_sfa_day_priorities"},
    ],
}


def setup_attendance_fields():
    """Custom field for the rep's top priorities captured at day-start."""
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
    create_custom_fields(ATTENDANCE_FIELDS, ignore_validate=True)
    frappe.db.commit()


SYNC_FIELDS = {
    "SFA Visit":           [{"fieldname": "custom_client_uuid", "label": "Client UUID", "fieldtype": "Data", "read_only": 1, "no_copy": 1, "search_index": 1}],
    "Sales Order":         [{"fieldname": "custom_client_uuid", "label": "Client UUID", "fieldtype": "Data", "read_only": 1, "no_copy": 1, "search_index": 1}],
    "SFA Payment":         [{"fieldname": "custom_client_uuid", "label": "Client UUID", "fieldtype": "Data", "read_only": 1, "no_copy": 1, "search_index": 1}],
    "SFA Form Response":   [{"fieldname": "custom_client_uuid", "label": "Client UUID", "fieldtype": "Data", "read_only": 1, "no_copy": 1, "search_index": 1}],
    "SFA GPS Track Point": [{"fieldname": "custom_client_uuid", "label": "Client UUID", "fieldtype": "Data", "read_only": 1, "no_copy": 1, "search_index": 1}],
}


def setup_sync_fields():
    """Client UUID on each device-pushable DocType so offline sync upserts are
    idempotent (push looks records up by it). Baked into install; a patch applies
    it to existing sites. Idempotent."""
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
    create_custom_fields(SYNC_FIELDS, ignore_validate=True)
    frappe.db.commit()
