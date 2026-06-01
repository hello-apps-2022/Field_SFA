"""Seed the configurable SFA Location Type list and reload the saved-location
doctypes so location_type (now a Link) and the new sync fields exist on
already-installed sites. Idempotent."""

import frappe
from sfa_core.field_sfa.install.after_install import setup_location_types


def execute():
    frappe.reload_doc("field_sfa", "doctype", "sfa_location_type")
    frappe.reload_doc("field_sfa", "doctype", "sfa_saved_location")
    setup_location_types()
    frappe.db.commit()
