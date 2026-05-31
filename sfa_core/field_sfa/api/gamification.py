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

    if period:
        leaderboard = frappe.db.sql("""
            SELECT 
                sales_person,
                SUM(points) as total_points,
                COUNT(DISTINCT reference_name) as activities
            FROM `tabSFA Rep Points Ledger`
            WHERE timestamp >= %s
            GROUP BY sales_person
            ORDER BY total_points DESC
            LIMIT %s
        """, (start_date, limit), as_dict=True)
    else:
        leaderboard = frappe.db.sql("""
            SELECT 
                sales_person,
                SUM(points) as total_points,
                COUNT(DISTINCT reference_name) as activities
            FROM `tabSFA Rep Points Ledger`
            GROUP BY sales_person
            ORDER BY total_points DESC
            LIMIT %s
        """, (limit,), as_dict=True)

    return leaderboard

@frappe.whitelist()
def get_rep_badges(sales_person):
    """Get badges for a sales person"""
    from sfa_core.api.auth import resolve_sales_person
    sales_person = resolve_sales_person(sales_person)
    badges = frappe.get_all("SFA Rep Badge",
        filters={"sales_person": sales_person},
        fields=["name", "badge", "awarded_date", "awarded_by"],
        order_by="awarded_date desc")

    return badges

@frappe.whitelist()
def get_rep_points(sales_person):
    """Get total points for a sales person"""
    from sfa_core.api.auth import resolve_sales_person
    sales_person = resolve_sales_person(sales_person)
    result = frappe.db.sql(
        "SELECT SUM(points) FROM `tabSFA Rep Points Ledger` WHERE sales_person = %s",
        (sales_person,)
    )
    total = result[0][0] or 0

    return {"sales_person": sales_person, "total_points": total}
