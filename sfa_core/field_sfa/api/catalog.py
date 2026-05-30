import frappe
from sfa_core.api.auth import get_user_context


def _require_manager():
    ctx = get_user_context()
    if not (ctx.get("is_admin") or ctx.get("is_manager")):
        frappe.throw("Not permitted to manage the catalog.", frappe.PermissionError)
    return ctx


# ── Companies ───────────────────────────────────────────────────────────────
@frappe.whitelist()
def get_companies():
    return frappe.get_all("SFA Company", fields=["name", "company_name", "enabled"],
                          order_by="company_name asc", ignore_permissions=True)


@frappe.whitelist()
def save_company(company_name, enabled=1, name=None):
    _require_manager()
    if name:
        doc = frappe.get_doc("SFA Company", name)
        doc.company_name = company_name
        doc.enabled = int(enabled)
        doc.save(ignore_permissions=True)
    else:
        doc = frappe.get_doc({"doctype": "SFA Company", "company_name": company_name, "enabled": int(enabled)})
        doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return doc.name


@frappe.whitelist()
def delete_company(name):
    _require_manager()
    frappe.delete_doc("SFA Company", name, ignore_permissions=True)
    frappe.db.commit()


# ── Categories (ERPNext Item Groups) ─────────────────────────────────────────
@frappe.whitelist()
def get_categories():
    return frappe.get_all("Item Group", filters={"is_group": 0}, fields=["name"],
                          order_by="name asc", ignore_permissions=True)


@frappe.whitelist()
def save_category(category_name, name=None):
    _require_manager()
    if name and name != category_name:
        frappe.rename_doc("Item Group", name, category_name, ignore_permissions=True)
        frappe.db.commit()
        return category_name
    if not name and not frappe.db.exists("Item Group", category_name):
        root = frappe.db.get_value("Item Group", {"is_group": 1, "parent_item_group": ""}, "name") or "All Item Groups"
        doc = frappe.get_doc({"doctype": "Item Group", "item_group_name": category_name,
                              "parent_item_group": root, "is_group": 0})
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return doc.name
    return name or category_name


# ── Products (ERPNext Items) ─────────────────────────────────────────────────
@frappe.whitelist()
def get_products(search=None):
    filters = {"is_sales_item": 1}
    if search:
        filters["item_name"] = ["like", "%" + search + "%"]
    return frappe.get_all(
        "Item", filters=filters,
        fields=["name", "item_name", "item_group", "custom_sfa_company",
                "custom_size", "custom_packaging", "custom_pack_config",
                "standard_rate", "disabled"],
        order_by="item_name asc", limit_page_length=0, ignore_permissions=True)


@frappe.whitelist()
def save_product(item_name, item_group, custom_sfa_company=None, custom_size=None,
                 custom_packaging=None, custom_pack_config=None, standard_rate=0,
                 name=None, stock_uom="Nos"):
    _require_manager()
    fields = {
        "item_name": item_name,
        "item_group": item_group,
        "custom_sfa_company": custom_sfa_company or None,
        "custom_size": custom_size or None,
        "custom_packaging": custom_packaging or None,
        "custom_pack_config": custom_pack_config or None,
        "standard_rate": standard_rate or 0,
    }
    if name:
        doc = frappe.get_doc("Item", name)
        for k, v in fields.items():
            setattr(doc, k, v)
        doc.save(ignore_permissions=True)
    else:
        doc = frappe.get_doc({
            "doctype": "Item",
            "item_code": item_name,
            "is_stock_item": 0,
            "is_sales_item": 1,
            "stock_uom": stock_uom or "Nos",
            **fields,
        })
        doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return doc.name


@frappe.whitelist()
def delete_product(name):
    """Disable rather than hard-delete — orders may reference the item."""
    _require_manager()
    frappe.db.set_value("Item", name, "disabled", 1)
    frappe.db.commit()
