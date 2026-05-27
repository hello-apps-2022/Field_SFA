import frappe
import json
from frappe.model.document import Document
from frappe.utils import now_datetime


class SFAFormTemplate(Document):

    def before_save(self):
        if not self.created_by:
            self.created_by = frappe.session.user
        if not self.created_on:
            self.created_on = now_datetime()
        if not self.version:
            self.version = 1

    def after_save(self):
        if self.survey_json:
            try:
                survey = json.loads(self.survey_json) if isinstance(self.survey_json, str) else self.survey_json
                self._sync_questions(survey)
            except Exception as e:
                frappe.log_error(f"Question sync failed: {e}", "SFA Form Template")

    def _sync_questions(self, survey_json):
        parsed_questions = []
        for page in survey_json.get("pages", []):
            for element in page.get("elements", []):
                self._extract_questions(element, parsed_questions)

        parsed_names = {q["question_name"] for q in parsed_questions}

        for q in parsed_questions:
            existing = frappe.get_all("SFA Form Question",
                filters={"form_template": self.name, "question_name": q["question_name"]},
                fields=["name"])
            if existing:
                frappe.db.set_value("SFA Form Question", existing[0]["name"], {
                    "question_title": q["question_title"],
                    "question_type": q["question_type"],
                })
            else:
                frappe.get_doc({
                    "doctype": "SFA Form Question",
                    "form_template": self.name,
                    "question_name": q["question_name"],
                    "question_title": q["question_title"],
                    "question_type": q["question_type"],
                    "page_number": q["page_number"],
                }).insert(ignore_permissions=True)

        frappe.db.delete("SFA Form Question", {
            "form_template": self.name,
            "question_name": ["not in", list(parsed_names)] if parsed_names else ["!=", ""]
        })

    def _extract_questions(self, element, result, parent_name="", page_number=1):
        if element.get("elements"):
            for sub in element["elements"]:
                self._extract_questions(sub, result, element.get("name", ""), page_number)
        else:
            title = element.get("title", "")
            if isinstance(title, dict):
                title = title.get("default", element.get("name", ""))
            result.append({
                "question_name": element.get("name", ""),
                "question_title": title or element.get("name", ""),
                "question_type": element.get("type", "text"),
                "parent_question": parent_name,
                "page_number": page_number,
            })

    def on_trash(self):
        frappe.db.delete("SFA Form Question", {"form_template": self.name})
