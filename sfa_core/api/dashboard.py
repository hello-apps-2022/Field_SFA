import frappe
from frappe.utils import nowdate, add_days, getdate, get_first_day, get_last_day


@frappe.whitelist()
def get_dashboard_data(period="today"):
    today = getdate(nowdate())

    if period == "today":
        date_from = today
        date_to = today
    elif period == "week":
        date_from = getdate(add_days(today, -6))
        date_to = today
    elif period == "month":
        date_from = get_first_day(today)
        date_to = today
    else:
        date_from = today
        date_to = today

    df = str(date_from)
    dt = str(date_to)

    # Active visits (in progress right now)
    active_visits = frappe.db.count("SFA Visit", {
        "status": "In Progress",
        "visit_date": ["between", [df, dt]],
    })

    # Completed visits
    completed_visits = frappe.db.count("SFA Visit", {
        "status": "Completed",
        "visit_date": ["between", [df, dt]],
    })

    # Total visits planned
    total_visits = frappe.db.count("SFA Visit", {
        "visit_date": ["between", [df, dt]],
        "status": ["not in", ["Cancelled"]],
    })

    # Orders
    order_stats = frappe.db.sql("""
        SELECT COUNT(*) as cnt, IFNULL(SUM(grand_total), 0) as revenue
        FROM `tabSales Order`
        WHERE transaction_date BETWEEN %s AND %s
        AND docstatus = 1
    """, (df, dt), as_dict=True)

    orders_count = order_stats[0].cnt if order_stats else 0
    revenue = order_stats[0].revenue if order_stats else 0

    # Payments collected
    payment_stats = frappe.db.sql("""
        SELECT IFNULL(SUM(amount), 0) as total
        FROM `tabSFA Payment`
        WHERE payment_date BETWEEN %s AND %s
        AND status IN ('Submitted', 'Reconciled')
    """, (df, dt), as_dict=True)

    payments = payment_stats[0].total if payment_stats else 0

    # Beat plan compliance — completed / total planned
    beat_total = frappe.db.count("SFA Visit", {
        "visit_date": ["between", [df, dt]],
        "beat_plan": ["!=", ""],
        "status": ["not in", ["Cancelled"]],
    })
    beat_completed = frappe.db.count("SFA Visit", {
        "visit_date": ["between", [df, dt]],
        "beat_plan": ["!=", ""],
        "status": "Completed",
    })
    compliance = round((beat_completed / beat_total * 100) if beat_total else 0)

    # New customers this period
    new_customers = frappe.db.count("Customer", {
        "creation": ["between", [df + " 00:00:00", dt + " 23:59:59"]],
    })

    # Forms submitted
    forms_submitted = frappe.db.count("SFA Form Response", {
        "response_date": ["between", [df + " 00:00:00", dt + " 23:59:59"]],
    })

    # Active reps today
    active_reps = frappe.db.sql("""
        SELECT COUNT(DISTINCT sales_person) as cnt
        FROM `tabSFA Visit`
        WHERE visit_date BETWEEN %s AND %s
        AND status != 'Cancelled'
    """, (df, dt), as_dict=True)
    active_reps_count = active_reps[0].cnt if active_reps else 0

    return {
        "active_visits": active_visits,
        "completed_visits": completed_visits,
        "total_visits": total_visits,
        "orders_count": orders_count,
        "revenue": float(revenue),
        "payments_collected": float(payments),
        "compliance_rate": compliance,
        "new_customers": new_customers,
        "forms_submitted": forms_submitted,
        "active_reps": active_reps_count,
        "date_from": df,
        "date_to": dt,
    }


@frappe.whitelist()
def get_leaderboard(period="today"):
    today = getdate(nowdate())

    if period == "today":
        date_from = date_to = today
    elif period == "week":
        date_from, date_to = getdate(add_days(today, -6)), today
    elif period == "month":
        date_from, date_to = get_first_day(today), today
    else:
        date_from = date_to = today

    df, dt = str(date_from), str(date_to)

    rows = frappe.db.sql("""
        SELECT
            v.sales_person,
            COUNT(v.name) as visits,
            SUM(CASE WHEN v.status = 'Completed' THEN 1 ELSE 0 END) as completed,
            IFNULL(SUM(o.grand_total), 0) as revenue,
            IFNULL(SUM(p.amount), 0) as collections,
            COUNT(DISTINCT v.customer) as customers_visited
        FROM `tabSFA Visit` v
        LEFT JOIN `tabSales Order` o
            ON o.customer = v.customer
            AND DATE(o.transaction_date) BETWEEN %s AND %s
            AND o.docstatus = 1
        LEFT JOIN `tabSFA Payment` p
            ON p.sales_person = v.sales_person
            AND p.payment_date BETWEEN %s AND %s
            AND p.status IN ('Submitted', 'Reconciled')
        WHERE v.visit_date BETWEEN %s AND %s
          AND v.status != 'Cancelled'
          AND v.sales_person IS NOT NULL
          AND v.sales_person != ''
        GROUP BY v.sales_person
        ORDER BY completed DESC, revenue DESC
        LIMIT 20
    """, (df, dt, df, dt, df, dt), as_dict=True)

    return rows


@frappe.whitelist()
def get_recent_visits(limit=10):
    return frappe.db.sql("""
        SELECT
            v.name, v.customer, v.sales_person, v.visit_date,
            v.status, v.check_in_time, v.visit_purpose,
            v.duration_minutes,
            c.custom_location_area, c.custom_location_city
        FROM `tabSFA Visit` v
        LEFT JOIN `tabCustomer` c ON c.name = v.customer
        ORDER BY v.modified DESC
        LIMIT %s
    """, (limit,), as_dict=True)


@frappe.whitelist()
def get_visit_trend(days=7):
    """Daily visit counts for the last N days."""
    today = getdate(nowdate())
    rows = []
    for i in range(days - 1, -1, -1):
        d = str(getdate(add_days(today, -i)))
        total = frappe.db.count("SFA Visit", {
            "visit_date": d,
            "status": ["not in", ["Cancelled"]],
        })
        completed = frappe.db.count("SFA Visit", {
            "visit_date": d,
            "status": "Completed",
        })
        rows.append({"date": d, "total": total, "completed": completed})
    return rows


@frappe.whitelist()
def get_overdue_customers(limit=10):
    """Customers whose next visit is overdue."""
    today = str(getdate(nowdate()))
    return frappe.get_all("Customer",
        filters={
            "custom_next_visit_due": ["<", today],
            "disabled": 0,
        },
        fields=[
            "name", "customer_name", "territory", "custom_sfa_rep",
            "custom_last_visit_date", "custom_next_visit_due",
            "custom_location_area", "custom_location_city",
        ],
        order_by="custom_next_visit_due asc",
        limit=limit,
    )


@frappe.whitelist()
def get_live_reps():
    """
    Returns current location + status of all reps for the live map.
    """
    from datetime import datetime, timedelta
    from frappe.utils import now_datetime

    today = nowdate()
    now = now_datetime()
    active_threshold = now - timedelta(hours=8)

    reps = frappe.db.sql("""
        SELECT
            sp.name, sp.custom_territory, sp.custom_mobile_no,
            sp.custom_last_seen, sp.custom_last_latitude,
            sp.custom_last_longitude, sp.custom_sfa_active
        FROM `tabSales Person` sp
        WHERE sp.is_group = 0
          AND sp.enabled = 1
    """, as_dict=True)

    result = []
    for rep in reps:
        # Latest GPS point today
        latest = frappe.db.sql("""
            SELECT latitude, longitude, timestamp, speed, battery_level, visit
            FROM `tabSFA GPS Track Point`
            WHERE sales_person = %s
              AND DATE(timestamp) = %s
              AND latitude IS NOT NULL AND latitude != 0
            ORDER BY timestamp DESC LIMIT 1
        """, (rep.name, today), as_dict=True)

        if latest:
            lat, lng = latest[0].latitude, latest[0].longitude
            last_seen = latest[0].timestamp
            speed = latest[0].speed or 0
        elif rep.custom_last_latitude and rep.custom_last_longitude:
            lat, lng = rep.custom_last_latitude, rep.custom_last_longitude
            last_seen = rep.custom_last_seen
            speed = 0
        else:
            continue  # no location at all, skip

        visits_today = frappe.db.count('SFA Visit', {
            'sales_person': rep.name, 'visit_date': today,
            'status': ['not in', ['Cancelled']],
        })
        completed_today = frappe.db.count('SFA Visit', {
            'sales_person': rep.name, 'visit_date': today, 'status': 'Completed',
        })
        active_visit = frappe.db.get_value('SFA Visit',
            {'sales_person': rep.name, 'status': 'In Progress', 'visit_date': today},
            ['name', 'customer', 'check_in_time'], as_dict=True
        )

        if active_visit:
            status = 'visiting'
        elif last_seen and frappe.utils.get_datetime(last_seen) > active_threshold:
            status = 'active'
        else:
            status = 'inactive'

        result.append({
            'name': rep.name,
            'territory': rep.custom_territory,
            'latitude': float(lat),
            'longitude': float(lng),
            'last_seen': str(last_seen) if last_seen else None,
            'speed': float(speed or 0),
            'status': status,
            'visits_today': visits_today,
            'completed_today': completed_today,
            'active_visit': active_visit,
        })

    return result
