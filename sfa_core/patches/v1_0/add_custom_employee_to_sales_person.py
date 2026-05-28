"""
Stage 2a — add custom_employee link field on Sales Person.

Guarded with has_column per the §6 lesson (verify custom fields exist before use).
Registered as: sfa_core.patches.v1_0.add_custom_employee_to_sales_person
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field


def execute():
    if frappe.db.has_column("Sales Person", "custom_employee"):
        return
    create_custom_field("Sales Person", {
        "fieldname": "custom_employee",
        "label": "Employee (HR)",
        "fieldtype": "Link",
        "options": "Employee",
        "insert_after": "custom_territory",
        "read_only": 1,            # set by the provisioning hook, not by hand
        "no_copy": 1,
        "description": "Auto-linked HR Employee record. Managed by FieldPro provisioning; "
                       "do not edit manually.",
    })
    frappe.clear_cache(doctype="Sales Person")
