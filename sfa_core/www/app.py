"""
sfa_core/www/app.py
Intercepts /app for SFA-only users and redirects to /sfa.
Place at: sfa_core/www/app.py
"""
import frappe

no_cache = 1

def get_context(context):
    user = frappe.session.user
    if not user or user in ('Administrator', 'Guest'):
        return

    roles = set(frappe.get_roles(user))
    sfa_only_roles = {'SFA Admin', 'SFA Manager', 'SFA Rep'}
    desk_roles = {'System Manager', 'Administrator'}

    # Only redirect if user has SFA role but NOT a desk-level role
    if sfa_only_roles.intersection(roles) and not desk_roles.intersection(roles):
        frappe.local.flags.redirect_location = "/sfa"
        raise frappe.Redirect
