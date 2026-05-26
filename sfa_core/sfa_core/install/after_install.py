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
    """Create SFA Core workspace with shortcuts and document links"""
    workspace_name = "SFA Core"
    
    # Delete old workspace if exists with wrong name
    if frappe.db.exists("Workspace", "SFA"):
        frappe.delete_doc("Workspace", "SFA", force=1, ignore_permissions=True)
        frappe.db.commit()
    
    if frappe.db.exists("Workspace", workspace_name):
        return  # Already set up correctly

    # Build content blocks for Frappe v15 workspace renderer
    content = [
        {
            "type": "header",
            "data": {
                "text": "SFA Core",
                "level": 1
            }
        },
        {
            "type": "shortcut",
            "data": {
                "shortcuts": [
                    {
                        "type": "DocType",
                        "label": "Beat Plans",
                        "link_to": "SFA Beat Plan",
                        "color": "#D97706",
                        "icon": "calendar"
                    },
                    {
                        "type": "DocType",
                        "label": "SFA Payments",
                        "link_to": "SFA Payment",
                        "color": "#E11D48",
                        "icon": "currency"
                    },
                    {
                        "type": "DocType",
                        "label": "SFA Visits",
                        "link_to": "SFA Visit",
                        "color": "#2563EB",
                        "icon": "map-marker"
                    },
                    {
                        "type": "DocType",
                        "label": "Form Templates",
                        "link_to": "SFA Form Template",
                        "color": "#7C3AED",
                        "icon": "form"
                    }
                ]
            }
        },
        {
            "type": "card",
            "data": {
                "card_name": "Field Operations",
                "links": [
                    {"label": "SFA Visit", "type": "DocType", "name": "SFA Visit"},
                    {"label": "SFA Beat Plan", "type": "DocType", "name": "SFA Beat Plan"},
                    {"label": "SFA Payment", "type": "DocType", "name": "SFA Payment"},
                    {"label": "SFA Field Activity", "type": "DocType", "name": "SFA Field Activity"},
                ]
            }
        },
        {
            "type": "card",
            "data": {
                "card_name": "Customers",
                "links": [
                    {"label": "Customer", "type": "DocType", "name": "Customer"},
                    {"label": "SFA Saved Location", "type": "DocType", "name": "SFA Saved Location"},
                ]
            }
        },
        {
            "type": "card",
            "data": {
                "card_name": "Forms",
                "links": [
                    {"label": "SFA Form Template", "type": "DocType", "name": "SFA Form Template"},
                    {"label": "SFA Form Response", "type": "DocType", "name": "SFA Form Response"},
                ]
            }
        },
        {
            "type": "card",
            "data": {
                "card_name": "Gamification",
                "links": [
                    {"label": "SFA Points Config", "type": "DocType", "name": "SFA Points Config"},
                    {"label": "SFA Badge", "type": "DocType", "name": "SFA Badge"},
                    {"label": "SFA Rep Points Ledger", "type": "DocType", "name": "SFA Rep Points Ledger"},
                ]
            }
        },
        {
            "type": "card",
            "data": {
                "card_name": "Settings",
                "links": [
                    {"label": "SFA Target Period", "type": "DocType", "name": "SFA Target Period"},
                    {"label": "SFA SKU Points Multiplier", "type": "DocType", "name": "SFA SKU Points Multiplier"},
                ]
            }
        }
    ]

    ws = frappe.get_doc({
        "doctype": "Workspace",
        "name": workspace_name,
        "label": workspace_name,
        "title": workspace_name,
        "icon": "target",
        "module": "SFA Core",
        "is_standard": 1,
        "public": 1,
        "for_user": "",
        "sequence_id": 99,
        "content": frappe.as_json(content),
        "shortcuts": [
            {"type": "DocType", "label": "Beat Plans", "link_to": "SFA Beat Plan", "color": "#D97706"},
            {"type": "DocType", "label": "SFA Payments", "link_to": "SFA Payment", "color": "#E11D48"},
            {"type": "DocType", "label": "SFA Visits", "link_to": "SFA Visit", "color": "#2563EB"},
            {"type": "DocType", "label": "Form Templates", "link_to": "SFA Form Template", "color": "#7C3AED"},
        ],
        "links": [
            {"type": "Card Break", "label": "Field Operations", "is_query_report": 0},
            {"type": "Link", "label": "SFA Visit", "link_type": "DocType", "link_to": "SFA Visit", "is_query_report": 0},
            {"type": "Link", "label": "SFA Beat Plan", "link_type": "DocType", "link_to": "SFA Beat Plan", "is_query_report": 0},
            {"type": "Link", "label": "SFA Payment", "link_type": "DocType", "link_to": "SFA Payment", "is_query_report": 0},
            {"type": "Link", "label": "SFA Field Activity", "link_type": "DocType", "link_to": "SFA Field Activity", "is_query_report": 0},
            {"type": "Card Break", "label": "Customers", "is_query_report": 0},
            {"type": "Link", "label": "Customer", "link_type": "DocType", "link_to": "Customer", "is_query_report": 0},
            {"type": "Link", "label": "SFA Saved Location", "link_type": "DocType", "link_to": "SFA Saved Location", "is_query_report": 0},
            {"type": "Card Break", "label": "Forms", "is_query_report": 0},
            {"type": "Link", "label": "SFA Form Template", "link_type": "DocType", "link_to": "SFA Form Template", "is_query_report": 0},
            {"type": "Link", "label": "SFA Form Response", "link_type": "DocType", "link_to": "SFA Form Response", "is_query_report": 0},
            {"type": "Card Break", "label": "Gamification", "is_query_report": 0},
            {"type": "Link", "label": "SFA Points Config", "link_type": "DocType", "link_to": "SFA Points Config", "is_query_report": 0},
            {"type": "Link", "label": "SFA Badge", "link_type": "DocType", "link_to": "SFA Badge", "is_query_report": 0},
            {"type": "Link", "label": "SFA Rep Points Ledger", "link_type": "DocType", "link_to": "SFA Rep Points Ledger", "is_query_report": 0},
            {"type": "Card Break", "label": "Settings", "is_query_report": 0},
            {"type": "Link", "label": "SFA Target Period", "link_type": "DocType", "link_to": "SFA Target Period", "is_query_report": 0},
            {"type": "Link", "label": "SFA SKU Points Multiplier", "link_type": "DocType", "link_to": "SFA SKU Points Multiplier", "is_query_report": 0},
        ],
    })
    ws.insert(ignore_permissions=True)
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
