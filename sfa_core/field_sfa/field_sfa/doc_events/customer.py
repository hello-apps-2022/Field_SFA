import frappe
from frappe import _

def validate(doc, method):
    """Validate customer SFA fields"""
    if doc.custom_visit_frequency and doc.custom_visit_frequency < 0:
        frappe.throw(_("Visit Frequency cannot be negative"))

def after_insert(doc, method):
    """Set default SFA status"""
    if not doc.custom_sfa_status:
        doc.db_set("custom_sfa_status", "Active")
