import frappe
from frappe import _
from frappe.utils import today, add_days, get_first_day_of_week, get_first_day


@frappe.whitelist()
def get_dashboard_data(period="today"):
    """Return aggregated metrics for the SFA dashboard."""
    date_filter = _get_date_filter(period)

    active_visits = frappe.db.count("SFA Visit", {
        "status": "In Progress",
        "visit_date": [">=", date_filter],
    })

    completed_visits = frappe.db.count("SFA Visit", {
        "status": "Completed",
        "visit_date": [">=", date_filter],
    })

    orders = frappe.db.sql("""
        SELECT COUNT(*) as cnt, IFNULL(SUM(total_qty), 0) as qty, IFNULL(SUM(grand_total), 0) as rev
        FROM `tabSales Order`
        WHERE transaction_date >= %s AND docstatus = 1
    """, date_filter, as_dict=True)

    payments = frappe.db.sql("""
        SELECT IFNULL(SUM(amount), 0) as total
        FROM `tabSFA Payment`
        WHERE payment_date >= %s AND docstatus = 1
    """, date_filter, as_dict=True)

    # Compliance: visits completed / total visits planned
    planned = frappe.db.count("SFA Visit", {"visit_date": [">=", date_filter]})
    compliance = round((completed_visits / planned * 100) if planned else 0, 1)

    return {
        "active_visits": active_visits,
        "completed_visits": completed_visits,
        "orders_today": int(orders[0].qty if orders else 0),
        "revenue_today": float(orders[0].rev if orders else 0),
        "payments_today": float(payments[0].total if payments else 0),
        "compliance_rate": compliance,
    }


@frappe.whitelist()
def get_leaderboard(period="month"):
    """Return ranked reps by visits + revenue."""
    date_filter = _get_date_filter(period)

    rows = frappe.db.sql("""
        SELECT
            v.sales_person,
            sp.territory,
            COUNT(v.name) AS visits,
            IFNULL(SUM(o.grand_total), 0) AS revenue,
            IFNULL(SUM(pl.points), 0) AS points
        FROM `tabSFA Visit` v
        LEFT JOIN `tabSales Person` sp ON sp.name = v.sales_person
        LEFT JOIN `tabSales Order` o ON o.owner = v.sales_person
            AND DATE(o.transaction_date) >= %s AND o.docstatus = 1
        LEFT JOIN `tabSFA Rep Points Ledger` pl ON pl.sales_person = v.sales_person
            AND pl.timestamp >= %s
        WHERE v.visit_date >= %s AND v.status = 'Completed'
        GROUP BY v.sales_person
        ORDER BY visits DESC, revenue DESC
        LIMIT 20
    """, (date_filter, date_filter, date_filter), as_dict=True)

    return rows


@frappe.whitelist()
def get_active_reps():
    """Return list of active SFA reps."""
    users = frappe.get_all(
        "User",
        filters={"enabled": 1, "user_type": "System User"},
        fields=["name", "full_name", "user_image"],
        limit=50,
    )
    return users


@frappe.whitelist()
def get_visit_activities(limit=20):
    """Recent visit activity for the live feed."""
    return frappe.get_all(
        "SFA Visit",
        fields=["name", "customer", "sales_person", "status", "visit_date", "check_in_time"],
        order_by="modified desc",
        limit=limit,
    )


def _get_date_filter(period):
    if period == "today":
        return today()
    elif period == "week":
        return get_first_day_of_week(today())
    elif period == "month":
        return get_first_day(today())
    elif period == "quarter":
        return add_days(today(), -90)
    return today()
