"""
Seed a Holiday List for Hema Beverages and attach it to the company + all
active employees. Without a Holiday List on Employee or Company, hrms's Leave
Application cannot compute total_leave_days and fails on insert (HTTP 417).

Pattern:
  - Weekly off: Sundays only
  - Fixed-date Uganda public holidays for the current FY (Apr 1 -> Mar 31)
  - List is FY-scoped, matching allocate_leave_for_current_fy
  - Eid and other moving holidays are NOT included — they shift by lunar
    calendar and need manual entry. Admin can add them via Frappe Desk.

Idempotent:
  - Holiday List with the same name is updated, not recreated
  - Company default_holiday_list is set only if not already set
  - Employees missing holiday_list get it; ones with their own keep theirs

Registered as: sfa_core.patches.v1_0.seed_uganda_holiday_list
Must run before allocate_leave_for_current_fy (Leave Allocation submission
calls get_holiday_list_for_employee internally).
"""

import frappe
from frappe.utils import getdate, today, add_days
from datetime import date, timedelta


COMPANY = "Hema Beverages Limited"

# Fixed-date Uganda public holidays. Date format: (MM, DD, description).
# Eid al-Fitr, Eid al-Adha, and Good Friday/Easter are deliberately omitted —
# they move yearly. Admin can add them per FY via the Frappe Desk.
UGANDA_FIXED_HOLIDAYS = [
    (1,  1,  "New Year's Day"),
    (1,  26, "Liberation Day"),
    (3,  8,  "International Women's Day"),
    (5,  1,  "Labour Day"),
    (6,  3,  "Martyrs' Day"),
    (6,  9,  "National Heroes' Day"),
    (10, 9,  "Independence Day"),
    (12, 25, "Christmas Day"),
    (12, 26, "Boxing Day"),
]


def _current_fy_range():
    """Return (from_date, to_date) for FY containing today. Apr 1 -> Mar 31."""
    t = getdate(today())
    from_year = t.year if t.month >= 4 else t.year - 1
    return date(from_year, 4, 1), date(from_year + 1, 3, 31)


def _fy_label(from_date):
    """Friendly label like 'Hema Holiday List 2026-27'."""
    return f"Hema Holiday List {from_date.year}-{str(from_date.year + 1)[-2:]}"


def _all_sundays_between(from_date, to_date):
    """Generate every Sunday between from_date and to_date inclusive."""
    # Python: Mon=0 ... Sun=6
    d = from_date
    # Step forward to the first Sunday on/after from_date
    while d.weekday() != 6:
        d += timedelta(days=1)
        if d > to_date:
            return
    while d <= to_date:
        yield d
        d += timedelta(days=7)


def _fixed_holidays_in_range(from_date, to_date):
    """Yield (date, description) for fixed-date holidays falling in the FY range.
    FY spans two calendar years, so we check both."""
    years = {from_date.year, to_date.year}
    for y in years:
        for m, d, desc in UGANDA_FIXED_HOLIDAYS:
            try:
                hd = date(y, m, d)
            except ValueError:
                continue
            if from_date <= hd <= to_date:
                yield hd, desc


def execute():
    from_date, to_date = _current_fy_range()
    list_name = _fy_label(from_date)
    print(f"[seed_uganda_holiday_list] FY: {from_date} -> {to_date} "
          f"(list: {list_name!r})")

    # ── 1. Build / update the Holiday List ──────────────────────────────
    if frappe.db.exists("Holiday List", list_name):
        hl = frappe.get_doc("Holiday List", list_name)
        # Clear and rebuild — keeps the doc idempotent for re-runs without
        # leaving stale holidays from a previous attempt.
        hl.holidays = []
    else:
        hl = frappe.new_doc("Holiday List")
        hl.holiday_list_name = list_name

    hl.from_date = from_date
    hl.to_date = to_date
    hl.weekly_off = "Sunday"  # only one weekly_off allowed per list (hrms convention)

    # Fixed-date public holidays first (so they have a stable position in the list)
    holiday_dates_added = set()
    for hd, desc in sorted(_fixed_holidays_in_range(from_date, to_date)):
        hl.append("holidays", {
            "holiday_date": hd,
            "description": desc,
            "weekly_off": 0,
        })
        holiday_dates_added.add(hd)

    # Weekly Sundays — skip any that coincide with a fixed holiday already
    # added (hrms's get_holidays_for_employee de-dupes by date, but cleaner
    # to not double-enter rows)
    for sd in _all_sundays_between(from_date, to_date):
        if sd in holiday_dates_added:
            continue
        hl.append("holidays", {
            "holiday_date": sd,
            "description": "Sunday",
            "weekly_off": 1,
        })

    hl.save(ignore_permissions=True)
    print(f"  + Holiday List saved with {len(hl.holidays)} holidays")

    # ── 2. Set as Company default ───────────────────────────────────────
    if frappe.db.exists("Company", COMPANY):
        current = frappe.db.get_value("Company", COMPANY, "default_holiday_list")
        if current != list_name:
            frappe.db.set_value("Company", COMPANY, "default_holiday_list", list_name)
            print(f"  + Company default_holiday_list -> {list_name}")
        else:
            print(f"  = Company default already set to {list_name}")
    else:
        print(f"  ! Company {COMPANY!r} not found — skipping company default")

    # ── 3. Backfill onto active employees missing a holiday_list ────────
    employees = frappe.get_all(
        "Employee",
        filters={"status": "Active", "company": COMPANY},
        fields=["name", "employee_name", "holiday_list"],
    )
    backfilled = 0
    for emp in employees:
        if emp.holiday_list:
            continue  # respect any per-employee override that's already set
        frappe.db.set_value("Employee", emp.name, "holiday_list", list_name)
        backfilled += 1
        print(f"  + {emp.employee_name or emp.name} -> {list_name}")

    frappe.db.commit()
    print(f"[seed_uganda_holiday_list] done — "
          f"holidays={len(hl.holidays)} employees_backfilled={backfilled}")
