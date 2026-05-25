import frappe
from frappe import _

@frappe.whitelist()
def create_order(customer, items, sales_person, visit=None, **kwargs):
    """Create sales order from mobile app"""
    from erpnext.selling.doctype.sales_order.sales_order import make_sales_order

    order_items = []
    for item in items:
        order_items.append({
            "item_code": item.get("item_code"),
            "qty": item.get("qty", 1),
            "rate": item.get("rate", 0),
            "custom_carton_qty": item.get("carton_qty", 0),
            "custom_free_qty": item.get("free_qty", 0),
            "custom_unpaid_qty": item.get("unpaid_qty", 0),
        })

    so = frappe.get_doc({
        "doctype": "Sales Order",
        "customer": customer,
        "custom_sfa_visit": visit,
        "custom_sfa_rep": sales_person,
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
