"""
Stage 1 — HR integration setup & seed.

Idempotent. Safe to re-run on every migrate (mirrors the gamification-seed pattern in §5).
- Sets Company.default_expense_claim_payable_account
- Seeds Uganda-specific Expense Claim Types mapped to existing CoA expense accounts
- Seeds Leave Types with sane allocations

Registered in apps/sfa_core/patches.txt (APP ROOT — see §6) as:
    sfa_core.patches.v1_0.setup_hr_integration
"""

import frappe

COMPANY = "Hema Beverages Limited"
ABBR = "HBL"
PAYABLE_ACCOUNT = f"Creditors - {ABBR}"
DEFAULT_COST_CENTER = f"Main - {ABBR}"

# Expense Claim Type -> GL expense account (existing CoA leaf accounts only).
# Per Diem / Fuel / Lodging intentionally share Travel Expenses; SFA-layer type
# names preserve per-category reporting even when GL account is shared.
# To split later: add dedicated accounts + change the mapping here (one-line edit).
EXPENSE_CLAIM_TYPES = [
    ("Per Diem", f"Travel Expenses - {ABBR}"),
    ("Fuel / Transport", f"Travel Expenses - {ABBR}"),
    ("Airtime / Data", f"Telephone Expenses - {ABBR}"),
    ("Lodging", f"Travel Expenses - {ABBR}"),
    ("Meals / Entertainment", f"Entertainment Expenses - {ABBR}"),
    ("Other", f"Miscellaneous Expenses - {ABBR}"),
]

# Leave Type -> dict of config. Allocation itself is per-employee (done elsewhere);
# these are the type definitions.
LEAVE_TYPES = [
    {"leave_type_name": "Annual Leave", "max_continuous_days_allowed": 21,
     "is_carry_forward": 1, "include_holiday": 0},
    {"leave_type_name": "Sick Leave", "max_continuous_days_allowed": 14,
     "is_carry_forward": 0, "include_holiday": 0},
    {"leave_type_name": "Unpaid Leave", "max_continuous_days_allowed": 0,
     "is_carry_forward": 0, "include_holiday": 0, "is_lwp": 1},
    {"leave_type_name": "Compassionate Leave", "max_continuous_days_allowed": 5,
     "is_carry_forward": 0, "include_holiday": 0},
]


def execute():
    if not frappe.db.exists("Company", COMPANY):
        frappe.log_error(f"[hr_setup] Company {COMPANY!r} not found; skipping HR seed.")
        return

    _set_company_payable_account()
    _seed_expense_claim_types()
    _seed_leave_types()
    frappe.db.commit()


def _set_company_payable_account():
    # hrms adds this field on install; guard in case of ordering.
    if not frappe.db.has_column("Company", "default_expense_claim_payable_account"):
        frappe.log_error("[hr_setup] default_expense_claim_payable_account column missing; "
                         "is hrms migrated? Skipping payable-account default.")
        return
    if not frappe.db.exists("Account", PAYABLE_ACCOUNT):
        frappe.log_error(f"[hr_setup] payable account {PAYABLE_ACCOUNT!r} missing; skipping.")
        return
    current = frappe.db.get_value("Company", COMPANY, "default_expense_claim_payable_account")
    if current != PAYABLE_ACCOUNT:
        frappe.db.set_value("Company", COMPANY, "default_expense_claim_payable_account",
                            PAYABLE_ACCOUNT)


def _seed_expense_claim_types():
    for type_name, account in EXPENSE_CLAIM_TYPES:
        if not frappe.db.exists("Account", account):
            frappe.log_error(f"[hr_setup] account {account!r} missing for claim type "
                             f"{type_name!r}; skipping this type.")
            continue
        if frappe.db.exists("Expense Claim Type", type_name):
            _ensure_account_row(type_name, account)
            continue
        doc = frappe.new_doc("Expense Claim Type")
        doc.expense_type = type_name
        doc.append("accounts", {
            "company": COMPANY,
            "default_account": account,
        })
        doc.insert(ignore_permissions=True)


def _ensure_account_row(type_name, account):
    """If the type exists but has no account row for our company, add it."""
    doc = frappe.get_doc("Expense Claim Type", type_name)
    has_company = any(r.company == COMPANY for r in doc.accounts)
    if not has_company:
        doc.append("accounts", {"company": COMPANY, "default_account": account})
        doc.save(ignore_permissions=True)


def _seed_leave_types():
    for cfg in LEAVE_TYPES:
        name = cfg["leave_type_name"]
        if frappe.db.exists("Leave Type", name):
            continue
        doc = frappe.new_doc("Leave Type")
        doc.update(cfg)
        doc.insert(ignore_permissions=True)
