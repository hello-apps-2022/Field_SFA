"""
Patch v1.0: Add the missing custom_mobile_no field to Customer.

Read by list.py and maps.py but never created — phone numbers had nowhere
to persist. Needed by the bulk outlet importer and the rep add-outlet flow.
Idempotent.
"""
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field


def execute():
	create_custom_field("Customer", {
		"fieldname": "custom_mobile_no",
		"label": "Mobile No",
		"fieldtype": "Data",
		"options": "Phone",
		"insert_after": "custom_last_visit_date",
		"description": "Outlet contact phone (SFA).",
	})
	frappe.db.commit()
