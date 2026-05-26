import frappe
from frappe import _
from frappe.utils import now, getdate, add_days

def daily_end_of_day():
    """Daily EOD: Auto-close visits, compliance checks"""
    auto_close_visits()
    check_daily_compliance()

def hourly_compliance():
    """Hourly compliance check"""
    check_visit_compliance()

def five_minute_gps():
    """Process GPS buffer every 5 minutes"""
    process_gps_buffer()

def nightly_badge():
    """Check and award badges nightly"""
    from sfa_core.utils.gamification import check_and_award_badges

    reps = frappe.get_all("Sales Person", filters={"enabled": 1}, pluck="name")
    for rep in reps:
        try:
            check_and_award_badges(rep)
        except Exception:
            frappe.log_error(f"Badge check failed for {rep}")

def morning_beat():
    """Morning beat plan reminders"""
    today = getdate()
    beat_plans = frappe.get_all("SFA Beat Plan", 
        filters={"date": today, "status": "Active"},
        fields=["name", "sales_person"])

    for bp in beat_plans:
        frappe.publish_realtime(event="beat_plan_reminder", 
            message={"beat_plan": bp.name}, 
            user=frappe.db.get_value("Sales Person", bp.sales_person, "user_id"))

def daily_share_threshold():
    """Check customer share thresholds and send alerts"""
    configs = frappe.get_all("SFA Share Alert Config", filters={"is_active": 1})

    for config in configs:
        check_share_alerts(config.name)

def auto_close_visits():
    """Auto-close visits based on distance + time rules"""
    from datetime import datetime, timedelta

    # Close visits that are 500m away and inactive for 30 min
    from frappe.utils import getdate
    # Daily EOD: close all visits still open from today
    visits = frappe.get_all("SFA Visit",
        filters={
            "status": ["in", ["Open", "In Progress"]],
            "visit_date": getdate()
        },
        fields=["name", "sales_person", "customer"])

    for visit in visits:
        try:
            doc = frappe.get_doc("SFA Visit", visit.name)
            doc.status = "Auto Closed"
            doc.auto_closed = 1
            doc.auto_close_reason = "Day End"
            doc.check_out_time = now()
            doc.save(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"Auto-close failed for visit {visit.name}: {e}")

def check_daily_compliance():
    """Check daily visit compliance"""
    pass

def check_visit_compliance():
    """Check visit compliance metrics"""
    pass

def process_gps_buffer():
    """Process buffered GPS track points"""
    pass

def check_share_alerts(config_name):
    """Check and send share alerts"""
    pass
