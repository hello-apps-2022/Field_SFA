"""
sfa_core/api/list.py
Guarded list endpoints for all main SFA doctypes.
All endpoints enforce row-level access based on role.
"""
import frappe
from sfa_core.api.auth import get_user_context


def _apply_role_filters(filters, ctx, rep_field='custom_sfa_rep', territory_field='territory'):
    """Apply role-based row filters to any query."""
    if ctx['is_admin']:
        return filters  # admin sees everything, no filter

    # Also let Administrator user through with no filter
    if frappe.session.user == 'Administrator':
        return filters

    if ctx['is_manager'] and ctx['territory']:
        filters[territory_field] = ctx['territory']
    elif ctx['is_rep']:
        if ctx['sales_person']:
            filters[rep_field] = ctx['sales_person']
        else:
            filters['name'] = '__no_access__'
    elif not ctx['role']:
        # User has no SFA role — check if they're a system admin
        from frappe.utils.user import SystemManager
        if not frappe.db.get_value('Has Role', {'parent': frappe.session.user, 'role': 'System Manager'}):
            filters['name'] = '__no_access__'
    return filters


# ── Customers ────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_customers(search=None, territory=None, customer_group=None,
                  outlet_tier=None, rep=None, visit_status=None,
                  start=0, page_length=50):
    ctx = get_user_context()
    filters = {'disabled': 0}
    _apply_role_filters(filters, ctx, rep_field='custom_sfa_rep', territory_field='territory')

    # Additional filters from UI — only allowed if within role scope
    if territory and ctx['is_admin']:
        filters['territory'] = territory
    if customer_group:
        filters['customer_group'] = customer_group
    if outlet_tier:
        filters['custom_outlet_tier'] = outlet_tier
    if rep and (ctx['is_admin'] or ctx['is_manager']):
        filters['custom_sfa_rep'] = rep
    if visit_status == 'overdue':
        from frappe.utils import nowdate
        filters['custom_next_visit_due'] = ['<', nowdate()]
    elif visit_status == 'never':
        filters['custom_last_visit_date'] = ['is', 'not set']

    # Text search as a DB-level OR filter so it spans the whole dataset.
    or_filters = None
    if search:
        like = f"%{search}%"
        or_filters = [
            ['customer_name', 'like', like],
            ['custom_location_area', 'like', like],
            ['custom_location_city', 'like', like],
        ]

    start = int(start)
    page_length = int(page_length)

    total = frappe.db.count('Customer', filters=filters) if not or_filters else len(
        frappe.get_all('Customer', filters=filters, or_filters=or_filters, fields=['name'])
    )

    customers = frappe.get_all('Customer',
        filters=filters,
        or_filters=or_filters,
        fields=[
            'name', 'customer_name', 'customer_group', 'territory',
            'custom_sfa_rep', 'custom_sfa_status', 'custom_outlet_tier',
            'custom_last_visit_date', 'custom_next_visit_due',
            'custom_visit_frequency', 'custom_latitude', 'custom_longitude',
            'custom_location_area', 'custom_location_city',
            'custom_outstanding_payments', 'custom_active_beat_plan',
        ],
        order_by='customer_name asc',
        start=start,
        page_length=page_length,
    )

    return {'items': customers, 'total': total}


# ── Visits ───────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_visits(search=None, rep=None, status=None, date_from=None,
               date_to=None, customer=None, start=0, page_length=50):
    ctx = get_user_context()
    filters = {}

    # Role-based scoping
    if ctx['is_rep']:
        if not ctx['sales_person']:
            return {'items': [], 'total': 0}
        filters['sales_person'] = ctx['sales_person']
    elif ctx['is_manager'] and ctx['territory']:
        # Scope to visits whose customer is in the manager's territory.
        terr_customers = frappe.get_all('Customer',
            filters={'territory': ctx['territory']}, pluck='name')
        if not terr_customers:
            return {'items': [], 'total': 0}
        filters['customer'] = ['in', terr_customers]

    # Additional filters
    if rep and ctx['is_admin']:
        filters['sales_person'] = rep
    if status:
        filters['status'] = status
    if date_from and date_to:
        filters['visit_date'] = ['between', [date_from, date_to]]
    elif date_from:
        filters['visit_date'] = ['>=', date_from]
    elif date_to:
        filters['visit_date'] = ['<=', date_to]
    if customer:
        filters['customer'] = customer

    or_filters = None
    if search:
        like = f"%{search}%"
        or_filters = [['customer', 'like', like], ['sales_person', 'like', like]]

    start = int(start)
    page_length = int(page_length)

    total = frappe.db.count('SFA Visit', filters=filters) if not or_filters else len(
        frappe.get_all('SFA Visit', filters=filters, or_filters=or_filters, fields=['name'])
    )

    visits = frappe.get_all('SFA Visit',
        filters=filters,
        or_filters=or_filters,
        fields=['name', 'customer', 'sales_person', 'visit_date',
                'status', 'visit_purpose', 'duration_minutes', 'beat_plan',
                'check_in_time'],
        order_by='visit_date desc',
        start=start,
        page_length=page_length,
    )

    return {'items': visits, 'total': total}


# ── Orders ───────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_orders(search=None, rep=None, status=None, date_from=None,
               date_to=None, customer=None, start=0, page_length=50):
    ctx = get_user_context()

    conditions = ["o.docstatus = 1"]
    values = []

    if ctx['is_rep']:
        if not ctx['sales_person']:
            return {'items': [], 'total': 0}
        conditions.append("c.custom_sfa_rep = %s")
        values.append(ctx['sales_person'])
    elif ctx['is_manager'] and ctx['territory']:
        conditions.append("c.territory = %s")
        values.append(ctx['territory'])

    # UI filters
    if rep and (ctx['is_admin'] or ctx['is_manager']):
        conditions.append("c.custom_sfa_rep = %s"); values.append(rep)
    if status:
        conditions.append("o.status = %s"); values.append(status)
    if date_from and date_to:
        conditions.append("DATE(o.transaction_date) BETWEEN %s AND %s")
        values += [date_from, date_to]
    if customer:
        conditions.append("o.customer = %s"); values.append(customer)
    if search:
        conditions.append("o.customer LIKE %s"); values.append(f"%{search}%")

    where = " AND ".join(conditions)

    total = frappe.db.sql(f"""
        SELECT COUNT(*) FROM `tabSales Order` o
        INNER JOIN `tabCustomer` c ON c.name = o.customer
        WHERE {where}
    """, values)[0][0]

    # Aggregate totals across ALL matching orders (not just this page).
    agg = frappe.db.sql(f"""
        SELECT COALESCE(SUM(o.grand_total), 0), COALESCE(SUM(o.total_qty), 0)
        FROM `tabSales Order` o
        INNER JOIN `tabCustomer` c ON c.name = o.customer
        WHERE {where}
    """, values)[0]

    orders = frappe.db.sql(f"""
        SELECT o.name, o.customer, o.transaction_date, o.grand_total,
               o.status, o.total_qty, c.custom_sfa_rep as sales_person,
               c.territory
        FROM `tabSales Order` o
        INNER JOIN `tabCustomer` c ON c.name = o.customer
        WHERE {where}
        ORDER BY o.transaction_date DESC
        LIMIT %s OFFSET %s
    """, values + [int(page_length), int(start)], as_dict=True)

    return {'items': orders, 'total': total,
            'sum_revenue': float(agg[0]), 'sum_qty': float(agg[1])}


# ── Payments ─────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_payments(search=None, rep=None, status=None, date_from=None,
                 date_to=None, customer=None, payment_mode=None,
                 start=0, page_length=50):
    ctx = get_user_context()
    filters = {}

    if ctx['is_rep']:
        if not ctx['sales_person']:
            return {'items': [], 'total': 0}
        filters['sales_person'] = ctx['sales_person']
    elif ctx['is_manager'] and ctx['territory']:
        # Payments have no territory field — scope via customer in territory.
        terr_customers = frappe.get_all('Customer',
            filters={'territory': ctx['territory']}, pluck='name')
        if not terr_customers:
            return {'items': [], 'total': 0}
        filters['customer'] = ['in', terr_customers]

    if rep and ctx['is_admin']:
        filters['sales_person'] = rep
    if status:
        filters['status'] = status
    if date_from and date_to:
        filters['payment_date'] = ['between', [date_from, date_to]]
    if customer:
        filters['customer'] = customer
    if payment_mode:
        filters['custom_payment_mode'] = payment_mode

    or_filters = None
    if search:
        or_filters = [['customer', 'like', f"%{search}%"]]

    start = int(start)
    page_length = int(page_length)

    total = frappe.db.count('SFA Payment', filters=filters) if not or_filters else len(
        frappe.get_all('SFA Payment', filters=filters, or_filters=or_filters, fields=['name'])
    )

    payments = frappe.get_all('SFA Payment',
        filters=filters,
        or_filters=or_filters,
        fields=['name', 'customer', 'payment_date', 'amount', 'payment_type',
                'status', 'sales_person', 'reference_no', 'custom_payment_mode'],
        order_by='payment_date desc',
        start=start,
        page_length=page_length,
    )

    # Aggregate across ALL matching payments (not just this page). Cartons are
    # explicitly tagged; everything else (Cash, or untagged) counts as cash.
    # Plain fields totalled in Python: function fields (COALESCE/SUM) in get_all
    # are blocked by frappe for non-System-Manager users (the 417).
    rows = frappe.get_all('SFA Payment', filters=filters, or_filters=or_filters,
                          fields=['amount', 'custom_payment_mode'])
    sum_amount = sum(float(r.amount or 0) for r in rows)
    carton_rows = [r for r in rows if r.custom_payment_mode == 'Cartons']
    sum_carton = sum(float(r.amount or 0) for r in carton_rows)
    carton_count = len(carton_rows)
    sum_cash = sum_amount - sum_carton

    return {'items': payments, 'total': total, 'sum_amount': sum_amount,
            'sum_cash': sum_cash, 'carton_count': carton_count}
