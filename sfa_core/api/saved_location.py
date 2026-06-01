"""
sfa_core/api/saved_location.py

Web CRUD for SFA Saved Location plus its configurable type list
(SFA Location Type). Saved locations are GPS pins the team drops — customer
sites, warehouses, competitor outlets, landmarks.

Row scope mirrors the rest of the admin app: admins and managers see every pin;
supervisors, reps and helpers see their own (by owner — SL carries no rep or
territory field). Writes go through the doctype permissions (no
ignore_permissions), so the SFA Saved Location role grants govern who may
create / edit / deactivate, exactly like every other admin surface.
"""

import frappe
from frappe import _
from frappe.utils import cint
from sfa_core.api.auth import get_scope_context

_FIELDS = [
    "name", "location_name", "latitude", "longitude", "accuracy", "captured_at",
    "address", "location_type", "linked_customer", "is_active",
    "owner", "creation", "modified",
]


def _row_scope():
    """Admins/managers -> all pins; everyone else -> their own (by owner)."""
    ctx = get_scope_context()
    if ctx["is_admin"] or frappe.session.user == "Administrator":
        return {}
    return {"owner": frappe.session.user}


@frappe.whitelist()
def get_saved_locations(search=None, location_type=None, linked_customer=None,
                        is_active=None, start=0, page_length=50):
    filters = _row_scope()
    if location_type:
        filters["location_type"] = location_type
    if linked_customer:
        filters["linked_customer"] = linked_customer
    if is_active not in (None, "", "all"):
        filters["is_active"] = cint(is_active)

    or_filters = None
    if search:
        like = "%%%s%%" % search
        or_filters = [["location_name", "like", like], ["address", "like", like]]

    start = cint(start)
    page_length = cint(page_length) or 50
    if or_filters:
        total = len(frappe.get_all("SFA Saved Location", filters=filters,
                                   or_filters=or_filters, fields=["name"]))
    else:
        total = frappe.db.count("SFA Saved Location", filters=filters)
    items = frappe.get_all("SFA Saved Location", filters=filters, or_filters=or_filters,
                           fields=_FIELDS, order_by="modified desc",
                           start=start, page_length=page_length)
    return {"items": items, "total": total}


@frappe.whitelist()
def get_saved_location(name):
    doc = frappe.get_doc("SFA Saved Location", name)
    doc.check_permission("read")
    return doc.as_dict()


@frappe.whitelist()
def create_saved_location(location_name, latitude, longitude, location_type,
                          accuracy=None, address=None, linked_customer=None,
                          captured_at=None):
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
    })
    doc.insert()  # doctype permissions enforced
    return doc.as_dict()


@frappe.whitelist()
def update_saved_location(name, location_name=None, latitude=None, longitude=None,
                          location_type=None, accuracy=None, address=None,
                          linked_customer=None, captured_at=None):
    doc = frappe.get_doc("SFA Saved Location", name)
    doc.check_permission("write")
    for field, value in (
        ("location_name", location_name), ("latitude", latitude),
        ("longitude", longitude), ("location_type", location_type),
        ("accuracy", accuracy), ("address", address),
        ("linked_customer", linked_customer), ("captured_at", captured_at),
    ):
        if value is not None:
            doc.set(field, value)
    if doc.location_type != "Customer":
        doc.linked_customer = None
    doc.save()
    return doc.as_dict()


@frappe.whitelist()
def set_saved_location_active(name, is_active):
    doc = frappe.get_doc("SFA Saved Location", name)
    doc.check_permission("write")
    doc.is_active = cint(is_active)
    doc.save()
    return {"name": doc.name, "is_active": doc.is_active}


# ── Configurable location types (admin/manager-managed, like Territories) ──────

@frappe.whitelist()
def get_location_types(include_inactive=0):
    filters = {} if cint(include_inactive) else {"is_active": 1}
    return frappe.get_all("SFA Location Type", filters=filters,
                          fields=["name", "option_name", "description", "is_active"],
                          order_by="option_name asc")


@frappe.whitelist()
def create_location_type(option_name, description=None):
    doc = frappe.get_doc({
        "doctype": "SFA Location Type",
        "option_name": option_name,
        "description": description,
        "is_active": 1,
    })
    doc.insert()  # perms enforced; option_name is unique
    return doc.as_dict()


@frappe.whitelist()
def update_location_type(name, option_name=None, description=None, is_active=None):
    doc = frappe.get_doc("SFA Location Type", name)
    doc.check_permission("write")
    if option_name is not None:
        doc.option_name = option_name
    if description is not None:
        doc.description = description
    if is_active is not None:
        doc.is_active = cint(is_active)
    doc.save()
    return doc.as_dict()
