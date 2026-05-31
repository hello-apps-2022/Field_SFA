import frappe
from frappe import _
from sfa_core.api.auth import resolve_sales_person

@frappe.whitelist()
def get_customers(sales_person=None, territory=None, limit=200):
    """Get customers for mobile app"""
    sales_person = resolve_sales_person(sales_person)
    filters = {"custom_sfa_status": ["!=", "Inactive"]}

    if sales_person:
        # Get customers assigned to this sales person via share log
        shared_customers = frappe.get_all("SFA Customer Share Log",
            filters={"sales_person": sales_person, "is_active": 1},
            pluck="customer")
        if shared_customers:
            filters["name"] = ["in", shared_customers]

    if territory:
        filters["territory"] = territory

    customers = frappe.get_all("Customer",
        filters=filters,
        fields=["name", "customer_name", "territory", "customer_group",
                "custom_sfa_status", "custom_last_visit_date", "custom_visit_frequency"],
        limit=limit,
        order_by="customer_name")

    return customers

@frappe.whitelist()
def get_customer_detail(customer):
    """Get full customer details"""
    if not frappe.db.exists("Customer", customer):
        frappe.throw(_("Customer not found"))

    customer_doc = frappe.get_doc("Customer", customer)

    # Get saved location
    location = frappe.db.get_value("SFA Saved Location",
        {"linked_customer": customer, "location_type": "Customer", "is_active": 1},
        ["latitude", "longitude", "address"], as_dict=True)

    # Get recent visits
    visits = frappe.get_all("SFA Visit",
        filters={"customer": customer},
        fields=["name", "visit_date", "status", "duration_minutes", "notes"],
        limit=5,
        order_by="visit_date desc")

    # Get outstanding amount
    outstanding = frappe.db.get_value("Customer", customer, "outstanding_amount") or 0

    return {
        "customer": customer_doc.as_dict(),
        "location": location,
        "recent_visits": visits,
        "outstanding_amount": outstanding
    }
