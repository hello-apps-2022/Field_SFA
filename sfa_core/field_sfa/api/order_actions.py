import frappe
from sfa_core.field_sfa.api.response import mobile_api
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
@mobile_api
def confirm_order(name):
    # Draft -> Submitted. Counts toward revenue/targets once submitted.
    doc = frappe.get_doc("Sales Order", name)
    if not _can_manage(doc):
        frappe.throw(_("You can only confirm your own orders."))
    if doc.docstatus == 0:
        doc.submit()
        doc.db_set("custom_sfa_confirmed_on", now_datetime(), update_modified=False)
        doc.db_set("custom_sfa_confirmed_by", frappe.session.user, update_modified=False)
        frappe.db.commit()
    return {"name": doc.name, "docstatus": doc.docstatus}


@frappe.whitelist()
@mobile_api
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
@mobile_api
def cancel_order(name):
    doc = frappe.get_doc("Sales Order", name)
    if not _can_manage(doc):
        frappe.throw(_("You can only cancel your own orders."))
    if doc.docstatus == 1:
        doc.cancel()
    return {"name": name, "docstatus": doc.docstatus}


@frappe.whitelist()
@mobile_api
def update_order_items(name, items):
    """Edit line items on a confirmed Booking order (before delivery)."""
    import json
    from frappe.utils import flt
    from erpnext.controllers.accounts_controller import update_child_qty_rate
    doc = frappe.get_doc("Sales Order", name)
    if not _can_manage(doc):
        frappe.throw(_("You can only edit your own orders."))
    if doc.docstatus != 1:
        frappe.throw(_("Only a confirmed order can be edited here."))
    if (doc.custom_sfa_order_type or "Booking") != "Booking":
        frappe.throw(_("Only Booking orders can be edited after confirmation."))
    if doc.custom_sfa_delivery_status == "Delivered":
        frappe.throw(_("A delivered order can no longer be edited."))
    if flt(doc.per_delivered) > 0 or flt(doc.per_billed) > 0:
        frappe.throw(_("This order is partly delivered or invoiced and can no longer be edited."))
    if isinstance(items, str):
        items = json.loads(items)
    if not items:
        frappe.throw(_("An order must have at least one item."))
    # Consolidate duplicate product lines (same SKU) into one row. Two paid
    # rows of the same product should not survive on a confirmed order; free
    # lines are kept separate (is_free_item) so a SKU can appear paid + free.
    # The first row keeps its docname (updated in place); the duplicate row is
    # left out of trans_items so update_child_qty_rate removes it.
    _agg, _order = {}, []
    for it in items:
        _code = it.get("item_code")
        if not _code:
            continue
        _free = 1 if it.get("is_free_item") else 0
        _key = (_code, _free)
        if _key not in _agg:
            _agg[_key] = {"item_code": _code, "qty": flt(it.get("qty")),
                          "rate": flt(it.get("rate")), "is_free_item": _free,
                          "docname": it.get("docname")}
            _order.append(_key)
        else:
            _g = _agg[_key]
            _g["qty"] += flt(it.get("qty"))
            _r = flt(it.get("rate"))
            if not _free and _r:
                _g["rate"] = max(_g["rate"], _r)
            if not _g.get("docname") and it.get("docname"):
                _g["docname"] = it.get("docname")
    items = [_agg[_k] for _k in _order]
    trans_items = []
    for it in items:
        row = {"item_code": it.get("item_code"), "qty": flt(it.get("qty")), "rate": flt(it.get("rate"))}
        if it.get("docname"):
            row["docname"] = it.get("docname")
        trans_items.append(row)
    update_child_qty_rate("Sales Order", json.dumps(trans_items), name)
    # Re-apply free-carton flags. update_child_qty_rate does not carry
    # is_free_item, so a line the client marked free (priced at 0) is re-flagged
    # here, and a line that is no longer free is cleared. Free lines stay at 0.
    free_codes = {it.get("item_code") for it in items if it.get("is_free_item")}
    doc.reload()
    for row in doc.items:
        want_free = 1 if (row.item_code in free_codes and flt(row.rate) == 0) else 0
        if int(row.is_free_item or 0) != want_free:
            frappe.db.set_value("Sales Order Item", row.name, "is_free_item", want_free)
    frappe.db.commit()
    try:
        from sfa_core.field_sfa.doc_events.sales_order import _refresh_customer_order_stats
        _refresh_customer_order_stats(doc.customer)
    except Exception:
        pass
    return {"name": name, "docstatus": 1}
