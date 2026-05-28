"""
Patch v1.0: Add the missing custom_sfa_rep field to Sales Order.

This field is referenced throughout the app (reports, order API, doc_events,
targets, maps, gamification) but was never created — causing 'Unknown column
custom_sfa_rep' errors. This creates it on existing sites.

Also backfills custom_sfa_rep on existing SFA-linked orders from their linked
visit's sales_person, so historical orders get rep attribution.
"""
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field


def execute():
	create_custom_field("Sales Order", {
		"fieldname": "custom_sfa_rep",
		"label": "SFA Rep",
		"fieldtype": "Link",
		"options": "Sales Person",
		"insert_after": "custom_sfa_visit",
		"description": "Sales Person (rep) who placed this order via SFA.",
	})
	frappe.db.commit()

	# Backfill from linked visit's sales_person where possible.
	frappe.db.sql("""
		UPDATE `tabSales Order` so
		JOIN `tabSFA Visit` v ON v.name = so.custom_sfa_visit
		SET so.custom_sfa_rep = v.sales_person
		WHERE so.custom_sfa_visit IS NOT NULL
		  AND (so.custom_sfa_rep IS NULL OR so.custom_sfa_rep = '')
		  AND v.sales_person IS NOT NULL
	""")
	frappe.db.commit()
