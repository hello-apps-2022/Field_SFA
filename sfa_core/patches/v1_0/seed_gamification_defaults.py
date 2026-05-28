"""
Patch v1.0: Seed gamification defaults (SFA Points Config + default Badges).

Idempotent — reuses the install seed function, which skips any rows that
already exist. Safe to run on installs that already have some config/badges.
"""
import frappe
from sfa_core.field_sfa.install.after_install import seed_gamification_defaults


def execute():
    seed_gamification_defaults()
    frappe.db.commit()
