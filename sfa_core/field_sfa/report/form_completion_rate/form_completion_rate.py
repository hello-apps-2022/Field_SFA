import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}

    columns = [
        {"label": _("Sales Person"), "fieldname": "sales_person", "fieldtype": "Link", "options": "Sales Person", "width": 160},
        {"label": _("Form Template"), "fieldname": "form_template", "fieldtype": "Link", "options": "SFA Form Template", "width": 200},
        {"label": _("Category"), "fieldname": "category", "fieldtype": "Data", "width": 130},
        {"label": _("Assigned"), "fieldname": "assigned", "fieldtype": "Int", "width": 100},
        {"label": _("Submitted"), "fieldname": "submitted", "fieldtype": "Int", "width": 100},
        {"label": _("Completion %"), "fieldname": "completion_rate", "fieldtype": "Percent", "width": 120},
        {"label": _("Avg per Day"), "fieldname": "avg_per_day", "fieldtype": "Float", "width": 110},
    ]

    conditions = _build_conditions(filters)

    data = frappe.db.sql("""
        SELECT
            r.sales_person,
            r.form_template,
            t.category,
            COUNT(r.name) AS submitted,
            ROUND(COUNT(r.name) /
                NULLIF(DATEDIFF(%(to_date)s, %(from_date)s) + 1, 0), 2
            ) AS avg_per_day,
            (
                SELECT COUNT(v.name)
                FROM `tabSFA Visit` v
                WHERE v.sales_person = r.sales_person
                  AND v.visit_date BETWEEN %(from_date)s AND %(to_date)s
                  AND v.status = 'Completed'
            ) AS assigned,
            ROUND(
                COUNT(r.name) * 100.0 /
                NULLIF(
                    (SELECT COUNT(v2.name)
                     FROM `tabSFA Visit` v2
                     WHERE v2.sales_person = r.sales_person
                       AND v2.visit_date BETWEEN %(from_date)s AND %(to_date)s
                       AND v2.status = 'Completed'),
                    0
                ),
                1
            ) AS completion_rate
        FROM `tabSFA Form Response` r
        LEFT JOIN `tabSFA Form Template` t ON t.name = r.form_template
        WHERE r.docstatus = 1
          AND DATE(r.response_date) BETWEEN %(from_date)s AND %(to_date)s
          {conditions}
        GROUP BY r.sales_person, r.form_template
        ORDER BY r.sales_person, completion_rate DESC
    """.format(conditions=conditions), {
        "from_date": filters.get("from_date", frappe.utils.add_months(frappe.utils.today(), -1)),
        "to_date": filters.get("to_date", frappe.utils.today()),
        "sales_person": filters.get("sales_person"),
        "form_template": filters.get("form_template"),
    }, as_dict=True)

    return columns, data


def _build_conditions(filters):
    parts = []
    if filters.get("sales_person"):
        parts.append("AND r.sales_person = %(sales_person)s")
    if filters.get("form_template"):
        parts.append("AND r.form_template = %(form_template)s")
    return " ".join(parts)
