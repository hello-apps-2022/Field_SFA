import frappe
from frappe import _

@frappe.whitelist()
def get_sync_data(sales_person, last_sync=None):
    """Get data for mobile sync (WatermelonDB pattern)"""
    data = {
        "customers": [],
        "beat_plans": [],
        "visits": [],
        "form_templates": [],
        "payments": [],
        "orders": [],
        "saved_locations": [],
        "points_config": []
    }

    # Get customers
    data["customers"] = frappe.get_all("Customer",
        filters={"custom_sfa_status": ["!=", "Inactive"]},
        fields=["name", "customer_name", "territory", "customer_group",
                "custom_sfa_status", "custom_last_visit_date", "custom_visit_frequency"])

    # Get beat plans
    data["beat_plans"] = frappe.get_all("SFA Beat Plan",
        filters={"sales_person": sales_person, "status": "Active"},
        fields=["name", "plan_name", "territory", "date", "status", "geofence_radius"])

    # Get today's visits
    from frappe.utils import getdate
    data["visits"] = frappe.get_all("SFA Visit",
        filters={"sales_person": sales_person, "visit_date": getdate()},
        fields=["name", "customer", "visit_date", "status", "check_in_time", "check_out_time"])

    # Get form templates
    data["form_templates"] = frappe.get_all("SFA Form Template",
        filters={"is_active": 1},
        fields=["name", "template_name", "survey_json", "is_mandatory", "version"])

    # Get points config
    data["points_config"] = frappe.get_all("SFA Points Config",
        filters={"is_active": 1},
        fields=["name", "activity_type", "points", "multiplier_field"])

    return data

@frappe.whitelist()
def push_sync_data(data):
    """Receive sync data from mobile app"""
    results = {
        "visits_created": 0,
        "payments_created": 0,
        "gps_tracks_created": 0,
        "form_responses_created": 0
    }

    # Process visits
    for visit in data.get("visits", []):
        try:
            v = frappe.get_doc({"doctype": "SFA Visit", **visit})
            v.insert(ignore_permissions=True)
            results["visits_created"] += 1
        except Exception:
            pass

    # Process payments
    for payment in data.get("payments", []):
        try:
            p = frappe.get_doc({"doctype": "SFA Payment", **payment})
            p.insert(ignore_permissions=True)
            results["payments_created"] += 1
        except Exception:
            pass

    # Process GPS tracks
    for track in data.get("gps_tracks", []):
        try:
            t = frappe.get_doc({"doctype": "SFA GPS Track Point", **track})
            t.insert(ignore_permissions=True)
            results["gps_tracks_created"] += 1
        except Exception:
            pass

    # Process form responses
    for response in data.get("form_responses", []):
        try:
            r = frappe.get_doc({"doctype": "SFA Form Response", **response})
            r.insert(ignore_permissions=True)
            results["form_responses_created"] += 1
        except Exception:
            pass

    return results
