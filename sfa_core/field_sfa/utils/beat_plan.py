import frappe
from frappe import _

def apply_amendment(amendment):
    """Apply approved amendment to beat plan"""
    beat_plan = frappe.get_doc("SFA Beat Plan", amendment.beat_plan)

    if amendment.amendment_type == "Add Customer":
        beat_plan.append("customers", {
            "customer": amendment.customer,
            "visit_sequence": amendment.new_sequence or len(beat_plan.customers) + 1,
            "visit_status": "Pending"
        })

    elif amendment.amendment_type == "Remove Customer":
        for i, cust in enumerate(beat_plan.customers):
            if cust.customer == amendment.customer:
                beat_plan.customers.pop(i)
                break

    elif amendment.amendment_type == "Reorder":
        for cust in beat_plan.customers:
            if cust.customer == amendment.customer:
                cust.visit_sequence = amendment.new_sequence
                break
        beat_plan.customers.sort(key=lambda x: x.visit_sequence)

    elif amendment.amendment_type == "Reschedule":
        if amendment.new_date:
            beat_plan.date = amendment.new_date

    beat_plan.save(ignore_permissions=True)
    frappe.msgprint(_("Beat plan updated with amendment"))
