import frappe
from frappe import _
from frappe.utils import flt

def before_validate(doc, method):
    """Capture the rate the SFA app submitted for each line, before ERPNext's
    price-list lookup can backfill it from a historical Item Price."""
    doc.flags.sfa_submitted_rates = [flt(getattr(it, "rate", 0)) for it in doc.items]


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

    # Pin each paid line to the rate the SFA app submitted. ERPNext backfills
    # a line's rate from the selling price list during validate, so a price
    # auto-stored from an earlier order would otherwise leak into this one.
    # Restoring the submitted rate keeps the catalog / rep-entered price
    # authoritative and stops historical prices from carrying over.
    _recompute = False
    subs = doc.flags.get("sfa_submitted_rates")
    if subs and len(subs) == len(doc.items):
        for item, want in zip(doc.items, subs):
            if getattr(item, "is_free_item", 0):
                continue
            want = flt(want)
            if (flt(item.rate) != want or flt(item.price_list_rate) != want
                    or flt(getattr(item, "discount_percentage", 0))):
                item.rate = want
                item.price_list_rate = want
                item.discount_percentage = 0
                item.discount_amount = 0
                item.margin_type = ""
                item.margin_rate_or_amount = 0
                item.rate_with_margin = 0
                _recompute = True

    # Free lines must never be charged. ERPNext backfills a rate-0 line from
    # the price list during validate, which would put the free value into
    # grand_total (and the customer's due). Force them back to zero and
    # recompute totals so free cartons never appear as owed.
    for item in doc.items:
        if getattr(item, "is_free_item", 0) and (item.rate or item.amount or item.price_list_rate):
            item.price_list_rate = 0
            item.discount_percentage = 0
            item.discount_amount = 0
            item.margin_rate_or_amount = 0
            item.rate = 0
            item.amount = 0
            item.base_rate = 0
            item.base_amount = 0
            _recompute = True
    if _recompute:
        doc.calculate_taxes_and_totals()

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
