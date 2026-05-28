"""
Stage 6.5 — allocate annual leave balances for all employees.

hrms's Leave Application requires a matching Leave Allocation covering the
application's date range — without one, applications fail with
"Application period cannot be outside leave allocation period". This patch
seeds full-year allocations for every active employee × every balance-bearing
leave type (i.e. leave types where is_lwp = 0).

Allocation period: financial year Apr 1 — Mar 31.

Pro-rating: NONE. Every employee gets the full max_leaves_allowed for the FY
regardless of hire date. Decision per project — when the team is small the
admin overhead of pro-rating outweighs the policy nicety. Revisit if/when
hiring volume grows.

Idempotent — skips employees who already have an allocation for that
leave type covering this FY. Safe to re-run; safe to register in patches.txt
(it just becomes a no-op once everyone is allocated).

For future financial years: re-run this patch after updating the FY constants,
OR replace with a scheduled job. Either way, allocations are only good for one
FY and need fresh ones each year.

Registered as: sfa_core.patches.v1_0.allocate_leave_for_current_fy
"""

import frappe
from frappe.utils import getdate, today


def _current_fy_range():
    """Return (from_date, to_date) for the financial year containing today.

    FY runs Apr 1 — Mar 31. If today is Jan-Mar, we're in the FY that started
    last April; otherwise we're in the FY that started this April.
    """
    t = getdate(today())
    if t.month >= 4:
        from_year = t.year
    else:
        from_year = t.year - 1
    from_date = f"{from_year}-04-01"
    to_date = f"{from_year + 1}-03-31"
    return from_date, to_date


def execute():
    from_date, to_date = _current_fy_range()
    print(f"[allocate_leave_for_current_fy] FY: {from_date} -> {to_date}")

    # Active employees only — no point allocating to inactive/left employees,
    # and Leave Allocation on a non-active emp would fail validation.
    employees = frappe.get_all(
        "Employee",
        filters={"status": "Active"},
        fields=["name", "employee_name"],
    )
    # Balance-bearing leave types: skip Unpaid Leave (is_lwp=1) — those don't
    # need allocations; hrms tracks them by direct application without a pool.
    leave_types = frappe.get_all(
        "Leave Type",
        filters={"is_lwp": 0},
        fields=["name", "max_leaves_allowed"],
    )

    created = 0
    skipped_existing = 0
    skipped_zero_max = 0

    for emp in employees:
        for lt in leave_types:
            max_days = lt.get("max_leaves_allowed") or 0
            if max_days <= 0:
                # Leave type with no annual cap — nothing to allocate.
                # (Unusual; would catch a misconfigured type.)
                skipped_zero_max += 1
                continue

            existing = frappe.db.exists(
                "Leave Allocation",
                {
                    "employee": emp.name,
                    "leave_type": lt.name,
                    "from_date": from_date,
                    "to_date": to_date,
                    "docstatus": ["!=", 2],  # ignore cancelled
                },
            )
            if existing:
                skipped_existing += 1
                continue

            try:
                alloc = frappe.get_doc({
                    "doctype": "Leave Allocation",
                    "employee": emp.name,
                    "leave_type": lt.name,
                    "from_date": from_date,
                    "to_date": to_date,
                    "new_leaves_allocated": max_days,
                    "carry_forward": 0,
                })
                alloc.insert(ignore_permissions=True)
                alloc.submit()
                created += 1
                print(
                    f"  + {max_days} {lt.name} for "
                    f"{emp.employee_name or emp.name}"
                )
            except Exception as e:
                # Don't let one bad employee/type combo abort the whole patch.
                # Surface the issue but keep going.
                print(
                    f"  ! FAILED {lt.name} for {emp.name}: {e}"
                )

    frappe.db.commit()
    print(
        f"[allocate_leave_for_current_fy] done — "
        f"created={created} skipped_existing={skipped_existing} "
        f"skipped_zero_max={skipped_zero_max}"
    )
