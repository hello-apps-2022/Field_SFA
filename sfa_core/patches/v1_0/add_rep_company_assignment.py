import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    frappe.reload_doc("field_sfa", "doctype", "sfa_sales_person_company")
    create_custom_fields({
        "Sales Person": [
            {
                "fieldname": "custom_sfa_companies",
                "label": "SFA Companies",
                "fieldtype": "Table",
                "options": "SFA Sales Person Company",
                "insert_after": "custom_territory",
                "description": "Companies whose products this rep can sell. Empty = all.",
            },
        ]
    }, ignore_validate=True)
    frappe.db.commit()
