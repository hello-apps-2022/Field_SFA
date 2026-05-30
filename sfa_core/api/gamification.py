import frappe
from frappe import _

def _salespersons_in_territory(territory):
    """Sales Person names belonging to a territory (via custom_territory)."""
    if not territory:
        return None
    return frappe.get_all("Sales Person",
        filters={"custom_territory": territory}, pluck="name")


def _resolve_date_range(period=None, date_from=None, date_to=None):
    """Resolve a (start, end) date window from either a preset period or an
    explicit custom range. Explicit dates win over the preset. Returns
    (start_date, end_date) where either may be None (open-ended)."""
    from frappe.utils import getdate, add_months, add_days

    # Explicit custom range takes precedence.
    if date_from or date_to:
        return (getdate(date_from) if date_from else None,
                getdate(date_to) if date_to else None)

    if period == "month":
        return add_months(getdate(), -1), None
    if period == "quarter":
        return add_months(getdate(), -3), None
    return None, None  # all time


@frappe.whitelist()
def get_leaderboard(period=None, date_from=None, date_to=None, territory=None, limit=50):
    """Get points leaderboard, scoped by preset period or custom date range."""
    start_date, end_date = _resolve_date_range(period, date_from, date_to)

    conditions = []
    values = []
    if start_date:
        conditions.append("timestamp >= %s")
        values.append(start_date)
    if end_date:
        # inclusive of the end day
        conditions.append("DATE(timestamp) <= %s")
        values.append(end_date)
    if territory:
        sps = _salespersons_in_territory(territory)
        if not sps:
            return []
        placeholders = ", ".join(["%s"] * len(sps))
        conditions.append(f"sales_person IN ({placeholders})")
        values.extend(sps)
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    leaderboard = frappe.db.sql(f"""
        SELECT
            sales_person,
            SUM(points) as total_points,
            COUNT(DISTINCT reference_name) as activities
        FROM `tabSFA Rep Points Ledger`
        {where}
        GROUP BY sales_person
        ORDER BY total_points DESC
        LIMIT %s
    """, values + [int(limit)], as_dict=True)

    return leaderboard

@frappe.whitelist()
def get_rep_badges(sales_person):
    """Get badges for a sales person"""
    badges = frappe.get_all("SFA Rep Badge",
        filters={"sales_person": sales_person},
        fields=["name", "badge", "awarded_date", "awarded_by"],
        order_by="awarded_date desc")

    return badges

@frappe.whitelist()
def get_rep_points(sales_person):
    """Get total points for a sales person"""
    result = frappe.db.sql(
        "SELECT SUM(points) FROM `tabSFA Rep Points Ledger` WHERE sales_person = %s",
        (sales_person,)
    )
    total = result[0][0] or 0

    return {"sales_person": sales_person, "total_points": total}


# --- Admin: points config + badge management --------------------------------

def _require_admin():
    from sfa_core.api.auth import get_user_context
    ctx = get_user_context()
    if not ctx.get("is_admin"):
        frappe.throw(_("Only SFA Admins can manage gamification settings"), frappe.PermissionError)


@frappe.whitelist()
def get_points_config():
    """List all points config rows (admin editor)."""
    _require_admin()
    return frappe.get_all("SFA Points Config",
        fields=["name", "activity_type", "points", "multiplier_field", "description", "is_active"],
        order_by="activity_type asc")


@frappe.whitelist()
def save_points_config(activity_type, points, is_active=1, description=None, multiplier_field=None):
    """Create or update a points config row by activity_type (autonamed)."""
    _require_admin()
    if frappe.db.exists("SFA Points Config", activity_type):
        doc = frappe.get_doc("SFA Points Config", activity_type)
    else:
        doc = frappe.new_doc("SFA Points Config")
        doc.activity_type = activity_type
    doc.points = int(points)
    doc.is_active = int(is_active)
    if description is not None:
        doc.description = description
    if multiplier_field is not None:
        doc.multiplier_field = multiplier_field
    doc.save(ignore_permissions=True)
    return {"status": "success", "name": doc.name}


@frappe.whitelist()
def get_badges():
    """List all badge definitions (admin editor)."""
    _require_admin()
    return frappe.get_all("SFA Badge",
        fields=["name", "badge_name", "description", "icon", "criteria_type",
                "threshold_value", "period_days", "points_bonus", "is_active"],
        order_by="badge_name asc")


@frappe.whitelist()
def save_badge(badge_name, criteria_type, threshold_value, period_days=0,
               points_bonus=0, icon=None, description=None, is_active=1, name=None):
    """Create or update a badge definition."""
    _require_admin()
    if name and frappe.db.exists("SFA Badge", name):
        doc = frappe.get_doc("SFA Badge", name)
    elif frappe.db.exists("SFA Badge", badge_name):
        doc = frappe.get_doc("SFA Badge", badge_name)
    else:
        doc = frappe.new_doc("SFA Badge")
    doc.badge_name = badge_name
    doc.criteria_type = criteria_type
    doc.threshold_value = int(threshold_value)
    doc.period_days = int(period_days or 0)
    doc.points_bonus = int(points_bonus or 0)
    doc.is_active = int(is_active)
    if icon is not None:
        doc.icon = icon
    if description is not None:
        doc.description = description
    doc.save(ignore_permissions=True)
    return {"status": "success", "name": doc.name}


@frappe.whitelist()
def toggle_badge(name, is_active):
    """Enable/disable a badge."""
    _require_admin()
    frappe.db.set_value("SFA Badge", name, "is_active", int(is_active))
    return {"status": "success"}


@frappe.whitelist()
def get_points_ledger(search=None, period=None, date_from=None, date_to=None, territory=None, start=0, page_length=50):
    """Paginated points ledger (admin/manager view), scoped by date + territory."""
    from sfa_core.api.auth import get_scope_context as get_user_context
    ctx = get_user_context()
    filters = {}
    # Reps see only their own ledger
    if ctx.get("is_rep") and ctx.get("sales_person"):
        filters["sales_person"] = ctx["sales_person"]
    elif territory:
        sps = _salespersons_in_territory(territory)
        if not sps:
            return {"items": [], "total": 0}
        filters["sales_person"] = ["in", sps]

    s, e = _resolve_date_range(period, date_from, date_to)
    if s and e:
        filters["timestamp"] = ["between", [s, e]]
    elif s:
        filters["timestamp"] = [">=", s]
    elif e:
        filters["timestamp"] = ["<=", e]

    or_filters = None
    if search:
        or_filters = [["sales_person", "like", f"%{search}%"],
                      ["activity_type", "like", f"%{search}%"]]

    start = int(start)
    page_length = int(page_length)
    total = frappe.db.count("SFA Rep Points Ledger", filters=filters) if not or_filters else len(
        frappe.get_all("SFA Rep Points Ledger", filters=filters, or_filters=or_filters, fields=["name"]))

    rows = frappe.get_all("SFA Rep Points Ledger",
        filters=filters, or_filters=or_filters,
        fields=["name", "sales_person", "activity_type", "points", "balance", "timestamp", "description"],
        order_by="timestamp desc", start=start, page_length=page_length)
    return {"items": rows, "total": total}


@frappe.whitelist()
def get_earned_badges(period=None, date_from=None, date_to=None, territory=None):
    """Earned badges (SFA Rep Badge), scoped by awarded date, territory and role."""
    from sfa_core.api.auth import get_scope_context as get_user_context
    ctx = get_user_context()
    filters = {}
    if ctx.get("is_rep") and ctx.get("sales_person"):
        filters["sales_person"] = ctx["sales_person"]
    elif territory:
        sps = _salespersons_in_territory(territory)
        if not sps:
            return []
        filters["sales_person"] = ["in", sps]

    s, e = _resolve_date_range(period, date_from, date_to)
    if s and e:
        filters["awarded_date"] = ["between", [s, e]]
    elif s:
        filters["awarded_date"] = [">=", s]
    elif e:
        filters["awarded_date"] = ["<=", e]

    return frappe.get_all("SFA Rep Badge",
        filters=filters,
        fields=["name", "sales_person", "badge", "awarded_date", "awarded_by"],
        order_by="awarded_date desc", limit=200)
