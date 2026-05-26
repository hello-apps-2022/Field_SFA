import frappe
from frappe import _

def validate(doc, method):
    """Validate field activity"""
    if doc.activity_type == "Photo" and not doc.photo:
        frappe.throw(_("Photo is required for Photo activity type"))
