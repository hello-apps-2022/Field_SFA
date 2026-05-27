import frappe


def validate(doc, method):
    if getattr(doc, 'custom_visit_frequency', None) and doc.custom_visit_frequency < 0:
        frappe.throw("Visit frequency cannot be negative")


def after_insert(doc, method):
    pass


def on_update(doc, method):
    pass
