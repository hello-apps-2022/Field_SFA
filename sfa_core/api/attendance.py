import frappe
from frappe import _
from frappe.utils import now_datetime, getdate, get_datetime, time_diff_in_hours, flt, add_days, add_to_date
from collections import defaultdict

from sfa_core.api.auth import get_user_context


def _current_employee():
    """The Employee linked to the logged-in user. Tries Employee.user_id first,
    then the Sales Person -> Employee link from the session context."""
    emp = frappe.db.get_value("Employee", {"user_id": frappe.session.user, "status": "Active"}, "name")
    if not emp:
        ctx = get_user_context()
        emp = ctx.get("employee")
    if not emp:
        frappe.throw(
            _("No Employee is linked to your user. Ask an admin to link one before marking attendance."),
            frappe.PermissionError,
        )
    return emp


def _day_bounds(d):
    d = getdate(d)
    return ["%s 00:00:00" % d, "%s 23:59:59" % d]


def _last_log_today(employee):
    rows = frappe.get_all(
        "Employee Checkin",
        filters={"employee": employee, "time": ["between", _day_bounds(getdate())]},
        fields=["name", "log_type", "time"],
        order_by="time desc, creation desc",
        limit=1,
    )
    return rows[0] if rows else None


def _sessions(items):
    """Pair an employee-day's logs into IN->OUT sessions (time-ordered).
    A trailing IN with no OUT is returned as an `open` session."""
    out = []
    open_in = None
    for l in items:
        if l.log_type == "IN":
            open_in = l
        elif l.log_type == "OUT" and open_in:
            paired = get_datetime(l.time) > get_datetime(open_in.time)
            out.append({
                "in_time": str(open_in.time), "in_lat": open_in.latitude, "in_lng": open_in.longitude,
                "out_time": str(l.time), "out_lat": l.latitude, "out_lng": l.longitude,
                "hours": round(time_diff_in_hours(l.time, open_in.time), 2) if paired else 0.0,
                "open": False,
            })
            open_in = None
    if open_in:
        out.append({
            "in_time": str(open_in.time), "in_lat": open_in.latitude, "in_lng": open_in.longitude,
            "out_time": None, "out_lat": None, "out_lng": None, "hours": None, "open": True,
        })
    return out


def _worked_hours(items):
    """Total worked time = sum of completed IN->OUT sessions (an open session
    and any mid-day break are excluded)."""
    total = sum((s["hours"] or 0) for s in _sessions(items) if not s["open"])
    return round(total, 2) if total else None


def _streak(employee):
    """Consecutive days (ending today or yesterday) the employee started a day."""
    rows = frappe.get_all(
        "Employee Checkin",
        filters={"employee": employee, "log_type": "IN", "time": [">=", "%s 00:00:00" % add_days(getdate(), -90)]},
        fields=["time"],
    )
    dayset = {getdate(r.time) for r in rows}
    if not dayset:
        return 0
    today = getdate()
    cursor = today if today in dayset else add_days(today, -1)
    if cursor not in dayset:
        return 0
    streak = 0
    while cursor in dayset:
        streak += 1
        cursor = add_days(cursor, -1)
    return streak


@frappe.whitelist()
def mark_attendance(latitude=None, longitude=None, accuracy=None, log_type=None, priorities=None, focus=None):
    """Mark a day start/end (HRMS Employee Checkin), GPS-tagged. Toggles IN/OUT
    from the last log today when log_type is omitted; a user may start again
    after ending (e.g. a half-day break). On a day-start (IN), the rep's
    priorities and focus areas for the day are stored on the checkin."""
    employee = _current_employee()
    last = _last_log_today(employee)

    if not log_type:
        log_type = "OUT" if (last and last["log_type"] == "IN") else "IN"
    if log_type not in ("IN", "OUT"):
        frappe.throw(_("Invalid log type."))
    if last and last["log_type"] == log_type:
        frappe.throw(_("Your day is already {0}.").format("started" if log_type == "IN" else "ended"))

    # HRMS strips checkin time to the whole second and rejects two logs that
    # share the same (second, log_type). Keep punches strictly increasing so a
    # rapid second tap can never collide with an existing punch.
    ts = now_datetime().replace(microsecond=0)
    if last:
        last_time = get_datetime(last["time"]).replace(microsecond=0)
        if ts <= last_time:
            ts = add_to_date(last_time, seconds=1)

    doc = {
        "doctype": "Employee Checkin",
        "employee": employee,
        "log_type": log_type,
        "time": ts,
        "latitude": flt(latitude) if latitude not in (None, "") else None,
        "longitude": flt(longitude) if longitude not in (None, "") else None,
        "device_id": "Field Pro",
    }
    if log_type == "IN":
        # Carry the day's plan only on the FIRST start of the day.
        first_today = not last
        if first_today:
            if priorities:
                doc["custom_sfa_day_priorities"] = priorities
            if focus:
                doc["custom_sfa_day_focus"] = focus

    checkin = frappe.get_doc(doc)
    checkin.insert(ignore_permissions=True)

    return {
        "name": checkin.name,
        "log_type": log_type,
        "time": str(checkin.time),
        "status": "checked_in" if log_type == "IN" else "checked_out",
    }


@frappe.whitelist()
def get_attendance_today():
    """The current user's day state: status, the day's logs, today's plan
    (priorities + focus), and the current streak."""
    employee = _current_employee()
    logs = frappe.get_all(
        "Employee Checkin",
        filters={"employee": employee, "time": ["between", _day_bounds(getdate())]},
        fields=["name", "log_type", "time", "latitude", "longitude",
                "custom_sfa_day_priorities", "custom_sfa_day_focus"],
        order_by="time asc, creation asc",
    )
    first_in = next((l for l in logs if l.log_type == "IN"), None)
    last_out = next((l for l in reversed(logs) if l.log_type == "OUT"), None)
    last = logs[-1] if logs else None
    status = "not_started"
    if last:
        status = "checked_in" if last.log_type == "IN" else "checked_out"

    return {
        "employee": employee,
        "status": status,
        "first_in": first_in,
        "last_out": last_out,
        "logs": logs,
        "priorities": (first_in.custom_sfa_day_priorities if first_in else None),
        "focus": (first_in.custom_sfa_day_focus if first_in else None),
        "worked_hours": _worked_hours(logs),
        "streak": _streak(employee),
    }


@frappe.whitelist()
def get_attendance_report(date_from=None, date_to=None, sales_person=None):
    """Per-employee, per-day attendance for a date range, broken into sessions.
    Each row carries a status (working / open / ended), the session breakdown,
    summed worked hours, and the day's focus + priorities. Reps/helpers see only
    their own; managers/admins/supervisors see everyone (optionally narrowed to
    one rep via sales_person)."""
    ctx = get_user_context()
    today = getdate()
    date_from = getdate(date_from) if date_from else today
    date_to = getdate(date_to) if date_to else today

    emp_filter = {}
    if ctx["is_rep"] or ctx["is_helper"]:
        emp_filter["employee"] = _current_employee()
    elif sales_person:
        emp = frappe.db.get_value("Sales Person", sales_person, "custom_employee")
        if not emp:
            return {"rows": [], "summary": {"records": 0, "present": 0, "working_now": 0},
                    "date_from": str(date_from), "date_to": str(date_to)}
        emp_filter["employee"] = emp

    logs = frappe.get_all(
        "Employee Checkin",
        filters=dict(emp_filter, time=["between", ["%s 00:00:00" % date_from, "%s 23:59:59" % date_to]]),
        fields=["employee", "employee_name", "log_type", "time", "latitude", "longitude",
                "custom_sfa_day_priorities", "custom_sfa_day_focus"],
        order_by="time asc, creation asc",
    )

    groups = defaultdict(list)
    for l in logs:
        groups[(l.employee, l.employee_name or l.employee, str(getdate(l.time)))].append(l)

    rows = []
    for (emp, emp_name, d), items in groups.items():
        ins = [i for i in items if i.log_type == "IN"]
        first_in = ins[0] if ins else None
        last = items[-1]
        is_today = getdate(d) == today
        if last.log_type == "IN":
            status = "working" if is_today else "open"   # open = forgot to clock out
        else:
            status = "ended"
        sessions = _sessions(items)
        last_out = next((i for i in reversed(items) if i.log_type == "OUT"), None)
        rows.append({
            "employee": emp,
            "employee_name": emp_name,
            "date": d,
            "status": status,
            "check_in": str(first_in.time) if first_in else None,
            "check_in_lat": first_in.latitude if first_in else None,
            "check_in_lng": first_in.longitude if first_in else None,
            "check_out": str(last_out.time) if (status == "ended" and last_out) else None,
            "check_out_lat": last_out.latitude if (status == "ended" and last_out) else None,
            "check_out_lng": last_out.longitude if (status == "ended" and last_out) else None,
            "hours": _worked_hours(items),
            "session_count": len([s for s in sessions if not s["open"]]),
            "sessions": sessions,
            "priorities": (first_in.custom_sfa_day_priorities if first_in else None),
            "focus": (first_in.custom_sfa_day_focus if first_in else None),
        })

    rows.sort(key=lambda r: (r["date"], r["employee_name"]), reverse=True)
    present = len([r for r in rows if r["check_in"]])
    working_now = len([r for r in rows if r["status"] == "working"])
    return {
        "rows": rows,
        "summary": {"records": len(rows), "present": present, "working_now": working_now},
        "date_from": str(date_from),
        "date_to": str(date_to),
    }
