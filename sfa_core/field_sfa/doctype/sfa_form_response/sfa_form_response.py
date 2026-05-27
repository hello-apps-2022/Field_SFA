import frappe
import json
from frappe.model.document import Document
from frappe.utils import now_datetime


class SFAFormResponse(Document):

    def before_insert(self):
        if not self.response_date:
            self.response_date = now_datetime()

    def validate(self):
        if not self.response_items and not self.survey_response_json:
            frappe.throw("At least one response item or raw JSON is required.")

        # If response_items are empty but raw JSON exists, auto-populate them
        if not self.response_items and self.survey_response_json:
            self._populate_response_items_from_json()

    def _populate_response_items_from_json(self):
        """
        Parse survey_response_json and populate response_items table.
        SurveyJS response JSON is a flat dict: { "question_name": answer_value, ... }
        """
        try:
            raw = json.loads(self.survey_response_json) if isinstance(self.survey_response_json, str) else self.survey_response_json
        except (json.JSONDecodeError, TypeError):
            return

        # Build a lookup of question metadata from the template
        question_meta = {}
        if self.form_template:
            questions = frappe.get_all(
                "SFA Form Question",
                filters={"form_template": self.form_template},
                fields=["question_name", "question_title", "question_type"]
            )
            question_meta = {q["question_name"]: q for q in questions}

        for question_name, answer in raw.items():
            meta = question_meta.get(question_name, {})
            question_title = meta.get("question_title", question_name)
            question_type = meta.get("question_type", "text")

            # For arrays / dicts, store in answer_text; for scalars, use answer_value
            if isinstance(answer, (list, dict)):
                self.append("response_items", {
                    "question_name": question_name,
                    "question_title": question_title,
                    "question_type": question_type,
                    "answer_value": "",
                    "answer_text": json.dumps(answer),
                })
            else:
                self.append("response_items", {
                    "question_name": question_name,
                    "question_title": question_title,
                    "question_type": question_type,
                    "answer_value": str(answer) if answer is not None else "",
                    "answer_text": "",
                })
