"""
Patch v1.0: Seed the SFA outlet-type Customer Groups and clean up junk groups.

- Creates the 15 canonical leaf Customer Groups (idempotent).
- Removes junk/duplicate groups (Commercial, Individual, Government, Non Profit).
  Any customers on a junk group are first reassigned to 'Retailer', then the
  junk group is deleted. A junk group that is itself a parent or otherwise
  un-deletable is left in place (logged), never force-removed.
"""
import frappe
from sfa_core.field_sfa.install.after_install import seed_customer_groups

JUNK_GROUPS = ["Commercial", "Individual", "Government", "Non Profit"]
FALLBACK_GROUP = "Retailer"


def execute():
	# 1. Ensure the canonical taxonomy exists (creates Retailer among others).
	seed_customer_groups()
	frappe.db.commit()

	if not frappe.db.exists("Customer Group", FALLBACK_GROUP):
		# Safety: if Retailer somehow isn't present, don't proceed with cleanup.
		frappe.log_error("SFA Core: fallback group 'Retailer' missing; skipping junk cleanup")
		return

	# 2. Clean up each junk group.
	for g in JUNK_GROUPS:
		if not frappe.db.exists("Customer Group", g):
			continue
		try:
			# Reassign any customers on this group to the fallback.
			customers = frappe.get_all("Customer", filters={"customer_group": g}, pluck="name")
			for c in customers:
				frappe.db.set_value("Customer", c, "customer_group", FALLBACK_GROUP)
			frappe.db.commit()

			# Don't delete if it's a group node with children.
			if frappe.db.get_value("Customer Group", g, "is_group"):
				frappe.log_error(f"SFA Core: '{g}' is a group node; left in place")
				continue

			frappe.delete_doc("Customer Group", g, ignore_permissions=True, force=False)
			frappe.db.commit()
		except Exception as e:
			frappe.log_error(f"SFA Core: could not remove junk group '{g}': {e}")
			frappe.db.rollback()
