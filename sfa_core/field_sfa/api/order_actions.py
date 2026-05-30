import frappe
from frappe import _
from frappe.utils import now_datetime


def _is_priv():
    return bool(set(frappe.get_roles()) & {"System Manager", "SFA Admin", "SFA Manager"})


def _rep_for_user():
    return frappe.db.get_value("Sales Person", {"custom_user_id": frappe.session.user}, "name")


def _can_manage(doc):
    if _is_priv():
        return True
    rep = _rep_for_user()
    return bool(rep and doc.custom_sfa_rep == rep)


@frappe.whitelist()
def confirm_order(name):
    # Draft -> Submitted. Counts toward revenue/targets once submitted.
    doc = frappe.get_doc("Sales Order", name)
    if not _can_manage(doc):
        frappe.throw(_("You can only confirm your own orders."))
    if doc.docstatus == 0:
        doc.submit()
    return {"name": doc.name, "docstatus": doc.docstatus}


@frappe.whitelist()
def mark_delivered(name):
    # Any rep/manager/admin can mark a confirmed order delivered (locks it).
    doc = frappe.get_doc("Sales Order", name)
    if doc.docstatus != 1:
        frappe.throw(_("Only a confirmed order can be marked delivered."))
    doc.db_set("custom_sfa_delivery_status", "Delivered", update_modified=True)
    doc.db_set("custom_sfa_delivered_on", now_datetime(), update_modified=False)
    doc.db_set("custom_sfa_delivered_by", frappe.session.user, update_modified=False)
    frappe.db.commit()
    try:
        from sfa_core.field_sfa.doc_events.sales_order import _refresh_customer_order_stats
        _refresh_customer_order_stats(doc.customer)
    except Exception:
        pass
    return {"name": name, "delivery_status": "Delivered"}


@frappe.whitelist()
def cancel_order(name):
    doc = frappe.get_doc("Sales Order", name)
    if not _can_manage(doc):
        frappe.throw(_("You can only cancel your own orders."))
    if doc.docstatus == 1:
        doc.cancel()
    return {"name": name, "docstatus": doc.docstatus}
