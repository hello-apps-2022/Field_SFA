import frappe
from frappe import _

@frappe.whitelist()
def get_form_templates(customer=None, visit=None):
    """Get applicable form templates for mobile app"""
    filters = {"is_active": 1}

    templates = frappe.get_all("SFA Form Template",
        filters=filters,
        fields=["name", "template_name", "description", "survey_json", 
                "is_mandatory", "version"],
        order_by="template_name")

    return templates

@frappe.whitelist()
def submit_form_response(form_template, visit, customer, sales_person, responses, **kwargs):
    """Submit form response from mobile app"""
    response = frappe.get_doc({
        "doctype": "SFA Form Response",
        "form_template": form_template,
        "visit": visit,
        "customer": customer,
        "sales_person": sales_person,
        "response_date": frappe.utils.now(),
        **kwargs
    })

    # Process responses
    for r in responses:
        q_type = r.get("question_type")
        if q_type == "number":
            response.append("responses", {
                "question_name": r.get("name"),
                "question_title": r.get("title"),
                "response_value": r.get("value")
            })
        elif q_type == "text":
            response.append("text_responses", {
                "question_name": r.get("name"),
                "question_title": r.get("title"),
                "response_value": r.get("value")
            })
        elif q_type == "option":
            response.append("option_responses", {
                "question_name": r.get("name"),
                "question_title": r.get("title"),
                "response_value": r.get("value")
            })
        elif q_type == "boolean":
            response.append("boolean_responses", {
                "question_name": r.get("name"),
                "question_title": r.get("title"),
                "response_value": r.get("value")
            })
        elif q_type == "file":
            response.append("file_responses", {
                "question_name": r.get("name"),
                "question_title": r.get("title"),
                "response_value": r.get("value")
            })

    response.insert(ignore_permissions=True)
    response.submit()

    return {"name": response.name, "status": "submitted"}
