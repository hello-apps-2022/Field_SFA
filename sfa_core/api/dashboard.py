import frappe
from frappe.utils import nowdate, add_days, getdate
from sfa_core.api.auth import get_scope_context as get_user_context, get_scoped_sales_persons, get_customer_scope_sp


@frappe.whitelist()
def get_dashboard_data(period='week'):
    ctx = get_user_context()
    today = getdate(nowdate())

    if period == 'today':
        date_from = date_to = today
    elif period == 'week':
        date_from = getdate(add_days(today, -6))
        date_to = today
    elif period == 'month':
        from frappe.utils import get_first_day
        date_from = get_first_day(today)
        date_to = today
    else:
        date_from = date_to = today

    df, dt = str(date_from), str(date_to)

    # Build territory/rep scope fragments based on role
    if ctx['is_rep']:
        _sps = get_scoped_sales_persons()
        _csps = get_customer_scope_sp()
        visit_filter = (f"AND v.sales_person IN ({', '.join(frappe.db.escape(s) for s in _sps)})" if _sps else "AND 1=0")
        cust_filter  = (f"AND c.custom_sfa_rep IN ({', '.join(frappe.db.escape(s) for s in _csps)})" if _csps else "AND 1=0")
    elif ctx['is_manager'] and ctx['territory']:
        visit_filter = f"AND c2.territory = {frappe.db.escape(ctx['territory'])}"
        cust_filter  = f"AND c.territory = {frappe.db.escape(ctx['territory'])}"
    else:
        visit_filter = ''
        cust_filter  = ''

    # Visits: total (non-cancelled), completed, in-progress, distinct reps
    v = frappe.db.sql(f"""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN v.status = 'Completed' THEN 1 ELSE 0 END) AS completed,
            SUM(CASE WHEN v.status = 'In Progress' THEN 1 ELSE 0 END) AS active,
            COUNT(DISTINCT v.sales_person) AS reps
        FROM `tabSFA Visit` v
        LEFT JOIN `tabCustomer` c2 ON c2.name = v.customer
        WHERE v.visit_date BETWEEN %s AND %s
          AND v.status != 'Cancelled'
          {visit_filter}
    """, (df, dt), as_dict=True)[0]
    total_v = int(v.total or 0)
    completed_v = int(v.completed or 0)

    # Orders (submitted) + revenue
    o = frappe.db.sql(f"""
        SELECT COUNT(*) AS cnt, IFNULL(SUM(o.grand_total), 0) AS total
        FROM `tabSales Order` o
        INNER JOIN `tabCustomer` c ON c.name = o.customer
        WHERE DATE(o.transaction_date) BETWEEN %s AND %s
          AND o.docstatus = 1
          {cust_filter}
    """, (df, dt), as_dict=True)[0]

    # Payments collected (not cancelled)
    payments = frappe.db.sql(f"""
        SELECT IFNULL(SUM(p.amount), 0) AS total
        FROM `tabSFA Payment` p
        INNER JOIN `tabCustomer` c ON c.name = p.customer
        WHERE p.payment_date BETWEEN %s AND %s
          AND IFNULL(p.status, '') != 'Cancelled'
          {cust_filter}
    """, (df, dt), as_dict=True)[0].total or 0

    # New customers created in the period
    new_customers = frappe.db.sql(f"""
        SELECT COUNT(*) AS cnt
        FROM `tabCustomer` c
        WHERE DATE(c.creation) BETWEEN %s AND %s
          AND c.disabled = 0
          {cust_filter}
    """, (df, dt), as_dict=True)[0].cnt or 0

    # Forms submitted in the period
    forms = frappe.db.sql(f"""
        SELECT COUNT(*) AS cnt
        FROM `tabSFA Form Response` r
        LEFT JOIN `tabCustomer` c ON c.name = r.customer
        WHERE DATE(r.response_date) BETWEEN %s AND %s
          {cust_filter}
    """, (df, dt), as_dict=True)[0].cnt or 0

    compliance = round((completed_v / total_v * 100) if total_v else 0)

    return {
        'active_visits': int(v.active or 0),
        'completed_visits': completed_v,
        'total_visits': total_v,
        'compliance_rate': compliance,
        'orders_count': int(o.cnt or 0),
        'revenue': float(o.total or 0),
        'payments_collected': float(payments or 0),
        'active_reps': int(v.reps or 0),
        'new_customers': int(new_customers),
        'forms_submitted': int(forms),
        'period': period,
        'date_from': df,
        'date_to': dt,
    }


@frappe.whitelist()
def get_leaderboard(period='week'):
    ctx = get_user_context()
    today = getdate(nowdate())

    if period == 'today':
        date_from = date_to = today
    elif period == 'week':
        date_from = getdate(add_days(today, -6))
        date_to = today
    else:
        from frappe.utils import get_first_day
        date_from = get_first_day(today)
        date_to = today

    df, dt = str(date_from), str(date_to)

    # Managers see their territory; reps see only their own
    if ctx['is_rep']:
        territory_join = ''
        having = f"HAVING v.sales_person = {frappe.db.escape(ctx['sales_person'])}"
    elif ctx['is_manager'] and ctx['territory']:
        territory_join = f"INNER JOIN `tabCustomer` tc ON tc.name = v.customer AND tc.territory = {frappe.db.escape(ctx['territory'])}"
        having = ''
    else:
        territory_join = ''
        having = ''

    return frappe.db.sql(f"""
        SELECT
            v.sales_person,
            COUNT(v.name) as visits,
            SUM(CASE WHEN v.status='Completed' THEN 1 ELSE 0 END) as completed,
            COUNT(DISTINCT v.customer) as customers,
            IFNULL(SUM(o.grand_total), 0) as revenue
        FROM `tabSFA Visit` v
        {territory_join}
        LEFT JOIN `tabSales Order` o
            ON o.customer = v.customer
            AND DATE(o.transaction_date) BETWEEN %s AND %s
            AND o.docstatus = 1
        WHERE v.visit_date BETWEEN %s AND %s
          AND v.status != 'Cancelled'
        GROUP BY v.sales_person
        {having}
        ORDER BY completed DESC
        LIMIT 20
    """, (df, dt, df, dt), as_dict=True)


@frappe.whitelist()
def get_recent_visits(limit=10):
    ctx = get_user_context()
    filters = {'status': ['!=', 'Cancelled']}
    if ctx['is_rep']:
        _sps = get_scoped_sales_persons()
        filters['sales_person'] = ['in', _sps] if _sps else ['in', ['__none__']]
    return frappe.get_all('SFA Visit',
        filters=filters,
        fields=['name', 'customer', 'sales_person',
                'visit_date', 'status', 'visit_purpose'],
        order_by='visit_date desc',
        limit=int(limit),
    )


@frappe.whitelist()
def get_overdue_customers(limit=10):
    ctx = get_user_context()
    # If rep has no sales person linked, return nothing
    if ctx['is_rep'] and not ctx['sales_person']:
        return []
    filters = {
        'disabled': 0,
        'custom_next_visit_due': ['<', str(getdate(nowdate()))],
    }
    if ctx['is_rep']:
        _csps = get_customer_scope_sp()
        filters['custom_sfa_rep'] = ['in', _csps] if _csps else ['in', ['__none__']]
    elif ctx['is_manager'] and ctx['territory']:
        filters['territory'] = ctx['territory']

    return frappe.get_all('Customer',
        filters=filters,
        fields=['name', 'customer_name', 'custom_sfa_rep', 'territory',
                'custom_last_visit_date', 'custom_next_visit_due'],
        order_by='custom_next_visit_due asc',
        limit=int(limit),
    )


@frappe.whitelist()
def get_visit_trend(days=7):
    ctx = get_user_context()
    today = getdate(nowdate())
    date_from = str(getdate(add_days(today, -int(days) + 1)))

    if ctx['is_rep']:
        _sps = get_scoped_sales_persons()
        extra = (f"AND v.sales_person IN ({', '.join(frappe.db.escape(s) for s in _sps)})" if _sps else "AND 1=0")
    elif ctx['is_manager'] and ctx['territory']:
        extra = f"AND c.territory = {frappe.db.escape(ctx['territory'])}"
    else:
        extra = ''

    return frappe.db.sql(f"""
        SELECT DATE(v.visit_date) as date,
               COUNT(*) as total,
               SUM(CASE WHEN v.status='Completed' THEN 1 ELSE 0 END) as completed
        FROM `tabSFA Visit` v
        LEFT JOIN `tabCustomer` c ON c.name = v.customer
        WHERE v.visit_date >= %s
          AND v.status != 'Cancelled'
          {extra}
        GROUP BY DATE(v.visit_date)
        ORDER BY date asc
    """, (date_from,), as_dict=True)


@frappe.whitelist()
def get_live_reps():
    ctx = get_user_context()
    if ctx['is_rep']:
        return []
    filters = {'custom_sfa_active': 1, 'is_group': 0}
    if ctx['is_manager'] and ctx['territory']:
        filters['custom_territory'] = ctx['territory']
    return frappe.get_all('Sales Person',
        filters=filters,
        fields=['name', 'sales_person_name', 'custom_territory',
                'custom_last_seen', 'custom_last_latitude', 'custom_last_longitude'],
        limit=100,
    )
