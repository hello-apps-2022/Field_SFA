import frappe
from frappe import _

def validate(doc, method):
    """Validate payment data"""
    if doc.amount <= 0:
        frappe.throw(_("Payment amount must be greater than zero"))

    if doc.payment_type == "Mobile Money" and not doc.mobile_money_transaction_id:
        frappe.throw(_("Mobile Money Transaction ID is required for Mobile Money payments"))

    if doc.payment_type == "Cheque" and not doc.cheque_no:
        frappe.throw(_("Cheque Number is required for cheque payments"))

def on_submit(doc, method):
    """Award points for payment collection"""
    from sfa_core.field_sfa.utils.gamification import award_points_for_payment
    award_points_for_payment(doc)
