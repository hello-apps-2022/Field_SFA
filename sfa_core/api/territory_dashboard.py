import frappe
from frappe.utils import nowdate, getdate, add_days, get_first_day, get_last_day
from sfa_core.api.auth import get_user_context, require_role


@frappe.whitelist()
def get_territory_dashboard(territory, period='month', date_from=None, date_to=None):
    require_role('SFA Admin', 'SFA Manager')
    ctx = get_user_context()
    if ctx['is_manager'] and not ctx['is_admin'] and ctx['territory'] and territory != ctx['territory']:
        frappe.throw('You can only view your own territory.', frappe.PermissionError)

    today = getdate(nowdate())

    # Custom date range overrides period
    if date_from and date_to:
        date_from = getdate(date_from)
        date_to = getdate(date_to)
    elif period == 'today':
        date_from = date_to = today
    elif period == 'yesterday':
        date_from = date_to = getdate(add_days(today, -1))
    elif period == 'week':
        date_from = getdate(add_days(today, -6))
        date_to = today
    elif period == 'last_week':
        date_to = getdate(add_days(today, -((today.weekday() + 1) % 7 + 1)))
        date_from = getdate(add_days(date_to, -6))
    elif period == 'month':
        date_from = get_first_day(today)
        date_to = today
    elif period == 'last_month':
        last = get_first_day(add_days(get_first_day(today), -1))
        date_from = last
        date_to = get_last_day(last)
    elif period == 'quarter':
        q_month = ((today.month - 1) // 3) * 3 + 1
        import datetime
        date_from = getdate(datetime.date(today.year, q_month, 1))
        date_to = today
    elif period == 'last_quarter':
        import datetime
        q_month = ((today.month - 1) // 3) * 3 + 1
        if q_month == 1:
            date_from = getdate(datetime.date(today.year - 1, 10, 1))
            date_to = getdate(datetime.date(today.year - 1, 12, 31))
        else:
            date_from = getdate(datetime.date(today.year, q_month - 3, 1))
            date_to = getdate(add_days(datetime.date(today.year, q_month, 1), -1))
    elif period == 'year':
        import datetime
        date_from = getdate(datetime.date(today.year, 1, 1))
        date_to = today
    else:
        date_from = get_first_day(today)
        date_to = today

    df, dt = str(date_from), str(date_to)

    # ── Rep Activity ─────────────────────────────────────────────
    reps = frappe.db.sql("""
        SELECT
            v.sales_person,
            COUNT(v.name) as total_visits,
            SUM(CASE WHEN v.status = 'Completed' THEN 1 ELSE 0 END) as completed,
            COUNT(DISTINCT v.customer) as customers_visited,
            IFNULL(SUM(o.grand_total), 0) as revenue
        FROM `tabSFA Visit` v
        INNER JOIN `tabCustomer` c ON c.name = v.customer
        LEFT JOIN `tabSales Order` o
            ON o.customer = v.customer
            AND DATE(o.transaction_date) BETWEEN %s AND %s
            AND o.docstatus = 1
        WHERE c.territory = %s
          AND v.visit_date BETWEEN %s AND %s
          AND v.status != 'Cancelled'
        GROUP BY v.sales_person
        ORDER BY completed DESC
    """, (df, dt, territory, df, dt), as_dict=True)

    # ── Coverage ─────────────────────────────────────────────────
    total_customers = frappe.db.count('Customer', {
        'territory': territory, 'disabled': 0
    })

    visited_customers = frappe.db.sql("""
        SELECT COUNT(DISTINCT v.customer) as cnt
        FROM `tabSFA Visit` v
        INNER JOIN `tabCustomer` c ON c.name = v.customer
        WHERE c.territory = %s
          AND v.visit_date BETWEEN %s AND %s
          AND v.status = 'Completed'
    """, (territory, df, dt), as_dict=True)[0].cnt or 0

    coverage_pct = round((visited_customers / total_customers * 100) if total_customers else 0)

    # ── Option B: Visit Frequency Compliance ─────────────────────
    # Customers whose next_visit_due is within the period and were actually visited
    due_in_period = frappe.db.count('Customer', {
        'territory': territory,
        'disabled': 0,
        'custom_next_visit_due': ['between', [df, dt]],
    })

    # Of those, how many were actually visited
    visited_on_time = frappe.db.sql("""
        SELECT COUNT(DISTINCT c.name) as cnt
        FROM `tabCustomer` c
        INNER JOIN `tabSFA Visit` v ON v.customer = c.name
        WHERE c.territory = %s
          AND c.custom_next_visit_due BETWEEN %s AND %s
          AND v.visit_date BETWEEN %s AND %s
          AND v.status = 'Completed'
    """, (territory, df, dt, df, dt), as_dict=True)[0].cnt or 0

    freq_compliance = round((visited_on_time / due_in_period * 100) if due_in_period else 0)

    # ── Option A: Beat Plan Compliance ───────────────────────────
    beat_plans = frappe.get_all('SFA Beat Plan', {
        'territory': territory,
        'status': 'Active',
    }, ['name'])

    beat_compliance = None
    if beat_plans:
        # Count total customer-days planned vs completed
        planned = 0
        completed = 0
        for bp in beat_plans:
            beats = frappe.get_all('SFA Beat Plan Beat',
                filters={'parent': bp.name, 'parentfield': 'custom_beats'},
                fields=['name', 'monday', 'tuesday', 'wednesday',
                        'thursday', 'friday', 'saturday', 'sunday']
            )
            for beat in beats:
                # Count how many days this beat runs in the period
                d = date_from
                while d <= date_to:
                    day_field = d.strftime('%A').lower()
                    if beat.get(day_field):
                        cust_count = frappe.db.count('SFA Beat Plan Beat Customer',
                            {'parent': beat.name})
                        planned += cust_count
                    d = getdate(add_days(d, 1))

        # Count completed visits linked to beat plans in territory
        completed = frappe.db.sql("""
            SELECT COUNT(*) as cnt
            FROM `tabSFA Visit` v
            INNER JOIN `tabCustomer` c ON c.name = v.customer
            WHERE c.territory = %s
              AND v.visit_date BETWEEN %s AND %s
              AND v.status = 'Completed'
              AND v.beat_plan IS NOT NULL
              AND v.beat_plan != ''
        """, (territory, df, dt), as_dict=True)[0].cnt or 0

        beat_compliance = round((completed / planned * 100) if planned else 0)

    # ── Revenue ──────────────────────────────────────────────────
    revenue = frappe.db.sql("""
        SELECT IFNULL(SUM(o.grand_total), 0) as total
        FROM `tabSales Order` o
        INNER JOIN `tabCustomer` c ON c.name = o.customer
        WHERE c.territory = %s
          AND DATE(o.transaction_date) BETWEEN %s AND %s
          AND o.docstatus = 1
    """, (territory, df, dt), as_dict=True)[0].total or 0

    # ── Overdue customers ─────────────────────────────────────────
    overdue = frappe.get_all('Customer',
        filters={
            'territory': territory,
            'disabled': 0,
            'custom_next_visit_due': ['<', str(today)],
        },
        fields=[
            'name', 'customer_name', 'custom_sfa_rep',
            'custom_last_visit_date', 'custom_next_visit_due',
            'custom_location_area', 'custom_location_city',
        ],
        order_by='custom_next_visit_due asc',
        limit=50,
    )

    # ── Unvisited customers ───────────────────────────────────────
    visited_set = set(r['customer'] for r in frappe.db.sql("""
        SELECT DISTINCT v.customer
        FROM `tabSFA Visit` v
        INNER JOIN `tabCustomer` c ON c.name = v.customer
        WHERE c.territory = %s
          AND v.visit_date BETWEEN %s AND %s
          AND v.status = 'Completed'
    """, (territory, df, dt), as_dict=True))

    unvisited = frappe.get_all('Customer',
        filters={'territory': territory, 'disabled': 0},
        fields=['name', 'customer_name', 'custom_sfa_rep',
                'custom_last_visit_date', 'custom_next_visit_due',
                'custom_location_area', 'custom_location_city'],
        limit=200,
    )
    unvisited = [c for c in unvisited if c.name not in visited_set][:50]

    return {
        'territory': territory,
        'period': period,
        'date_from': df,
        'date_to': dt,
        'summary': {
            'total_customers': total_customers,
            'visited_customers': visited_customers,
            'coverage_pct': coverage_pct,
            'freq_compliance': freq_compliance,
            'freq_compliance_base': due_in_period,
            'beat_compliance': beat_compliance,
            'revenue': float(revenue),
            'active_reps': len(reps),
        },
        'reps': reps,
        'overdue': overdue,
        'unvisited': unvisited,
    }


@frappe.whitelist()
def get_territories_list():
    return frappe.get_all('Territory',
        filters={'is_group': 0},
        fields=['name'],
        order_by='name asc',
        limit=100,
    )
