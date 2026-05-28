import frappe
from frappe import _
from frappe.utils import get_system_timezone

no_cache = 1


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/sfa"
        raise frappe.Redirect

    # Users with no SFA role at all → redirect to Desk
    user_roles = set(frappe.get_roles(frappe.session.user))
    sfa_roles = {'SFA Admin', 'SFA Manager', 'SFA Rep'}
    has_sfa = bool(sfa_roles.intersection(user_roles))

    # Administrator and System Manager can access SFA if they have an SFA role
    # If they have no SFA role, send them to Desk
    if not has_sfa and frappe.session.user != 'Administrator':
        frappe.local.flags.redirect_location = "/app"
        raise frappe.Redirect

    frappe.db.commit()
    context.boot = get_boot()
    return context


@frappe.whitelist(methods=["POST"], allow_guest=True)
def get_context_for_dev():
    if not frappe.conf.developer_mode:
        frappe.throw(_("This method is only available in developer mode"))
    return get_boot()


@frappe.whitelist()
def get_csrf_token():
    token = frappe.sessions.get_csrf_token()
    frappe.db.commit()
    return token


def get_boot():
    user = frappe.session.user
    csrf_token = frappe.sessions.get_csrf_token()
    frappe.db.commit()

    # SFA role context
    try:
        from sfa_core.api.auth import get_user_context
        sfa_ctx = get_user_context()
    except Exception:
        sfa_ctx = {
            'role': None, 'is_admin': False, 'is_manager': False,
            'is_rep': False, 'sales_person': None, 'territory': None,
        }

    return frappe._dict({
        "frappe_version": frappe.__version__,
        "site_name": frappe.local.site,
        "csrf_token": csrf_token,
        "sysdefaults": frappe.defaults.get_defaults(),
        "user": {
            "name": user,
            "image": frappe.db.get_value("User", user, "user_image") or "",
            "full_name": frappe.db.get_value("User", user, "full_name") or user,
            "roles": frappe.get_roles(user),
        },
        "timezone": {
            "system": get_system_timezone(),
            "user": frappe.db.get_value("User", user, "time_zone") or get_system_timezone(),
        },
        "sfa": sfa_ctx,
    })
