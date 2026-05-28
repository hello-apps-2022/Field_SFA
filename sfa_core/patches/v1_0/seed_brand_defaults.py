"""
Patch v1.0: Seed FieldPro brand defaults into SFA Brand Settings.

after_install only fires on fresh installs, so existing sites (e.g. hema.local)
need this to populate the product brand defaults and mirror them into Frappe's
login/navbar/favicon slots. Idempotent — only fills blank fields.
"""
import frappe


def execute():
	if not frappe.db.exists("DocType", "SFA Brand Settings"):
		return

	from sfa_core.field_sfa.install.after_install import seed_brand_defaults

	seed_brand_defaults()
	frappe.db.commit()
