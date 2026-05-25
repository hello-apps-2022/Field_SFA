import frappe
from frappe import _

def validate_response(doc, method):
    """Validate form response"""
    if not doc.responses and not doc.text_responses and not doc.option_responses:
        frappe.throw(_("At least one response is required"))

def on_submit(doc, method):
    """Award points for form submission"""
    from sfa_core.utils.gamification import award_points
    award_points(doc.sales_person, "Form Submitted", 5, "SFA Form Response", doc.name)

    # Update form assignment if linked
    if doc.form_assignment:
        frappe.db.set_value("SFA Form Assignment", doc.form_assignment, {
            "status": "Completed",
            "completed_date": now(),
            "form_response": doc.name
        })
