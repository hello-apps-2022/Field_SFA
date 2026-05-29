# sfa_core/api/leave_validation.py
"""
Effective-balance pre-submit validator for Leave Applications.

WHY
---
hrms's submit-time check uses the leave LEDGER balance as-of the application's
from_date. The ledger only counts entries dated on/before that date, so an
APPROVED leave dated later than this one is invisible to it. Result: a rep with
days already locked in a future month can still over-apply, because hrms thinks
those days are free.

This re-checks the requested days against the EFFECTIVE balance (allocation
minus ALL submitted leaves in the period, including future-dated ones) and
blocks the application if it would over-draw.

HOW IT'S WIRED
--------------
doc_events -> Leave Application -> validate   (see hooks.py).
Frappe runs validate on every save AND on submit, so this single function
covers: rep create/edit, rep submit (Draft->Pending), and manager approve
(Pending->Approved) -- from the SPA and from Desk alike. No dead ends.

NOTE: hooks live in redis cache. After editing hooks.py you MUST run
`bench --site <site> clear-cache` (and restart) or the new hook won't register.

ON THE BALANCE SOURCE
---------------------
This is self-contained: it uses hrms's own get_leave_balance_on() with
consider_all_leaves_in_the_allocation_period=True, which counts every submitted
(=approved) leave in the allocation period regardless of date. That's the same
"approved-only, future-inclusive" number your UI wrapper produces. Once you
share get_leave_balance, we can extract a single shared core so the displayed
balance and this check are guaranteed to use identical logic.

Quick sanity check (bench --site hema.local console):
    from sfa_core.api.leave_validation import _effective_balance
    import frappe
    _effective_balance("HR-EMP-00001", "Sick Leave", frappe.utils.nowdate())  # -> number
"""

import frappe
from frappe import _
from hrms.hr.doctype.leave_application.leave_application import get_number_of_leave_days


def validate_effective_leave_balance(doc, method=None):
    if not _is_quota_tracked(doc):
        return

    requested = get_number_of_leave_days(
        doc.employee,
        doc.leave_type,
        doc.from_date,
        doc.to_date,
        doc.half_day,        # 0/None until half-day ships; then this is honored
        doc.half_day_date,
    )

    effective = _effective_balance(doc.employee, doc.leave_type, doc.from_date)

    if requested > effective:
        frappe.throw(
            _(
                "Not enough {0} balance: {1} day(s) available after approved "
                "future leave, but this application needs {2} day(s)."
            ).format(doc.leave_type, effective, requested),
            title=_("Leave Balance Exceeded"),
        )


def _effective_balance(employee, leave_type, on_date):
    """Approved-only, future-inclusive balance for the allocation period that
    `on_date` falls in.

    consider_all_leaves_in_the_allocation_period=True is the key: it ignores the
    as-of-date cutoff (the source of the original bug) and nets out every
    submitted leave in the period, including ones dated after this application.
    The current doc isn't submitted yet at validate time, so it never counts
    against itself.
    """
    from hrms.hr.doctype.leave_application.leave_application import get_leave_balance_on

    balance = get_leave_balance_on(
        employee,
        leave_type,
        on_date,
        consider_all_leaves_in_the_allocation_period=True,
    )
    if isinstance(balance, dict):          # only with for_consumption=True
        balance = balance.get("leave_balance", 0)
    return float(balance or 0)


def _is_quota_tracked(doc):
    """Skip LWP and any type with no allocation for this employee/period."""
    if frappe.db.get_value("Leave Type", doc.leave_type, "is_lwp"):
        return False
    return bool(
        frappe.db.exists(
            "Leave Allocation",
            {
                "employee": doc.employee,
                "leave_type": doc.leave_type,
                "docstatus": 1,
                "from_date": ["<=", doc.from_date],
                "to_date": [">=", doc.to_date],
            },
        )
    )
