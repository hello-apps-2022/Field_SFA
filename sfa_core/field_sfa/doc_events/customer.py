import frappe


def validate(doc, method):
    freq = getattr(doc, 'custom_visit_frequency', None)
    # Convert to int safely — empty string or None both become None
    if freq is not None and freq != '':
        try:
            if int(freq) < 0:
                frappe.throw("Visit frequency cannot be negative")
        except (ValueError, TypeError):
            pass


def after_insert(doc, method):
    pass


def on_update(doc, method):
    pass
