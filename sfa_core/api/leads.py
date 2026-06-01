"""
sfa_core/api/leads.py

Web CRUD for prospecting Leads. Leads are ERPNext `Lead` records extended with
SFA fields (assigned rep, lifecycle status, GPS capture). They convert into the
standard Customer everything else uses, via ERPNext's own make_customer mapper
plus an SFA stamp (rep / territory / GPS / back-link).

Row scope mirrors Customers: admins & managers see all; supervisors see their
territory; reps & helpers see leads assigned to themselves (and downline).
Identity for writes is session-authoritative (resolve_sales_person) — a client
can never assign a lead to someone else by passing a rep id.
"""

import frappe
from frappe import _
from frappe.utils import cint
from sfa_core.api.auth import (
    get_scope_context,
    resolve_sales_person,
    get_scoped_sales_persons,
)

_FIELDS = [
    "name", "lead_name", "company_name", "email_id", "mobile_no",
    "status", "custom_sfa_status", "custom_sfa_rep", "territory", "source",
    "customer", "custom_sfa_latitude", "custom_sfa_longitude",
    "custom_sfa_captured_at", "creation", "modified",
]

_MUTABLE = ("lead_name", "company_name", "email_id", "mobile_no",
            "territory", "source", "custom_sfa_status")


def _lead_scope(ctx):
    """Admins/managers -> all; supervisors -> their territory; reps -> own +
    downline sales persons. Mirrors the Customer list scoping."""
    if ctx["is_admin"] or frappe.session.user == "Administrator":
        return {}
    if ctx["is_manager"] and ctx["territory"]:        # supervisor tier
        return {"territory": ctx["territory"]}
    if ctx["is_rep"]:
        sps = get_scoped_sales_persons()
        return {"custom_sfa_rep": ["in", sps] if sps else ["in", ["__none__"]]}
    return {"name": "__no_access__"}


def _guard(name, ctx):
    """Ensure the acting user may act on this lead, by re-checking scope."""
    filters = _lead_scope(ctx)
    filters["name"] = name
    if not frappe.db.exists("Lead", filters):
        frappe.throw(_("Not permitted for that lead"), frappe.PermissionError)


@frappe.whitelist()
def get_leads(search=None, status=None, territory=None, rep=None, source=None,
              converted=None, start=0, page_length=50):
    ctx = get_scope_context()
    filters = _lead_scope(ctx)
    if status:
        filters["custom_sfa_status"] = status
    if territory and ctx["is_admin"]:
        filters["territory"] = territory
    if rep and (ctx["is_admin"] or ctx["is_manager"]):
        filters["custom_sfa_rep"] = rep
    if source:
        filters["source"] = source
    if converted == "1":
        filters["customer"] = ["is", "set"]
    elif converted == "0":
        filters["customer"] = ["is", "not set"]

    or_filters = None
    if search:
        like = "%%%s%%" % search
        or_filters = [["lead_name", "like", like], ["company_name", "like", like],
                      ["mobile_no", "like", like], ["email_id", "like", like]]

    start = cint(start)
    page_length = cint(page_length) or 50
    if or_filters:
        total = len(frappe.get_all("Lead", filters=filters, or_filters=or_filters, fields=["name"]))
    else:
        total = frappe.db.count("Lead", filters=filters)
    items = frappe.get_all("Lead", filters=filters, or_filters=or_filters,
                           fields=_FIELDS, order_by="modified desc",
                           start=start, page_length=page_length)
    return {"items": items, "total": total}


@frappe.whitelist()
def get_lead(name):
    ctx = get_scope_context()
    _guard(name, ctx)
    return frappe.get_doc("Lead", name).as_dict()


@frappe.whitelist()
def create_lead(lead_name, mobile_no=None, email_id=None, company_name=None,
                territory=None, source=None, sales_person=None,
                latitude=None, longitude=None, accuracy=None, captured_at=None,
                notes=None):
    if not (lead_name or "").strip():
        frappe.throw(_("Lead name is required."))
    rep = resolve_sales_person(sales_person)  # session-authoritative
    doc = frappe.get_doc({
        "doctype": "Lead",
        "lead_name": lead_name,
        "company_name": company_name,
        "email_id": email_id,
        "mobile_no": mobile_no,
        "territory": territory,
        "source": source,
        "custom_sfa_rep": rep,
        "custom_sfa_status": "New",
        "custom_sfa_latitude": latitude,
        "custom_sfa_longitude": longitude,
        "custom_sfa_gps_accuracy": accuracy,
        "custom_sfa_captured_at": captured_at,
        "notes": notes,
    })
    doc.insert(ignore_permissions=True)
    return {"name": doc.name, "lead_name": doc.lead_name}


@frappe.whitelist()
def update_lead(name, **kwargs):
    ctx = get_scope_context()
    _guard(name, ctx)
    doc = frappe.get_doc("Lead", name)
    for field in _MUTABLE:
        if field in kwargs and kwargs[field] is not None:
            doc.set(field, kwargs[field])
    for gps in ("custom_sfa_latitude", "custom_sfa_longitude",
                "custom_sfa_gps_accuracy", "custom_sfa_captured_at"):
        if kwargs.get(gps) is not None:
            doc.set(gps, kwargs[gps])
    doc.save(ignore_permissions=True)
    return {"name": doc.name}


@frappe.whitelist()
def set_lead_status(name, status):
    ctx = get_scope_context()
    _guard(name, ctx)
    frappe.db.set_value("Lead", name, "custom_sfa_status", status)
    return {"name": name, "custom_sfa_status": status}


@frappe.whitelist()
def reassign_lead(name, sales_person):
    ctx = get_scope_context()
    if not (ctx["is_admin"] or ctx["is_manager"]):
        frappe.throw(_("Only managers can reassign leads."), frappe.PermissionError)
    _guard(name, ctx)
    target = resolve_sales_person(sales_person)  # validates the target is in scope
    frappe.db.set_value("Lead", name, "custom_sfa_rep", target)
    return {"name": name, "custom_sfa_rep": target}


@frappe.whitelist()
def convert_lead(name, customer_group=None):
    """Convert a lead into a Customer via ERPNext's make_customer, then stamp the
    SFA fields (rep, territory, GPS) and mark the lead Converted. Idempotent: a
    lead already linked to a Customer returns that Customer."""
    ctx = get_scope_context()
    _guard(name, ctx)

    existing = frappe.db.get_value("Customer", {"lead_name": name}, "name")
    if existing:
        frappe.db.set_value("Lead", name, "custom_sfa_status", "Converted")
        return {"customer": existing, "status": "exists"}

    lead = frappe.get_doc("Lead", name)
    from erpnext.crm.doctype.lead.lead import make_customer
    cust = make_customer(name)  # mapped Customer doc (sets customer_name + lead_name back-link)
    # make_customer auto-copies same-named fields between Lead and Customer. The
    # lead's lifecycle status ("New"/"Contacted"/...) is not a valid value for the
    # Customer's own custom_sfa_status select — clear it so the converted customer
    # initialises blank, exactly like a normally-created outlet.
    cust.custom_sfa_status = None
    if customer_group:
        cust.customer_group = customer_group
    if not cust.customer_group:
        from sfa_core.api.customer import _default_group
        cust.customer_group = _default_group()
    if lead.territory:
        cust.territory = lead.territory
    if lead.custom_sfa_rep:
        cust.custom_sfa_rep = lead.custom_sfa_rep
    if lead.get("custom_sfa_latitude"):
        cust.custom_latitude = lead.custom_sfa_latitude
    if lead.get("custom_sfa_longitude"):
        cust.custom_longitude = lead.custom_sfa_longitude
    if lead.get("custom_sfa_gps_accuracy"):
        cust.custom_sfa_gps_accuracy = lead.custom_sfa_gps_accuracy
    if lead.get("custom_sfa_captured_at"):
        cust.custom_sfa_captured_at = lead.custom_sfa_captured_at
    cust.insert(ignore_permissions=True)

    frappe.db.set_value("Lead", name, {"custom_sfa_status": "Converted", "status": "Converted"})
    return {"customer": cust.name, "customer_name": cust.customer_name, "status": "converted"}
