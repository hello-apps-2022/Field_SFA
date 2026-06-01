import frappe
from sfa_core.field_sfa.api.response import mobile_api
from frappe import _
from sfa_core.api.auth import resolve_sales_person
from frappe.utils import cint

@frappe.whitelist()
@mobile_api
def upload_gps_track(points):
    """Upload GPS track points from mobile app"""
    sp = resolve_sales_person()
    created = 0
    for point in points:
        track = frappe.get_doc({
            "doctype": "SFA GPS Track Point",
            "sales_person": sp,
            "timestamp": point.get("timestamp"),
            "latitude": point.get("latitude"),
            "longitude": point.get("longitude"),
            "accuracy": point.get("accuracy"),
            "altitude": point.get("altitude"),
            "speed": point.get("speed"),
            "battery_level": point.get("battery_level"),
            "visit": point.get("visit"),
            "sync_status": "Synced"
        })
        track.insert(ignore_permissions=True)
        created += 1

    return {"created": created}

@frappe.whitelist()
@mobile_api
def get_gps_tracks(sales_person, date=None, start=0, page_length=1000):
    """Get GPS tracks for a sales person"""
    sales_person = resolve_sales_person(sales_person)
    filters = {"sales_person": sales_person}
    if date:
        filters["timestamp"] = ["like", f"{date}%"]

    tracks = frappe.get_all("SFA GPS Track Point",
        filters=filters,
        fields=["name", "timestamp", "latitude", "longitude", "accuracy", 
                "altitude", "speed", "battery_level"],
        limit_start=cint(start),
        limit_page_length=min(cint(page_length) or 1000, 5000),
        order_by="timestamp")

    return {"items": tracks, "total": frappe.db.count("SFA GPS Track Point", filters)}
