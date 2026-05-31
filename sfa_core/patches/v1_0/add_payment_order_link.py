import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    create_custom_fields({
        "SFA Payment": [
            {"fieldname": "custom_sales_order", "label": "Against Order", "fieldtype": "Link",
             "options": "Sales Order", "insert_after": "visit"},
        ]
    }, ignore_validate=True)
    frappe.db.commit()
