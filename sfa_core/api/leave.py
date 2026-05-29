"""
Leave Application API for the SPA.

Path: sfa_core.api.leave  (lists return {items, total} per §3).

Endpoints:
  get_leave_applications(start, page_length, status, from_date, to_date, territory)
  get_leave_application(name)
  apply_leave(payload)                  -> Draft
  submit_leave(name)                    -> Pending Approval
  action_leave(name, action)            -> workflow transition
  get_leave_balance()                   -> per-type balance for current rep
  get_leave_meta()                      -> types, statuses
"""

import json
import frappe
from frappe.utils import getdate
from sfa_core.api.hr_common import (
    get_hr_context, scoped_employee_filter, assert_can_act_on,
)

WORKFLOW_ACTIONS = {
    "approve": "Approve",
    "reject": "Reject",
}


@frappe.whitelist()
def get_leave_applications(start=0, page_length=50, status=None,
                           from_date=None, to_date=None, territory=None):
    ctx = get_hr_context()
    filters = scoped_employee_filter(ctx)

    if territory and (ctx.is_admin or ctx.is_manager):
        emps = frappe.get_all("Sales Person",
                              filters={"custom_territory": territory,
                                       "custom_employee": ["is", "set"]},
                              fields=["custom_employee"])
        names = {e.custom_employee for e in emps if e.custom_employee}
        filters = dict(filters)
        filters["employee"] = ["in", sorted(names) or ["__none__"]]

    if status:
        filters["workflow_state"] = status
    if from_date and to_date:
        # Range-overlap match: include any leave whose date range INTERSECTS
        # the filter window, not just leaves whose start date falls inside.
        # E.g. a leave May 30 -> Jun 7 should appear in a "May" filter even
        # though its start is on the last day of the window.
        # Overlap condition: leave.from_date <= filter.to AND leave.to_date >= filter.from
        filters["from_date"] = ["<=", getdate(to_date)]
        filters["to_date"] = [">=", getdate(from_date)]

    fields = ["name", "employee", "employee_name", "leave_type",
              "from_date", "to_date", "total_leave_days",
              "workflow_state", "status"]

    total = frappe.db.count("Leave Application", filters)
    items = frappe.get_all("Leave Application", filters=filters, fields=fields,
                           start=int(start), page_length=int(page_length),
                           order_by="from_date desc, creation desc")
    return {"items": items, "total": total}


@frappe.whitelist()
def get_leave_application(name):
    ctx = get_hr_context()
    doc = frappe.get_doc("Leave Application", name)
    _assert_visible(ctx, doc.employee)
    return doc.as_dict()


@frappe.whitelist()
def apply_leave(payload):
    """payload: {leave_type, from_date, to_date, half_day(0/1), reason}"""
    ctx = get_hr_context()
    if not ctx.employee:
        frappe.throw("No Employee linked to your account.", frappe.PermissionError)
    if isinstance(payload, str):
        payload = json.loads(payload)

    doc = frappe.new_doc("Leave Application")
    doc.employee = ctx.employee
    doc.leave_type = payload["leave_type"]
    doc.from_date = getdate(payload["from_date"])
    doc.to_date = getdate(payload["to_date"])
    doc.half_day = int(payload.get("half_day", 0))
    doc.half_day_date = getdate(payload["half_day_date"]) if payload.get("half_day_date") else None
    doc.description = payload.get("reason", "")
    doc.workflow_state = "Draft"
    doc.status = "Open"
    doc.insert(ignore_permissions=True)
    leave_days = frappe.db.get_value("Leave Application", doc.name, "total_leave_days")
    return {"name": doc.name, "workflow_state": doc.workflow_state,
            "total_leave_days": leave_days}


@frappe.whitelist()
def update_leave_draft(name, payload):
    """
    Edit a Draft or Rejected leave application — the rep's fix-and-resubmit path.
    Owner-only, only while editable. Submitting is a separate call.
    """
    ctx = get_hr_context()
    if not ctx.employee:
        frappe.throw("No Employee linked to your account.", frappe.PermissionError)
    if isinstance(payload, str):
        payload = json.loads(payload)

    doc = frappe.get_doc("Leave Application", name)
    if doc.employee != ctx.employee:
        frappe.throw("You can only edit your own leave requests.", frappe.PermissionError)
    if doc.workflow_state not in ("Draft", "Rejected"):
        frappe.throw(
            f"This leave is {doc.workflow_state} and cannot be edited.",
            frappe.PermissionError,
        )

    if "leave_type" in payload:
        doc.leave_type = payload["leave_type"]
    if "from_date" in payload:
        doc.from_date = getdate(payload["from_date"])
    if "to_date" in payload:
        doc.to_date = getdate(payload["to_date"])
    if "half_day" in payload:
        doc.half_day = int(payload.get("half_day", 0))
        doc.half_day_date = getdate(payload["half_day_date"]) if payload.get("half_day_date") else None
    if "reason" in payload:
        doc.description = payload.get("reason", "")

    if doc.workflow_state == "Rejected":
        doc.custom_rejection_reason = ""
        doc.workflow_state = "Draft"
        doc.status = "Open"

    doc.save(ignore_permissions=True)
    return {"name": doc.name, "workflow_state": doc.workflow_state}


@frappe.whitelist()
def submit_leave(name):
    ctx = get_hr_context()
    doc = frappe.get_doc("Leave Application", name)
    if doc.employee != ctx.employee and not ctx.is_admin:
        frappe.throw("You can only submit your own leave.", frappe.PermissionError)
    if doc.workflow_state != "Draft":
        frappe.throw(f"Leave is already {doc.workflow_state}.")
    _apply_workflow(doc, "Submit for Approval")
    return {"name": doc.name, "workflow_state": doc.workflow_state}


@frappe.whitelist()
def action_leave(name, action, reason=None):
    """
    Mirror of action_expense_claim for Leave Application.
    reason: required on *_reject actions; stored on custom_rejection_reason.
    """
    ctx = get_hr_context()
    doc = frappe.get_doc("Leave Application", name)
    assert_can_act_on(ctx, doc.employee)
    if doc.employee == ctx.employee and not ctx.is_admin:
        frappe.throw("You cannot approve or reject your own leave.",
                     frappe.PermissionError)
    if not (ctx.is_manager or ctx.is_admin):
        frappe.throw("Only a manager or admin can approve or reject leave requests.",
                     frappe.PermissionError)
    wf_action = WORKFLOW_ACTIONS.get(action)
    if not wf_action:
        frappe.throw(f"Unknown action {action!r}.")

    is_reject = (action == "reject")
    if is_reject:
        reason_clean = (reason or "").strip()
        if not reason_clean:
            frappe.throw("A reason is required when rejecting a leave request.")
        doc.custom_rejection_reason = reason_clean
        doc.save(ignore_permissions=True)
    elif action == "approve" and doc.get("custom_rejection_reason"):
        doc.custom_rejection_reason = ""
        doc.save(ignore_permissions=True)

    _apply_workflow(doc, wf_action)
    return {"name": doc.name, "workflow_state": doc.workflow_state,
            "docstatus": doc.docstatus}


@frappe.whitelist()
def get_leave_balance():
    """
    Per-type *effective remaining* balance — what the rep can still plan with.

    hrms's get_leave_balance_on returns the as-of-today ledger balance; future-
    dated approved leaves aren't deducted until the leave actually starts. For
    a planning UI that's confusing (a rep with 14 Sick Leave who's already
    locked Aug 10-13 still sees 14, but they only have 10 left to plan).

    We subtract days from approved, future-dated leaves so the strip reads as
    "how much you can still take" instead of "what's on the ledger today".
    """
    ctx = get_hr_context()
    if not ctx.employee:
        return {"balances": []}
    from hrms.hr.doctype.leave_application.leave_application import get_leave_balance_on
    types = frappe.get_all("Leave Type", fields=["name"])
    today = frappe.utils.today()

    # Future-dated approved leaves not yet deducted from hrms's ledger.
    # docstatus=1 + status='Approved' + from_date > today.
    future_approved = frappe.db.sql("""
        select leave_type, sum(total_leave_days) as days
        from `tabLeave Application`
        where employee = %(emp)s and docstatus = 1 and status = 'Approved'
          and from_date > %(today)s
        group by leave_type
    """, {"emp": ctx.employee, "today": today}, as_dict=1)
    future_days = {r.leave_type: float(r.days or 0) for r in future_approved}

    balances = []
    for t in types:
        try:
            bal = get_leave_balance_on(ctx.employee, t.name, today)
        except Exception:
            bal = None
        if bal is not None:
            bal = float(bal) - future_days.get(t.name, 0.0)
        balances.append({"leave_type": t.name, "balance": bal})
    return {"balances": balances}


@frappe.whitelist()
def get_leave_meta():
    types = frappe.get_all("Leave Type", fields=["name"], order_by="name")
    return {
        "leave_types": [t.name for t in types],
        "statuses": ["Draft", "Pending Approval", "Approved", "Rejected"],
    }


# ── helpers ──────────────────────────────────────────────────────────────────

def _assert_visible(ctx, employee):
    if ctx.is_admin:
        return
    f = scoped_employee_filter(ctx)
    emp_filter = f.get("employee")
    if emp_filter is None:
        return
    if isinstance(emp_filter, list) and emp_filter[0] == "in":
        if employee not in emp_filter[1]:
            frappe.throw("Not permitted.", frappe.PermissionError)
    elif emp_filter != employee:
        frappe.throw("Not permitted.", frappe.PermissionError)


def _apply_workflow(doc, action):
    from frappe.model.workflow import apply_workflow
    apply_workflow(doc, action)
