import frappe
import json


@frappe.whitelist()
def save_doc(doc):
    """
    Save a document without timestamp mismatch check.
    Used by SFA frontend to avoid TimestampMismatchError
    from after_save hooks that bump modified.
    """
    if isinstance(doc, str):
        doc = json.loads(doc)

    doctype = doc.get('doctype')
    name = doc.get('name')

    if not doctype or not name:
        frappe.throw("doctype and name are required")

    d = frappe.get_doc(doctype, name)

    # Fields to never overwrite from client
    skip = {
        'name', 'doctype', 'modified', 'modified_by', 'creation',
        'owner', 'naming_series', 'amended_from', 'docstatus',
        'idx', '__islocal', '__unsaved',
    }

    for key, value in doc.items():
        if key not in skip:
            try:
                setattr(d, key, value)
            except Exception:
                pass

    d.flags.ignore_version = True
    d.save(ignore_permissions=False)
    frappe.db.commit()
    return d.as_dict()
