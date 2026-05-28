"""
Patch v1.0: Add the per-user 'can export reports' flag to User.

Runs on existing sites since setup_custom_fields only fires on fresh install.
Idempotent — create_custom_field is a no-op if the field already exists.
"""
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field


def execute():
	create_custom_field("User", {
		"fieldname": "custom_can_export_reports",
		"label": "Can Export SFA Reports",
		"fieldtype": "Check",
		"insert_after": "username",
		"default": 0,
		"description": "Allow this user to download/export SFA reports (CSV/Excel). Admins can always export.",
	})
	frappe.db.commit()
