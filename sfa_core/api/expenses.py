"""
Expense Claim API for the SPA.

Path: sfa_core.api.expenses  (SPA-facing — call() reads res.message; lists return
{items, total} per §3).

Endpoints:
  get_expense_claims(start, page_length, status, from_date, to_date, territory)
  get_expense_claim(name)
  create_expense_claim(payload)            -> Draft
  submit_expense_claim(name)               -> Pending Approval
  action_expense_claim(name, action)       -> workflow transition (approve/reject)
  get_expense_claim_meta()                 -> types, statuses for the form
"""

import json
import frappe
from frappe.utils import flt, getdate
from sfa_core.api.hr_common import (
    get_hr_context, scoped_employee_filter, assert_can_act_on,
)

COMPANY = "Hema Beverages Limited"
DEFAULT_COST_CENTER = "Main - HBL"

WORKFLOW_ACTIONS = {
    "approve": "Approve",
    "reject": "Reject",
}


@frappe.whitelist()
def get_expense_claims(start=0, page_length=50, status=None,
                       from_date=None, to_date=None, territory=None):
    ctx = get_hr_context()
    filters = scoped_employee_filter(ctx)

    # Optional manager/admin territory narrowing on top of the RBAC scope.
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
        filters["posting_date"] = ["between", [getdate(from_date), getdate(to_date)]]

    fields = ["name", "employee", "employee_name", "posting_date",
              "total_claimed_amount", "total_sanctioned_amount",
              "workflow_state", "status", "company",
              # Stage 4 — activity grouping; show in list for context.
              "custom_activity_type", "custom_purpose"]

    total = frappe.db.count("Expense Claim", filters)
    items = frappe.get_all("Expense Claim", filters=filters, fields=fields,
                           start=int(start), page_length=int(page_length),
                           order_by="posting_date desc, creation desc")

    # Server-side aggregate (matches Orders/Payments pattern).
    agg = frappe.db.get_all("Expense Claim", filters=filters,
                            fields=["sum(total_claimed_amount) as claimed",
                                    "sum(total_sanctioned_amount) as sanctioned"])
    totals = {
        "claimed": flt(agg[0].claimed) if agg else 0,
        "sanctioned": flt(agg[0].sanctioned) if agg else 0,
    }
    return {"items": items, "total": total, "totals": totals}


@frappe.whitelist()
def get_expense_claim(name):
    ctx = get_hr_context()
    doc = frappe.get_doc("Expense Claim", name)
    _assert_visible(ctx, doc.employee)
    return doc.as_dict()


@frappe.whitelist()
def create_expense_claim(payload):
    """
    payload: {
        expenses: [{expense_date, expense_type, amount, description}],
        remark,
        activity_type,  # one of the Select options on custom_activity_type
        purpose,        # free text
    }
    """
    ctx = get_hr_context()
    if not ctx.employee:
        frappe.throw("No Employee linked to your account.", frappe.PermissionError)
    if isinstance(payload, str):
        payload = json.loads(payload)

    doc = frappe.new_doc("Expense Claim")
    doc.employee = ctx.employee
    doc.company = COMPANY
    doc.posting_date = frappe.utils.today()
    doc.workflow_state = "Draft"
    doc.cost_center = DEFAULT_COST_CENTER

    # Activity tagging (Stage 4) — header-level grouping for reporting.
    # Fields added by patch v1_0.add_activity_fields_to_expense_claim.
    if payload.get("activity_type"):
        doc.custom_activity_type = payload["activity_type"]
    if payload.get("purpose"):
        doc.custom_purpose = payload["purpose"]

    for row in payload.get("expenses", []):
        doc.append("expenses", {
            "expense_date": row.get("expense_date") or frappe.utils.today(),
            "expense_type": row["expense_type"],
            "amount": flt(row["amount"]),
            "sanctioned_amount": flt(row["amount"]),
            "description": row.get("description", ""),
            # hrms requires a cost center on EACH expense line for GL posting,
            # not just the parent. Default to the company cost center.
            "cost_center": DEFAULT_COST_CENTER,
        })
    if payload.get("remark"):
        doc.remark = payload["remark"]

    doc.insert(ignore_permissions=True)
    return {"name": doc.name, "workflow_state": doc.workflow_state}


@frappe.whitelist()
def update_expense_claim_draft(name, payload):
    """
    Edit a Draft or Rejected claim — the rep's "fix and resubmit" path.
    Only the owner can update, only while the claim is editable (Draft/Rejected).
    Rebuilds the expenses child table from the payload (simpler than diffing).
    Submitting (workflow state advance) is still a separate call to
    submit_expense_claim, so the rep can save iteratively without committing.
    """
    ctx = get_hr_context()
    if not ctx.employee:
        frappe.throw("No Employee linked to your account.", frappe.PermissionError)
    if isinstance(payload, str):
        payload = json.loads(payload)

    doc = frappe.get_doc("Expense Claim", name)
    if doc.employee != ctx.employee:
        frappe.throw("You can only edit your own claims.", frappe.PermissionError)
    if doc.workflow_state not in ("Draft", "Rejected"):
        frappe.throw(
            f"This claim is {doc.workflow_state} and cannot be edited.",
            frappe.PermissionError,
        )

    # Header-level fields the rep is allowed to change.
    if "activity_type" in payload:
        doc.custom_activity_type = payload.get("activity_type") or ""
    if "purpose" in payload:
        doc.custom_purpose = payload.get("purpose") or ""
    if "remark" in payload:
        doc.remark = payload.get("remark") or ""

    # If a Rejected claim is being edited, the rep is acting on the previous
    # reason — wipe it so a fresh review starts clean.
    if doc.workflow_state == "Rejected":
        doc.custom_rejection_reason = ""
        # And bounce back to Draft so submit_expense_claim can route it through
        # the workflow again from a known starting point.
        doc.workflow_state = "Draft"
        doc.approval_status = "Draft"

    # Rebuild the lines from the payload.
    if "expenses" in payload:
        doc.set("expenses", [])
        for row in payload.get("expenses", []) or []:
            if not row.get("expense_type") or not row.get("amount"):
                continue
            doc.append("expenses", {
                "expense_date": row.get("expense_date") or frappe.utils.today(),
                "expense_type": row["expense_type"],
                "amount": flt(row["amount"]),
                "sanctioned_amount": flt(row["amount"]),
                "description": row.get("description", ""),
                "cost_center": DEFAULT_COST_CENTER,
            })

    doc.save(ignore_permissions=True)
    return {"name": doc.name, "workflow_state": doc.workflow_state}


@frappe.whitelist()
def submit_expense_claim(name):
    ctx = get_hr_context()
    doc = frappe.get_doc("Expense Claim", name)
    if doc.employee != ctx.employee and not ctx.is_admin:
        frappe.throw("You can only submit your own claims.", frappe.PermissionError)
    if doc.workflow_state != "Draft":
        frappe.throw(f"Claim is already {doc.workflow_state}.")
    _apply_workflow(doc, "Submit for Approval")
    return {"name": doc.name, "workflow_state": doc.workflow_state}


@frappe.whitelist()
def action_expense_claim(name, action, reason=None):
    """
    action: 'approve' or 'reject' (single-tier workflow).
    reason: required for reject; stored on custom_rejection_reason so the rep
            can see why and act on it.
    """
    ctx = get_hr_context()
    doc = frappe.get_doc("Expense Claim", name)
    assert_can_act_on(ctx, doc.employee)
    # Block self-approval: a manager who files a claim can't be the one to
    # approve/reject it. Admin can act on anyone's claim including their own
    # only if there's literally no other approver — kept here as a defense
    # against accidental misuse.
    if doc.employee == ctx.employee and not ctx.is_admin:
        frappe.throw("You cannot approve or reject your own claim.",
                     frappe.PermissionError)
    # Single-tier guard: anyone with manager OR admin role can approve.
    if not (ctx.is_manager or ctx.is_admin):
        frappe.throw("Only a manager or admin can approve or reject claims.",
                     frappe.PermissionError)
    wf_action = WORKFLOW_ACTIONS.get(action)
    if not wf_action:
        frappe.throw(f"Unknown action {action!r}.")

    # Rejection accountability — every reject must come with a reason so the rep
    # has something actionable, and the approver leaves a paper trail.
    is_reject = (action == "reject")
    if is_reject:
        reason_clean = (reason or "").strip()
        if not reason_clean:
            frappe.throw("A reason is required when rejecting a claim.")
        doc.custom_rejection_reason = reason_clean
        # Save the reason before the workflow transition fires; the workflow's
        # update_field/update_value handles the status field, but our custom
        # field needs an explicit save.
        doc.save(ignore_permissions=True)
    elif action == "approve" and doc.get("custom_rejection_reason"):
        # If a previously-rejected claim is being re-routed (e.g. resubmitted
        # after a fix), clear the stale reason so it doesn't confuse readers.
        doc.custom_rejection_reason = ""
        doc.save(ignore_permissions=True)

    _apply_workflow(doc, wf_action)
    return {"name": doc.name, "workflow_state": doc.workflow_state,
            "docstatus": doc.docstatus}


@frappe.whitelist()
def get_expense_claim_meta():
    types = frappe.get_all("Expense Claim Type", fields=["name"], order_by="name")
    return {
        "expense_types": [t.name for t in types],
        "statuses": ["Draft", "Pending Approval", "Approved", "Rejected"],
        # Stage 4 — populated from the Select field's options so the UI dropdown
        # stays in sync with the doctype definition (single source of truth).
        "activity_types": _get_activity_type_options(),
    }


def _get_activity_type_options():
    """Read Select options from the custom field; fall back to empty if missing."""
    try:
        meta = frappe.get_meta("Expense Claim")
        f = meta.get_field("custom_activity_type")
        if not f or not f.options:
            return []
        return [o for o in f.options.split("\n") if o.strip()]
    except Exception:
        return []


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
