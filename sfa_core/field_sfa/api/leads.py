"""
sfa_core/field_sfa/api/leads.py

Mobile lead endpoints. Reps capture prospects in the field (GPS-tagged),
progress them through the SFA lifecycle, and convert qualified ones into
Customers. Rep identity is session-authoritative; creates are idempotent by
client_uuid for offline-safe retries. Wrapped in the mobile error envelope.
Offline-created leads also flow through sync push (see sync.py).
"""

import frappe
from frappe import _
from frappe.utils import cint
from sfa_core.api.auth import resolve_sales_person
from sfa_core.field_sfa.api.response import mobile_api

_FIELDS = ["name", "lead_name", "company_name", "email_id", "mobile_no",
           "custom_sfa_status", "custom_sfa_rep", "territory", "source",
           "customer", "custom_sfa_latitude", "custom_sfa_longitude",
           "custom_sfa_captured_at", "creation", "modified"]


def _own_lead_or_throw(name, sp):
    owner_rep = frappe.db.get_value("Lead", name, "custom_sfa_rep")
    if owner_rep != sp:
        frappe.throw(_("Not your lead"), frappe.PermissionError)


@frappe.whitelist()
@mobile_api
def get_leads(status=None, start=0, page_length=100):
    sp = resolve_sales_person()
    filters = {"custom_sfa_rep": sp}
    if status:
        filters["custom_sfa_status"] = status
    start = cint(start)
    page_length = min(cint(page_length) or 100, 500)
    total = frappe.db.count("Lead", filters=filters)
    items = frappe.get_all("Lead", filters=filters, fields=_FIELDS,
                           order_by="modified desc", start=start, page_length=page_length)
    return {"items": items, "total": total}


@frappe.whitelist()
@mobile_api
def create_lead(lead_name, latitude=None, longitude=None, mobile_no=None,
                email_id=None, company_name=None, territory=None, source=None,
                accuracy=None, captured_at=None, notes=None, client_uuid=None):
    sp = resolve_sales_person()
    if client_uuid:
        existing = frappe.db.get_value("Lead", {"custom_client_uuid": client_uuid}, "name")
        if existing:
            return {"name": existing, "status": "duplicate"}
    doc = frappe.get_doc({
        "doctype": "Lead",
        "lead_name": lead_name,
        "company_name": company_name,
        "email_id": email_id,
        "mobile_no": mobile_no,
        "territory": territory,
        "source": source,
        "custom_sfa_rep": sp,
        "custom_sfa_status": "New",
        "custom_sfa_latitude": latitude,
        "custom_sfa_longitude": longitude,
        "custom_sfa_gps_accuracy": accuracy,
        "custom_sfa_captured_at": captured_at,
        "notes": notes,
        "custom_client_uuid": client_uuid,
    })
    doc.insert(ignore_permissions=True)
    return {"name": doc.name, "status": "created"}


@frappe.whitelist()
@mobile_api
def set_lead_status(name, status):
    sp = resolve_sales_person()
    _own_lead_or_throw(name, sp)
    frappe.db.set_value("Lead", name, "custom_sfa_status", status)
    return {"name": name, "custom_sfa_status": status}


@frappe.whitelist()
@mobile_api
def convert_lead(name, customer_group=None):
    sp = resolve_sales_person()
    _own_lead_or_throw(name, sp)
    from sfa_core.api.leads import convert_lead as _convert
    return _convert(name, customer_group=customer_group)
