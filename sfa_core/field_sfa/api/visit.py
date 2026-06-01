import frappe
from sfa_core.field_sfa.api.response import mobile_api
from frappe import _
from sfa_core.api.auth import resolve_sales_person
from frappe.utils import getdate, now, cint

@frappe.whitelist()
@mobile_api
def get_visits(sales_person=None, date=None, status=None, start=0, page_length=50):
    """Get visits for mobile app"""
    sales_person = resolve_sales_person(sales_person)
    filters = {}
    if sales_person:
        filters["sales_person"] = sales_person
    if date:
        filters["visit_date"] = getdate(date)
    if status:
        filters["status"] = status

    visits = frappe.get_all("SFA Visit",
        filters=filters,
        fields=["name", "customer", "visit_date", "status", "check_in_time", 
                "check_out_time", "duration_minutes", "visit_purpose", "notes"],
        limit_start=cint(start),
        limit_page_length=min(cint(page_length) or 50, 1000),
        order_by="visit_date desc")

    return {"items": visits, "total": frappe.db.count("SFA Visit", filters)}

@frappe.whitelist()
@mobile_api
def create_visit(customer, sales_person, visit_date=None, **kwargs):
    """Create a new visit from mobile app"""
    sales_person = resolve_sales_person(sales_person)
    client_uuid = kwargs.pop("client_uuid", None) or kwargs.get("custom_client_uuid")
    if client_uuid:
        _dupe = frappe.db.get_value("SFA Visit", {"custom_client_uuid": client_uuid}, "name")
        if _dupe:
            return _dupe
        kwargs["custom_client_uuid"] = client_uuid
    if not visit_date:
        visit_date = getdate()

    visit = frappe.get_doc({
        "doctype": "SFA Visit",
        "customer": customer,
        "sales_person": sales_person,
        "visit_date": visit_date,
        **kwargs
    })
    visit.insert(ignore_permissions=True)
    return visit.name

@frappe.whitelist()
@mobile_api
def check_in_visit(visit, latitude, longitude, accuracy=None):
    """Check in to a visit"""
    visit_doc = frappe.get_doc("SFA Visit", visit)
    visit_doc.check_in_time = now()
    visit_doc.check_in_latitude = latitude
    visit_doc.check_in_longitude = longitude
    if accuracy:
        visit_doc.check_in_accuracy = accuracy
    visit_doc.status = "In Progress"
    visit_doc.save(ignore_permissions=True)
    return {"status": "success", "visit": visit}

@frappe.whitelist()
@mobile_api
def check_out_visit(visit, latitude, longitude, accuracy=None, notes=None):
    """Check out of a visit"""
    visit_doc = frappe.get_doc("SFA Visit", visit)
    visit_doc.check_out_time = now()
    visit_doc.check_out_latitude = latitude
    visit_doc.check_out_longitude = longitude
    if accuracy:
        visit_doc.check_out_accuracy = accuracy
    if notes:
        visit_doc.notes = notes
    visit_doc.status = "Completed"
    visit_doc.save(ignore_permissions=True)

    # Award points (amount from SFA Points Config, with fallback)
    from sfa_core.field_sfa.utils.gamification import award_points, get_config_points
    visit_pts, _mf = get_config_points("Visit Complete")
    award_points(visit_doc.sales_person, "Visit Complete", visit_pts, "SFA Visit", visit)

    return {"status": "success", "visit": visit}
