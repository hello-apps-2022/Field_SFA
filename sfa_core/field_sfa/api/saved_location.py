"""
sfa_core/field_sfa/api/saved_location.py

Mobile saved-location endpoints. Reps drop GPS pins in the field; these are
owner-scoped (a rep only ever sees / creates their own) and idempotent by
client_uuid for offline-safe retries. Every method is wrapped in the mobile
error envelope. Offline-created pins also flow through sync push (see sync.py).
"""

import frappe
from frappe import _
from frappe.utils import cint
from sfa_core.field_sfa.api.response import mobile_api

_FIELDS = ["name", "location_name", "latitude", "longitude", "accuracy",
           "captured_at", "address", "location_type", "linked_customer",
           "is_active", "creation", "modified"]


@frappe.whitelist()
@mobile_api
def get_saved_locations(location_type=None, is_active=1, start=0, page_length=200):
    filters = {"owner": frappe.session.user}
    if location_type:
        filters["location_type"] = location_type
    if is_active not in (None, "", "all"):
        filters["is_active"] = cint(is_active)
    start = cint(start)
    page_length = min(cint(page_length) or 200, 1000)
    total = frappe.db.count("SFA Saved Location", filters=filters)
    items = frappe.get_all("SFA Saved Location", filters=filters, fields=_FIELDS,
                           order_by="modified desc", start=start, page_length=page_length)
    return {"items": items, "total": total}


@frappe.whitelist()
@mobile_api
def create_saved_location(location_name, latitude, longitude, location_type,
                          accuracy=None, address=None, linked_customer=None,
                          captured_at=None, client_uuid=None):
    # Idempotency: a retried create with the same client_uuid returns the original.
    if client_uuid:
        existing = frappe.db.get_value(
            "SFA Saved Location",
            {"custom_client_uuid": client_uuid, "owner": frappe.session.user},
            "name",
        )
        if existing:
            return {"name": existing, "status": "duplicate"}
    doc = frappe.get_doc({
        "doctype": "SFA Saved Location",
        "location_name": location_name,
        "latitude": latitude,
        "longitude": longitude,
        "location_type": location_type,
        "accuracy": accuracy,
        "address": address,
        "linked_customer": linked_customer if location_type == "Customer" else None,
        "captured_at": captured_at,
        "custom_client_uuid": client_uuid,
    })
    # Pins are owner-scoped; the creator owns the row, reads never cross owners.
    doc.insert(ignore_permissions=True)
    return {"name": doc.name, "status": "created"}


@frappe.whitelist()
@mobile_api
def get_location_types():
    return frappe.get_all("SFA Location Type", filters={"is_active": 1},
                          fields=["option_name", "description"],
                          order_by="option_name asc")
