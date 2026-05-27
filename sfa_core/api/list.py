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
        return filters  # no restriction
    if ctx['is_manager'] and ctx['territory']:
        filters[territory_field] = ctx['territory']
    elif ctx['is_rep']:
        if ctx['sales_person']:
            filters[rep_field] = ctx['sales_person']
        else:
            filters['name'] = '__no_access__'
    return filters


# ── Customers ────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_customers(search=None, territory=None, customer_group=None,
                  outlet_tier=None, rep=None, visit_status=None, limit=200):
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

    customers = frappe.get_all('Customer',
        filters=filters,
        fields=[
            'name', 'customer_name', 'customer_group', 'territory',
            'custom_sfa_rep', 'custom_sfa_status', 'custom_outlet_tier',
            'custom_last_visit_date', 'custom_next_visit_due',
            'custom_visit_frequency', 'custom_latitude', 'custom_longitude',
            'custom_location_area', 'custom_location_city',
            'custom_outstanding_payments', 'custom_active_beat_plan',
        ],
        order_by='customer_name asc',
        limit=int(limit),
    )

    # Apply text search client-side friendly — filter after fetch
    if search:
        q = search.lower()
        customers = [c for c in customers if
            q in (c.customer_name or '').lower() or
            q in (c.custom_location_area or '').lower() or
            q in (c.custom_location_city or '').lower()]

    return customers


# ── Visits ───────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_visits(search=None, rep=None, status=None, date_from=None,
               date_to=None, customer=None, limit=200):
    ctx = get_user_context()
    filters = {}

    # Role-based: reps see own visits, managers see territory visits
    if ctx['is_rep']:
        if ctx['sales_person']:
            filters['sales_person'] = ctx['sales_person']
        else:
            return []
    elif ctx['is_manager'] and ctx['territory']:
        # Join through customer for territory — use SQL
        return _get_visits_for_territory(ctx['territory'], rep, status,
                                         date_from, date_to, customer, search, limit)

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

    visits = frappe.get_all('SFA Visit',
        filters=filters,
        fields=['name', 'customer', 'sales_person', 'visit_date',
                'status', 'visit_purpose', 'duration_minutes', 'beat_plan'],
        order_by='visit_date desc',
        limit=int(limit),
    )

    if search:
        q = search.lower()
        visits = [v for v in visits if q in (v.customer or '').lower() or
                  q in (v.sales_person or '').lower()]

    return visits


def _get_visits_for_territory(territory, rep, status, date_from, date_to,
                               customer, search, limit):
    conditions = ["c.territory = %s"]
    values = [territory]
    if rep:
        conditions.append("v.sales_person = %s"); values.append(rep)
    if status:
        conditions.append("v.status = %s"); values.append(status)
    if date_from and date_to:
        conditions.append("v.visit_date BETWEEN %s AND %s")
        values += [date_from, date_to]
    if customer:
        conditions.append("v.customer = %s"); values.append(customer)

    where = " AND ".join(conditions)
    visits = frappe.db.sql(f"""
        SELECT v.name, v.customer, v.sales_person, v.visit_date,
               v.status, v.visit_purpose, v.duration_minutes, v.beat_plan
        FROM `tabSFA Visit` v
        INNER JOIN `tabCustomer` c ON c.name = v.customer
        WHERE {where}
        ORDER BY v.visit_date DESC
        LIMIT %s
    """, values + [int(limit)], as_dict=True)

    if search:
        q = search.lower()
        visits = [v for v in visits if q in (v.customer or '').lower() or
                  q in (v.sales_person or '').lower()]
    return visits


# ── Orders ───────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_orders(search=None, rep=None, status=None, date_from=None,
               date_to=None, customer=None, limit=100):
    ctx = get_user_context()

    conditions = ["o.docstatus = 1"]
    values = []

    if ctx['is_rep']:
        if not ctx['sales_person']:
            return []
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

    where = " AND ".join(conditions)
    orders = frappe.db.sql(f"""
        SELECT o.name, o.customer, o.transaction_date, o.grand_total,
               o.status, o.total_qty, c.custom_sfa_rep as sales_person,
               c.territory
        FROM `tabSales Order` o
        INNER JOIN `tabCustomer` c ON c.name = o.customer
        WHERE {where}
        ORDER BY o.transaction_date DESC
        LIMIT %s
    """, values + [int(limit)], as_dict=True)

    if search:
        q = search.lower()
        orders = [o for o in orders if q in (o.customer or '').lower()]

    return orders


# ── Payments ─────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_payments(search=None, rep=None, status=None, date_from=None,
                 date_to=None, customer=None, payment_mode=None, limit=100):
    ctx = get_user_context()
    filters = {}

    if ctx['is_rep']:
        if not ctx['sales_person']:
            return []
        filters['sales_person'] = ctx['sales_person']
    elif ctx['is_manager'] and ctx['territory']:
        # Payments don't have territory — join through customer
        return _get_payments_for_territory(ctx['territory'], rep, status,
                                           date_from, date_to, customer,
                                           payment_mode, search, limit)

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

    payments = frappe.get_all('SFA Payment',
        filters=filters,
        fields=['name', 'customer', 'payment_date', 'amount', 'payment_type',
                'status', 'sales_person', 'reference_no', 'custom_payment_mode'],
        order_by='payment_date desc',
        limit=int(limit),
    )

    if search:
        q = search.lower()
        payments = [p for p in payments if q in (p.customer or '').lower()]

    return payments


def _get_payments_for_territory(territory, rep, status, date_from, date_to,
                                customer, payment_mode, search, limit):
    conditions = ["c.territory = %s"]
    values = [territory]
    if rep:
        conditions.append("p.sales_person = %s"); values.append(rep)
    if status:
        conditions.append("p.status = %s"); values.append(status)
    if date_from and date_to:
        conditions.append("p.payment_date BETWEEN %s AND %s")
        values += [date_from, date_to]
    if customer:
        conditions.append("p.customer = %s"); values.append(customer)
    if payment_mode:
        conditions.append("p.custom_payment_mode = %s"); values.append(payment_mode)

    where = " AND ".join(conditions)
    payments = frappe.db.sql(f"""
        SELECT p.name, p.customer, p.payment_date, p.amount, p.payment_type,
               p.status, p.sales_person, p.reference_no, p.custom_payment_mode
        FROM `tabSFA Payment` p
        INNER JOIN `tabCustomer` c ON c.name = p.customer
        WHERE {where}
        ORDER BY p.payment_date DESC
        LIMIT %s
    """, values + [int(limit)], as_dict=True)

    if search:
        q = search.lower()
        payments = [p for p in payments if q in (p.customer or '').lower()]
    return payments
