import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}

    if not filters.get("form_template") or not filters.get("question_name"):
        frappe.throw(_("Please select a Form Template and Question."))

    columns = [
        {"label": _("Answer Option"), "fieldname": "answer_value", "fieldtype": "Data", "width": 240},
        {"label": _("Count"), "fieldname": "count", "fieldtype": "Int", "width": 100},
        {"label": _("Percentage"), "fieldname": "percentage", "fieldtype": "Percent", "width": 120},
        {"label": _("Last Seen"), "fieldname": "last_seen", "fieldtype": "Date", "width": 120},
    ]

    args = {
        "form_template": filters["form_template"],
        "question_name": filters["question_name"],
        "from_date": filters.get("from_date", frappe.utils.add_months(frappe.utils.today(), -1)),
        "to_date": filters.get("to_date", frappe.utils.today()),
    }

    # Total responses for this question in period
    total_result = frappe.db.sql("""
        SELECT COUNT(ri.name) as total
        FROM `tabSFA Response Item` ri
        INNER JOIN `tabSFA Form Response` r ON r.name = ri.parent
        WHERE r.form_template = %(form_template)s
          AND r.docstatus = 1
          AND ri.question_name = %(question_name)s
          AND DATE(r.response_date) BETWEEN %(from_date)s AND %(to_date)s
    """, args, as_dict=True)
    total = total_result[0]["total"] if total_result else 0

    rows = frappe.db.sql("""
        SELECT
            ri.answer_value,
            COUNT(*) AS count,
            MAX(DATE(r.response_date)) AS last_seen
        FROM `tabSFA Response Item` ri
        INNER JOIN `tabSFA Form Response` r ON r.name = ri.parent
        WHERE r.form_template = %(form_template)s
          AND r.docstatus = 1
          AND ri.question_name = %(question_name)s
          AND ri.answer_value != ''
          AND DATE(r.response_date) BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY ri.answer_value
        ORDER BY count DESC
    """, args, as_dict=True)

    data = []
    for row in rows:
        row["percentage"] = round(row["count"] * 100.0 / total, 1) if total else 0
        data.append(row)

    return columns, data
