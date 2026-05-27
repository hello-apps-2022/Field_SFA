import frappe
from frappe.utils import nowdate, getdate
import json


@frappe.whitelist()
def get_beat_plans(sales_person=None, territory=None, status=None):
    filters = {}
    if sales_person: filters['sales_person'] = sales_person
    if territory: filters['territory'] = territory
    if status: filters['status'] = status

    plans = frappe.get_all('SFA Beat Plan',
        filters=filters,
        fields=[
            'name', 'plan_name', 'territory', 'sales_person', 'status',
            'custom_effective_from', 'custom_effective_to', 'custom_discovery_count',
        ],
        order_by='creation desc',
        limit=200,
    )

    for plan in plans:
        # Count beats and total customers
        beats = frappe.get_all('SFA Beat Plan Beat',
            filters={'parent': plan['name'], 'parentfield': 'custom_beats'},
            fields=['name', 'beat_name', 'monday', 'tuesday', 'wednesday',
                    'thursday', 'friday', 'saturday', 'sunday', 'area_name'],
        )
        plan['beat_count'] = len(beats)
        plan['beats_summary'] = beats  # for day coverage display

        # Total unique customers across all beats
        total = 0
        for beat in beats:
            total += frappe.db.count('SFA Beat Plan Beat Customer',
                {'parent': beat['name']})
        plan['customer_count'] = total

    return plans


@frappe.whitelist()
def get_beat_plan(name):
    doc = frappe.get_doc('SFA Beat Plan', name)
    result = doc.as_dict()

    # Fetch beats directly from DB — custom Table fields need explicit query
    beats_raw = frappe.get_all('SFA Beat Plan Beat',
        filters={'parent': name, 'parentfield': 'custom_beats'},
        fields=[
            'name', 'beat_name', 'area_name', 'area_notes', 'estimated_outlets',
            'monday', 'tuesday', 'wednesday', 'thursday',
            'friday', 'saturday', 'sunday', 'idx',
        ],
        order_by='idx asc',
    )

    enriched_beats = []
    for beat in beats_raw:
        # Get customers for this beat
        customers_raw = frappe.get_all('SFA Beat Plan Beat Customer',
            filters={'parent': beat['name']},
            fields=['name', 'customer', 'customer_name', 'visit_sequence', 'notes'],
            order_by='visit_sequence asc',
        )
        enriched_customers = []
        for c in customers_raw:
            cust = frappe.db.get_value('Customer', c['customer'], [
                'customer_name', 'custom_location_area', 'custom_location_city',
                'custom_last_visit_date', 'custom_latitude', 'custom_longitude',
            ], as_dict=True) or {}
            enriched_customers.append({
                **c,
                'customer_name': cust.get('customer_name', c['customer']),
                'location_area': cust.get('custom_location_area', ''),
                'location_city': cust.get('custom_location_city', ''),
                'last_visit_date': cust.get('custom_last_visit_date'),
                'latitude': cust.get('custom_latitude'),
                'longitude': cust.get('custom_longitude'),
            })
        beat['customers'] = enriched_customers
        enriched_beats.append(beat)

    result['custom_beats'] = enriched_beats
    return result


@frappe.whitelist()
def can_rep_create():
    user_roles = frappe.get_roles(frappe.session.user)
    is_manager = 'Sales Manager' in user_roles or 'System Manager' in user_roles
    rep_can_create = frappe.db.get_default('beat_plan_rep_can_create')
    if rep_can_create is None:
        rep_can_create = '1'
    return {
        'can_create': is_manager or rep_can_create == '1',
        'is_manager': is_manager,
        'rep_setting': rep_can_create == '1',
    }


@frappe.whitelist()
def set_rep_creation_permission(allow):
    frappe.db.set_default('beat_plan_rep_can_create', '1' if allow else '0')
    frappe.db.commit()
    return {'success': True}


@frappe.whitelist()
def add_beat(beat_plan, beat_name, days, area_name=None, area_notes=None):
    """Add a new beat (named route) to a beat plan by inserting child doc directly."""
    if isinstance(days, str):
        days = json.loads(days)

    beat = frappe.get_doc({
        'doctype': 'SFA Beat Plan Beat',
        'parent': beat_plan,
        'parenttype': 'SFA Beat Plan',
        'parentfield': 'custom_beats',
        'beat_name': beat_name,
        'area_name': area_name or '',
        'area_notes': area_notes or '',
        'monday': 1 if 'monday' in days else 0,
        'tuesday': 1 if 'tuesday' in days else 0,
        'wednesday': 1 if 'wednesday' in days else 0,
        'thursday': 1 if 'thursday' in days else 0,
        'friday': 1 if 'friday' in days else 0,
        'saturday': 1 if 'saturday' in days else 0,
        'sunday': 1 if 'sunday' in days else 0,
    })
    beat.insert(ignore_permissions=True)
    frappe.db.commit()
    return {'success': True, 'name': beat.name}


@frappe.whitelist()
def add_customer_to_beat(beat_name, customer):
    """Add customer to a specific beat row."""
    beat_doc = frappe.get_doc('SFA Beat Plan Beat', beat_name)

    # Check if already exists
    for c in beat_doc.customers:
        if c.customer == customer:
            frappe.throw(f'{customer} is already in this beat')

    next_seq = max([c.visit_sequence or 0 for c in beat_doc.customers], default=0) + 1
    customer_name = frappe.db.get_value('Customer', customer, 'customer_name') or customer

    beat_doc.append('customers', {
        'customer': customer,
        'customer_name': customer_name,
        'visit_sequence': next_seq,
    })
    beat_doc.flags.ignore_version = True
    beat_doc.save(ignore_permissions=False)

    # Increment discovery count on parent beat plan
    parent = beat_doc.parent
    if parent:
        current = frappe.db.get_value('SFA Beat Plan', parent, 'custom_discovery_count') or 0
        frappe.db.set_value('SFA Beat Plan', parent, 'custom_discovery_count', current + 1)

    # Link customer to beat plan
    frappe.db.set_value('Customer', customer, {
        'custom_active_beat_plan': beat_doc.parent,
        'custom_beat_territory': frappe.db.get_value('SFA Beat Plan', beat_doc.parent, 'territory'),
    })
    frappe.db.commit()
    return {'success': True, 'sequence': next_seq}


@frappe.whitelist()
def remove_customer_from_beat(beat_name, customer):
    beat_doc = frappe.get_doc('SFA Beat Plan Beat', beat_name)
    beat_doc.customers = [c for c in beat_doc.customers if c.customer != customer]
    for i, c in enumerate(beat_doc.customers, 1):
        c.visit_sequence = i
    beat_doc.flags.ignore_version = True
    beat_doc.save(ignore_permissions=False)
    frappe.db.commit()
    return {'success': True}


@frappe.whitelist()
def reorder_beat_customers(beat_name, customer_order):
    if isinstance(customer_order, str):
        customer_order = json.loads(customer_order)
    beat_doc = frappe.get_doc('SFA Beat Plan Beat', beat_name)
    order_map = {name: i + 1 for i, name in enumerate(customer_order)}
    for c in beat_doc.customers:
        if c.customer in order_map:
            c.visit_sequence = order_map[c.customer]
    beat_doc.customers.sort(key=lambda x: x.visit_sequence or 999)
    beat_doc.flags.ignore_version = True
    beat_doc.save(ignore_permissions=False)
    frappe.db.commit()
    return {'success': True}


@frappe.whitelist()
def get_todays_beats(sales_person=None):
    """Returns beats scheduled for today for a given rep."""
    today = getdate(nowdate())
    day_field = today.strftime('%A').lower()  # e.g. 'monday'

    filters = {'status': 'Active'}
    if sales_person:
        filters['sales_person'] = sales_person

    plans = frappe.get_all('SFA Beat Plan', filters=filters,
        fields=['name', 'plan_name', 'territory', 'sales_person',
                'custom_effective_from', 'custom_effective_to'])

    result = []
    for plan in plans:
        ef = plan.get('custom_effective_from')
        et = plan.get('custom_effective_to')
        if ef and getdate(ef) > today: continue
        if et and getdate(et) < today: continue

        # Get beats for today
        beats = frappe.get_all('SFA Beat Plan Beat',
            filters={'parent': plan['name'], 'parentfield': 'custom_beats',
                     day_field: 1},
            fields=['name', 'beat_name', 'area_name'])

        if beats:
            plan['todays_beats'] = beats
            result.append(plan)

    return result
