import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}

    columns = [
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 180},
        {"label": _("Territory"), "fieldname": "territory", "fieldtype": "Link", "options": "Territory", "width": 130},
        {"label": _("Total Visits"), "fieldname": "total_visits", "fieldtype": "Int", "width": 110},
        {"label": _("Forms Submitted"), "fieldname": "forms_submitted", "fieldtype": "Int", "width": 130},
        {"label": _("Last Form Date"), "fieldname": "last_form_date", "fieldtype": "Date", "width": 120},
        {"label": _("Templates Used"), "fieldname": "templates_used", "fieldtype": "Data", "width": 200},
        {"label": _("Unique Questions Answered"), "fieldname": "questions_answered", "fieldtype": "Int", "width": 180},
    ]

    conditions = []
    args = {
        "from_date": filters.get("from_date", frappe.utils.add_months(frappe.utils.today(), -1)),
        "to_date": filters.get("to_date", frappe.utils.today()),
    }

    if filters.get("territory"):
        conditions.append("AND c.territory = %(territory)s")
        args["territory"] = filters["territory"]
    if filters.get("customer"):
        conditions.append("AND r.customer = %(customer)s")
        args["customer"] = filters["customer"]

    condition_str = " ".join(conditions)

    data = frappe.db.sql("""
        SELECT
            r.customer,
            c.territory,
            (
                SELECT COUNT(v.name)
                FROM `tabSFA Visit` v
                WHERE v.customer = r.customer
                  AND v.status = 'Completed'
                  AND v.visit_date BETWEEN %(from_date)s AND %(to_date)s
            ) AS total_visits,
            COUNT(DISTINCT r.name) AS forms_submitted,
            MAX(DATE(r.response_date)) AS last_form_date,
            GROUP_CONCAT(DISTINCT t.template_name ORDER BY t.template_name SEPARATOR ', ') AS templates_used,
            COUNT(ri.name) AS questions_answered
        FROM `tabSFA Form Response` r
        LEFT JOIN `tabCustomer` c ON c.name = r.customer
        LEFT JOIN `tabSFA Form Template` t ON t.name = r.form_template
        LEFT JOIN `tabSFA Response Item` ri ON ri.parent = r.name
        WHERE r.docstatus = 1
          AND DATE(r.response_date) BETWEEN %(from_date)s AND %(to_date)s
          {conditions}
        GROUP BY r.customer
        ORDER BY forms_submitted DESC
    """.format(conditions=condition_str), args, as_dict=True)

    return columns, data
