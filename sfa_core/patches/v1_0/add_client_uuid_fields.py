import frappe
from sfa_core.field_sfa.install.after_install import setup_sync_fields


def execute():
    setup_sync_fields()
