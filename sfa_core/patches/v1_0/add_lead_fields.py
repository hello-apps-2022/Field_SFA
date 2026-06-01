"""Add the SFA custom fields to the ERPNext Lead doctype on already-installed
sites: the assigned rep, the SFA lifecycle status, the GPS capture quad, and the
offline-sync client uuid. Idempotent."""

import frappe
from sfa_core.field_sfa.install.after_install import setup_lead_fields


def execute():
    setup_lead_fields()
    frappe.db.commit()
