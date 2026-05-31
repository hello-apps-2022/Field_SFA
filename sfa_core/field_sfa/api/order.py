import frappe
from frappe import _
from sfa_core.api.auth import resolve_sales_person

@frappe.whitelist()
def create_order(customer, items, sales_person, visit=None, latitude=None, longitude=None, accuracy=None, captured_at=None, **kwargs):
    """Create sales order from mobile app"""
    sales_person = resolve_sales_person(sales_person)
    order_items = []
    for item in items:
        if item.get("is_free") or item.get("is_free_item"):
            order_items.append({
                "item_code": item.get("item_code"),
                "qty": item.get("qty", 1),
                "rate": 0,
                "is_free_item": 1,
            })
        else:
            order_items.append({
                "item_code": item.get("item_code"),
                "qty": item.get("qty", 1),
                "rate": item.get("rate", 0),
                "custom_carton_qty": item.get("carton_qty", 0),
                "custom_unpaid_qty": item.get("unpaid_qty", 0),
            })

    so = frappe.get_doc({
        "doctype": "Sales Order",
        "customer": customer,
        "custom_sfa_visit": visit,
        "custom_sfa_rep": sales_person,
        "custom_sfa_latitude": latitude,
        "custom_sfa_longitude": longitude,
        "custom_sfa_gps_accuracy": accuracy,
        "custom_sfa_captured_at": captured_at,
        "delivery_date": frappe.utils.add_days(frappe.utils.nowdate(), 1),
        "items": order_items,
        **kwargs
    })
    so.insert(ignore_permissions=True)
    so.submit()

    return {"name": so.name, "status": "submitted"}

@frappe.whitelist()
def get_orders(sales_person=None, customer=None, limit=50):
    """Get orders for mobile app"""
    sales_person = resolve_sales_person(sales_person)
    filters = {"docstatus": 1}
    if sales_person:
        filters["custom_sfa_rep"] = sales_person
    if customer:
        filters["customer"] = customer

    orders = frappe.get_all("Sales Order",
        filters=filters,
        fields=["name", "customer", "transaction_date", "grand_total", "status", 
                "custom_sfa_visit", "custom_sfa_rep"],
        limit=limit,
        order_by="transaction_date desc")

    return orders
