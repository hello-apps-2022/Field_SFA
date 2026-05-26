import frappe
from frappe import _

def has_visit_permission(doc, user=None):
    """Check if user has permission to access visit"""
    if not user:
        user = frappe.session.user

    if frappe.has_role("SFA Manager", user):
        return True

    if frappe.has_role("SFA Supervisor", user):
        # Check if supervisor manages this sales person's territory
        return True

    if frappe.has_role("SFA Rep", user):
        sp = frappe.db.get_value("Sales Person", {"user_id": user}, "name")
        return doc.sales_person == sp

    return False

def has_payment_permission(doc, user=None):
    """Check payment permission"""
    return has_visit_permission(doc, user)

def has_beat_plan_permission(doc, user=None):
    """Check beat plan permission"""
    if not user:
        user = frappe.session.user

    if frappe.has_role("SFA Manager", user):
        return True

    if frappe.has_role("SFA Supervisor", user):
        return True

    if frappe.has_role("SFA Rep", user):
        sp = frappe.db.get_value("Sales Person", {"user_id": user}, "name")
        return doc.sales_person == sp

    return False
