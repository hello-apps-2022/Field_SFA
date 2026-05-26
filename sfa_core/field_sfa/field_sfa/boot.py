import frappe


def boot_session(bootinfo):
    """Add SFA config to boot session"""
    bootinfo.sfa_config = {
        "auto_close_distance": 500,
        "auto_close_time": 30,
        "geofence_default_radius": 500,
        "mandatory_form_gate": True,
        "gt_pricing_configurable": True,
        "mt_credit_block_configurable": True,
    }

    # Add user roles for frontend routing
    user_roles = frappe.get_roles()
    bootinfo.sfa_roles = {
        "is_manager": "SFA Manager" in user_roles,
        "is_supervisor": "SFA Supervisor" in user_roles,
        "is_rep": "SFA Rep" in user_roles,
    }

    # Ensure field_sfa module is always in module_app
    # This fixes a Frappe v15 issue where app_modules cache
    # may be built before sfa_core is fully registered
    if "field_sfa" not in bootinfo.module_app:
        bootinfo.module_app["field_sfa"] = "sfa_core"
