import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    create_custom_fields({
        "Sales Order": [
            {"fieldname": "custom_sfa_confirmed_on", "label": "Confirmed On", "fieldtype": "Datetime",
             "insert_after": "custom_sfa_order_type", "read_only": 1, "allow_on_submit": 1},
            {"fieldname": "custom_sfa_confirmed_by", "label": "Confirmed By", "fieldtype": "Link",
             "options": "User", "insert_after": "custom_sfa_confirmed_on", "read_only": 1, "allow_on_submit": 1},
        ]
    }, ignore_validate=True)
    frappe.db.commit()
