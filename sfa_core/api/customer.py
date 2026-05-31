"""
sfa_core/api/customer.py
Outlet (Customer) creation: single create (used by the rep field-add flow)
and bulk CSV import (admin-only). Outlets are Frappe Customers with SFA
custom fields. Duplicates are skipped and reported.
"""
import frappe
from frappe import _
from sfa_core.api.auth import get_scope_context as get_user_context

IMPORT_COLUMNS = ["customer_name", "territory", "mobile_no", "customer_group", "outlet_tier", "location_area", "location_city"]
REQUIRED_COLUMNS = ["customer_name", "territory"]


def _normalize(s):
	return (s or "").strip()


def _find_duplicate(customer_name, territory, mobile_no):
	"""A duplicate = same name in same territory, or same phone (if given)."""
	name = _normalize(customer_name)
	terr = _normalize(territory)
	phone = _normalize(mobile_no)

	existing = frappe.db.get_value(
		"Customer",
		{"customer_name": name, "territory": terr},
		"name",
	)
	if existing:
		return existing
	if phone:
		existing = frappe.db.get_value("Customer", {"custom_mobile_no": phone}, "name")
		if existing:
			return existing
	return None


def _create_one(data, rep=None):
	"""Create a single Customer/outlet. Returns the new name. Caller handles
	dedup/validation. `data` keys map to SFA fields."""
	doc = frappe.new_doc("Customer")
	doc.customer_name = _normalize(data.get("customer_name"))
	doc.customer_type = "Company"
	doc.customer_group = _resolve_group(data.get("customer_group"))
	doc.territory = _normalize(data.get("territory"))

	if data.get("mobile_no"):
		doc.custom_mobile_no = _normalize(data.get("mobile_no"))
	if data.get("outlet_tier"):
		doc.custom_outlet_tier = _normalize(data.get("outlet_tier"))
	if data.get("location_area"):
		doc.custom_location_area = _normalize(data.get("location_area"))
	if data.get("location_city"):
		doc.custom_location_city = _normalize(data.get("location_city"))
	if data.get("latitude"):
		doc.custom_latitude = data.get("latitude")
	if data.get("longitude"):
		doc.custom_longitude = data.get("longitude")
	if data.get("accuracy"):
		doc.custom_sfa_gps_accuracy = data.get("accuracy")
	if data.get("captured_at"):
		doc.custom_sfa_captured_at = data.get("captured_at")

	doc.custom_sfa_status = "Active"
	if rep:
		doc.custom_sfa_rep = rep

	doc.insert(ignore_permissions=True)
	return doc.name


def _default_group():
	"""Pick a sensible default leaf (non-group) Customer Group. ERPNext only
	allows assigning customers to non-group nodes."""
	for g in ("Retailer", "Kiosk / Duka", "Convenience Store"):
		if frappe.db.get_value("Customer Group", g, "is_group") == 0:
			return g
	# Otherwise the first available leaf group.
	return frappe.db.get_value("Customer Group", {"is_group": 0}, "name")


def _resolve_group(value):
	"""Return a valid leaf Customer Group. If the supplied value is a real
	non-group node, use it; otherwise fall back to the default."""
	val = _normalize(value)
	if val and frappe.db.get_value("Customer Group", val, "is_group") == 0:
		return val
	return _default_group()


@frappe.whitelist()
def create_customer(customer_name, territory=None, mobile_no=None,
                    customer_group=None, outlet_tier=None,
                    latitude=None, longitude=None,
                    location_area=None, location_city=None, accuracy=None, captured_at=None):
	"""Create a single outlet. Used by the in-app New Customer / rep field-add
	flow. Reps get the new outlet auto-assigned to themselves and scoped to
	their territory."""
	ctx = get_user_context()

	name = _normalize(customer_name)
	if not name:
		frappe.throw(_("Outlet name is required."))

	terr = _normalize(territory)
	rep = None
	if ctx.get("is_rep"):
		# Reps create within their own territory, assigned to themselves.
		rep = ctx.get("sales_person")
		terr = terr or ctx.get("territory")
	if not terr:
		frappe.throw(_("Territory is required."))

	dup = _find_duplicate(name, terr, mobile_no)
	if dup:
		frappe.throw(_("An outlet '{0}' already exists in {1}.").format(name, terr))

	new_name = _create_one({
		"customer_name": name,
		"territory": terr,
		"mobile_no": mobile_no,
		"customer_group": customer_group,
		"outlet_tier": outlet_tier,
		"latitude": latitude,
		"longitude": longitude,
		"location_area": location_area,
		"location_city": location_city,
		"accuracy": accuracy,
		"captured_at": captured_at,
	}, rep=rep)

	return {"name": new_name, "customer_name": name}


@frappe.whitelist()
def get_import_template():
	"""Return CSV header text for the download-template button."""
	header = ",".join(IMPORT_COLUMNS)
	sample = "Mukasa General Store,Kampala,256770000000,Commercial,A,Nakawa,Kampala"
	return {"columns": IMPORT_COLUMNS, "required": REQUIRED_COLUMNS,
	        "csv": header + "\n" + sample + "\n"}


@frappe.whitelist()
def bulk_import_customers(rows):
	"""Admin-only. Take parsed rows (list of dicts), validate, skip duplicates,
	create the rest. Returns a per-row result report."""
	ctx = get_user_context()
	if not ctx.get("is_admin"):
		frappe.throw(_("Only administrators can bulk-import outlets."), frappe.PermissionError)

	if isinstance(rows, str):
		import json
		rows = json.loads(rows or "[]")

	# Cache valid territories once for validation.
	valid_territories = set(frappe.get_all("Territory", pluck="name"))

	created, skipped, errors = 0, 0, 0
	report = []
	for i, raw in enumerate(rows):
		row_no = i + 1
		name = _normalize(raw.get("customer_name"))
		terr = _normalize(raw.get("territory"))
		phone = _normalize(raw.get("mobile_no"))

		if not name or not terr:
			errors += 1
			report.append({"row": row_no, "name": name or "(blank)",
			               "status": "error", "reason": "Missing required name or territory"})
			continue
		if terr not in valid_territories:
			errors += 1
			report.append({"row": row_no, "name": name,
			               "status": "error", "reason": f"Unknown territory '{terr}'"})
			continue

		dup = _find_duplicate(name, terr, phone)
		if dup:
			skipped += 1
			report.append({"row": row_no, "name": name,
			               "status": "skipped", "reason": f"Already exists ({dup})"})
			continue

		try:
			_create_one({
				"customer_name": name, "territory": terr, "mobile_no": phone,
				"customer_group": raw.get("customer_group"),
				"outlet_tier": raw.get("outlet_tier"),
				"location_area": raw.get("location_area"),
				"location_city": raw.get("location_city"),
			})
			created += 1
			report.append({"row": row_no, "name": name, "status": "created", "reason": ""})
		except Exception as e:
			errors += 1
			report.append({"row": row_no, "name": name,
			               "status": "error", "reason": str(e)[:140]})

	frappe.db.commit()
	return {"created": created, "skipped": skipped, "errors": errors,
	        "total": len(rows), "report": report}
