"""
sfa_core/api/reports.py
In-app report viewer backend.

Wraps the existing Frappe query reports so the SFA SPA can run them without
Desk access. Applies RBAC scoping server-side (reps -> own data, managers ->
own territory, admins -> all) so filters cannot be tampered with to widen
access. Export (CSV/Excel) is gated by a per-user flag; admins always allowed.
"""
import frappe
from frappe import _
from sfa_core.api.auth import get_scope_context as get_user_context


# Allowlist of reports the SPA may run, with display metadata + which filter
# controls the frontend should render. Keep in sync with the report folders.
REPORTS = {
	"rep_productivity": {
		"label": "Rep Productivity",
		"desc": "Orders, payments and visits per rep",
		"icon": "trending-up",
		"filters": ["from_date", "to_date", "territory", "sales_person"],
		"chart": {"type": "bar", "x": "sales_person", "y": "points"},
	},
	"sales_performance": {
		"label": "Sales Performance",
		"desc": "Revenue and order performance by territory",
		"icon": "bar-chart-2",
		"filters": ["from_date", "to_date", "territory"],
		"chart": {"type": "bar", "x": "territory", "y": "revenue"},
	},
	"visit_compliance": {
		"label": "Visit Compliance",
		"desc": "Beat plan adherence and visit completion",
		"icon": "activity",
		"filters": ["from_date", "to_date", "territory", "sales_person"],
		"chart": {"type": "bar", "x": "sales_person", "y": "compliance_pct"},
	},
	"leaderboard": {
		"label": "Leaderboard",
		"desc": "Gamification points and badges ranking",
		"icon": "award",
		"filters": ["from_date", "to_date", "territory"],
		"chart": {"type": "bar", "x": "sales_person", "y": "points"},
	},
	"form_completion_rate": {
		"label": "Form Completion Rate",
		"desc": "Completion % by rep, template, date range",
		"icon": "check-circle",
		"filters": ["from_date", "to_date", "sales_person", "form_template"],
		"chart": {"type": "bar", "x": "sales_person", "y": "completion_pct"},
	},
	"response_by_question": {
		"label": "Response By Question",
		"desc": "Per-question trends, top answers, skip rates",
		"icon": "help-circle",
		"filters": ["from_date", "to_date", "form_template"],
		"chart": None,
	},
	"outlet_feedback_summary": {
		"label": "Outlet Feedback Summary",
		"desc": "Forms submitted per customer and territory",
		"icon": "map-pin",
		"filters": ["from_date", "to_date", "territory", "customer"],
		"chart": None,
	},
	"rep_survey_activity": {
		"label": "Rep Survey Activity",
		"desc": "Weekly/monthly form submission by rep",
		"icon": "user",
		"filters": ["from_date", "to_date", "sales_person"],
		"chart": {"type": "bar", "x": "sales_person", "y": "submissions"},
	},
	"option_distribution": {
		"label": "Option Distribution",
		"desc": "MCQ answer breakdown per question",
		"icon": "pie-chart",
		"filters": ["from_date", "to_date", "form_template", "question_name"],
		"chart": {"type": "pie", "x": "option", "y": "count"},
	},
	"beat_plan_survey_coverage": {
		"label": "Beat Plan Survey Coverage",
		"desc": "Form coverage per route and territory",
		"icon": "map",
		"filters": ["from_date", "to_date", "territory", "sales_person"],
		"chart": None,
	},
	"customer_share_analysis": {
		"label": "Customer Share Analysis",
		"desc": "Outlet sharing activity and reach",
		"icon": "share-2",
		"filters": ["from_date", "to_date", "territory"],
		"chart": None,
	},
}


def _apply_rbac(filters):
	"""Force role-appropriate scoping into the filters. Reps are locked to
	their own sales_person; managers to their territory. Admins unrestricted.
	This overrides any client-supplied value for those keys."""
	ctx = get_user_context()
	filters = dict(filters or {})

	if ctx["is_admin"]:
		return filters, ctx

	if ctx["is_manager"]:
		if ctx.get("territory"):
			filters["territory"] = ctx["territory"]
		return filters, ctx

	# Rep (or anything else): lock to own sales_person, drop territory widening
	if ctx.get("sales_person"):
		filters["sales_person"] = ctx["sales_person"]
	else:
		filters["sales_person"] = "__no_access__"
	filters.pop("territory", None)
	return filters, ctx


def _can_export():
	"""Admins always; otherwise the per-user flag on User."""
	ctx = get_user_context()
	if ctx["is_admin"]:
		return True
	return bool(
		frappe.db.get_value("User", frappe.session.user, "custom_can_export_reports")
	)


@frappe.whitelist()
def get_reports_list():
	"""Return the allowlisted reports (metadata only) for the launcher grid,
	plus whether the current user may export."""
	return {
		"reports": [
			{"name": key, **{k: v for k, v in meta.items() if k != "chart"},
			 "has_chart": bool(meta.get("chart"))}
			for key, meta in REPORTS.items()
		],
		"can_export": _can_export(),
	}


@frappe.whitelist()
def run_report(report_name, filters=None):
	"""Run an allowlisted report with RBAC-scoped filters, return columns+data."""
	if report_name not in REPORTS:
		frappe.throw(_("Unknown report: {0}").format(report_name))

	if isinstance(filters, str):
		import json
		filters = json.loads(filters or "{}")

	scoped, ctx = _apply_rbac(filters)

	module = frappe.get_attr(
		f"sfa_core.field_sfa.report.{report_name}.{report_name}.execute"
	)
	result = module(frappe._dict(scoped))
	columns, data = result[0], result[1]

	return {
		"columns": columns,
		"data": data,
		"chart": REPORTS[report_name].get("chart"),
		"can_export": _can_export(),
		"meta": {k: v for k, v in REPORTS[report_name].items() if k != "chart"},
	}


@frappe.whitelist()
def export_report(report_name, filters=None, file_format="Excel"):
	"""Export a report to Excel or CSV. Gated by the per-user export flag."""
	if not _can_export():
		frappe.throw(
			_("You do not have permission to export reports."),
			frappe.PermissionError,
		)
	if report_name not in REPORTS:
		frappe.throw(_("Unknown report: {0}").format(report_name))

	if isinstance(filters, str):
		import json
		filters = json.loads(filters or "{}")

	scoped, ctx = _apply_rbac(filters)
	module = frappe.get_attr(
		f"sfa_core.field_sfa.report.{report_name}.{report_name}.execute"
	)
	result = module(frappe._dict(scoped))
	columns, data = result[0], result[1]

	header = [c.get("label") for c in columns]
	fieldnames = [c.get("fieldname") for c in columns]
	rows = [header]
	for row in data:
		rows.append([row.get(fn) if isinstance(row, dict) else None for fn in fieldnames])

	label = REPORTS[report_name]["label"].replace(" ", "_")

	if file_format == "CSV":
		from frappe.utils.csvutils import to_csv
		content = to_csv(rows)
		frappe.response["result"] = content
		frappe.response["type"] = "csv"
		frappe.response["doctype"] = label
	else:
		from frappe.utils.xlsxutils import make_xlsx
		xlsx_file = make_xlsx(rows, label)
		frappe.response["filename"] = f"{label}.xlsx"
		frappe.response["filecontent"] = xlsx_file.getvalue()
		frappe.response["type"] = "binary"
