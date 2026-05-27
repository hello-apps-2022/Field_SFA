import frappe
from frappe import _
from frappe.utils import now_datetime


def validate(doc, method):
    """Validate SFA Form Response."""
    if not doc.response_items and not doc.survey_response_json:
        frappe.throw(_("At least one response is required"))


def on_submit(doc, method):
    """
    On submit:
    1. Award gamification points to the sales rep
    2. Mark the visit's mandatory form as completed if applicable
    """
    # Gamification points
    from sfa_core.field_sfa.utils.gamification import award_points
    award_points(doc.sales_person, "Form Submitted", 5, "SFA Form Response", doc.name)

    # Mark visit mandatory form completed
    if doc.visit:
        template = frappe.db.get_value("SFA Form Template", doc.form_template, ["is_mandatory", "trigger_point"], as_dict=True)
        if template and template.get("is_mandatory"):
            frappe.db.set_value("SFA Visit", doc.visit, "is_mandatory_form_completed", 1)
