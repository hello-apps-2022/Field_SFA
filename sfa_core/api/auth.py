"""
sfa_core/api/auth.py
Central auth utilities for SFA. Every API endpoint uses these.
"""
import frappe


SFA_ROLES = ['SFA Admin', 'SFA Manager', 'SFA Supervisor', 'SFA Rep', 'SFA Field Helper']
MANAGER_ROLES = ['SFA Admin', 'SFA Manager', 'System Manager']
ADMIN_ROLES = ['SFA Admin', 'System Manager']


def get_user_role():
    """Returns the highest SFA role for the current user."""
    roles = frappe.get_roles(frappe.session.user)
    if 'System Manager' in roles or 'SFA Admin' in roles:
        return 'SFA Admin'
    if 'SFA Manager' in roles:
        return 'SFA Manager'
    if 'SFA Supervisor' in roles:
        return 'SFA Supervisor'
    if 'SFA Rep' in roles:
        return 'SFA Rep'
    if 'SFA Field Helper' in roles:
        return 'SFA Field Helper'
    return None


def get_current_sales_person():
    """Returns the Sales Person record linked to the current user."""
    user = frappe.session.user
    sp = frappe.db.get_value('Sales Person',
        {'custom_user_id': user},
        ['name', 'sales_person_name', 'custom_territory',
         'custom_mobile_no', 'custom_sfa_active', 'custom_employee',
         'parent_sales_person'],
        as_dict=True
    )
    return sp


@frappe.whitelist()
def get_reporting_chain(sales_person=None):
    """Sales Persons up the reporting line (manager and above) from the
    given sales person, or the current user's. Only ancestors linked to a
    real user are returned; purely structural nodes (e.g. 'Sales Team')
    are skipped. Non-oversight callers may only resolve their own chain."""
    role = get_user_role()
    if sales_person and role not in ('SFA Admin', 'SFA Manager', 'SFA Supervisor'):
        sales_person = None
    if not sales_person:
        sp = get_current_sales_person()
        sales_person = sp.get('name') if sp else None
    if not sales_person:
        return []
    chain, seen = [], set()
    parent = frappe.db.get_value('Sales Person', sales_person, 'parent_sales_person')
    while parent and parent not in seen:
        seen.add(parent)
        row = frappe.db.get_value('Sales Person', parent, ['name', 'custom_user_id'], as_dict=True)
        if not row:
            break
        if row.custom_user_id:
            chain.append(row.name)
        parent = frappe.db.get_value('Sales Person', parent, 'parent_sales_person')
    return chain


def _allow_disc_free():
    try:
        return bool(frappe.db.get_single_value("SFA Brand Settings", "allow_discretionary_free"))
    except Exception:
        return False


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
            'is_supervisor': False,
            'is_rep': False,
            'is_helper': False,
            'sales_person': None,
            'sales_person_name': None,
            'employee': None,
            'territory': None,
            'reports_to': None,
            'companies': [],
            'allow_discretionary_free': _allow_disc_free(),
            'user': user,
        }

    role = get_user_role()
    sp = get_current_sales_person()
    territory = sp.custom_territory if sp else None
    reports_to = sp.parent_sales_person if sp else None

    # Also treat System Manager as admin
    if not role and 'System Manager' in frappe.get_roles(user):
        role = 'SFA Admin'

    return {
        'role': role,
        'is_admin': role == 'SFA Admin',
        'is_manager': role in ('SFA Admin', 'SFA Manager'),
        'is_supervisor': role == 'SFA Supervisor',
        'is_rep': role == 'SFA Rep',
        'is_helper': role == 'SFA Field Helper',
        'sales_person': sp.name if sp else None,
        'sales_person_name': sp.sales_person_name if sp else None,
        'employee': (sp.custom_employee if sp else None),
        'territory': territory,
        'reports_to': reports_to,
        'companies': frappe.get_all('SFA Sales Person Company', filters={'parent': sp.name}, pluck='company') if sp else [],
        'allow_discretionary_free': _allow_disc_free(),
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


def get_scope_context():
    """
    Role flags remapped to DATA-SCOPE semantics for the five-tier model:
      Admin / Manager -> full access (all territories)
      Supervisor      -> own territory only
      Rep / Helper    -> own sales person (plus downline, see get_scoped_sales_persons)
    Data endpoints should adopt this in place of get_user_context() so the
    territory scope follows the Supervisor tier, not the Manager tier.
    """
    ctx = get_user_context()
    scoped = dict(ctx)
    scoped['is_admin'] = bool(ctx['is_admin'] or ctx['is_manager'])
    scoped['is_manager'] = bool(ctx['is_supervisor'])
    scoped['is_rep'] = bool(ctx['is_rep'] or ctx['is_helper'])
    return scoped


def get_scoped_sales_persons():
    """Sales Person names this user owns by attribution:
       Rep -> self + helpers reporting to them; Helper -> self; others -> []."""
    ctx = get_user_context()
    sp = ctx.get('sales_person')
    if not sp:
        return []
    if ctx['is_rep']:
        helpers = frappe.get_all('Sales Person',
            filters={'parent_sales_person': sp}, pluck='name')
        return [sp] + helpers
    if ctx['is_helper']:
        return [sp]
    return []


def get_customer_scope_sp():
    """Sales Person values to match against Customer.custom_sfa_rep:
       Helper -> parent rep (sees the rep's customers); Rep -> self + helpers."""
    ctx = get_user_context()
    if ctx['is_helper']:
        return [ctx['reports_to']] if ctx.get('reports_to') else []
    if ctx['is_rep']:
        return get_scoped_sales_persons()
    return []


@frappe.whitelist()
def get_session_context():
    """Called on SFA boot — returns user role and identity to frontend."""
    ctx = get_user_context()
    return ctx


def on_session_creation(login_manager=None):
    """
    Frappe on_session_creation hook — fires when a new session is created.

    Sets a per-user redirect cache so SFA users land on /sfa after login.
    This is a secondary mechanism; the primary /sfa redirect is the
    login.html patch on login_handlers[200].

    Must tolerate being called for Guest/Administrator and with or without a
    login_manager (Frappe calls it as on_session_creation(login_manager=self)),
    and must never raise — a failure here would break login/logout entirely.
    """
    try:
        user = frappe.session.user
        if not user or user in ('Administrator', 'Guest'):
            return

        roles = set(frappe.get_roles(user))
        sfa_roles = set(SFA_ROLES)
        if sfa_roles.intersection(roles):
            frappe.cache.hset("redirect_after_login", user, "/sfa")
    except Exception:
        # Never let session creation fail because of this hook.
        pass


def on_login(login_manager):
    """
    Frappe on_login hook — fires after successful authentication.
    Redirects SFA users to /sfa instead of /app.
    """
    user = login_manager.user
    if not user or user in ('Administrator', 'Guest'):
        return

    roles = frappe.get_roles(user)
    sfa_roles = set(SFA_ROLES)

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
        sfa_roles = set(SFA_ROLES)
        desk_roles = {'System Manager', 'Administrator'}

        if sfa_roles.intersection(roles) and not desk_roles.intersection(roles):
            frappe.local.flags.redirect_location = '/sfa'
            raise frappe.Redirect
    except frappe.Redirect:
        raise
    except Exception:
        pass
