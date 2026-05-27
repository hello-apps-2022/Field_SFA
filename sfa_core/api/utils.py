import frappe
import json


@frappe.whitelist()
def save_doc(doc):
    """
    Save a document bypassing timestamp mismatch check.
    Works for any doctype — uses the document's own attribute presence
    to determine which fields to set.
    """
    if isinstance(doc, str):
        doc = json.loads(doc)

    doctype = doc.get('doctype')
    name = doc.get('name')

    if not doctype:
        frappe.throw("doctype is required")
    if not name:
        frappe.throw("name is required")

    d = frappe.get_doc(doctype, name)

    # Fields that must never be overwritten from the client
    SKIP = {
        'name', 'doctype', 'modified', 'modified_by', 'creation',
        'owner', 'naming_series', 'amended_from', 'docstatus',
        'idx', '__islocal', '__unsaved', '__run_link_triggers',
        '__last_sync_on', 'meta', 'flags',
    }

    for key, value in doc.items():
        if key in SKIP:
            continue
        # Use hasattr to check whether this field exists on the loaded document
        # This covers all fieldtypes including standard ERPNext fields + custom fields
        if hasattr(d, key):
            try:
                setattr(d, key, value)
            except Exception:
                pass

    d.flags.ignore_version = True
    d.save(ignore_permissions=False)
    frappe.db.commit()
    return d.as_dict()
