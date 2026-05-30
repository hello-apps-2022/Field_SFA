import frappe


def execute():
    # SFA Supervisor already exists from install; ensure the helper role too.
    for role_name in ("SFA Supervisor", "SFA Field Helper"):
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({
                "doctype": "Role",
                "role_name": role_name,
                "desk_access": 0,
            }).insert(ignore_permissions=True)

    frappe.db.commit()
