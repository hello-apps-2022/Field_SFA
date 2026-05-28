"""
Fix Leave Type quotas — setup_hr_integration creates the Leave Type records
but never sets max_leaves_allowed, so every type sits at 0. Without a non-zero
quota, allocate_leave_for_current_fy correctly refuses to create allocations
(zero days = nothing to allocate), and Leave Application then fails with
"Application period cannot be outside leave allocation period".

This patch sets the per-year quota on each balance-bearing leave type.
Unpaid Leave (is_lwp=1) stays at 0 — by definition it has no balance.

Idempotent: db_set only writes if the existing value differs.

Registered as: sfa_core.patches.v1_0.fix_leave_type_quotas
Order matters: this MUST run before allocate_leave_for_current_fy.
"""

import frappe

# Annual quotas decided per project (Stage 1 conversation):
#   Annual 21, Sick 14, Compassionate 5, Unpaid (lwp) — no balance
QUOTAS = {
    "Annual Leave":        21,
    "Sick Leave":          14,
    "Compassionate Leave": 5,
}


def execute():
    for lt_name, days in QUOTAS.items():
        if not frappe.db.exists("Leave Type", lt_name):
            print(f"  ? Leave Type {lt_name!r} missing — skipping. "
                  f"(setup_hr_integration should have created it.)")
            continue
        current = frappe.db.get_value("Leave Type", lt_name, "max_leaves_allowed") or 0
        if float(current) == float(days):
            continue
        frappe.db.set_value("Leave Type", lt_name, "max_leaves_allowed", days)
        print(f"  + {lt_name}: max_leaves_allowed {current} -> {days}")
    frappe.db.commit()
