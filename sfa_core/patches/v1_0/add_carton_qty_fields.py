"""
Patch v1.0: Add missing carton-quantity custom fields to Sales Order Item.

custom_carton_qty / custom_free_qty / custom_unpaid_qty are written by the
order API and validated by doc_events, and underpin the free-carton pricing
model — but were never created, causing 'Unknown column' errors (e.g. in the
Sales Performance report). Creates them on existing sites. Idempotent.
"""
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

FIELDS = [
	{"fieldname": "custom_carton_qty", "label": "Carton Qty", "fieldtype": "Float",
	 "insert_after": "qty", "description": "Paid carton quantity (SFA free-carton pricing model)."},
	{"fieldname": "custom_free_qty", "label": "Free Qty", "fieldtype": "Float",
	 "insert_after": "custom_carton_qty", "description": "Free carton quantity (margin embedded as free stock)."},
	{"fieldname": "custom_unpaid_qty", "label": "Unpaid Qty", "fieldtype": "Float",
	 "insert_after": "custom_free_qty", "description": "Unpaid/credit carton quantity."},
]


def execute():
	for f in FIELDS:
		create_custom_field("Sales Order Item", f)
	frappe.db.commit()
