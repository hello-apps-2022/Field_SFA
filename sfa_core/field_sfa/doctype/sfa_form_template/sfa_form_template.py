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
        """Auto-create/update SFA Form Question records from survey_json."""
        if self.survey_json:
            try:
                survey = json.loads(self.survey_json) if isinstance(self.survey_json, str) else self.survey_json
                self._sync_questions(survey)
            except (json.JSONDecodeError, Exception) as e:
                frappe.log_error(f"SFA Form Template question sync failed: {e}", "SFA Form Template")

    def _sync_questions(self, survey_json):
        """Parse SurveyJS JSON and keep SFA Form Question records in sync."""
        parsed_questions = []
        for page in survey_json.get("pages", []):
            for element in page.get("elements", []):
                self._extract_questions(element, parsed_questions, parent_name="")

        parsed_names = {q["question_name"] for q in parsed_questions}

        # Upsert each question
        for q in parsed_questions:
            existing = frappe.get_all(
                "SFA Form Question",
                filters={"form_template": self.name, "question_name": q["question_name"]},
                fields=["name"]
            )
            if existing:
                doc = frappe.get_doc("SFA Form Question", existing[0]["name"])
                doc.question_title = q["question_title"]
                doc.question_type = q["question_type"]
                doc.parent_question = q["parent_question"]
                doc.page_number = q["page_number"]
                doc.save(ignore_permissions=True)
            else:
                frappe.get_doc({
                    "doctype": "SFA Form Question",
                    "form_template": self.name,
                    "question_name": q["question_name"],
                    "question_title": q["question_title"],
                    "question_type": q["question_type"],
                    "parent_question": q["parent_question"],
                    "page_number": q["page_number"],
                }).insert(ignore_permissions=True)

        # Delete questions removed from the survey
        existing_all = frappe.get_all(
            "SFA Form Question",
            filters={"form_template": self.name},
            fields=["name", "question_name"]
        )
        for existing in existing_all:
            if existing["question_name"] not in parsed_names:
                frappe.delete_doc("SFA Form Question", existing["name"], ignore_permissions=True)

    def _extract_questions(self, element, result, parent_name, page_number=1):
        """Recursively extract questions, handling panels."""
        sub_elements = element.get("elements")
        if sub_elements:
            # Panel — recurse into sub-elements
            for sub in sub_elements:
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
        """Clean up questions when template is deleted."""
        frappe.db.delete("SFA Form Question", {"form_template": self.name})
