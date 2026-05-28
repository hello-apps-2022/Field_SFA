import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}

    if not filters.get("form_template"):
        frappe.throw(_("Please select a Form Template to analyse responses by question."))

    columns = [
        {"label": _("Question"), "fieldname": "question_title", "fieldtype": "Data", "width": 260},
        {"label": _("Question Type"), "fieldname": "question_type", "fieldtype": "Data", "width": 120},
        {"label": _("Total Responses"), "fieldname": "total_responses", "fieldtype": "Int", "width": 130},
        {"label": _("Answered"), "fieldname": "answered", "fieldtype": "Int", "width": 100},
        {"label": _("Skipped"), "fieldname": "skipped", "fieldtype": "Int", "width": 100},
        {"label": _("Most Common Answer"), "fieldname": "top_answer", "fieldtype": "Data", "width": 200},
        {"label": _("Avg Score"), "fieldname": "avg_score", "fieldtype": "Float", "width": 110,
         "description": "For numeric/rating questions only"},
    ]

    date_filter = ""
    args = {
        "form_template": filters["form_template"],
        "from_date": filters.get("from_date", frappe.utils.add_months(frappe.utils.today(), -1)),
        "to_date": filters.get("to_date", frappe.utils.today()),
    }

    if filters.get("from_date") and filters.get("to_date"):
        date_filter = "AND DATE(r.response_date) BETWEEN %(from_date)s AND %(to_date)s"

    # Get question list for this template
    questions = frappe.get_all(
        "SFA Form Question",
        filters={"form_template": filters["form_template"]},
        fields=["question_name", "question_title", "question_type"],
        order_by="page_number asc"
    )

    # Total responses for this template in the period
    total_count = frappe.db.sql("""
        SELECT COUNT(r.name) as cnt
        FROM `tabSFA Form Response` r
        WHERE r.form_template = %(form_template)s
          AND r.docstatus = 1
          {date_filter}
    """.format(date_filter=date_filter), args, as_dict=True)
    total = (total_count[0]["cnt"] if total_count else 0) or 0

    data = []
    for q in questions:
        q_args = dict(args, question_name=q["question_name"])

        # Count how many responses have an answer for this question
        answered_result = frappe.db.sql("""
            SELECT COUNT(ri.name) as cnt
            FROM `tabSFA Response Item` ri
            INNER JOIN `tabSFA Form Response` r ON r.name = ri.parent
            WHERE r.form_template = %(form_template)s
              AND r.docstatus = 1
              AND ri.question_name = %(question_name)s
              AND (ri.answer_value != '' OR ri.answer_text != '')
              {date_filter}
        """.format(date_filter=date_filter), q_args, as_dict=True)
        answered = answered_result[0]["cnt"] if answered_result else 0

        # Most common answer (for short answers / options)
        top_answer_result = frappe.db.sql("""
            SELECT ri.answer_value, COUNT(*) as freq
            FROM `tabSFA Response Item` ri
            INNER JOIN `tabSFA Form Response` r ON r.name = ri.parent
            WHERE r.form_template = %(form_template)s
              AND r.docstatus = 1
              AND ri.question_name = %(question_name)s
              AND ri.answer_value != ''
              {date_filter}
            GROUP BY ri.answer_value
            ORDER BY freq DESC
            LIMIT 1
        """.format(date_filter=date_filter), q_args, as_dict=True)
        top_answer = top_answer_result[0]["answer_value"] if top_answer_result else ""

        # Average numeric score (for rating, number type questions)
        avg_score = None
        if q["question_type"] in ("rating", "text", "expression"):
            avg_result = frappe.db.sql("""
                SELECT AVG(CAST(ri.answer_value AS DECIMAL(10,2))) as avg_val
                FROM `tabSFA Response Item` ri
                INNER JOIN `tabSFA Form Response` r ON r.name = ri.parent
                WHERE r.form_template = %(form_template)s
                  AND r.docstatus = 1
                  AND ri.question_name = %(question_name)s
                  AND ri.answer_value REGEXP '^[0-9]+\\.?[0-9]*$'
                  {date_filter}
            """.format(date_filter=date_filter), q_args, as_dict=True)
            if avg_result and avg_result[0]["avg_val"] is not None:
                avg_score = round(float(avg_result[0]["avg_val"]), 2)

        data.append({
            "question_title": q["question_title"],
            "question_type": q["question_type"],
            "total_responses": total,
            "answered": answered,
            "skipped": total - answered,
            "top_answer": top_answer,
            "avg_score": avg_score,
        })

    return columns, data
