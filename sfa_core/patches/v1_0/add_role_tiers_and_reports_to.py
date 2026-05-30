import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    # SFA Supervisor already exists from install; ensure the helper role too.
    for role_name in ("SFA Supervisor", "SFA Field Helper"):
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({
                "doctype": "Role",
                "role_name": role_name,
                "desk_access": 0,
            }).insert(ignore_permissions=True)

    # "Reports to" link on Sales Person — drives the helper -> rep -> supervisor
    # roll-up. For a field helper/driver this points at the rep they work under.
    create_custom_fields({
        "Sales Person": [
            {
                "fieldname": "custom_sfa_reports_to",
                "label": "SFA Reports To",
                "fieldtype": "Link",
                "options": "Sales Person",
                "insert_after": "custom_territory",
                "description": "For a field helper/driver: the rep they work under. "
                               "Their activity rolls up to that rep.",
            },
        ]
    }, ignore_validate=True)
    frappe.db.commit()
