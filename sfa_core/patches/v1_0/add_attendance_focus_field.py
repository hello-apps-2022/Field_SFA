import frappe
from sfa_core.field_sfa.install.after_install import setup_attendance_fields


def execute():
    setup_attendance_fields()
