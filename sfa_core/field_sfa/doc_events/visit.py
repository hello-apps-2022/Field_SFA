import frappe
from frappe.utils import now, getdate, add_days
from frappe.utils import time_diff_in_seconds


def validate(doc, method):
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

        # Total orders
        order_stats = frappe.db.sql("""
            SELECT COUNT(*) as cnt, IFNULL(SUM(grand_total), 0) as total
            FROM `tabSales Order`
            WHERE customer = %s AND docstatus = 1
        """, customer_name, as_dict=True)

        # Outstanding payments (submitted but not reconciled)
        outstanding = frappe.db.sql("""
            SELECT IFNULL(SUM(amount), 0) as total
            FROM `tabSFA Payment`
            WHERE customer = %s AND status = 'Draft' AND docstatus < 2
        """, customer_name, as_dict=True)

        update = {}
        if last_visit:
            update["custom_last_visit_date"] = last_visit

        if order_stats:
            update["custom_total_orders"] = order_stats[0].cnt
            update["custom_total_revenue"] = order_stats[0].total

        if outstanding:
            update["custom_outstanding_payments"] = outstanding[0].total

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
