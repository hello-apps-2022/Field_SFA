import frappe
from frappe import _
from frappe.utils import now, time_diff_in_minutes, getdate

def validate_visit(doc, method):
    """Validate visit data"""
    if doc.check_in_time and doc.check_out_time:
        if doc.check_out_time < doc.check_in_time:
            frappe.throw(_("Check Out time cannot be before Check In time"))

        duration = time_diff_in_minutes(doc.check_out_time, doc.check_in_time)
        doc.duration_minutes = int(duration)

    # Validate geofence if customer has saved location
    if doc.customer and doc.check_in_latitude:
        from sfa_core.utils.geo import get_customer_location, calculate_distance
        cust_loc = get_customer_location(doc.customer)
        if cust_loc:
            dist = calculate_distance(
                doc.check_in_latitude, doc.check_in_longitude,
                cust_loc["lat"], cust_loc["lng"]
            )
            doc.distance_from_customer = dist

def on_submit(doc, method):
    """Award points and update customer last visit"""
    if doc.status == "Completed":
        frappe.db.set_value("Customer", doc.customer, "custom_last_visit_date", getdate(doc.visit_date))

        from sfa_core.utils.gamification import award_points
        award_points(doc.sales_person, "Visit Complete", 10, "SFA Visit", doc.name)

def on_update(doc, method):
    """Auto-close check if needed"""
    pass
