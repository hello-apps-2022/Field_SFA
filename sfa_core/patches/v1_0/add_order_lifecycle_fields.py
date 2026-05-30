import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    create_custom_fields({
        "Sales Order": [
            {"fieldname": "custom_sfa_order_type", "label": "Order Type", "fieldtype": "Select",
             "options": "Booking\nVan Sale", "default": "Booking", "insert_after": "custom_sfa_rep"},
            {"fieldname": "custom_sfa_delivery_status", "label": "Delivery Status", "fieldtype": "Select",
             "options": "Pending\nDelivered", "default": "Pending", "insert_after": "custom_sfa_order_type",
             "read_only": 1, "allow_on_submit": 1},
            {"fieldname": "custom_sfa_delivered_on", "label": "Delivered On", "fieldtype": "Datetime",
             "insert_after": "custom_sfa_delivery_status", "read_only": 1, "allow_on_submit": 1},
            {"fieldname": "custom_sfa_delivered_by", "label": "Delivered By", "fieldtype": "Link",
             "options": "User", "insert_after": "custom_sfa_delivered_on", "read_only": 1, "allow_on_submit": 1},
        ]
    }, ignore_validate=True)
    frappe.db.commit()
