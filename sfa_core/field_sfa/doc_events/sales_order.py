import frappe
from frappe import _

def validate(doc, method):
    """Link SFA visit and validate carton quantities"""
    if doc.custom_sfa_visit:
        visit = frappe.get_doc("SFA Visit", doc.custom_sfa_visit)
        if visit.customer != doc.customer:
            frappe.throw(_("Sales Order customer does not match linked SFA Visit customer"))

    # Free-carton entitlement flag: native is_free_item lines vs active schemes.
    from sfa_core.field_sfa.api.free_carton import free_entitlement_for_order
    paid_qty, free_given = {}, {}
    for item in doc.items:
        if getattr(item, "is_free_item", 0):
            free_given[item.item_code] = free_given.get(item.item_code, 0) + (item.qty or 0)
        else:
            paid_qty[item.item_code] = paid_qty.get(item.item_code, 0) + (item.qty or 0)
    entitled = free_entitlement_for_order(doc.customer, paid_qty)
    beyond = any(qty > entitled.get(code, 0) for code, qty in free_given.items())
    doc.custom_free_beyond_entitlement = 1 if beyond else 0

def on_submit(doc, method):
    """Award points for order placement"""
    if doc.custom_sfa_visit and doc.custom_sfa_rep:
        from sfa_core.field_sfa.utils.gamification import award_points_for_order
        award_points_for_order(doc)
    _refresh_customer_order_stats(doc.customer)

def on_cancel(doc, method):
    """Reverse points on cancellation"""
    if doc.custom_sfa_visit:
        from sfa_core.field_sfa.utils.gamification import reverse_order_points
        reverse_order_points(doc)
    _refresh_customer_order_stats(doc.customer)


def _refresh_customer_order_stats(customer):
    """Recompute Customer order count / revenue / outstanding after an order
    state change (mirrors the recompute done on visit save)."""
    if not customer:
        return
    try:
        from sfa_core.field_sfa.doc_events.visit import _update_customer_stats
        _update_customer_stats(customer)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "SFA: order stats refresh failed")
