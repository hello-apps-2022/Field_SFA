import frappe
from frappe import _

def execute(filters=None):
    columns = [
        {"label": _("Rank"), "fieldname": "rank", "fieldtype": "Int", "width": 60},
        {"label": _("Sales Person"), "fieldname": "sales_person", "fieldtype": "Link", "options": "Sales Person", "width": 150},
        {"label": _("Territory"), "fieldname": "territory", "fieldtype": "Link", "options": "Territory", "width": 120},
        {"label": _("Total Points"), "fieldname": "total_points", "fieldtype": "Int", "width": 120},
        {"label": _("Badges"), "fieldname": "badges", "fieldtype": "Int", "width": 100},
        {"label": _("Visits"), "fieldname": "visits", "fieldtype": "Int", "width": 100},
        {"label": _("Orders"), "fieldname": "orders", "fieldtype": "Int", "width": 100},
    ]

    data = frappe.db.sql("""
        SELECT 
            ROW_NUMBER() OVER (ORDER BY COALESCE(SUM(pl.points), 0) DESC) as rank,
            sp.name as sales_person,
            sp.custom_territory as territory,
            COALESCE(SUM(pl.points), 0) as total_points,
            COUNT(DISTINCT rb.name) as badges,
            COUNT(DISTINCT v.name) as visits,
            COUNT(DISTINCT so.name) as orders
        FROM `tabSales Person` sp
        LEFT JOIN `tabSFA Rep Points Ledger` pl ON pl.sales_person = sp.name
        LEFT JOIN `tabSFA Rep Badge` rb ON rb.sales_person = sp.name
        LEFT JOIN `tabSFA Visit` v ON v.sales_person = sp.name AND v.docstatus = 1
        LEFT JOIN `tabSales Order` so ON so.custom_sfa_rep = sp.name AND so.docstatus = 1
        WHERE sp.enabled = 1
        GROUP BY sp.name
        ORDER BY total_points DESC
        LIMIT 50
    """, as_dict=True)

    return columns, data
