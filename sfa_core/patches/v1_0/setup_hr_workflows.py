"""
Stage 3 (revised in Stage 6) — single-tier approval Workflows for Expense Claim
& Leave Application. Originally two-tier; collapsed because Hema doesn't have a
dedicated finance approver yet.

State machine (both doctypes):
    Draft
      -> Pending Approval   (rep submits)
      -> Approved           (SFA Manager OR SFA Admin approves -> docstatus 1, GL post)
    Rejected at the approval step -> Rejected (docstatus 0; editable & resubmittable)

Approval is allowed for SFA Manager OR SFA Admin (newline-joined in the
transition's 'allowed' field). Territory scoping for managers is enforced in
the API layer; the workflow's role gate is defense in depth.

Registered as: sfa_core.patches.v1_0.setup_hr_workflows
Idempotent: recreates transitions if the workflow exists but is out of date.
"""

import frappe

MANAGER_ROLE = "SFA Manager"
ADMIN_ROLE = "SFA Admin"
# Frappe Workflow Transition's 'allowed' field is a Link to Role — exactly ONE
# role per row. To grant "any of these roles can take this transition" we emit
# multiple transition rows (one per role) with the same action label and same
# from/to states. Frappe treats matching action labels as the same UI button,
# so the user sees ONE Approve action; the workflow engine picks the row whose
# 'allowed' role the actor has. (Earlier experiment with newline-joining the
# string failed with LinkValidationError — Frappe tried to find a role literally
# named "SFA Manager\nSFA Admin".)
APPROVER_ROLES = [MANAGER_ROLE, ADMIN_ROLE]

# Single-tier state machine. (state, doc_status, style)
# Was two-tier (Pending Manager / Pending Finance) — collapsed in stage 6 because
# Hema doesn't have a dedicated finance approver yet; the two-tier flow was just
# making the same admin click twice. Reintroduce tiers if/when a finance role
# is genuinely staffed.
STATES = [
    ("Draft", "0", "Warning"),
    ("Pending Approval", "0", "Info"),
    ("Approved", "1", "Success"),
    # Rejected stays at docstatus 0 (a turned-down draft, not a cancelled submitted
    # doc). Frappe forbids 0->2 transition (must submit before cancel); 0->0 is fine,
    # and lets a rejected claim be edited + resubmitted.
    ("Rejected", "0", "Danger"),
]

# (action, from, to, allowed_role, condition_or_None, allow_self_approval)
# allow_self_approval: 1 only for "Submit for Approval" — a rep IS submitting their
# own draft by definition. Approve/Reject keep 0 so a manager/admin can't act on
# their own claim (API guards this too; workflow flag is defense in depth).
TRANSITIONS = [
    ("Submit for Approval", "Draft", "Pending Approval", None, None, 1),
    ("Approve", "Pending Approval", "Approved", APPROVER_ROLES, None, 0),
    ("Reject", "Pending Approval", "Rejected", APPROVER_ROLES, None, 0),
]

# hrms's Expense Claim and Leave Application each enforce their OWN native status
# field in on_submit (independent of workflow_state). Each state maps to
# (native_field, value) so the status flips BEFORE the docstatus-1 submit fires.
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
            "Pending Approval": "Draft",
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
            "Pending Approval": "Open",
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
        # The 'allowed' field on Workflow Transition is a Link to Role (one value
        # per row). To allow multiple roles for the same logical action, emit a
        # separate transition row per role — Frappe treats rows with matching
        # action labels as the same UI button.
        roles = role if isinstance(role, (list, tuple)) else [role or "SFA Rep"]
        for r in roles:
            row = {
                "state": frm,
                "action": action,
                "next_state": to,
                "allowed": r,
                "allow_self_approval": allow_self,
            }
            if condition:
                row["condition"] = condition
            doc.append("transitions", row)

    doc.save(ignore_permissions=True)


def _editor_for_state(state):
    if state == "Draft":
        return "SFA Rep"
    if state == "Pending Approval":
        # Either approver role can edit while the doc is in their court.
        # Frappe's allow_edit takes a single role; pick MANAGER_ROLE since it's
        # the lower-privilege role (admins have access regardless via role
        # inheritance on most installs).
        return MANAGER_ROLE
    # Terminal states (Approved/Rejected) — only admin can touch after the fact.
    return ADMIN_ROLE
