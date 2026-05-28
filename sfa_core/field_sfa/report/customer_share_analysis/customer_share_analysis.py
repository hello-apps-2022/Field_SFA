import frappe
from frappe import _

def execute(filters=None):
    columns = [
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 150},
        {"label": _("Current Rep"), "fieldname": "current_rep", "fieldtype": "Link", "options": "Sales Person", "width": 150},
        {"label": _("Share Type"), "fieldname": "share_type", "fieldtype": "Data", "width": 120},
        {"label": _("Since"), "fieldname": "since", "fieldtype": "Date", "width": 120},
        {"label": _("Days Since Visit"), "fieldname": "days_since_visit", "fieldtype": "Int", "width": 140},
        {"label": _("Outstanding"), "fieldname": "outstanding", "fieldtype": "Currency", "width": 140},
        {"label": _("Territory"), "fieldname": "territory", "fieldtype": "Link", "options": "Territory", "width": 120},
    ]

    data = frappe.db.sql("""
        SELECT 
            csl.customer,
            c.customer_name,
            csl.sales_person as current_rep,
            csl.share_type,
            csl.share_date as since,
            DATEDIFF(CURDATE(), c.custom_last_visit_date) as days_since_visit,
            c.custom_outstanding_payments as outstanding,
            c.territory
        FROM `tabSFA Customer Share Log` csl
        JOIN `tabCustomer` c ON c.name = csl.customer
        WHERE csl.is_active = 1
        ORDER BY days_since_visit DESC
    """, as_dict=True)

    return columns, data
