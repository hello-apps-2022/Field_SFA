import frappe
from frappe.utils import getdate, nowdate, add_days


@frappe.whitelist()
def get_rep_activity(sales_person, date_from=None, date_to=None,
                     time_from="00:00", time_to="23:59"):
    """
    Returns GPS track points + visits for a rep across a date/time range.
    """
    if not date_from:
        date_from = nowdate()
    if not date_to:
        date_to = date_from

    date_from = getdate(date_from)
    date_to = getdate(date_to)

    # Build datetime boundaries
    dt_from = f"{date_from} {time_from}:00"
    dt_to   = f"{date_to} {time_to}:59"

    track_points = frappe.db.sql("""
        SELECT
            latitude, longitude, accuracy, speed,
            timestamp, battery_level, visit
        FROM `tabSFA GPS Track Point`
        WHERE sales_person = %(sp)s
          AND timestamp BETWEEN %(dt_from)s AND %(dt_to)s
          AND latitude IS NOT NULL
          AND latitude != 0
        ORDER BY timestamp ASC
        LIMIT 5000
    """, {
        'sp': sales_person,
        'dt_from': dt_from,
        'dt_to': dt_to,
    }, as_dict=True)

    visits = frappe.db.sql("""
        SELECT
            v.name, v.customer, v.status, v.visit_purpose,
            v.check_in_time, v.check_out_time, v.visit_date,
            v.check_in_latitude, v.check_in_longitude,
            v.check_out_latitude, v.check_out_longitude,
            v.duration_minutes, v.distance_from_customer,
            c.custom_location_area, c.custom_location_city
        FROM `tabSFA Visit` v
        LEFT JOIN `tabCustomer` c ON c.name = v.customer
        WHERE v.sales_person = %(sp)s
          AND v.visit_date BETWEEN %(date_from)s AND %(date_to)s
        ORDER BY COALESCE(v.check_in_time, v.visit_date) ASC
    """, {
        'sp': sales_person,
        'date_from': str(date_from),
        'date_to': str(date_to),
    }, as_dict=True)

    return {
        'track_points': track_points,
        'visits': visits,
        'date_from': str(date_from),
        'date_to': str(date_to),
        'time_from': time_from,
        'time_to': time_to,
        'sales_person': sales_person,
    }


@frappe.whitelist()
def get_all_reps_today():
    reps = frappe.db.sql("""
        SELECT
            sp.name, sp.custom_territory,
            sp.custom_last_seen, sp.custom_last_latitude,
            sp.custom_last_longitude, sp.custom_sfa_active,
            sp.custom_mobile_no
        FROM `tabSales Person` sp
        WHERE sp.is_group = 0
          AND sp.custom_sfa_active = 1
    """, as_dict=True)

    today = nowdate()
    for rep in reps:
        rep['visits_today'] = frappe.db.count('SFA Visit', {
            'sales_person': rep['name'],
            'visit_date': today,
        })
        rep['completed_today'] = frappe.db.count('SFA Visit', {
            'sales_person': rep['name'],
            'visit_date': today,
            'status': 'Completed',
        })
    return reps


@frappe.whitelist()
def get_customers_map(territory=None, customer_group=None,
                      outlet_tier=None, has_location_only=1):
    filters = {}
    if territory:
        filters['territory'] = territory
    if customer_group:
        filters['customer_group'] = customer_group
    if outlet_tier:
        filters['custom_outlet_tier'] = outlet_tier
    if int(has_location_only):
        filters['custom_latitude'] = ['!=', 0]

    return frappe.get_all('Customer',
        filters=filters,
        fields=[
            'name', 'customer_name', 'customer_group', 'territory',
            'mobile_no', 'custom_sfa_rep', 'custom_outlet_tier',
            'custom_latitude', 'custom_longitude',
            'custom_location_area', 'custom_location_city',
            'custom_last_visit_date', 'custom_next_visit_due',
            'custom_total_orders', 'custom_total_revenue',
            'custom_outstanding_payments', 'disabled',
        ],
        order_by='customer_name asc',
        limit=2000,
    )


@frappe.whitelist()
def get_territories():
    return frappe.get_all('Territory',
        filters={'is_group': 0},
        fields=['name'],
        order_by='name asc',
        limit=100,
    )


@frappe.whitelist()
def get_active_sales_persons():
    return frappe.get_all('Sales Person',
        filters={'is_group': 0},
        fields=['name', 'custom_territory', 'custom_sfa_active'],
        order_by='name asc',
        limit=200,
    )
