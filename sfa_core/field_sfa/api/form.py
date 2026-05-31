import frappe
from frappe import _
import json
from frappe.utils import now_datetime


@frappe.whitelist()
def get_form_templates(customer=None, visit=None):
    """
    Return active form templates applicable to a visit/customer.
    Called by the mobile app when loading forms for a visit.
    """
    filters = {"is_active": 1}

    templates = frappe.get_all(
        "SFA Form Template",
        filters=filters,
        fields=[
            "name", "template_name", "category", "description",
            "survey_json", "is_mandatory", "trigger_point", "version"
        ],
        order_by="template_name"
    )

    # If a customer is provided, filter by scope
    if customer:
        customer_doc = frappe.db.get_value("Customer", customer, ["customer_group", "territory"], as_dict=True)
        scoped = []
        for t in templates:
            applicable = frappe.db.get_value("SFA Form Template", t["name"], "applicable_to")
            if applicable == "All Customers":
                scoped.append(t)
            elif applicable == "Customer Group" and customer_doc:
                cg = frappe.db.get_value("SFA Form Template", t["name"], "customer_group")
                if cg == customer_doc.get("customer_group"):
                    scoped.append(t)
            elif applicable == "Territory" and customer_doc:
                ter = frappe.db.get_value("SFA Form Template", t["name"], "territory")
                if ter == customer_doc.get("territory"):
                    scoped.append(t)
            else:
                scoped.append(t)
        templates = scoped

    # Parse survey_json so the mobile app gets a proper object
    for t in templates:
        if t.get("survey_json"):
            try:
                t["survey_json"] = json.loads(t["survey_json"]) if isinstance(t["survey_json"], str) else t["survey_json"]
            except json.JSONDecodeError:
                t["survey_json"] = {}

    return templates


@frappe.whitelist()
def submit_form_response(form_template, visit, customer, sales_person,
                         survey_response_json, latitude=None, longitude=None, accuracy=None, captured_at=None, **kwargs):
    """
    Submit a completed form response from the mobile app.

    survey_response_json: flat dict of { question_name: answer_value } as produced
    by SurveyJS Model.getData()
    """
    from sfa_core.api.auth import resolve_sales_person
    sales_person = resolve_sales_person(sales_person)
    # Avoid duplicate submission for the same visit + template
    existing = frappe.db.exists("SFA Form Response", {
        "form_template": form_template,
        "visit": visit,
        "docstatus": ["!=", 2],  # not cancelled
    })
    if existing:
        return {"name": existing, "status": "already_exists"}

    survey_version = frappe.db.get_value("SFA Form Template", form_template, "version") or 1

    response = frappe.get_doc({
        "doctype": "SFA Form Response",
        "form_template": form_template,
        "visit": visit,
        "customer": customer,
        "sales_person": sales_person,
        "response_date": now_datetime(),
        "latitude": latitude,
        "longitude": longitude,
        "custom_sfa_gps_accuracy": accuracy,
        "custom_sfa_captured_at": captured_at,
        "sync_status": "Synced",
        "survey_version": survey_version,
        "survey_response_json": survey_response_json
            if isinstance(survey_response_json, str)
            else json.dumps(survey_response_json),
    })

    # Populate response_items from the JSON automatically (via controller)
    response.insert(ignore_permissions=True)
    response.submit()

    return {"name": response.name, "status": "submitted"}


@frappe.whitelist()
def get_form_responses(form_template=None, visit=None, customer=None,
                       sales_person=None, from_date=None, to_date=None, limit=50):
    """
    Fetch form responses with optional filters.
    Used by Frappe desk and reporting.
    """
    filters = {}
    if form_template:
        filters["form_template"] = form_template
    if visit:
        filters["visit"] = visit
    if customer:
        filters["customer"] = customer
    if sales_person:
        filters["sales_person"] = sales_person
    if from_date:
        filters["response_date"] = [">=", from_date]
    if to_date:
        if "response_date" in filters:
            filters["response_date"] = ["between", [from_date, to_date]]
        else:
            filters["response_date"] = ["<=", to_date]

    responses = frappe.get_all(
        "SFA Form Response",
        filters=filters,
        fields=[
            "name", "form_template", "visit", "customer",
            "sales_person", "response_date", "sync_status", "survey_version"
        ],
        limit=limit,
        order_by="response_date desc"
    )
    return responses


@frappe.whitelist()
def get_response_detail(response_name):
    """
    Return full response including all response_items.
    """
    doc = frappe.get_doc("SFA Form Response", response_name)
    return doc.as_dict()


@frappe.whitelist()
def duplicate_form_template(template_name):
    """
    Duplicate a form template (called from FormTemplates.vue).
    """
    source = frappe.get_doc("SFA Form Template", template_name)
    new_doc = frappe.copy_doc(source)
    new_doc.template_name = f"Copy of {source.template_name}"
    new_doc.version = 1
    new_doc.insert(ignore_permissions=True)
    return {"name": new_doc.name, "template_name": new_doc.template_name}
