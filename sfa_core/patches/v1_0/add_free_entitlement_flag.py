import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    """Read-only flag set by Sales Order validate when free cartons given exceed
    the active free-carton scheme entitlement. Surfaced in reporting (allowed,
    not blocked)."""
    create_custom_fields({
        "Sales Order": [
            {
                "fieldname": "custom_free_beyond_entitlement",
                "label": "Free Beyond Entitlement",
                "fieldtype": "Check",
                "insert_after": "custom_sfa_rep",
                "read_only": 1,
                "in_standard_filter": 1,
                "description": "Set when free cartons given exceed the active free-carton scheme entitlement.",
            },
        ]
    }, ignore_validate=True)
    frappe.db.commit()
