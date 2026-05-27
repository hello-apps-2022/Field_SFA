import frappe
from frappe import _
from frappe.utils import get_system_timezone

no_cache = 1


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/sfa"
        raise frappe.Redirect

    frappe.db.commit()
    context.boot = get_boot()
    return context


@frappe.whitelist(methods=["POST"], allow_guest=True)
def get_context_for_dev():
    if not frappe.conf.developer_mode:
        frappe.throw(_("This method is only available in developer mode"))
    return get_boot()


def get_boot():
    user = frappe.session.user
    return frappe._dict({
        "frappe_version": frappe.__version__,
        "site_name": frappe.local.site,
        "csrf_token": frappe.sessions.get_csrf_token(),
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
    })
