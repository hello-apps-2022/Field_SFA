import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}

    columns = [
        {"label": _("Sales Person"), "fieldname": "sales_person", "fieldtype": "Link", "options": "Sales Person", "width": 160},
        {"label": _("Period"), "fieldname": "period", "fieldtype": "Data", "width": 100},
        {"label": _("Completed Visits"), "fieldname": "completed_visits", "fieldtype": "Int", "width": 140},
        {"label": _("Forms Submitted"), "fieldname": "forms_submitted", "fieldtype": "Int", "width": 130},
        {"label": _("Mandatory Submitted"), "fieldname": "mandatory_submitted", "fieldtype": "Int", "width": 160},
        {"label": _("Submission Rate %"), "fieldname": "submission_rate", "fieldtype": "Percent", "width": 140},
        {"label": _("Unique Templates"), "fieldname": "unique_templates", "fieldtype": "Int", "width": 140},
    ]

    group_by = "DATE_FORMAT(r.response_date, '%Y-%m')"
    if filters.get("group_by") == "Week":
        group_by = "YEARWEEK(r.response_date, 1)"

    conditions = []
    args = {
        "from_date": filters.get("from_date", frappe.utils.add_months(frappe.utils.today(), -3)),
        "to_date": filters.get("to_date", frappe.utils.today()),
    }
    if filters.get("sales_person"):
        conditions.append("AND r.sales_person = %(sales_person)s")
        args["sales_person"] = filters["sales_person"]

    condition_str = " ".join(conditions)

    data = frappe.db.sql("""
        SELECT
            r.sales_person,
            DATE_FORMAT(r.response_date, '%%Y-%%m') AS period,
            (
                SELECT COUNT(v.name)
                FROM `tabSFA Visit` v
                WHERE v.sales_person = r.sales_person
                  AND v.status = 'Completed'
                  AND DATE_FORMAT(v.visit_date, '%%Y-%%m') = DATE_FORMAT(r.response_date, '%%Y-%%m')
            ) AS completed_visits,
            COUNT(r.name) AS forms_submitted,
            SUM(
                CASE WHEN t.is_mandatory = 1 THEN 1 ELSE 0 END
            ) AS mandatory_submitted,
            ROUND(
                COUNT(r.name) * 100.0 /
                NULLIF((
                    SELECT COUNT(v2.name)
                    FROM `tabSFA Visit` v2
                    WHERE v2.sales_person = r.sales_person
                      AND v2.status = 'Completed'
                      AND DATE_FORMAT(v2.visit_date, '%%Y-%%m') = DATE_FORMAT(r.response_date, '%%Y-%%m')
                ), 0),
                1
            ) AS submission_rate,
            COUNT(DISTINCT r.form_template) AS unique_templates
        FROM `tabSFA Form Response` r
        LEFT JOIN `tabSFA Form Template` t ON t.name = r.form_template
        WHERE r.docstatus = 1
          AND DATE(r.response_date) BETWEEN %(from_date)s AND %(to_date)s
          {conditions}
        GROUP BY r.sales_person, DATE_FORMAT(r.response_date, '%%Y-%%m')
        ORDER BY r.sales_person, period DESC
    """.format(conditions=condition_str), args, as_dict=True)

    return columns, data
