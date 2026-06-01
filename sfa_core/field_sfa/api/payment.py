import frappe
from sfa_core.field_sfa.api.response import mobile_api
from frappe import _
from sfa_core.api.auth import resolve_sales_person
from frappe.utils import cint

@frappe.whitelist()
@mobile_api
def create_payment(customer, amount, payment_type, sales_person, visit=None, latitude=None, longitude=None, accuracy=None, captured_at=None, **kwargs):
    """Create payment from mobile app"""
    sales_person = resolve_sales_person(sales_person)
    client_uuid = kwargs.pop("client_uuid", None) or kwargs.get("custom_client_uuid")
    if client_uuid:
        _dupe = frappe.db.get_value("SFA Payment", {"custom_client_uuid": client_uuid}, "name")
        if _dupe:
            return {"name": _dupe, "status": "duplicate"}
        kwargs["custom_client_uuid"] = client_uuid
    payment = frappe.get_doc({
        "doctype": "SFA Payment",
        "customer": customer,
        "amount": amount,
        "payment_type": payment_type,
        "sales_person": sales_person,
        "visit": visit,
        "custom_sfa_latitude": latitude,
        "custom_sfa_longitude": longitude,
        "custom_sfa_gps_accuracy": accuracy,
        "custom_sfa_captured_at": captured_at,
        "payment_date": frappe.utils.nowdate(),
        **kwargs
    })
    payment.insert(ignore_permissions=True)
    payment.submit()

    return {"name": payment.name, "status": "submitted"}

@frappe.whitelist()
@mobile_api
def get_payments(sales_person=None, customer=None, start=0, page_length=50):
    """Get payments for mobile app"""
    sales_person = resolve_sales_person(sales_person)
    filters = {"docstatus": 1}
    if sales_person:
        filters["sales_person"] = sales_person
    if customer:
        filters["customer"] = customer

    payments = frappe.get_all("SFA Payment",
        filters=filters,
        fields=["name", "customer", "payment_date", "amount", "payment_type", 
                "status", "visit", "sales_person"],
        limit_start=cint(start),
        limit_page_length=min(cint(page_length) or 50, 1000),
        order_by="payment_date desc")

    return {"items": payments, "total": frappe.db.count("SFA Payment", filters)}
