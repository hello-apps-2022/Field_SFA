"""
Shared resolver for the HR (expense/leave) APIs.

Bridges the SFA identity (Sales Person/territory — the RBAC anchor) to the HR identity
(Employee — what Expense Claim / Leave Application key off). This is the ONLY place the
two identity models meet; the rest of SFA is untouched.

Path: sfa_core.api.hr_common  (SPA-facing api/ tree — §2)
"""

import frappe


class HRContext:
    def __init__(self, user, sales_person, employee, territory, is_admin, is_manager, is_rep):
        self.user = user
        self.sales_person = sales_person
        self.employee = employee
        self.territory = territory
        self.is_admin = is_admin
        self.is_manager = is_manager
        self.is_rep = is_rep


def get_hr_context():
    """Resolve the current session user into an HRContext, mirroring the auth chain in §3."""
    user = frappe.session.user
    roles = set(frappe.get_roles(user))
    is_admin = "SFA Admin" in roles
    is_manager = "SFA Manager" in roles
    is_rep = "SFA Rep" in roles

    sp = frappe.db.get_value(
        "Sales Person",
        {"custom_user_id": user},
        ["name", "custom_territory", "custom_employee"],
        as_dict=True,
    )

    sales_person = sp.name if sp else None
    territory = sp.custom_territory if sp else None
    employee = sp.custom_employee if sp else None

    # Fallback: resolve Employee directly by user_id if the link is missing.
    if not employee:
        employee = frappe.db.get_value("Employee", {"user_id": user}, "name")

    return HRContext(user, sales_person, employee, territory,
                     is_admin, is_manager, is_rep)


def scoped_employee_filter(ctx):
    """
    Return a filter dict constraining HR docs to what `ctx` may see:
      - admin/finance: everything (no employee filter)
      - manager: all reps in their territory
      - rep: only their own Employee
    Raises if a non-admin has no resolvable identity.
    """
    if ctx.is_admin:
        return {}

    if ctx.is_manager:
        emps = _employees_in_territory(ctx.territory)
        # include the manager's own Employee too
        if ctx.employee:
            emps.add(ctx.employee)
        if not emps:
            return {"employee": "__none__"}  # matches nothing
        return {"employee": ["in", sorted(emps)]}

    # rep
    if not ctx.employee:
        frappe.throw("No Employee record linked to your account. "
                     "Contact an administrator.", frappe.PermissionError)
    return {"employee": ctx.employee}


def _employees_in_territory(territory):
    """All Employees linked to Sales Persons in the given territory."""
    if not territory:
        return set()
    rows = frappe.get_all(
        "Sales Person",
        filters={"custom_territory": territory, "custom_employee": ["is", "set"]},
        fields=["custom_employee"],
    )
    return {r.custom_employee for r in rows if r.custom_employee}


def assert_can_act_on(ctx, employee):
    """Guard used by approve/reject: may ctx approve a doc belonging to `employee`?"""
    if ctx.is_admin:
        return
    if ctx.is_manager:
        allowed = _employees_in_territory(ctx.territory)
        if ctx.employee:
            allowed.add(ctx.employee)
        if employee not in allowed:
            frappe.throw("You can only act on requests within your territory.",
                         frappe.PermissionError)
        return
    frappe.throw("You are not permitted to approve requests.", frappe.PermissionError)
