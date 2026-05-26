import frappe
from frappe import _

def execute(filters=None):
    columns = [
        {"label": _("Sales Person"), "fieldname": "sales_person", "fieldtype": "Link", "options": "Sales Person", "width": 150},
        {"label": _("Visits"), "fieldname": "visits", "fieldtype": "Int", "width": 100},
        {"label": _("Visit Hours"), "fieldname": "visit_hours", "fieldtype": "Float", "width": 120},
        {"label": _("Orders"), "fieldname": "orders", "fieldtype": "Int", "width": 100},
        {"label": _("Payments"), "fieldname": "payments", "fieldtype": "Int", "width": 100},
        {"label": _("Forms"), "fieldname": "forms", "fieldtype": "Int", "width": 100},
        {"label": _("GPS Points"), "fieldname": "gps_points", "fieldtype": "Int", "width": 120},
        {"label": _("Points"), "fieldname": "points", "fieldtype": "Int", "width": 100},
    ]

    data = frappe.db.sql("""
        SELECT 
            sp.name as sales_person,
            COUNT(DISTINCT v.name) as visits,
            ROUND(SUM(v.duration_minutes)/60, 1) as visit_hours,
            COUNT(DISTINCT so.name) as orders,
            COUNT(DISTINCT p.name) as payments,
            COUNT(DISTINCT fr.name) as forms,
            COUNT(DISTINCT gp.name) as gps_points,
            COALESCE(SUM(pl.points), 0) as points
        FROM `tabSales Person` sp
        LEFT JOIN `tabSFA Visit` v ON v.sales_person = sp.name AND v.docstatus = 1
        LEFT JOIN `tabSales Order` so ON so.custom_sfa_rep = sp.name AND so.docstatus = 1
        LEFT JOIN `tabSFA Payment` p ON p.sales_person = sp.name AND p.docstatus = 1
        LEFT JOIN `tabSFA Form Response` fr ON fr.sales_person = sp.name AND fr.docstatus = 1
        LEFT JOIN `tabSFA GPS Track Point` gp ON gp.sales_person = sp.name
        LEFT JOIN `tabSFA Rep Points Ledger` pl ON pl.sales_person = sp.name
        WHERE sp.enabled = 1
        GROUP BY sp.name
        ORDER BY points DESC
    """, as_dict=True)

    return columns, data
