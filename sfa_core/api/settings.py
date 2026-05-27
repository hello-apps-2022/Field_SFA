import frappe
from frappe.utils.password import update_password
from sfa_core.api.auth import require_role


@frappe.whitelist()
def get_team_hierarchy():
    """Returns tree structure of all SFA users for hierarchy view."""
    require_role('SFA Admin')
    users = _get_all_users()
    by_sp = {u['sales_person']: u for u in users}

    # Initialize children lists
    for u in users:
        u['children'] = []

    roots = []
    for u in users:
        manager = u.get('reports_to')
        if manager and manager in by_sp:
            by_sp[manager]['children'].append(u)
        else:
            roots.append(u)

    # If everything is flat (all roots), group by role for visual hierarchy
    if len(roots) == len(users) and len(users) > 1:
        # Sort: admins first, then managers, then reps
        role_order = {'SFA Admin': 0, 'SFA Manager': 1, 'SFA Rep': 2, None: 3}
        roots.sort(key=lambda u: role_order.get(u.get('role'), 3))

    return roots


def _get_all_users():
    sales_persons = frappe.get_all('Sales Person',
        filters={'is_group': 0},
        fields=['name', 'sales_person_name', 'custom_user_id', 'parent_sales_person',
                'custom_territory', 'custom_mobile_no', 'custom_sfa_active', 'custom_last_seen'],
        order_by='sales_person_name asc',
    )
    result = []
    for sp in sales_persons:
        user = None
        role = None
        if sp.custom_user_id:
            user = frappe.db.get_value('User', sp.custom_user_id,
                ['name', 'full_name', 'email', 'enabled', 'user_image'], as_dict=True)
            if user:
                roles = frappe.get_roles(sp.custom_user_id)
                if 'SFA Admin' in roles: role = 'SFA Admin'
                elif 'SFA Manager' in roles: role = 'SFA Manager'
                elif 'SFA Rep' in roles: role = 'SFA Rep'
        # Get manager name for display
        reports_to_name = None
        if sp.parent_sales_person and sp.parent_sales_person != 'Sales Team':
            reports_to_name = frappe.db.get_value('Sales Person', sp.parent_sales_person, 'sales_person_name')
        result.append({
            'sales_person': sp.name,
            'sales_person_name': sp.sales_person_name,
            'user_id': sp.custom_user_id,
            'full_name': user.full_name if user else sp.sales_person_name,
            'email': user.email if user else sp.custom_user_id,
            'enabled': user.enabled if user else 0,
            'user_image': user.user_image if user else None,
            'territory': sp.custom_territory,
            'mobile_no': sp.custom_mobile_no,
            'sfa_active': sp.custom_sfa_active,
            'last_seen': sp.custom_last_seen,
            'role': role,
            'has_user': bool(user),
            'reports_to': sp.parent_sales_person if sp.parent_sales_person != 'Sales Team' else None,
            'reports_to_name': reports_to_name,
        })
    return result


@frappe.whitelist()
def get_users():
    """Get all SFA users with their Sales Person details."""
    require_role('SFA Admin')

    sales_persons = frappe.get_all('Sales Person',
        filters={'is_group': 0},
        fields=[
            'name', 'sales_person_name', 'custom_user_id',
            'custom_territory', 'custom_mobile_no', 'custom_sfa_active',
            'custom_last_seen',
        ],
        order_by='sales_person_name asc',
    )

    result = []
    for sp in sales_persons:
        user = None
        role = None
        if sp.custom_user_id:
            user = frappe.db.get_value('User', sp.custom_user_id,
                ['name', 'full_name', 'email', 'enabled', 'user_image'],
                as_dict=True)
            if user:
                roles = frappe.get_roles(sp.custom_user_id)
                if 'SFA Admin' in roles:
                    role = 'SFA Admin'
                elif 'SFA Manager' in roles:
                    role = 'SFA Manager'
                elif 'SFA Rep' in roles:
                    role = 'SFA Rep'

        result.append({
            'sales_person': sp.name,
            'sales_person_name': sp.sales_person_name,
            'user_id': sp.custom_user_id,
            'full_name': user.full_name if user else sp.sales_person_name,
            'email': user.email if user else sp.custom_user_id,
            'enabled': user.enabled if user else 0,
            'user_image': user.user_image if user else None,
            'territory': sp.custom_territory,
            'mobile_no': sp.custom_mobile_no,
            'sfa_active': sp.custom_sfa_active,
            'last_seen': sp.custom_last_seen,
            'role': role,
            'has_user': bool(user),
        })

    return result


@frappe.whitelist()
def create_user(first_name, last_name, email, password, role,
                territory=None, mobile_no=None, reports_to=None):
    """Create a Frappe User + Sales Person and link them."""
    require_role('SFA Admin')

    # Validate role
    if role not in ('SFA Admin', 'SFA Manager', 'SFA Rep'):
        frappe.throw('Invalid role')

    # Check if user already exists
    if frappe.db.exists('User', email):
        frappe.throw(f'A user with email {email} already exists')

    # Create Frappe User
    user = frappe.get_doc({
        'doctype': 'User',
        'email': email,
        'first_name': first_name,
        'last_name': last_name or '',
        'full_name': f'{first_name} {last_name}'.strip(),
        'send_welcome_email': 0,
        'enabled': 1,
        'roles': [{'role': role}],
    })
    user.insert(ignore_permissions=True)
    update_password(email, password)

    # Create Sales Person
    sales_person_name = f'{first_name} {last_name}'.strip()
    # Determine parent and territory
    parent_sp = 'Sales Team'
    if reports_to:
        parent_sp = reports_to
        # Inherit territory from manager if not specified
        if not territory:
            territory = frappe.db.get_value('Sales Person', reports_to, 'custom_territory') or ''

    sp = frappe.get_doc({
        'doctype': 'Sales Person',
        'sales_person_name': sales_person_name,
        'parent_sales_person': parent_sp,
        'is_group': 0,
        'custom_user_id': email,
        'custom_territory': territory or '',
        'custom_mobile_no': mobile_no or '',
        'custom_sfa_active': 1,
    })
    sp.insert(ignore_permissions=True)

    frappe.db.commit()
    return {
        'success': True,
        'user': email,
        'sales_person': sp.name,
    }


@frappe.whitelist()
def update_user(sales_person, role=None, territory=None, mobile_no=None,
                sfa_active=None, first_name=None, last_name=None, reports_to=None):
    """Update a user's role, territory, or status."""
    require_role('SFA Admin')

    # Update Sales Person
    sp_update = {}
    if territory is not None:
        sp_update['custom_territory'] = territory
    if mobile_no is not None:
        sp_update['custom_mobile_no'] = mobile_no
    if sfa_active is not None:
        sp_update['custom_sfa_active'] = 1 if sfa_active else 0
    if reports_to is not None:
        sp_update['parent_sales_person'] = reports_to or 'Sales Team'
    if sp_update:
        frappe.db.set_value('Sales Person', sales_person, sp_update)

    # Update User
    user_id = frappe.db.get_value('Sales Person', sales_person, 'custom_user_id')
    if user_id:
        if role:
            # Remove existing SFA roles
            frappe.db.delete('Has Role', {
                'parent': user_id,
                'role': ['in', ['SFA Admin', 'SFA Manager', 'SFA Rep']],
            })
            # Add new role
            frappe.get_doc({
                'doctype': 'Has Role',
                'parent': user_id,
                'parenttype': 'User',
                'parentfield': 'roles',
                'role': role,
            }).insert(ignore_permissions=True)
            frappe.clear_cache(user=user_id)

        if first_name:
            frappe.db.set_value('User', user_id, {
                'first_name': first_name,
                'last_name': last_name or '',
                'full_name': f'{first_name} {last_name or ""}'.strip(),
            })

    frappe.db.commit()
    return {'success': True}


@frappe.whitelist()
def reset_password(sales_person, new_password):
    """Reset a user's password."""
    require_role('SFA Admin')
    user_id = frappe.db.get_value('Sales Person', sales_person, 'custom_user_id')
    if not user_id:
        frappe.throw('No user linked to this sales person')
    update_password(user_id, new_password)
    frappe.db.commit()
    return {'success': True}


@frappe.whitelist()
def toggle_user_active(sales_person, enabled):
    """Enable or disable a user account."""
    require_role('SFA Admin')
    user_id = frappe.db.get_value('Sales Person', sales_person, 'custom_user_id')
    if user_id:
        frappe.db.set_value('User', user_id, 'enabled', 1 if enabled else 0)
    frappe.db.set_value('Sales Person', sales_person, 'custom_sfa_active', 1 if enabled else 0)
    frappe.db.commit()
    return {'success': True}


@frappe.whitelist()
def get_territories():
    return frappe.get_all('Territory',
        filters={'is_group': 0},
        fields=['name'],
        order_by='name asc',
        limit=100,
    )
