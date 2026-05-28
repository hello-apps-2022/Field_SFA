"""
Stage 3 — two-tier approval Workflows for Expense Claim & Leave Application.

State machine (both doctypes):
    Draft
      -> Pending Manager Approval   (rep submits)
      -> Pending Finance Approval   (Tier 1: SFA Manager approves)
      -> Approved                   (Tier 2: SFA Admin/finance approves -> docstatus 1, GL post)
    Rejected at either tier -> Rejected (docstatus 0; editable & resubmittable)

Tier 1 transition is allowed for SFA Manager; territory scoping (manager only acts on
their own territory's reps) is enforced in the API layer + a transition `condition`,
because Workflow conditions can read doc fields but not the full Sales Person->territory
chain cleanly. The API is the authoritative RBAC gate; the workflow condition is defense
in depth.

Registered as: sfa_core.patches.v1_0.setup_hr_workflows
Idempotent: recreates transitions if the workflow exists but is out of date.
"""

import frappe

MANAGER_ROLE = "SFA Manager"
FINANCE_ROLE = "SFA Admin"

# Workflow states shared by both doctypes. (state, doc_status, style)
STATES = [
    ("Draft", "0", "Warning"),
    ("Pending Manager Approval", "0", "Info"),
    ("Pending Finance Approval", "0", "Primary"),
    ("Approved", "1", "Success"),
    # Rejected stays at docstatus 0 (a turned-down draft, not a cancelled submitted
    # doc). Frappe forbids a 0->2 transition (must submit before cancel); 0->0 is fine,
    # and it lets a rejected claim be edited + resubmitted. See project-state s11.
    ("Rejected", "0", "Danger"),
]

# (action, from, to, allowed_role, condition_or_None, allow_self_approval)
# allow_self_approval: 1 only for "Submit for Approval" — a rep IS submitting their
# own draft by definition, so the strict self-approval guard would block them. The
# four manager/finance transitions keep 0 so a manager can't approve their own
# claim (the API also guards this; the workflow flag is defense in depth).
TRANSITIONS = [
    ("Submit for Approval", "Draft", "Pending Manager Approval", None, None, 1),
    ("Manager Approve", "Pending Manager Approval", "Pending Finance Approval",
     MANAGER_ROLE, None, 0),
    ("Manager Reject", "Pending Manager Approval", "Rejected", MANAGER_ROLE, None, 0),
    ("Finance Approve", "Pending Finance Approval", "Approved", FINANCE_ROLE, None, 0),
    ("Finance Reject", "Pending Finance Approval", "Rejected", FINANCE_ROLE, None, 0),
]

# hrms's Expense Claim and Leave Application each enforce their OWN native status
# field in on_submit (independent of workflow_state). The workflow must drive that
# native field, or on_submit throws ("Approval Status must be 'Approved'/'Rejected'")
# and GL never posts. Each state maps to (native_field, value) so the status flips
# BEFORE the docstatus-1 submit fires.
#   Expense Claim: approval_status in {Draft, Approved, Rejected}
#   Leave Application: status in {Open, Approved, Rejected, Cancelled}
WORKFLOWS = [
    {
        "workflow_name": "FieldPro Expense Claim Approval",
        "document_type": "Expense Claim",
        "workflow_state_field": "workflow_state",
        "status_field": "approval_status",
        "state_status": {
            "Draft": "Draft",
            "Pending Manager Approval": "Draft",
            "Pending Finance Approval": "Draft",
            "Approved": "Approved",
            "Rejected": "Rejected",
        },
    },
    {
        "workflow_name": "FieldPro Leave Approval",
        "document_type": "Leave Application",
        "workflow_state_field": "workflow_state",
        "status_field": "status",
        "state_status": {
            "Draft": "Open",
            "Pending Manager Approval": "Open",
            "Pending Finance Approval": "Open",
            "Approved": "Approved",
            "Rejected": "Rejected",
        },
    },
]


def execute():
    _ensure_workflow_state_masters()
    _ensure_workflow_action_masters()
    for wf in WORKFLOWS:
        _seed_workflow(wf)
    frappe.db.commit()


def _ensure_workflow_state_masters():
    for state, _ds, style in STATES:
        if not frappe.db.exists("Workflow State", state):
            frappe.get_doc({
                "doctype": "Workflow State",
                "workflow_state_name": state,
                "style": style,
            }).insert(ignore_permissions=True)


def _ensure_workflow_action_masters():
    actions = {t[0] for t in TRANSITIONS}
    for action in actions:
        if not frappe.db.exists("Workflow Action Master", action):
            frappe.get_doc({
                "doctype": "Workflow Action Master",
                "workflow_action_name": action,
            }).insert(ignore_permissions=True)


def _seed_workflow(wf):
    name = wf["workflow_name"]
    existing = frappe.db.exists("Workflow", name)
    doc = frappe.get_doc("Workflow", name) if existing else frappe.new_doc("Workflow")

    doc.workflow_name = name
    doc.document_type = wf["document_type"]
    doc.workflow_state_field = wf["workflow_state_field"]
    doc.is_active = 1
    doc.send_email_alert = 0
    doc.override_status = 0

    doc.set("states", [])
    status_field = wf.get("status_field")
    state_status = wf.get("state_status", {})
    for state, ds, style in STATES:
        row = {
            "state": state,
            "doc_status": ds,
            "style": style,
            # Allow the relevant role to edit while the doc sits in its court.
            "allow_edit": _editor_for_state(state),
        }
        # Drive the doctype's NATIVE status field so on_submit passes & GL posts.
        if status_field and state in state_status:
            row["update_field"] = status_field
            row["update_value"] = state_status[state]
        doc.append("states", row)

    doc.set("transitions", [])
    for action, frm, to, role, condition, allow_self in TRANSITIONS:
        row = {
            "state": frm,
            "action": action,
            "next_state": to,
            "allowed": role or "SFA Rep",
            "allow_self_approval": allow_self,
        }
        if condition:
            row["condition"] = condition
        doc.append("transitions", row)

    doc.save(ignore_permissions=True)


def _editor_for_state(state):
    if state == "Draft":
        return "SFA Rep"
    if state == "Pending Manager Approval":
        return MANAGER_ROLE
    if state == "Pending Finance Approval":
        return FINANCE_ROLE
    return FINANCE_ROLE
