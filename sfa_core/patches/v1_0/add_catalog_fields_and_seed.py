import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

COMPANIES = [
    "Hema Beverages Limited",
    "Nutricom Food & Beverages Limited",
    "United Beverages Limited",
]

CATEGORIES = ["Water", "Carbonated Drinks", "Fermented Drinks", "Spirits"]

# (item_name, category, company, size, packaging, pack_config)
PRODUCTS = [
    ("Hema Water 550ml Shrink Wrap", "Water", "Hema Beverages Limited", "550ml", "Shrink Wrap", "12pack*2 shrink"),
    ("Hema Water 1.5L Shrink Wrap", "Water", "Hema Beverages Limited", "1.5L", "Shrink Wrap", "6 Pack*2 shrink"),
    ("Hema Water 1.5L", "Water", "Hema Beverages Limited", "1.5L", "Pack", "12 Pack"),
    ("Hema Water 1.5L Box", "Water", "Hema Beverages Limited", "1.5L", "Box", "12 Pack"),
    ("Hema Water 550ml Box", "Water", "Hema Beverages Limited", "550ml", "Box", "24 Pack"),
    ("Cheetah Energy", "Carbonated Drinks", "Hema Beverages Limited", "", "", ""),
    ("Leo 12 Pack", "Fermented Drinks", "Nutricom Food & Beverages Limited", "", "", "12 Pack"),
    ("Leo 18 Pack", "Fermented Drinks", "Nutricom Food & Beverages Limited", "", "", "18 Pack"),
    ("Leo 24 Pack", "Fermented Drinks", "Nutricom Food & Beverages Limited", "", "", "24 Pack"),
    ("Jajja Alcoholic", "Fermented Drinks", "Nutricom Food & Beverages Limited", "", "", ""),
    ("Jajja Non-Alcoholic", "Fermented Drinks", "Nutricom Food & Beverages Limited", "", "", ""),
    ("Farmers Kombucha", "Fermented Drinks", "United Beverages Limited", "", "", ""),
    ("El Salvador 200ml", "Spirits", "Hema Beverages Limited", "200ml", "", ""),
    ("El Salvador 100ml", "Spirits", "Hema Beverages Limited", "100ml", "", ""),
    ("Haveon 200ml", "Spirits", "Hema Beverages Limited", "200ml", "", ""),
    ("Rider 200ml", "Spirits", "Hema Beverages Limited", "200ml", "", ""),
    ("Goal 200ml", "Spirits", "Hema Beverages Limited", "200ml", "", ""),
    ("K'Wa 200ml", "Spirits", "Hema Beverages Limited", "200ml", "", ""),
]


def execute():
    _add_item_fields()
    frappe.reload_doc("field_sfa", "doctype", "sfa_company")
    _seed_companies()
    _seed_categories()
    _seed_products()
    frappe.db.commit()


def _add_item_fields():
    create_custom_fields({
        "Item": [
            {"fieldname": "custom_sfa_company", "label": "SFA Company", "fieldtype": "Link",
             "options": "SFA Company", "insert_after": "item_group"},
            {"fieldname": "custom_size", "label": "Size", "fieldtype": "Data",
             "insert_after": "custom_sfa_company"},
            {"fieldname": "custom_packaging", "label": "Packaging", "fieldtype": "Data",
             "insert_after": "custom_size"},
            {"fieldname": "custom_pack_config", "label": "Pack Config", "fieldtype": "Data",
             "insert_after": "custom_packaging"},
        ]
    }, ignore_validate=True)
    frappe.db.commit()


def _seed_companies():
    for c in COMPANIES:
        if not frappe.db.exists("SFA Company", c):
            frappe.get_doc({"doctype": "SFA Company", "company_name": c, "enabled": 1}).insert(ignore_permissions=True)
            print("  + SFA Company: " + c)


def _seed_categories():
    root = frappe.db.get_value("Item Group", {"is_group": 1, "parent_item_group": ""}, "name") or "All Item Groups"
    for cat in CATEGORIES:
        if not frappe.db.exists("Item Group", cat):
            frappe.get_doc({"doctype": "Item Group", "item_group_name": cat,
                            "parent_item_group": root, "is_group": 0}).insert(ignore_permissions=True)
            print("  + Item Group: " + cat)


def _seed_products():
    for (name, cat, company, size, packaging, pack) in PRODUCTS:
        if frappe.db.exists("Item", {"item_name": name}) or frappe.db.exists("Item", name):
            continue
        doc = frappe.get_doc({
            "doctype": "Item",
            "item_code": name,
            "item_name": name,
            "item_group": cat,
            "stock_uom": "Nos",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "standard_rate": 0,
            "custom_sfa_company": company,
            "custom_size": size or None,
            "custom_packaging": packaging or None,
            "custom_pack_config": pack or None,
        })
        doc.insert(ignore_permissions=True)
        print("  + Item: " + name)
