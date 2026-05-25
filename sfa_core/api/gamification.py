import frappe
from frappe import _

@frappe.whitelist()
def get_leaderboard(period=None, limit=50):
    """Get points leaderboard"""
    from frappe.utils import getdate, add_months

    filters = {}
    if period:
        start_date = add_months(getdate(), -1) if period == "month" else add_months(getdate(), -3)
        filters["timestamp"] = [">=", start_date]

    leaderboard = frappe.db.sql("""
        SELECT 
            sales_person,
            SUM(points) as total_points,
            COUNT(DISTINCT reference_name) as activities
        FROM `tabSFA Rep Points Ledger`
        WHERE 1=1 {condition}
        GROUP BY sales_person
        ORDER BY total_points DESC
        LIMIT %s
    """.format(condition="AND timestamp >= %(start_date)s" if period else ""),
    {"start_date": start_date if period else None, "limit": limit}, as_dict=True)

    return leaderboard

@frappe.whitelist()
def get_rep_badges(sales_person):
    """Get badges for a sales person"""
    badges = frappe.get_all("SFA Rep Badge",
        filters={"sales_person": sales_person},
        fields=["name", "badge", "awarded_date", "awarded_by"],
        order_by="awarded_date desc")

    return badges

@frappe.whitelist()
def get_rep_points(sales_person):
    """Get total points for a sales person"""
    total = frappe.db.get_value("SFA Rep Points Ledger",
        {"sales_person": sales_person}, "SUM(points)") or 0

    return {"sales_person": sales_person, "total_points": total}
