import frappe
from frappe import _
from sfa_core.api.auth import resolve_sales_person

@frappe.whitelist()
def create_payment(customer, amount, payment_type, sales_person, visit=None, latitude=None, longitude=None, accuracy=None, captured_at=None, **kwargs):
    """Create payment from mobile app"""
    sales_person = resolve_sales_person(sales_person)
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
def get_payments(sales_person=None, customer=None, limit=50):
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
        limit=limit,
        order_by="payment_date desc")

    return payments
