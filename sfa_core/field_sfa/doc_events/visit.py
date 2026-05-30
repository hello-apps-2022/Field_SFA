import frappe
from frappe.utils import now, getdate, add_days
from frappe.utils import time_diff_in_seconds


def validate(doc, method):
    # Auto-track check-in/out so field reps don't tap buttons:
    #   check-in  = when the visit is created
    #   check-out = when the visit is marked Completed
    if doc.is_new() and not doc.check_in_time:
        doc.check_in_time = now()
    if doc.status == "Completed" and not doc.check_out_time:
        doc.check_out_time = now()
    if doc.check_in_time and doc.check_out_time:
        doc.duration_minutes = int(
            (time_diff_in_seconds(doc.check_out_time, doc.check_in_time) or 0) / 60
        )


def on_update(doc, method):
    if doc.status == "Completed" and doc.customer:
        _update_customer_stats(doc.customer)


def on_submit(doc, method):
    if doc.customer:
        _update_customer_stats(doc.customer)


def _update_customer_stats(customer_name):
    """Update last visit date, total orders, revenue on Customer record."""
    try:
        # Last completed visit date
        last_visit = frappe.db.get_value(
            "SFA Visit",
            filters={"customer": customer_name, "status": "Completed"},
            fieldname="visit_date",
            order_by="visit_date desc",
        )

        # Confirmed orders: count + billed value
        order_stats = frappe.db.sql("""
            SELECT COUNT(*) as cnt, IFNULL(SUM(grand_total), 0) as total
            FROM `tabSales Order`
            WHERE customer = %s AND docstatus = 1
        """, customer_name, as_dict=True)

        # Collected payments (finalized: Submitted / Reconciled)
        collected = frappe.db.sql("""
            SELECT IFNULL(SUM(amount), 0) as total
            FROM `tabSFA Payment`
            WHERE customer = %s AND status IN ('Submitted', 'Reconciled')
        """, customer_name, as_dict=True)

        order_total = order_stats[0].total if order_stats else 0
        collected_total = collected[0].total if collected else 0
        due = order_total - collected_total
        if due < 0:
            due = 0

        update = {}
        if last_visit:
            update["custom_last_visit_date"] = last_visit

        if order_stats:
            update["custom_total_orders"] = order_stats[0].cnt

        # Revenue = collected payments; Due = billed orders - collected
        update["custom_total_revenue"] = collected_total
        update["custom_outstanding_payments"] = due

        # Compute next visit due
        freq = frappe.db.get_value("Customer", customer_name, "custom_visit_frequency")
        if last_visit and freq:
            update["custom_next_visit_due"] = add_days(last_visit, int(freq))

        if update:
            frappe.db.set_value("Customer", customer_name, update)
            frappe.db.commit()

    except Exception as e:
        frappe.log_error(f"Failed to update customer stats for {customer_name}: {e}",
                         "SFA Visit Hook")
