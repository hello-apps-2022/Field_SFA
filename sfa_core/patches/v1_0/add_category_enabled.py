import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    create_custom_fields({
        "Item Group": [
            {"fieldname": "custom_sfa_enabled", "label": "Enabled for SFA",
             "fieldtype": "Check", "default": "1", "insert_after": "is_group"},
        ]
    }, ignore_validate=True)
    frappe.db.sql("update `tabItem Group` set custom_sfa_enabled = 1")
    frappe.db.commit()
