import frappe

@frappe.whitelist()
def duplicate_form_template(template_name):
    if not template_name:
        frappe.throw("Template name required")

    original = frappe.get_doc("SFA Form Template", template_name)
    new_doc = frappe.copy_doc(original)
    new_doc.template_name = f"{original.template_name} (Copy)"
    new_doc.insert()
    return new_doc.name
