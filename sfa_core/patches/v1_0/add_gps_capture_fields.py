import frappe
from sfa_core.field_sfa.install.after_install import setup_gps_capture_fields


def execute():
    setup_gps_capture_fields()
