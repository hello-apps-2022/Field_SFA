import frappe
from frappe import _


def after_install():
    """Post-install setup for SFA Core"""
    create_sfa_roles()
    frappe.db.commit()
    setup_sfa_module()
    frappe.db.commit()
    setup_sfa_workspace()
    setup_custom_fields()
    frappe.db.commit()
    frappe.msgprint(_("SFA Core installed successfully. Please run bench migrate if DocTypes are not visible."))


def create_sfa_roles():
    """Create SFA-specific roles"""
    roles = [
        {"role_name": "SFA Manager", "desk_access": 1},
        {"role_name": "SFA Supervisor", "desk_access": 1},
        {"role_name": "SFA Rep", "desk_access": 0},
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
            "dt": "Sales Order",
            "fieldname": "custom_sfa_visit",
            "label": "Linked SFA Visit",
            "fieldtype": "Link",
            "options": "SFA Visit",
            "insert_after": "customer",
        },
    ]

    for field in fields:
        try:
            dt = field.pop("dt")
            create_custom_field(dt, field)
        except Exception as e:
            frappe.log_error(f"SFA Core: Failed to create custom field {field.get('fieldname')}: {str(e)}")
