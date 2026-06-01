import frappe
from sfa_core.field_sfa.api.response import mobile_api
from frappe.utils import nowdate

_FIELDS = ["name", "target_type", "customer", "territory",
           "buy_item", "buy_qty", "free_item", "free_qty",
           "valid_from", "valid_to", "enabled"]


def _scheme_targets(names):
    # -> {scheme_name: {"customers": [...], "territories": [...]}}
    out = {n: {"customers": [], "territories": []} for n in names}
    if not names:
        return out
    names = list(names)
    for r in frappe.get_all("SFA Free Carton Scheme Customer",
                            filters={"parent": ["in", names]},
                            fields=["parent", "customer"], ignore_permissions=True):
        out.setdefault(r.parent, {"customers": [], "territories": []})["customers"].append(r.customer)
    for r in frappe.get_all("SFA Free Carton Scheme Territory",
                            filters={"parent": ["in", names]},
                            fields=["parent", "territory"], ignore_permissions=True):
        out.setdefault(r.parent, {"customers": [], "territories": []})["territories"].append(r.territory)
    return out


def _legacy_fallback(row, custs, terrs):
    # old single-target schemes (no child rows) keep working
    if custs or terrs:
        return custs, terrs
    if row.get("target_type") == "Customer" and row.get("customer"):
        return [row["customer"]], []
    if row.get("target_type") == "Territory" and row.get("territory"):
        return [], [row["territory"]]
    return custs, terrs


@frappe.whitelist()
@mobile_api
def get_free_carton_schemes(customer):
    # Active schemes applying to a customer directly or via its territory.
    if not customer:
        return []
    territory = frappe.db.get_value("Customer", customer, "territory")
    today = nowdate()
    schemes = frappe.get_all(
        "SFA Free Carton Scheme",
        filters={"enabled": 1, "valid_from": ["<=", today], "valid_to": [">=", today]},
        fields=_FIELDS, ignore_permissions=True,
    )
    if not schemes:
        return []
    targets = _scheme_targets([s.name for s in schemes])
    out = []
    for s in schemes:
        t = targets.get(s.name, {"customers": [], "territories": []})
        custs, terrs = _legacy_fallback(s, t["customers"], t["territories"])
        if customer in custs or (territory and territory in terrs):
            out.append(s)
    return out


def free_entitlement_for_order(customer, paid_qty_map):
    # {item_code: total_paid_qty} -> {free_item: entitled_free_qty}
    entitled = {}
    if not customer:
        return entitled
    for s in get_free_carton_schemes(customer):
        bought = paid_qty_map.get(s["buy_item"], 0)
        if s["buy_qty"]:
            multiples = int(bought // s["buy_qty"])
            if multiples > 0:
                entitled[s["free_item"]] = entitled.get(s["free_item"], 0) + multiples * (s["free_qty"] or 0)
    return entitled


@frappe.whitelist()
@mobile_api
def get_schemes():
    # CRUD-screen list, each row enriched with its customer/territory lists.
    rows = frappe.get_list(
        "SFA Free Carton Scheme",
        fields=_FIELDS + ["modified"],
        order_by="modified desc", limit_page_length=500,
    )
    targets = _scheme_targets([r.name for r in rows])
    for r in rows:
        t = targets.get(r.name, {"customers": [], "territories": []})
        custs, terrs = _legacy_fallback(r, t["customers"], t["territories"])
        r["customers"] = custs
        r["territories"] = terrs
    return rows


def _norm_list(val):
    if isinstance(val, str):
        try:
            val = frappe.parse_json(val)
        except Exception:
            val = [v.strip() for v in val.split(",") if v.strip()]
    return [v for v in (val or []) if v]


@frappe.whitelist()
@mobile_api
def save_scheme(data):
    if isinstance(data, str):
        data = frappe.parse_json(data)
    customers = _norm_list(data.get("customers"))
    territories = _norm_list(data.get("territories"))
    if not customers and not territories:
        frappe.throw("Select at least one customer or territory.")

    name = data.get("name")
    doc = frappe.get_doc("SFA Free Carton Scheme", name) if name else frappe.new_doc("SFA Free Carton Scheme")
    doc.target_type = "Customer" if customers else "Territory"
    doc.customer = customers[0] if (customers and not territories) else None
    doc.territory = territories[0] if (territories and not customers) else None
    doc.buy_item = data.get("buy_item")
    doc.buy_qty = data.get("buy_qty")
    doc.free_item = data.get("free_item")
    doc.free_qty = data.get("free_qty")
    doc.valid_from = data.get("valid_from")
    doc.valid_to = data.get("valid_to")
    doc.enabled = 1 if data.get("enabled") else 0
    doc.set("customers", [{"customer": c} for c in customers])
    doc.set("territories", [{"territory": t} for t in territories])
    doc.save()
    frappe.db.commit()
    return doc.name


@frappe.whitelist()
@mobile_api
def delete_scheme(name):
    frappe.delete_doc("SFA Free Carton Scheme", name)
    frappe.db.commit()
    return True


@frappe.whitelist()
@mobile_api
def get_free_carton_policy():
    return {"allow_discretionary_free": bool(frappe.db.get_single_value("SFA Brand Settings", "allow_discretionary_free"))}


@frappe.whitelist()
@mobile_api
def set_free_carton_policy(allow):
    from sfa_core.api.auth import require_role
    require_role("SFA Admin", "SFA Manager")
    val = 1 if str(allow).lower() in ("1", "true", "yes") else 0
    frappe.db.set_single_value("SFA Brand Settings", "allow_discretionary_free", val)
    frappe.db.commit()
    return {"allow_discretionary_free": bool(val)}
