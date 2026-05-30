import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    create_custom_fields({
        "SFA Payment": [
            {"fieldname": "custom_payment_mode", "label": "Payment Mode", "fieldtype": "Select",
             "options": "\nCash\nCartons", "default": "Cash", "insert_after": "payment_type",
             "in_list_view": 1,
             "description": "Cash = enter amount directly. Cartons = calculate from items \u00d7 rate."},
            {"fieldname": "custom_carton_section", "label": "Carton Details", "fieldtype": "Section Break",
             "insert_after": "custom_payment_mode",
             "depends_on": "eval:doc.custom_payment_mode == 'Cartons'"},
            {"fieldname": "custom_carton_items", "label": "Carton Items", "fieldtype": "Table",
             "options": "SFA Payment Carton Item", "insert_after": "custom_carton_section",
             "depends_on": "eval:doc.custom_payment_mode == 'Cartons'"},
            {"fieldname": "custom_carton_total", "label": "Carton Total", "fieldtype": "Currency",
             "insert_after": "custom_carton_items", "read_only": 1,
             "depends_on": "eval:doc.custom_payment_mode == 'Cartons'",
             "description": "Auto-calculated from carton items \u00d7 rate per carton"},
        ]
    }, ignore_validate=True)
    frappe.db.commit()
