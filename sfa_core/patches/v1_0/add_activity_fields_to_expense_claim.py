"""
Stage 4 — activity-type tagging on Expense Claim.

Adds two custom fields at the claim header level so reps can group a claim by
what it was for, and reports can aggregate by activity. Header-level (not per
line) — one tag for the whole trip/event.

  custom_activity_type  (Select) — Field Visit / Product Launch / Distributor
                                   Meeting / Training / Administrative / Other.
                                   Drives reporting; pre-defined for consistency.
  custom_purpose        (Small Text) — free-text specifics ("Cheetah Launch –
                                       Kayunga East door-to-door, 28 May").

Idempotent: skips fields that already exist; safe to re-run.
Registered as: sfa_core.patches.v1_0.add_activity_fields_to_expense_claim
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


ACTIVITY_TYPES = [
    "",  # blank default
    "Field Visit",
    "Product Launch",
    "Distributor Meeting",
    "Training",
    "Administrative",
    "Other",
]


def execute():
    create_custom_fields(
        {
            "Expense Claim": [
                {
                    "fieldname": "custom_activity_type",
                    "label": "Activity Type",
                    "fieldtype": "Select",
                    "options": "\n".join(ACTIVITY_TYPES),
                    # Place after the existing 'department' column so it lives
                    # in the natural "context about this claim" area, not buried.
                    "insert_after": "department",
                    "in_list_view": 1,
                    "in_standard_filter": 1,
                },
                {
                    "fieldname": "custom_purpose",
                    "label": "Purpose",
                    "fieldtype": "Small Text",
                    "insert_after": "custom_activity_type",
                    "in_list_view": 0,
                    "description": "What this claim was for, e.g. 'Cheetah Launch — Kayunga East'",
                },
            ]
        },
        ignore_validate=True,
    )
    frappe.db.commit()
