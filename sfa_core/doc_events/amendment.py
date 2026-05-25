import frappe
from frappe import _

def validate_amendment(doc, method):
    """Validate amendment request"""
    if doc.status != "Pending" and not doc.approved_by:
        frappe.throw(_("Approved By is required for approved/rejected amendments"))

def on_submit(doc, method):
    """Apply approved amendment to beat plan"""
    if doc.status == "Approved":
        from sfa_core.utils.beat_plan import apply_amendment
        apply_amendment(doc)
