import frappe


def validate(doc, method):
    freq = getattr(doc, 'custom_visit_frequency', None)
    if freq is not None and freq < 0:
        frappe.throw("Visit frequency cannot be negative")


def after_insert(doc, method):
    pass


def on_update(doc, method):
    pass
