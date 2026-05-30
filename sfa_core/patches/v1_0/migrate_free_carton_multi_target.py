import frappe


def execute():
    frappe.reload_doc("field_sfa", "doctype", "sfa_free_carton_scheme_customer")
    frappe.reload_doc("field_sfa", "doctype", "sfa_free_carton_scheme_territory")
    frappe.reload_doc("field_sfa", "doctype", "sfa_free_carton_scheme")
    for s in frappe.get_all("SFA Free Carton Scheme",
                            fields=["name", "target_type", "customer", "territory"]):
        doc = frappe.get_doc("SFA Free Carton Scheme", s.name)
        changed = False
        if not doc.get("customers") and s.target_type == "Customer" and s.customer:
            doc.append("customers", {"customer": s.customer}); changed = True
        if not doc.get("territories") and s.target_type == "Territory" and s.territory:
            doc.append("territories", {"territory": s.territory}); changed = True
        if changed:
            doc.save(ignore_permissions=True)
    frappe.db.commit()
