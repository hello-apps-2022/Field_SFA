import frappe
from sfa_core.api.auth import get_scope_context as get_user_context, require_role


@frappe.whitelist()
def get_target_sets(territory=None, status=None):
    ctx = get_user_context()
    if not ctx['is_manager'] and not ctx['is_admin']:
        frappe.throw('Insufficient permissions', frappe.PermissionError)

    filters = {}
    if ctx['is_manager'] and not ctx['is_admin']:
        filters['territory'] = ctx['territory']
    elif territory:
        filters['territory'] = territory
    if status:
        filters['status'] = status

    sets = frappe.get_all('SFA Target Set',
        filters=filters,
        fields=['name', 'target_set_name', 'territory', 'date_from', 'date_to', 'status', 'notes'],
        order_by='date_from desc',
        limit=100,
    )

    for s in sets:
        s['rep_count'] = frappe.db.count('SFA Target Set Rep', {'parent': s['name']})

    return sets


@frappe.whitelist()
def get_target_set(name):
    ctx = get_user_context()
    if not ctx['is_manager'] and not ctx['is_admin']:
        frappe.throw('Insufficient permissions', frappe.PermissionError)

    doc = frappe.get_doc('SFA Target Set', name)
    result = doc.as_dict()

    # Enrich with actual performance data
    reps = frappe.get_all('SFA Target Set Rep',
        filters={'parent': name},
        fields=['name', 'sales_person', 'sales_person_name',
                'target_visits', 'target_revenue',
                'target_new_customers', 'target_compliance_pct'],
        order_by='sales_person_name asc',
    )

    df, dt = str(doc.date_from), str(doc.date_to)
    for rep in reps:
        # Actual visits
        actuals = frappe.db.sql("""
            SELECT
                COUNT(*) as visits,
                SUM(CASE WHEN status='Completed' THEN 1 ELSE 0 END) as completed
            FROM `tabSFA Visit`
            WHERE sales_person = %s AND visit_date BETWEEN %s AND %s
            AND status != 'Cancelled'
        """, (rep['sales_person'], df, dt), as_dict=True)[0]

        # Actual revenue
        revenue = frappe.db.sql("""
            SELECT IFNULL(SUM(o.grand_total), 0) as total
            FROM `tabSales Order` o
            INNER JOIN `tabCustomer` c ON c.name = o.customer
            WHERE c.custom_sfa_rep = %s
            AND DATE(o.transaction_date) BETWEEN %s AND %s
            AND o.docstatus = 1
        """, (rep['sales_person'], df, dt), as_dict=True)[0].total or 0

        # New customers
        new_custs = frappe.db.count('Customer', {
            'custom_sfa_rep': rep['sales_person'],
            'creation': ['between', [df + ' 00:00:00', dt + ' 23:59:59']],
        })

        rep['actual_visits'] = actuals.completed or 0
        rep['actual_revenue'] = float(revenue)
        rep['actual_new_customers'] = new_custs
        rep['actual_compliance_pct'] = round(
            (actuals.completed / actuals.visits * 100) if actuals.visits else 0
        )

    result['rep_targets'] = reps
    return result


@frappe.whitelist()
def get_reps_for_territory(territory):
    ctx = get_user_context()
    if not ctx['is_manager'] and not ctx['is_admin']:
        frappe.throw('Insufficient permissions', frappe.PermissionError)

    return frappe.get_all('Sales Person',
        filters={'is_group': 0, 'custom_territory': territory, 'custom_sfa_active': 1},
        fields=['name', 'sales_person_name', 'custom_territory'],
        order_by='sales_person_name asc',
    )


@frappe.whitelist()
def create_target_set(target_set_name, territory, date_from, date_to,
                      status='Draft', notes=None, rep_targets=None):
    ctx = get_user_context()
    if not ctx['is_manager'] and not ctx['is_admin']:
        frappe.throw('Insufficient permissions', frappe.PermissionError)

    import json
    if isinstance(rep_targets, str):
        rep_targets = json.loads(rep_targets)

    doc = frappe.get_doc({
        'doctype': 'SFA Target Set',
        'target_set_name': target_set_name,
        'territory': territory,
        'date_from': date_from,
        'date_to': date_to,
        'status': status,
        'notes': notes or '',
    })

    for r in (rep_targets or []):
        doc.append('rep_targets', {
            'sales_person': r['sales_person'],
            'sales_person_name': r.get('sales_person_name', ''),
            'target_visits': r.get('target_visits', 0),
            'target_revenue': r.get('target_revenue', 0),
            'target_new_customers': r.get('target_new_customers', 0),
            'target_compliance_pct': r.get('target_compliance_pct', 80),
        })

    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {'success': True, 'name': doc.name}


@frappe.whitelist()
def update_target_set(name, target_set_name=None, date_from=None, date_to=None,
                      status=None, notes=None, rep_targets=None):
    ctx = get_user_context()
    if not ctx['is_manager'] and not ctx['is_admin']:
        frappe.throw('Insufficient permissions', frappe.PermissionError)

    import json
    if isinstance(rep_targets, str):
        rep_targets = json.loads(rep_targets)

    doc = frappe.get_doc('SFA Target Set', name)
    if target_set_name: doc.target_set_name = target_set_name
    if date_from: doc.date_from = date_from
    if date_to: doc.date_to = date_to
    if status: doc.status = status
    if notes is not None: doc.notes = notes

    if rep_targets is not None:
        doc.rep_targets = []
        for r in rep_targets:
            doc.append('rep_targets', {
                'sales_person': r['sales_person'],
                'sales_person_name': r.get('sales_person_name', ''),
                'target_visits': r.get('target_visits', 0),
                'target_revenue': r.get('target_revenue', 0),
                'target_new_customers': r.get('target_new_customers', 0),
                'target_compliance_pct': r.get('target_compliance_pct', 80),
            })

    doc.flags.ignore_version = True
    doc.save(ignore_permissions=True)
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


@frappe.whitelist()
def debug_actuals(sales_person, date_from, date_to):
    """Debug endpoint to check what actuals exist for a rep."""
    require_role('SFA Admin', 'SFA Manager')
    visits = frappe.db.sql("""
        SELECT name, sales_person, visit_date, status, customer
        FROM `tabSFA Visit`
        WHERE sales_person = %s AND visit_date BETWEEN %s AND %s
        LIMIT 10
    """, (sales_person, date_from, date_to), as_dict=True)

    all_sp = frappe.db.sql("""
        SELECT DISTINCT sales_person FROM `tabSFA Visit` LIMIT 10
    """, as_dict=True)

    return {
        'queried_sales_person': sales_person,
        'visits_found': visits,
        'all_sales_persons_in_visits': all_sp,
    }
