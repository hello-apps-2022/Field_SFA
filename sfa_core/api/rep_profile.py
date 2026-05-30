import frappe
from frappe.utils import flt, today, get_first_day
from sfa_core.api.auth import get_user_context


def _gate(ctx, sales_person):
    # Admin: any. Manager: own territory or self. Rep: self only.
    if ctx.get("is_admin"):
        return
    if ctx.get("sales_person") and ctx["sales_person"] == sales_person:
        return
    if ctx.get("is_manager"):
        terr = frappe.db.get_value("Sales Person", sales_person, "custom_territory")
        if terr and terr == ctx.get("territory"):
            return
    frappe.throw("You do not have permission to view this profile", frappe.PermissionError)


@frappe.whitelist()
def get_rep_profile(sales_person, date_from=None, date_to=None):
    ctx = get_user_context()
    _gate(ctx, sales_person)

    ranged = bool(date_from and date_to)
    win_from = str(date_from) if ranged else str(get_first_day(today()))
    win_to = str(date_to) if ranged else str(today())

    sp = frappe.db.get_value(
        "Sales Person", sales_person,
        ["name", "sales_person_name", "custom_user_id", "custom_territory",
         "custom_mobile_no", "custom_sfa_active", "custom_employee",
         "custom_last_seen", "custom_last_latitude", "custom_last_longitude",
         "parent_sales_person"],
        as_dict=True,
    )
    if not sp:
        frappe.throw("Sales Person not found")

    role, user = None, None
    if sp.custom_user_id:
        user = frappe.db.get_value(
            "User", sp.custom_user_id,
            ["name", "full_name", "email", "enabled", "user_image",
             "custom_can_export_reports"],
            as_dict=True,
        )
        if user:
            roles = frappe.get_roles(sp.custom_user_id)
            for rname in ("SFA Admin", "SFA Manager", "SFA Rep"):
                if rname in roles:
                    role = rname
                    break

    companies = frappe.get_all(
        "SFA Sales Person Company",
        filters={"parent": sales_person, "parenttype": "Sales Person"},
        fields=["company"], pluck="company",
    )

    manager_name = None
    if sp.parent_sales_person and sp.parent_sales_person != "Sales Team":
        manager_name = frappe.db.get_value(
            "Sales Person", sp.parent_sales_person, "sales_person_name"
        ) or sp.parent_sales_person

    employee_name = None
    if sp.custom_employee:
        employee_name = frappe.db.get_value("Employee", sp.custom_employee, "employee_name")

    points = frappe.db.sql(
        "SELECT IFNULL(SUM(points),0) FROM `tabSFA Rep Points Ledger` WHERE sales_person=%s",
        (sales_person,),
    )[0][0] or 0
    badges = frappe.get_all(
        "SFA Rep Badge", filters={"sales_person": sales_person},
        fields=["badge", "awarded_date"], order_by="awarded_date desc", limit=12,
    )

    profile = {
        "sales_person": sp.name,
        "sales_person_name": sp.sales_person_name,
        "full_name": (user.full_name if user else sp.sales_person_name),
        "email": (user.email if user else sp.custom_user_id),
        "user_id": sp.custom_user_id,
        "user_image": (user.user_image if user else None),
        "enabled": (user.enabled if user else 0),
        "role": role,
        "territory": sp.custom_territory,
        "mobile_no": sp.custom_mobile_no,
        "sfa_active": sp.custom_sfa_active,
        "last_seen": sp.custom_last_seen,
        "last_latitude": sp.custom_last_latitude,
        "last_longitude": sp.custom_last_longitude,
        "reports_to": (sp.parent_sales_person if sp.parent_sales_person != "Sales Team" else None),
        "manager_name": manager_name,
        "employee": sp.custom_employee,
        "employee_name": employee_name,
        "companies": companies,
        "can_export_reports": bool(user.custom_can_export_reports) if user else False,
        "points": int(points),
        "badges": badges,
    }

    vis = frappe.db.sql("""
        SELECT COUNT(*) total,
               SUM(CASE WHEN status='Completed' THEN 1 ELSE 0 END) completed
        FROM `tabSFA Visit`
        WHERE sales_person=%s AND visit_date BETWEEN %s AND %s AND status!='Cancelled'
    """, (sales_person, win_from, win_to), as_dict=True)[0]

    omtd = frappe.db.sql("""
        SELECT COUNT(*) orders, IFNULL(SUM(grand_total),0) revenue
        FROM `tabSales Order`
        WHERE custom_sfa_rep=%s AND transaction_date BETWEEN %s AND %s AND docstatus<2
    """, (sales_person, win_from, win_to), as_dict=True)[0]

    free_mtd = frappe.db.sql("""
        SELECT IFNULL(SUM(soi.qty),0) free_qty
        FROM `tabSales Order Item` soi
        INNER JOIN `tabSales Order` o ON o.name=soi.parent
        WHERE o.custom_sfa_rep=%s AND o.transaction_date BETWEEN %s AND %s
          AND o.docstatus<2 AND soi.is_free_item=1
    """, (sales_person, win_from, win_to), as_dict=True)[0]

    pay_mtd = frappe.db.sql("""
        SELECT IFNULL(SUM(amount),0) amt
        FROM `tabSFA Payment`
        WHERE sales_person=%s AND payment_date BETWEEN %s AND %s AND status!='Cancelled'
    """, (sales_person, win_from, win_to), as_dict=True)[0]

    new_cust_mtd = frappe.db.count("Customer", {
        "custom_sfa_rep": sales_person,
        "creation": ["between", [win_from + " 00:00:00", win_to + " 23:59:59"]],
    })

    kpis = {
        "visits": vis.total or 0,
        "visits_completed": vis.completed or 0,
        "orders": omtd.orders or 0,
        "revenue": flt(omtd.revenue),
        "free_qty": flt(free_mtd.free_qty),
        "payments": flt(pay_mtd.amt),
        "new_customers": new_cust_mtd,
    }

    vfilters = {"sales_person": sales_person}
    if ranged:
        vfilters["visit_date"] = ["between", [win_from, win_to]]
    visits = frappe.get_all(
        "SFA Visit", filters=vfilters,
        fields=["name", "customer", "visit_date", "status", "visit_purpose",
                "check_in_time", "check_out_time", "duration_minutes"],
        order_by="visit_date desc, check_in_time desc", limit=200,
    )

    o_params = [sales_person]
    o_date = ""
    if ranged:
        o_date = "AND o.transaction_date BETWEEN %s AND %s"
        o_params += [win_from, win_to]
    orders = frappe.db.sql("""
        SELECT o.name, o.customer, o.transaction_date, o.docstatus, o.status, o.grand_total,
               IFNULL(SUM(CASE WHEN soi.is_free_item=1 THEN soi.qty ELSE 0 END),0) free_qty,
               IFNULL(SUM(CASE WHEN soi.is_free_item=1 THEN 0 ELSE soi.amount END),0) paid_total
        FROM `tabSales Order` o
        LEFT JOIN `tabSales Order Item` soi ON soi.parent=o.name
        WHERE o.custom_sfa_rep=%s {date}
        GROUP BY o.name
        ORDER BY o.transaction_date DESC, o.creation DESC
        LIMIT 200
    """.format(date=o_date), tuple(o_params), as_dict=True)
    _ds = {0: "Draft", 1: "Submitted", 2: "Cancelled"}
    for o in orders:
        o["doc_status"] = _ds.get(o.get("docstatus"), "")

    pfilters = {"sales_person": sales_person}
    if ranged:
        pfilters["payment_date"] = ["between", [win_from, win_to]]
    payments = frappe.get_all(
        "SFA Payment", filters=pfilters,
        fields=["name", "customer", "payment_date", "amount", "payment_type", "status"],
        order_by="payment_date desc", limit=200,
    )

    performance = _performance(sales_person)

    leave = {"items": [], "pending": 0, "approved": 0}
    expenses = {"items": [], "claimed": 0, "sanctioned": 0}
    if sp.custom_employee:
        lf = {"employee": sp.custom_employee}
        if ranged:
            lf["from_date"] = ["between", [win_from, win_to]]
        litems = frappe.get_all(
            "Leave Application", filters=lf,
            fields=["name", "leave_type", "from_date", "to_date", "total_leave_days",
                    "status", "workflow_state"],
            order_by="from_date desc", limit=100,
        )
        leave["items"] = litems
        _closed = ("Approved", "Rejected", "Cancelled")
        leave["pending"] = sum(1 for l in litems if (l.get("workflow_state") or l.get("status")) not in _closed)
        leave["approved"] = sum(1 for l in litems if (l.get("workflow_state") or l.get("status")) == "Approved")

        ef = {"employee": sp.custom_employee}
        if ranged:
            ef["posting_date"] = ["between", [win_from, win_to]]
        eitems = frappe.get_all(
            "Expense Claim", filters=ef,
            fields=["name", "posting_date", "total_claimed_amount",
                    "total_sanctioned_amount", "approval_status"],
            order_by="posting_date desc", limit=100,
        )
        expenses["items"] = eitems
        expenses["claimed"] = sum(flt(e.get("total_claimed_amount")) for e in eitems)
        expenses["sanctioned"] = sum(flt(e.get("total_sanctioned_amount")) for e in eitems)

    return {
        "profile": profile,
        "kpis": kpis,
        "range": {"from": win_from, "to": win_to, "ranged": ranged},
        "visits": visits,
        "orders": orders,
        "payments": payments,
        "performance": performance,
        "leave": leave,
        "expenses": expenses,
    }


def _performance(sales_person):
    # Rep's target row from their target set (Active preferred, else most recent),
    # actuals computed exactly like the Targets page so the numbers match.
    rows = frappe.get_all(
        "SFA Target Set Rep", filters={"sales_person": sales_person},
        fields=["parent", "target_visits", "target_revenue",
                "target_new_customers", "target_compliance_pct"],
    )
    if not rows:
        return {"has_targets": False}

    sets = {}
    for r in rows:
        s = frappe.db.get_value(
            "SFA Target Set", r["parent"],
            ["name", "target_set_name", "date_from", "date_to", "status"],
            as_dict=True,
        )
        if s:
            s["row"] = r
            sets[s["name"]] = s
    if not sets:
        return {"has_targets": False}

    chosen = None
    for s in sets.values():
        if s["status"] == "Active":
            if not chosen or str(s["date_from"]) > str(chosen["date_from"]):
                chosen = s
    if not chosen:
        chosen = sorted(sets.values(), key=lambda x: str(x["date_from"]), reverse=True)[0]

    r = chosen["row"]
    df, dt = str(chosen["date_from"]), str(chosen["date_to"])

    act = frappe.db.sql("""
        SELECT COUNT(*) visits,
               SUM(CASE WHEN status='Completed' THEN 1 ELSE 0 END) completed
        FROM `tabSFA Visit`
        WHERE sales_person=%s AND visit_date BETWEEN %s AND %s AND status!='Cancelled'
    """, (sales_person, df, dt), as_dict=True)[0]

    rev = frappe.db.sql("""
        SELECT IFNULL(SUM(o.grand_total),0) total
        FROM `tabSales Order` o
        INNER JOIN `tabCustomer` c ON c.name=o.customer
        WHERE c.custom_sfa_rep=%s AND DATE(o.transaction_date) BETWEEN %s AND %s
          AND o.docstatus=1
    """, (sales_person, df, dt), as_dict=True)[0].total or 0

    newc = frappe.db.count("Customer", {
        "custom_sfa_rep": sales_person,
        "creation": ["between", [df + " 00:00:00", dt + " 23:59:59"]],
    })

    return {
        "has_targets": True,
        "period_name": chosen["target_set_name"],
        "date_from": df, "date_to": dt, "status": chosen["status"],
        "target_visits": r["target_visits"] or 0,
        "actual_visits": act.completed or 0,
        "target_revenue": flt(r["target_revenue"]),
        "actual_revenue": flt(rev),
        "target_new_customers": r["target_new_customers"] or 0,
        "actual_new_customers": newc,
        "target_compliance_pct": r["target_compliance_pct"] or 0,
        "actual_compliance_pct": round((act.completed / act.visits * 100) if act.visits else 0),
    }
