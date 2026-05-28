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

    # Brand (white-label) — single source of truth for logo, name, tagline, theme
    try:
        bs = frappe.get_cached_doc("SFA Brand Settings")
        bootinfo.sfa_brand = {
            "product_name": bs.product_name or "FieldPro",
            "tenant_name": bs.tenant_name or "",
            "login_tagline": bs.login_tagline or "",
            "logo_login": bs.logo_login or "/assets/sfa_core/images/fieldpro-logo.svg",
            "logo_navbar": bs.logo_navbar or "/assets/sfa_core/images/fieldpro-mark.svg",
            "favicon": bs.favicon or "/assets/sfa_core/images/fieldpro-favicon.svg",
            "primary_color": bs.primary_color or "#1A1A2E",
            "accent_color": bs.accent_color or "#378ADD",
            "support_email": bs.support_email or "",
        }
    except Exception:
        bootinfo.sfa_brand = {
            "product_name": "FieldPro",
            "tenant_name": "",
            "login_tagline": "Know your field.",
            "logo_login": "/assets/sfa_core/images/fieldpro-logo.svg",
            "logo_navbar": "/assets/sfa_core/images/fieldpro-mark.svg",
            "favicon": "/assets/sfa_core/images/fieldpro-favicon.svg",
            "primary_color": "#1A1A2E",
            "accent_color": "#378ADD",
            "support_email": "",
        }


def update_website_context(context):
    """Override the Desk/login splash logo (defaults to ERPNext's 'E').

    Runs after ERPNext sets its own splash, so this takes precedence.
    Uses the FieldPro mark, or the tenant's navbar logo if set.
    """
    splash = "/assets/sfa_core/images/fieldpro-mark.svg"
    try:
        bs = frappe.get_cached_doc("SFA Brand Settings")
        if bs.logo_navbar:
            splash = bs.logo_navbar
    except Exception:
        pass
    context["splash_image"] = splash
