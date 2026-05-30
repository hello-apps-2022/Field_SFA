import frappe
from frappe.utils import time_diff_in_seconds


def execute():
    """Backfill check-in/out for existing visits under the auto-track model:
    check-in = creation time; check-out = completion time (best-effort: the
    record's modified time for visits already marked Completed)."""
    visits = frappe.get_all(
        "SFA Visit",
        fields=["name", "creation", "modified", "status", "check_in_time", "check_out_time"],
    )
    for v in visits:
        upd = {}
        if not v.check_in_time:
            upd["check_in_time"] = v.creation
        if not v.check_out_time and v.status == "Completed":
            upd["check_out_time"] = v.modified
        ci = upd.get("check_in_time") or v.check_in_time
        co = upd.get("check_out_time") or v.check_out_time
        if ci and co:
            upd["duration_minutes"] = int((time_diff_in_seconds(co, ci) or 0) / 60)
        if upd:
            frappe.db.set_value("SFA Visit", v.name, upd, update_modified=False)
    frappe.db.commit()
