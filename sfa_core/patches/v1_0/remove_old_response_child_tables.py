"""
Patch v1.0: Remove old typed response child tables.
They are replaced by the unified SFA Response Item table.
"""
import frappe


def execute():
    old_tables = [
        "tabSFA Response Boolean",
        "tabSFA Response File",
        "tabSFA Response Number",
        "tabSFA Response Option",
        "tabSFA Response Text",
    ]
    for table in old_tables:
        if frappe.db.table_exists(table):
            frappe.db.sql(f"DROP TABLE IF EXISTS `{table}`")
            frappe.db.commit()

    # Also remove the DocType records from the database if they exist
    old_doctypes = [
        "SFA Response Boolean",
        "SFA Response File",
        "SFA Response Number",
        "SFA Response Option",
        "SFA Response Text",
    ]
    for dt in old_doctypes:
        if frappe.db.exists("DocType", dt):
            frappe.delete_doc("DocType", dt, ignore_permissions=True, force=True)
