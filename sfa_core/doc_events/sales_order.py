import frappe
from frappe import _

def validate_order(doc, method):
    """Link SFA visit and validate carton quantities"""
    if doc.custom_sfa_visit:
        visit = frappe.get_doc("SFA Visit", doc.custom_sfa_visit)
        if visit.customer != doc.customer:
            frappe.throw(_("Sales Order customer does not match linked SFA Visit customer"))

    # Validate carton quantities
    for item in doc.items:
        total = (item.custom_carton_qty or 0) + (item.custom_free_qty or 0) + (item.custom_unpaid_qty or 0)
        if total > 0 and abs(total - item.qty) > 0.01:
            frappe.msgprint(_("Warning: Carton quantities sum ({0}) does not match order qty ({1}) for item {2}").format(
                total, item.qty, item.item_code), indicator="orange")

def on_submit(doc, method):
    """Award points for order placement"""
    if doc.custom_sfa_visit and doc.custom_sfa_rep:
        from sfa_core.utils.gamification import award_points_for_order
        award_points_for_order(doc)

def on_cancel(doc, method):
    """Reverse points on cancellation"""
    if doc.custom_sfa_visit:
        from sfa_core.utils.gamification import reverse_order_points
        reverse_order_points(doc)
