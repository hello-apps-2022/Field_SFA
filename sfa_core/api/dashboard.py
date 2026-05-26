import frappe

@frappe.whitelist()
def get_active_reps():
    return frappe.db.get_all("User",
        filters={"enabled": 1},
        fields=["name", "full_name"],
        limit=10
    )

@frappe.whitelist()
def get_leaderboard():
    return []

@frappe.whitelist()
def get_visit_activities():
    return []
