import frappe
from frappe import _

def after_install():
    """Post-install setup for SFA Core"""
    create_sfa_roles()
    frappe.db.commit()
    setup_sfa_module()
    setup_sfa_workspace()
    setup_custom_fields()
    frappe.db.commit()
    frappe.msgprint(_("SFA Core installed successfully."))

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
            "custom": 0
        })
        module.insert(ignore_permissions=True)
        frappe.db.commit()

def setup_sfa_workspace():
    """Create SFA Dashboard workspace"""
    if frappe.db.exists("Workspace", "SFA"):
        return
    
    # Ensure module exists before creating workspace
    if not frappe.db.exists("Module Def", "SFA Core"):
        setup_sfa_module()
    
    workspace = frappe.get_doc({
        "doctype": "Workspace",
        "name": "SFA",
        "label": "SFA",
        "title": "SFA",
        "icon": "dashboard",
        "module": "SFA Core",
        "for_user": "",
        "is_standard": 1,
        "public": 1,
        "charts": [],
        "shortcuts": [],
        "links": []
    })
    workspace.insert(ignore_permissions=True, ignore_links=True, ignore_mandatory=True)
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

def delete_sfa_pages():
    """Remove SFA pages on uninstall"""
    pages = ["sfa-dashboard", "sfa-visits", "sfa-form-templates"]
    for page in pages:
        if frappe.db.exists("Page", page):
            frappe.delete_doc("Page", page, ignore_permissions=True)

def remove_custom_fields():
    """Remove custom fields on uninstall"""
    fields = [
        ("Customer", "custom_sfa_status"),
        ("Customer", "custom_last_visit_date"),
        ("Customer", "custom_visit_frequency"),
        ("Territory", "custom_sfa_region"),
        ("Sales Order", "custom_sfa_visit"),
        ("Sales Order", "custom_sfa_rep"),
        ("Sales Order Item", "custom_carton_qty"),
        ("Sales Order Item", "custom_free_qty"),
        ("Sales Order Item", "custom_unpaid_qty"),
        ("Expense Claim", "custom_sfa_trip"),
    ]
    for dt, fieldname in fields:
        if frappe.db.exists("Custom Field", {"dt": dt, "fieldname": fieldname}):
            frappe.delete_doc("Custom Field", f"{dt}-{fieldname}", ignore_permissions=True)
