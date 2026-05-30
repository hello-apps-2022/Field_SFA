import frappe


def execute():
    frappe.delete_doc("Custom Field", "Sales Person-custom_sfa_reports_to",
                      ignore_missing=True, force=True)
    frappe.db.commit()
