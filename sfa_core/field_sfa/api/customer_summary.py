import frappe
from sfa_core.field_sfa.api.response import mobile_api
from frappe import _


def _f(v):
    try:
        return float(v or 0)
    except Exception:
        return 0.0


@frappe.whitelist()
@mobile_api
def get_customer_summary(customer, date_from=None, date_to=None):
    """Date-filtered activity roll-up for one customer."""
    if not customer or not frappe.db.exists("Customer", customer):
        frappe.throw(_("Customer not found"))
    if not frappe.has_permission("Customer", "read", customer):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    df = date_from or "2000-01-01"
    dt = date_to or frappe.utils.nowdate()
    params = {"c": customer, "df": df, "dt": dt}

    # Products purchased (submitted orders only) — paid vs free split.
    products = frappe.db.sql("""
        SELECT soi.item_code, soi.item_name,
            SUM(CASE WHEN soi.is_free_item = 1 THEN 0 ELSE soi.qty END) AS paid_qty,
            SUM(CASE WHEN soi.is_free_item = 1 THEN soi.qty ELSE 0 END) AS free_qty,
            SUM(soi.amount) AS amount
        FROM `tabSales Order Item` soi
        INNER JOIN `tabSales Order` so ON so.name = soi.parent
        WHERE so.customer = %(c)s AND so.docstatus = 1
          AND so.transaction_date BETWEEN %(df)s AND %(dt)s
        GROUP BY soi.item_code, soi.item_name
        ORDER BY paid_qty DESC
    """, params, as_dict=True)
    for p in products:
        p["paid_qty"] = _f(p.get("paid_qty"))
        p["free_qty"] = _f(p.get("free_qty"))
        p["amount"] = _f(p.get("amount"))

    totals = {
        "paid_qty": sum(p["paid_qty"] for p in products),
        "free_qty": sum(p["free_qty"] for p in products),
        "value": sum(p["amount"] for p in products),
    }

    # Visits done, by rep (excluding cancelled).
    visits = frappe.db.sql("""
        SELECT sales_person, COUNT(*) AS cnt
        FROM `tabSFA Visit`
        WHERE customer = %(c)s AND IFNULL(status, '') != 'Cancelled'
          AND visit_date BETWEEN %(df)s AND %(dt)s
        GROUP BY sales_person ORDER BY cnt DESC
    """, params, as_dict=True)
    for v in visits:
        v["cnt"] = int(v.get("cnt") or 0)
    visits_total = sum(v["cnt"] for v in visits)

    # Forms filled.
    forms = frappe.db.sql("""
        SELECT form_template, COUNT(*) AS cnt
        FROM `tabSFA Form Response`
        WHERE customer = %(c)s
          AND DATE(response_date) BETWEEN %(df)s AND %(dt)s
        GROUP BY form_template ORDER BY cnt DESC
    """, params, as_dict=True)
    for f in forms:
        f["cnt"] = int(f.get("cnt") or 0)
    forms_total = sum(f["cnt"] for f in forms)

    # Cash payments by type (carton-mode excluded).
    cash = frappe.db.sql("""
        SELECT payment_type, COUNT(*) AS cnt, IFNULL(SUM(amount), 0) AS amt
        FROM `tabSFA Payment`
        WHERE customer = %(c)s AND IFNULL(status, '') != 'Cancelled'
          AND IFNULL(custom_payment_mode, 'Cash') != 'Cartons'
          AND payment_date BETWEEN %(df)s AND %(dt)s
        GROUP BY payment_type ORDER BY amt DESC
    """, params, as_dict=True)
    for r in cash:
        r["cnt"] = int(r.get("cnt") or 0)
        r["amt"] = _f(r.get("amt"))
    cash_total = sum(r["amt"] for r in cash)

    # Carton payments: count from parent; cartons total from the child table if
    # it exists (guarded so a missing table never breaks the summary).
    carton_count = frappe.db.count("SFA Payment", {
        "customer": customer,
        "custom_payment_mode": "Cartons",
        "status": ["!=", "Cancelled"],
        "payment_date": ["between", [df, dt]],
    })
    carton_total = None
    try:
        if frappe.db.table_exists("SFA Payment Carton Item"):
            res = frappe.db.sql("""
                SELECT IFNULL(SUM(ci.cartons), 0) AS cartons
                FROM `tabSFA Payment Carton Item` ci
                INNER JOIN `tabSFA Payment` p ON p.name = ci.parent
                WHERE p.customer = %(c)s AND p.custom_payment_mode = 'Cartons'
                  AND IFNULL(p.status, '') != 'Cancelled'
                  AND p.payment_date BETWEEN %(df)s AND %(dt)s
            """, params, as_dict=True)
            carton_total = _f(res[0].get("cartons")) if res else 0.0
    except Exception:
        carton_total = None

    return {
        "range": {"from": df, "to": dt},
        "products": products,
        "totals": totals,
        "visits": {"total": visits_total, "by_rep": visits},
        "forms": {"total": forms_total, "by_template": forms},
        "payments": {
            "cash_total": cash_total,
            "by_type": cash,
            "carton_count": int(carton_count or 0),
            "carton_total": carton_total,
        },
    }
