"""
Stage 5 — rejection reason capture.

When a manager or finance rejects a claim/leave, they're required to explain why
(approver accountability + a paper trail the rep can act on). This patch adds a
free-text 'Rejection Reason' field on both Expense Claim and Leave Application.

  custom_rejection_reason (Small Text) — stamped by the API on any *_reject action.
                                          Shown back to the rep in the drawer so
                                          they can fix and resubmit.

Idempotent: create_custom_fields skips fields that already exist.
Registered as: sfa_core.patches.v1_0.add_rejection_reason_fields
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    fields = {
        "fieldname": "custom_rejection_reason",
        "label": "Rejection Reason",
        "fieldtype": "Small Text",
        # Place near the workflow_state column so it sits with other approval-status
        # context; if workflow_state isn't a known anchor on a doctype, the field
        # just lands at the end, which is fine.
        "insert_after": "workflow_state",
        "in_list_view": 0,
        "read_only": 1,  # set only by the API, never user-edited directly
        "description": "Reason given by the approver when this was rejected.",
    }
    create_custom_fields(
        {
            "Expense Claim": [fields],
            "Leave Application": [fields],
        },
        ignore_validate=True,
    )
    frappe.db.commit()
