import frappe
from frappe import _

def execute(filters=None):
    columns = [
        {"label": _("Sales Person"), "fieldname": "sales_person", "fieldtype": "Link", "options": "Sales Person", "width": 150},
        {"label": _("Period"), "fieldname": "period", "fieldtype": "Data", "width": 120},
        {"label": _("Orders"), "fieldname": "orders", "fieldtype": "Int", "width": 100},
        {"label": _("Order Value"), "fieldname": "order_value", "fieldtype": "Currency", "width": 140},
        {"label": _("Payments"), "fieldname": "payments", "fieldtype": "Int", "width": 100},
        {"label": _("Payment Value"), "fieldname": "payment_value", "fieldtype": "Currency", "width": 140},
        {"label": _("Cartons"), "fieldname": "cartons", "fieldtype": "Float", "width": 100},
        {"label": _("Free Qty"), "fieldname": "free_qty", "fieldtype": "Float", "width": 100},
    ]

    data = frappe.db.sql("""
        SELECT 
            so.custom_sfa_rep as sales_person,
            DATE_FORMAT(so.transaction_date, '%Y-%m') as period,
            COUNT(DISTINCT so.name) as orders,
            SUM(so.grand_total) as order_value,
            COUNT(DISTINCT p.name) as payments,
            SUM(p.amount) as payment_value,
            SUM(soi.custom_carton_qty) as cartons,
            SUM(soi.custom_free_qty) as free_qty
        FROM `tabSales Order` so
        LEFT JOIN `tabSales Order Item` soi ON soi.parent = so.name
        LEFT JOIN `tabSFA Payment` p ON p.sales_person = so.custom_sfa_rep AND p.payment_date = so.transaction_date
        WHERE so.docstatus = 1 AND so.custom_sfa_rep IS NOT NULL
        GROUP BY so.custom_sfa_rep, DATE_FORMAT(so.transaction_date, '%Y-%m')
        ORDER BY period DESC
    """, as_dict=True)

    return columns, data
