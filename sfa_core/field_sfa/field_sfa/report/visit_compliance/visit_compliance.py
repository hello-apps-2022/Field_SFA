import frappe
from frappe import _

def execute(filters=None):
    columns = [
        {"label": _("Sales Person"), "fieldname": "sales_person", "fieldtype": "Link", "options": "Sales Person", "width": 150},
        {"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 100},
        {"label": _("Planned Visits"), "fieldname": "planned", "fieldtype": "Int", "width": 120},
        {"label": _("Completed"), "fieldname": "completed", "fieldtype": "Int", "width": 100},
        {"label": _("Skipped"), "fieldname": "skipped", "fieldtype": "Int", "width": 100},
        {"label": _("Compliance %"), "fieldname": "compliance", "fieldtype": "Percent", "width": 120},
        {"label": _("Avg Duration (min)"), "fieldname": "avg_duration", "fieldtype": "Float", "width": 140},
    ]

    data = frappe.db.sql("""
        SELECT 
            bp.sales_person,
            bp.date,
            COUNT(bpc.name) as planned,
            SUM(CASE WHEN bpc.visit_status = 'Visited' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN bpc.visit_status = 'Skipped' THEN 1 ELSE 0 END) as skipped,
            ROUND(SUM(CASE WHEN bpc.visit_status = 'Visited' THEN 1 ELSE 0 END) / COUNT(bpc.name) * 100, 2) as compliance,
            ROUND(AVG(v.duration_minutes), 1) as avg_duration
        FROM `tabSFA Beat Plan` bp
        LEFT JOIN `tabSFA Beat Plan Customer` bpc ON bpc.parent = bp.name
        LEFT JOIN `tabSFA Visit` v ON v.customer = bpc.customer AND v.visit_date = bp.date AND v.sales_person = bp.sales_person
        WHERE bp.docstatus = 1
        GROUP BY bp.sales_person, bp.date
        ORDER BY bp.date DESC
    """, as_dict=True)

    return columns, data
