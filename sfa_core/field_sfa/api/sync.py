"""Offline sync primitive for the Field Pro mobile app (WatermelonDB shape).

Pull is live: `pull_changes(last_pulled_at, schema_version)` returns
`{ "changes": { <table>: { created, updated, deleted } }, "timestamp": <ms> }`,
scoped to the acting rep (derived from the session, never from client input),
using `modified > last_pulled_at` and the core Deleted Document log for
tombstones.

Push (`push_changes`) is intentionally not implemented yet — it requires a
per-DocType client_uuid field for idempotency plus conflict handling, and is
the next increment. The previous blind-insert `push_sync_data` (which spread
arbitrary client fields into new docs with no permission or idempotency checks)
has been removed; creates continue to go through the typed endpoints
(create_order, create_payment, create_visit, submit_form_response,
upload_gps_track) until push lands.
"""

import datetime
import json

import frappe
from sfa_core.field_sfa.api.response import mobile_api
import pytz
from frappe import _
from frappe.utils import get_datetime, get_system_timezone, now_datetime

from sfa_core.api.auth import get_user_context, resolve_sales_person


# --------------------------------------------------------------------------- #
# Time helpers
# WatermelonDB's lastPulledAt is a millisecond epoch (UTC). Frappe stores
# `modified` as a naive datetime in the system timezone. Convert through the
# system tz so the SQL boundary lines up with stored `modified` while the
# number handed to the device is a correct UTC epoch.
# --------------------------------------------------------------------------- #
def _sys_tz():
    return pytz.timezone(get_system_timezone() or "UTC")


def _to_ms(dt):
    if dt is None:
        return None
    if isinstance(dt, str):
        dt = get_datetime(dt)
    aware = _sys_tz().localize(dt) if dt.tzinfo is None else dt
    return int(aware.timestamp() * 1000)


def _from_ms(ms):
    aware = datetime.datetime.fromtimestamp(int(ms) / 1000.0, tz=_sys_tz())
    return aware.replace(tzinfo=None)


# --------------------------------------------------------------------------- #
# Per-table scope (mirrors the existing typed read endpoints exactly)
# --------------------------------------------------------------------------- #
def _customer_scope(sp, ctx):
    # A rep's customers: those where they are the primary rep
    # (Customer.custom_sfa_rep) plus any explicitly shared via the active share
    # log. Empty -> nothing (never the whole book).
    names = set(frappe.get_all("Customer", filters={"custom_sfa_rep": sp}, pluck="name"))
    names.update(frappe.get_all(
        "SFA Customer Share Log",
        filters={"sales_person": sp, "is_active": 1},
        pluck="customer",
    ))
    # Referential closure: also include any customer referenced by the rep's
    # own visits / orders / payments, so the device never holds a dangling
    # reference to a customer that fell outside the assigned/shared scope.
    names.update(frappe.get_all("SFA Visit", filters={"sales_person": sp}, pluck="customer"))
    names.update(frappe.get_all("Sales Order", filters={"custom_sfa_rep": sp}, pluck="customer"))
    names.update(frappe.get_all("SFA Payment", filters={"sales_person": sp}, pluck="customer"))
    names.discard(None)
    names.discard("")
    return {"name": ["in", list(names) or [""]]}


# Each table: device key -> how to pull it.
#   doctype       Frappe DocType
#   scope(sp,ctx) filter dict, scoped to the rep
#   child_fields  table fieldnames to embed (None = none; [] also none)
TABLES = [
    {"key": "customers",      "doctype": "Customer",            "scope": _customer_scope, "full": True,
     "fields": ["name", "customer_name", "customer_group", "territory",
                "custom_sfa_status", "custom_sfa_rep", "custom_last_visit_date",
                "custom_visit_frequency", "disabled", "creation", "modified"]},
    {"key": "beat_plans",     "doctype": "SFA Beat Plan",       "scope": lambda sp, ctx: {"sales_person": sp},
     "child_fields": ["customers", "route_waypoints"]},
    {"key": "visits",         "doctype": "SFA Visit",           "scope": lambda sp, ctx: {"sales_person": sp}},
    {"key": "orders",         "doctype": "Sales Order",         "scope": lambda sp, ctx: {"custom_sfa_rep": sp, "docstatus": 1},
     "child_fields": ["items"]},
    {"key": "payments",       "doctype": "SFA Payment",         "scope": lambda sp, ctx: {"sales_person": sp, "docstatus": 1}},
    {"key": "form_templates", "doctype": "SFA Form Template",   "scope": lambda sp, ctx: {"is_active": 1}},
    {"key": "form_responses", "doctype": "SFA Form Response",   "scope": lambda sp, ctx: {"sales_person": sp},
     "child_fields": None},  # embed all children (answers)
    {"key": "gps_tracks",     "doctype": "SFA GPS Track Point", "scope": lambda sp, ctx: {"sales_person": sp}},
    {"key": "leads",          "doctype": "Lead",                "scope": lambda sp, ctx: {"custom_sfa_rep": sp},
     "fields": ["name", "lead_name", "company_name", "email_id", "mobile_no",
                "custom_sfa_status", "custom_sfa_rep", "territory", "source", "customer",
                "custom_sfa_latitude", "custom_sfa_longitude", "custom_sfa_gps_accuracy",
                "custom_sfa_captured_at", "creation", "modified"]},
    {"key": "saved_locations","doctype": "SFA Saved Location",  "scope": lambda sp, ctx: {"is_active": 1, "owner": frappe.session.user}},
    {"key": "points_config",  "doctype": "SFA Points Config",   "scope": lambda sp, ctx: {"is_active": 1}},
    {"key": "location_types", "doctype": "SFA Location Type",   "scope": lambda sp, ctx: {"is_active": 1}},
]

EMBED_ALL = object()  # sentinel: spec present but child_fields key absent -> none


def _child_field_names(doctype, allow):
    meta = frappe.get_meta(doctype)
    table_fields = meta.get_table_fields()
    names = [tf.fieldname for tf in table_fields]
    if allow is EMBED_ALL:
        return names
    if allow is None:
        return names  # explicit None in a spec means "all children"
    return [f for f in names if f in allow]


def _attach_children(doctype, rows, allow):
    if not rows:
        return
    fieldnames = _child_field_names(doctype, allow)
    if not fieldnames:
        return
    names = [r["name"] for r in rows]
    by_name = {r["name"]: r for r in rows}
    meta = frappe.get_meta(doctype)
    options = {tf.fieldname: tf.options for tf in meta.get_table_fields()}
    for fieldname in fieldnames:
        for r in rows:
            r.setdefault(fieldname, [])
        child_rows = frappe.get_all(
            options[fieldname],
            filters={"parent": ["in", names], "parenttype": doctype, "parentfield": fieldname},
            fields=["*"],
            order_by="idx asc",
        )
        for cr in child_rows:
            cr["id"] = cr.get("name")
            parent = by_name.get(cr.get("parent"))
            if parent is not None:
                parent[fieldname].append(cr)


def _is_created(row, boundary):
    c = row.get("creation")
    if not c:
        return True
    if isinstance(c, str):
        c = get_datetime(c)
    return c > boundary


def _deletions(doctype, boundary_str):
    """Hard-deletes recorded since the boundary (core Deleted Document log).
    Returns plain ids; unknown ids are harmless no-ops on the device."""
    return frappe.get_all(
        "Deleted Document",
        filters={"deleted_doctype": doctype, "restored": 0, "creation": [">", boundary_str]},
        pluck="deleted_name",
    )


def _pull_table(spec, sp, ctx, boundary, boundary_str):
    doctype = spec["doctype"]
    filters = dict(spec["scope"](sp, ctx))
    if boundary_str and not spec.get("full"):
        filters["modified"] = [">", boundary_str]

    fields = spec.get("fields") or ["*"]
    rows = frappe.get_all(doctype, filters=filters, fields=fields, order_by="modified asc")
    allow = spec["child_fields"] if "child_fields" in spec else EMBED_ALL
    if allow is not EMBED_ALL:
        _attach_children(doctype, rows, allow)

    created, updated = [], []
    for r in rows:
        r["id"] = r.get("name")
        if boundary is None or _is_created(r, boundary):
            created.append(r)
        else:
            updated.append(r)

    deleted = _deletions(doctype, boundary_str) if boundary_str else []
    return {"created": created, "updated": updated, "deleted": deleted}


@frappe.whitelist()
@mobile_api
def pull_changes(last_pulled_at=None, schema_version=None):
    """WatermelonDB pull. `last_pulled_at` is the ms-epoch the device received
    from its previous pull (omit/null/0 for a first full sync). `schema_version`
    is accepted for forward compatibility and currently unused."""
    ctx = get_user_context()
    sp = resolve_sales_person()  # session-derived; client cannot widen scope
    if not sp:
        frappe.throw(_("Sync requires a linked Sales Person."), frappe.PermissionError)

    server_now = now_datetime()
    boundary = None
    if last_pulled_at not in (None, "", 0, "0"):
        boundary = _from_ms(last_pulled_at)
    boundary_str = boundary.strftime("%Y-%m-%d %H:%M:%S.%f") if boundary else None

    changes = {}
    for spec in TABLES:
        changes[spec["key"]] = _pull_table(spec, sp, ctx, boundary, boundary_str)

    return {"changes": changes, "timestamp": _to_ms(server_now)}


# --------------------------------------------------------------------------- #
# Push — device-created records routed through the typed create endpoints so
# all server-side logic (pricing, settlement, validation, identity) runs.
# Idempotent by client_uuid; per-record results; never a blind insert.
# --------------------------------------------------------------------------- #
def _h_visit(rec, sp, uuid):
    from sfa_core.field_sfa.api.visit import create_visit
    extra = {}
    for k in ("status", "check_in_time", "check_out_time",
              "custom_sfa_latitude", "custom_sfa_longitude",
              "custom_sfa_gps_accuracy", "custom_sfa_captured_at"):
        if rec.get(k) is not None:
            extra[k] = rec[k]
    name = create_visit(customer=rec.get("customer"), sales_person=sp,
                         visit_date=rec.get("visit_date"),
                         custom_client_uuid=uuid, **extra)
    return name if isinstance(name, str) else (name or {}).get("name")


def _h_order(rec, sp, uuid):
    from sfa_core.field_sfa.api.order import create_order
    r = create_order(customer=rec.get("customer"), items=rec.get("items") or [],
                      sales_person=sp, visit=rec.get("visit"),
                      latitude=rec.get("latitude"), longitude=rec.get("longitude"),
                      accuracy=rec.get("accuracy"), captured_at=rec.get("captured_at"),
                      custom_client_uuid=uuid)
    return r.get("name")


def _h_payment(rec, sp, uuid):
    from sfa_core.field_sfa.api.payment import create_payment
    r = create_payment(customer=rec.get("customer"), amount=rec.get("amount"),
                        payment_type=rec.get("payment_type"), sales_person=sp,
                        visit=rec.get("visit"),
                        latitude=rec.get("latitude"), longitude=rec.get("longitude"),
                        accuracy=rec.get("accuracy"), captured_at=rec.get("captured_at"),
                        custom_client_uuid=uuid)
    return r.get("name")


def _h_form(rec, sp, uuid):
    from sfa_core.field_sfa.api.form import submit_form_response
    r = submit_form_response(form_template=rec.get("form_template"),
                             visit=rec.get("visit"), customer=rec.get("customer"),
                             sales_person=sp,
                             survey_response_json=rec.get("survey_response_json") or rec.get("answers"),
                             latitude=rec.get("latitude"), longitude=rec.get("longitude"),
                             accuracy=rec.get("accuracy"), captured_at=rec.get("captured_at"),
                             custom_client_uuid=uuid)
    return (r or {}).get("name")


def _h_gps(rec, sp, uuid):
    track = frappe.get_doc({
        "doctype": "SFA GPS Track Point", "sales_person": sp,
        "timestamp": rec.get("timestamp"), "latitude": rec.get("latitude"),
        "longitude": rec.get("longitude"), "accuracy": rec.get("accuracy"),
        "altitude": rec.get("altitude"), "speed": rec.get("speed"),
        "battery_level": rec.get("battery_level"), "visit": rec.get("visit"),
        "sync_status": "Synced", "custom_client_uuid": uuid,
    })
    track.insert(ignore_permissions=True)
    return track.name


def _h_saved_location(rec, sp, uuid):
    from sfa_core.field_sfa.api.saved_location import create_saved_location
    r = create_saved_location(location_name=rec.get("location_name"),
                              latitude=rec.get("latitude"), longitude=rec.get("longitude"),
                              location_type=rec.get("location_type"),
                              accuracy=rec.get("accuracy"), address=rec.get("address"),
                              linked_customer=rec.get("linked_customer"),
                              captured_at=rec.get("captured_at"), client_uuid=uuid)
    return (r or {}).get("name")


def _h_lead(rec, sp, uuid):
    from sfa_core.field_sfa.api.leads import create_lead
    r = create_lead(lead_name=rec.get("lead_name"),
                    latitude=rec.get("latitude") or rec.get("custom_sfa_latitude"),
                    longitude=rec.get("longitude") or rec.get("custom_sfa_longitude"),
                    mobile_no=rec.get("mobile_no"), email_id=rec.get("email_id"),
                    company_name=rec.get("company_name"), territory=rec.get("territory"),
                    source=rec.get("source"),
                    accuracy=rec.get("accuracy") or rec.get("custom_sfa_gps_accuracy"),
                    captured_at=rec.get("captured_at") or rec.get("custom_sfa_captured_at"),
                    notes=rec.get("notes"), client_uuid=uuid)
    return (r or {}).get("name")


PUSH_TABLES = {
    "visits":         {"doctype": "SFA Visit",           "handler": _h_visit},
    "orders":         {"doctype": "Sales Order",         "handler": _h_order},
    "payments":       {"doctype": "SFA Payment",         "handler": _h_payment},
    "form_responses": {"doctype": "SFA Form Response",   "handler": _h_form},
    "gps_tracks":     {"doctype": "SFA GPS Track Point", "handler": _h_gps},
    "leads":          {"doctype": "Lead",                "handler": _h_lead},
    "saved_locations": {"doctype": "SFA Saved Location",  "handler": _h_saved_location},
}


def _push_one(spec, rec, sp):
    uuid = rec.get("client_uuid") or rec.get("id")
    doctype = spec["doctype"]
    if uuid:
        existing = frappe.db.get_value(doctype, {"custom_client_uuid": uuid}, "name")
        if existing:
            return {"client_uuid": uuid, "id": existing, "status": "ok", "duplicate": True}
    savept = "sp_" + frappe.generate_hash(length=12)
    frappe.db.savepoint(savept)
    try:
        name = spec["handler"](rec, sp, uuid)
        return {"client_uuid": uuid, "id": name, "status": "ok"}
    except frappe.PermissionError as e:
        frappe.db.rollback(save_point=savept)
        return {"client_uuid": uuid, "status": "rejected", "reason": str(e)}
    except Exception as e:
        frappe.db.rollback(save_point=savept)
        frappe.log_error(message=f"{doctype} {uuid}: {e}", title="Field Pro sync push")
        return {"client_uuid": uuid, "status": "failed", "reason": str(e)}


def _apply_table(table, tc, sp):
    spec = PUSH_TABLES[table]
    out = []
    for rec in (tc.get("created") or []):
        out.append(_push_one(spec, rec, sp))
    for rec in (tc.get("updated") or []):
        out.append({"client_uuid": rec.get("client_uuid") or rec.get("id"),
                    "id": rec.get("id"), "status": "rejected",
                    "reason": "updates are applied via the typed action endpoints, not sync (v1)"})
    for rid in (tc.get("deleted") or []):
        out.append({"id": rid, "status": "rejected",
                    "reason": "deletes from the device are not accepted (v1)"})
    return out


@frappe.whitelist()
@mobile_api
def push_changes(changes=None, last_pulled_at=None):
    """WatermelonDB push. Applies device-created records idempotently (by
    client_uuid) by routing each through its typed create endpoint, so
    server-side pricing/settlement/validation and identity all run. Returns
    explicit per-record results (ok / rejected / failed) — never silent.

    v1 scope: creates for visits, orders, payments, form responses, gps tracks
    (all referencing already-synced customers). Updates/deletes are reported as
    not-applied; use the typed action endpoints. New-customer push and
    local->server id remapping are a later increment."""
    sp = resolve_sales_person()
    if not sp:
        frappe.throw(_("Sync requires a linked Sales Person."), frappe.PermissionError)
    if isinstance(changes, str):
        changes = json.loads(changes or "{}")
    changes = changes or {}
    results = {}
    for table in PUSH_TABLES:
        results[table] = _apply_table(table, changes.get(table) or {}, sp)
    return {"results": results, "timestamp": _to_ms(now_datetime())}
