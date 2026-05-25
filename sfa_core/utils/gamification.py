import frappe
from frappe import _
from frappe.utils import now

def award_points(sales_person, activity_type, base_points, reference_doctype=None, reference_name=None, multiplier=1):
    """Award points to a sales person"""

    # Check for SKU multiplier if applicable
    if activity_type == "Order Placed" and reference_doctype == "Sales Order":
        multiplier = get_order_multiplier(reference_name)

    points = int(base_points * multiplier)

    # Get current balance
    current_balance = frappe.db.get_value("SFA Rep Points Ledger", 
        {"sales_person": sales_person}, "SUM(points)") or 0

    ledger = frappe.get_doc({
        "doctype": "SFA Rep Points Ledger",
        "sales_person": sales_person,
        "timestamp": now(),
        "activity_type": activity_type,
        "points": points,
        "reference_doctype": reference_doctype,
        "reference_name": reference_name,
        "description": f"{activity_type}: {points} points",
        "balance": current_balance + points
    })
    ledger.insert(ignore_permissions=True)

    return points

def award_points_for_order(sales_order):
    """Award points for order placement with SKU multipliers"""
    total_points = 0
    for item in sales_order.items:
        multiplier = frappe.db.get_value("SFA SKU Points Multiplier", 
            {"item": item.item_code, "is_active": 1}, "points_per_carton") or 1

        carton_qty = item.custom_carton_qty or item.qty
        points = int(20 * carton_qty * multiplier)
        total_points += points

    if total_points > 0:
        award_points(sales_order.custom_sfa_rep, "Order Placed", total_points, 
                     "Sales Order", sales_order.name)

def award_points_for_payment(payment):
    """Award points for payment collection"""
    points = int(15 * (payment.amount / 100000))  # 15 points per 100k
    award_points(payment.sales_person, "Payment Collected", max(points, 15), 
                 "SFA Payment", payment.name)

def reverse_order_points(sales_order):
    """Reverse points when order is cancelled"""
    existing = frappe.get_all("SFA Rep Points Ledger",
        filters={"reference_doctype": "Sales Order", "reference_name": sales_order.name},
        fields=["name", "points"])

    for entry in existing:
        award_points(sales_order.custom_sfa_rep, "Manual Adjustment", -entry.points,
                     "Sales Order", sales_order.name)

def get_order_multiplier(sales_order_name):
    """Calculate multiplier based on SKU points config"""
    so = frappe.get_doc("Sales Order", sales_order_name)
    total_multiplier = 0
    total_qty = 0

    for item in so.items:
        multiplier = frappe.db.get_value("SFA SKU Points Multiplier",
            {"item": item.item_code, "is_active": 1}, "points_per_carton") or 1
        qty = item.custom_carton_qty or item.qty
        total_multiplier += multiplier * qty
        total_qty += qty

    return total_multiplier / total_qty if total_qty > 0 else 1

def check_and_award_badges(sales_person):
    """Check criteria and award badges"""
    from datetime import datetime, timedelta

    badges = frappe.get_all("SFA Badge", 
        filters={"is_active": 1}, 
        fields=["name", "badge_name", "criteria_type", "threshold_value", "period_days", "points_bonus"])

    for badge in badges:
        if check_badge_criteria(sales_person, badge):
            award_badge(sales_person, badge)

def check_badge_criteria(sales_person, badge):
    """Check if sales person meets badge criteria"""
    from datetime import datetime, timedelta

    period_start = None
    if badge.period_days > 0:
        period_start = datetime.now() - timedelta(days=badge.period_days)

    if badge.criteria_type == "Visit Count":
        count = frappe.db.count("SFA Visit", {
            "sales_person": sales_person,
            "status": "Completed",
            "creation": [">=", period_start] if period_start else [">=", "2000-01-01"]
        })
        return count >= badge.threshold_value

    elif badge.criteria_type == "Order Value":
        total = frappe.db.get_value("Sales Order", {
            "custom_sfa_rep": sales_person,
            "docstatus": 1,
            "creation": [">=", period_start] if period_start else [">=", "2000-01-01"]
        }, "SUM(grand_total)") or 0
        return total >= badge.threshold_value

    elif badge.criteria_type == "Payment Amount":
        total = frappe.db.get_value("SFA Payment", {
            "sales_person": sales_person,
            "status": "Submitted",
            "creation": [">=", period_start] if period_start else [">=", "2000-01-01"]
        }, "SUM(amount)") or 0
        return total >= badge.threshold_value

    elif badge.criteria_type == "Points Threshold":
        total = frappe.db.get_value("SFA Rep Points Ledger", {
            "sales_person": sales_person,
            "creation": [">=", period_start] if period_start else [">=", "2000-01-01"]
        }, "SUM(points)") or 0
        return total >= badge.threshold_value

    return False

def award_badge(sales_person, badge):
    """Award a badge to sales person"""
    if frappe.db.exists("SFA Rep Badge", {"sales_person": sales_person, "badge": badge.name}):
        return

    rep_badge = frappe.get_doc({
        "doctype": "SFA Rep Badge",
        "sales_person": sales_person,
        "badge": badge.name,
        "awarded_date": now(),
        "awarded_by": frappe.session.user
    })
    rep_badge.insert(ignore_permissions=True)

    # Award bonus points
    if badge.points_bonus > 0:
        award_points(sales_person, "Badge Awarded", badge.points_bonus, "SFA Badge", badge.name)
