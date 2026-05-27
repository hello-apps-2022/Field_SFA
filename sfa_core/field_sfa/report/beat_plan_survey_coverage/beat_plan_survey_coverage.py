import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}

    columns = [
        {"label": _("Beat Plan"), "fieldname": "beat_plan", "fieldtype": "Link", "options": "SFA Beat Plan", "width": 180},
        {"label": _("Territory"), "fieldname": "territory", "fieldtype": "Link", "options": "Territory", "width": 130},
        {"label": _("Sales Person"), "fieldname": "sales_person", "fieldtype": "Link", "options": "Sales Person", "width": 150},
        {"label": _("Customers on Route"), "fieldname": "customers_on_route", "fieldtype": "Int", "width": 160},
        {"label": _("Visits Completed"), "fieldname": "visits_completed", "fieldtype": "Int", "width": 140},
        {"label": _("Forms Submitted"), "fieldname": "forms_submitted", "fieldtype": "Int", "width": 130},
        {"label": _("Mandatory Completed"), "fieldname": "mandatory_completed", "fieldtype": "Int", "width": 170},
        {"label": _("Coverage %"), "fieldname": "coverage_pct", "fieldtype": "Percent", "width": 110},
    ]

    conditions = []
    args = {
        "from_date": filters.get("from_date", frappe.utils.add_months(frappe.utils.today(), -1)),
        "to_date": filters.get("to_date", frappe.utils.today()),
    }
    if filters.get("territory"):
        conditions.append("AND bp.territory = %(territory)s")
        args["territory"] = filters["territory"]
    if filters.get("sales_person"):
        conditions.append("AND bp.sales_person = %(sales_person)s")
        args["sales_person"] = filters["sales_person"]

    condition_str = " ".join(conditions)

    data = frappe.db.sql("""
        SELECT
            bp.name AS beat_plan,
            bp.territory,
            bp.sales_person,
            COUNT(DISTINCT bpc.customer) AS customers_on_route,
            COUNT(DISTINCT v.name) AS visits_completed,
            COUNT(DISTINCT r.name) AS forms_submitted,
            SUM(
                CASE WHEN t.is_mandatory = 1 AND r.name IS NOT NULL THEN 1 ELSE 0 END
            ) AS mandatory_completed,
            ROUND(
                COUNT(DISTINCT r.name) * 100.0 /
                NULLIF(COUNT(DISTINCT v.name), 0),
                1
            ) AS coverage_pct
        FROM `tabSFA Beat Plan` bp
        LEFT JOIN `tabSFA Beat Plan Customer` bpc ON bpc.parent = bp.name
        LEFT JOIN `tabSFA Visit` v ON v.customer = bpc.customer
            AND v.sales_person = bp.sales_person
            AND v.status = 'Completed'
            AND v.visit_date BETWEEN %(from_date)s AND %(to_date)s
        LEFT JOIN `tabSFA Form Response` r ON r.visit = v.name
            AND r.docstatus = 1
        LEFT JOIN `tabSFA Form Template` t ON t.name = r.form_template
        WHERE bp.docstatus = 1
          {conditions}
        GROUP BY bp.name
        ORDER BY coverage_pct ASC
    """.format(conditions=condition_str), args, as_dict=True)

    return columns, data
