import frappe
from frappe import _
from frappe.utils import cint
from sfa_core.field_sfa.api.response import mobile_api

ALERT_FIELDS = ["name", "subject", "type", "email_content",
                "document_type", "document_name", "link",
                "from_user", "read", "creation"]


@frappe.whitelist()
@mobile_api
def get_alerts(start=0, page_length=20, unread_only=0):
    """Notification feed for the current user, backed by Frappe's Notification
    Log (assignments, mentions, shares, and anything the app pushes)."""
    user = frappe.session.user
    filters = {"for_user": user}
    if cint(unread_only):
        filters["read"] = 0
    items = frappe.get_all(
        "Notification Log", filters=filters, fields=ALERT_FIELDS,
        limit_start=cint(start),
        limit_page_length=min(cint(page_length) or 20, 100),
        order_by="creation desc")
    return {
        "items": items,
        "total": frappe.db.count("Notification Log", filters),
        "unread": frappe.db.count("Notification Log", {"for_user": user, "read": 0}),
    }


@frappe.whitelist()
@mobile_api
def mark_alerts_read(name=None, mark_all=0):
    """Mark one alert (by name) or all of the current user's alerts as read."""
    user = frappe.session.user
    if cint(mark_all):
        frappe.db.set_value("Notification Log", {"for_user": user, "read": 0},
                            "read", 1, update_modified=False)
        return {"status": "ok"}
    if not name:
        frappe.throw(_("Provide an alert name or mark_all=1."), frappe.ValidationError)
    owner = frappe.db.get_value("Notification Log", name, "for_user")
    if not owner:
        frappe.throw(_("Alert {0} not found.").format(name), frappe.DoesNotExistError)
    if owner != user:
        frappe.throw(_("Not your alert."), frappe.PermissionError)
    frappe.db.set_value("Notification Log", name, "read", 1, update_modified=False)
    return {"status": "ok", "name": name}
