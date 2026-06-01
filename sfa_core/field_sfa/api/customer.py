import frappe
from sfa_core.field_sfa.api.response import mobile_api
from frappe import _
from sfa_core.api.auth import resolve_sales_person
from frappe.utils import cint

@frappe.whitelist()
@mobile_api
def get_customers(sales_person=None, territory=None, start=0, page_length=200):
    """Get customers for mobile app"""
    sales_person = resolve_sales_person(sales_person)
    filters = {"custom_sfa_status": ["!=", "Inactive"]}

    if sales_person:
        # Customers assigned to this rep: primary rep on the Customer
        # (custom_sfa_rep) plus any explicitly shared via the active share log.
        # Empty -> nothing (never the whole book).
        names = set(frappe.get_all("Customer",
            filters={"custom_sfa_rep": sales_person}, pluck="name"))
        names.update(frappe.get_all("SFA Customer Share Log",
            filters={"sales_person": sales_person, "is_active": 1},
            pluck="customer"))
        filters["name"] = ["in", list(names) or [""]]

    if territory:
        filters["territory"] = territory

    customers = frappe.get_all("Customer",
        filters=filters,
        fields=["name", "customer_name", "territory", "customer_group",
                "custom_sfa_status", "custom_last_visit_date", "custom_visit_frequency"],
        limit_start=cint(start),
        limit_page_length=min(cint(page_length) or 200, 1000),
        order_by="customer_name")

    return {"items": customers, "total": frappe.db.count("Customer", filters)}

@frappe.whitelist()
@mobile_api
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
