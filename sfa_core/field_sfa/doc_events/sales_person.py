"""
Stage 2b — Sales Person <-> Employee provisioning & sync.

The linked-identity model (chosen over full re-point):
  - Sales Person stays the SFA/RBAC anchor (territory, customers, gamification).
  - Employee is a first-class linked HR identity, enforced 1:1 via custom_employee.
  - SFA resolution (auth.py, RBAC, gamification) is UNCHANGED — it still keys off
    Sales Person. Employee is only consulted by the HR (expense/leave) APIs.

Wire in hooks.py:
    doc_events = {
        "Sales Person": {
            "after_insert": "sfa_core.field_sfa.doc_events.sales_person.provision_employee",
            "on_update":    "sfa_core.field_sfa.doc_events.sales_person.sync_employee",
        },
    }

NOTE: lives under field_sfa/doc_events/ (the LIVE module — §6), path
sfa_core.field_sfa.doc_events.sales_person — NOT sfa_core.doc_events.
"""

import frappe
from frappe.utils import today

COMPANY = "Hema Beverages Limited"

# Sales Person tree root + known test records that must never get an Employee.
EXCLUDED_SALES_PERSONS = {"Sales Team", "Test Rep", "Sales Person 1"}


def _is_provisionable(doc):
    """A Sales Person earns an Employee only if it's a real leaf person with a login."""
    if doc.name in EXCLUDED_SALES_PERSONS:
        return False
    if getattr(doc, "is_group", 0):
        return False
    if not (doc.get("custom_user_id") or "").strip():
        return False
    return True


def provision_employee(doc, method=None):
    """after_insert: create + link an Employee if this Sales Person qualifies."""
    if not _is_provisionable(doc):
        return
    if doc.get("custom_employee") and frappe.db.exists("Employee", doc.custom_employee):
        return  # already linked
    _create_and_link(doc)


def sync_employee(doc, method=None):
    """on_update: keep the linked Employee in step; enforce 1:1; provision if newly eligible."""
    emp_name = doc.get("custom_employee")

    if not _is_provisionable(doc):
        return

    if not emp_name or not frappe.db.exists("Employee", emp_name):
        # became eligible (e.g. user_id added later), or link dangling -> (re)provision
        _create_and_link(doc)
        return

    # Mirror mutable fields onto the Employee.
    emp = frappe.get_doc("Employee", emp_name)
    changed = False

    desired_name = (doc.get("sales_person_name") or doc.name or "").strip()
    if desired_name and emp.employee_name != desired_name:
        emp.employee_name = desired_name
        changed = True

    desired_user = (doc.get("custom_user_id") or "").strip()
    if desired_user and emp.user_id != desired_user:
        emp.user_id = desired_user
        changed = True

    # Mirror active/inactive status.
    sp_enabled = not getattr(doc, "enabled", 1) == 0
    desired_status = "Active" if sp_enabled else "Inactive"
    if emp.status != desired_status:
        emp.status = desired_status
        changed = True

    if changed:
        emp.save(ignore_permissions=True)


def _default_gender():
    """Pick a valid Gender for the placeholder. 'Prefer not to say' is the most
    neutral standard value; fall back to whatever Gender records exist."""
    for candidate in ("Prefer not to say", "Other", "Male", "Female"):
        if frappe.db.exists("Gender", candidate):
            return candidate
    any_gender = frappe.db.get_value("Gender", {}, "name")
    return any_gender  # may be None; if so, Gender master is empty (unexpected)


def _create_and_link(doc):
    """Create an Employee from a Sales Person and write back the link. Enforces 1:1."""
    user_id = (doc.get("custom_user_id") or "").strip()
    emp_name_field = (doc.get("sales_person_name") or doc.name or "").strip()

    # Guard: an Employee may already exist for this user_id (e.g. created out of band).
    existing = None
    if user_id:
        existing = frappe.db.get_value("Employee", {"user_id": user_id}, "name")

    if existing:
        emp_name = existing
    else:
        emp = frappe.new_doc("Employee")
        emp.employee_name = emp_name_field
        emp.first_name = emp_name_field  # Employee requires first_name
        emp.company = COMPANY
        emp.date_of_joining = today()
        # gender + date_of_birth are mandatory in hrms but unknown at backfill time.
        # Use neutral placeholders; correct later in the HR UI per real records.
        emp.gender = _default_gender()
        emp.date_of_birth = "1990-01-01"
        if user_id:
            emp.user_id = user_id
        emp.status = "Active"
        emp.insert(ignore_permissions=True)
        emp_name = emp.name

    # Write the link back without re-triggering on_update recursively.
    frappe.db.set_value("Sales Person", doc.name, "custom_employee", emp_name,
                        update_modified=False)
    doc.custom_employee = emp_name
