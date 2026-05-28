"""
Stage 6 — collapse two-tier approval to single-tier (Pending Approval).

The original workflow had separate Manager and Finance tiers, but Hema doesn't
have a dedicated finance approver yet. Two clicks by the same person was just
bureaucratic theater. Until a finance role exists, both Managers and Admins
can approve in a single step.

New state machine (both Expense Claim and Leave Application):
    Draft
      -> Pending Approval (rep submits)
      -> Approved          (Manager OR Admin approves -> docstatus 1, GL post)
    Rejected at the approval step -> Rejected (docstatus 0; editable & resubmittable)

The actual workflow definition lives in setup_hr_workflows.py — this patch:
  1. Re-runs that seeder so the workflow object reflects the new state machine,
  2. Remaps any in-flight docs from old states to the new "Pending Approval".

The remap is necessary because the old states ("Pending Manager Approval" /
"Pending Finance Approval") may not exist after the workflow is rewritten,
and any doc with a stale state would be unactionable in the UI.

Registered as: sfa_core.patches.v1_0.collapse_to_single_tier_approval
"""

import frappe


# State remap: any claim in one of these old states becomes "Pending Approval".
# Note: a doc already at "Approved" or "Rejected" is left alone — those are
# terminal states that survived the old workflow and remain valid in the new one.
OLD_TO_NEW_STATE = {
    "Pending Manager Approval": "Pending Approval",
    "Pending Finance Approval": "Pending Approval",
}

DOCTYPES = ["Expense Claim", "Leave Application"]


def execute():
    # 1. Re-run the workflow seeder so the Workflow doc is rewritten to the
    #    new single-tier shape. (Idempotent — overwrites states/transitions.)
    from sfa_core.patches.v1_0 import setup_hr_workflows
    setup_hr_workflows.execute()

    # 2. Remap in-flight docs whose workflow_state no longer exists in the new
    #    workflow. Set workflow_state directly (not via apply_workflow, since
    #    there's no transition from the old states to the new ones).
    remapped = {dt: 0 for dt in DOCTYPES}
    for dt in DOCTYPES:
        for old_state, new_state in OLD_TO_NEW_STATE.items():
            names = frappe.get_all(dt, filters={"workflow_state": old_state}, pluck="name")
            for name in names:
                # db_set bypasses validations and on_update hooks — safe here since
                # we're only changing a string state column on a draft doc; no
                # transition-side-effects need to fire.
                frappe.db.set_value(dt, name, "workflow_state", new_state)
                remapped[dt] += 1

    frappe.db.commit()

    if any(remapped.values()):
        print(f"[collapse_to_single_tier_approval] remapped: {remapped}")
