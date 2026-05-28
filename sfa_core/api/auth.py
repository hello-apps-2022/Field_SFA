"""
sfa_core/api/auth.py
Central auth utilities for SFA. Every API endpoint uses these.
"""
import frappe


SFA_ROLES = ['SFA Admin', 'SFA Manager', 'SFA Rep']
MANAGER_ROLES = ['SFA Admin', 'SFA Manager', 'System Manager']
ADMIN_ROLES = ['SFA Admin', 'System Manager']


def get_user_role():
    """Returns the highest SFA role for the current user."""
    roles = frappe.get_roles(frappe.session.user)
    if 'System Manager' in roles or 'SFA Admin' in roles:
        return 'SFA Admin'
    if 'SFA Manager' in roles:
        return 'SFA Manager'
    if 'SFA Rep' in roles:
        return 'SFA Rep'
    return None


def get_current_sales_person():
    """Returns the Sales Person record linked to the current user."""
    user = frappe.session.user
    sp = frappe.db.get_value('Sales Person',
        {'custom_user_id': user},
        ['name', 'sales_person_name', 'custom_territory',
         'custom_mobile_no', 'custom_sfa_active'],
        as_dict=True
    )
    return sp


def get_user_context():
    """
    Full context for the current user.
    Returns role, sales_person, territory.
    """
    user = frappe.session.user

    # Administrator always gets full admin access
    if user == 'Administrator':
        return {
            'role': 'SFA Admin',
            'is_admin': True,
            'is_manager': True,
            'is_rep': False,
            'sales_person': None,
            'sales_person_name': None,
            'territory': None,
            'user': user,
        }

    role = get_user_role()
    sp = get_current_sales_person()
    territory = sp.custom_territory if sp else None

    # Also treat System Manager as admin
    if not role and 'System Manager' in frappe.get_roles(user):
        role = 'SFA Admin'

    return {
        'role': role,
        'is_admin': role == 'SFA Admin',
        'is_manager': role in ('SFA Admin', 'SFA Manager'),
        'is_rep': role == 'SFA Rep',
        'sales_person': sp.name if sp else None,
        'sales_person_name': sp.sales_person_name if sp else None,
        'territory': territory,
        'user': user,
    }


def require_role(*allowed_roles):
    """
    Decorator / guard — raises PermissionError if user doesn't have required role.
    Usage: require_role('SFA Admin', 'SFA Manager')
    """
    role = get_user_role()
    if role not in allowed_roles and 'System Manager' not in frappe.get_roles(frappe.session.user):
        frappe.throw('You do not have permission to perform this action.', frappe.PermissionError)


def filter_by_user(filters=None):
    """
    Returns filters to scope a query to the current user's access level.
    - Admin: no extra filter
    - Manager: filter by territory
    - Rep: filter by sales_person (custom_sfa_rep)
    """
    ctx = get_user_context()
    filters = filters or {}

    if ctx['is_admin']:
        return filters  # no restriction

    if ctx['is_manager'] and ctx['territory']:
        filters['territory'] = ctx['territory']
        return filters

    if ctx['is_rep']:
        if ctx['sales_person']:
            filters['custom_sfa_rep'] = ctx['sales_person']
        else:
            # Rep with no Sales Person linked — show nothing
            filters['name'] = '__no_access__'
        return filters

    # No role — return impossible filter to show nothing
    filters['name'] = '__no_access__'
    return filters


@frappe.whitelist()
def get_session_context():
    """Called on SFA boot — returns user role and identity to frontend."""
    ctx = get_user_context()
    return ctx


def on_login(login_manager):
    """
    Frappe on_login hook — fires after successful authentication.
    Redirects SFA users to /sfa instead of /app.
    """
    user = login_manager.user
    if not user or user in ('Administrator', 'Guest'):
        return

    roles = frappe.get_roles(user)
    sfa_roles = {'SFA Admin', 'SFA Manager', 'SFA Rep'}

    if sfa_roles.intersection(set(roles)):
        # Set the redirect target for this session
        frappe.local.response["home_page"] = "/sfa"


def redirect_sfa_users():
    """
    before_request hook — intercepts /app requests from SFA-only users
    and redirects them to /sfa instead.
    """
    try:
        if not frappe.local.request:
            return

        path = frappe.local.request.path
        if path != '/app' and not path.startswith('/app/'):
            return

        user = frappe.session.user
        if not user or user in ('Administrator', 'Guest'):
            return

        roles = set(frappe.get_roles(user))
        sfa_roles = {'SFA Admin', 'SFA Manager', 'SFA Rep'}
        desk_roles = {'System Manager', 'Administrator'}

        if sfa_roles.intersection(roles) and not desk_roles.intersection(roles):
            frappe.local.flags.redirect_location = '/sfa'
            raise frappe.Redirect
    except frappe.Redirect:
        raise
    except Exception:
        pass
