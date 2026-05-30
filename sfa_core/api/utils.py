import frappe
import json
from sfa_core.api.auth import get_user_context


@frappe.whitelist()
def save_doc(doc):
    """Save a document bypassing timestamp mismatch check."""
    if isinstance(doc, str):
        doc = json.loads(doc)

    doctype = doc.get('doctype')
    name = doc.get('name')

    if not doctype: frappe.throw("doctype is required")
    if not name: frappe.throw("name is required")

    d = frappe.get_doc(doctype, name)

    SKIP = {
        'name', 'doctype', 'modified', 'modified_by', 'creation',
        'owner', 'naming_series', 'amended_from', 'docstatus',
        'idx', '__islocal', '__unsaved', '__run_link_triggers',
        '__last_sync_on', 'meta', 'flags',
    }

    for key, value in doc.items():
        if key in SKIP:
            continue
        if hasattr(d, key):
            try:
                if isinstance(value, list):
                    d.set(key, value)
                else:
                    setattr(d, key, value)
            except Exception:
                pass

    d.flags.ignore_version = True
    d.save(ignore_permissions=False)
    frappe.db.commit()
    return d.as_dict()


@frappe.whitelist()
def insert_doc(doc):
    """
    Insert a new document with automatic rep assignment.
    For SFA Visit and SFA Payment, auto-sets sales_person to
    the logged-in user's Sales Person if not provided.
    """
    if isinstance(doc, str):
        doc = json.loads(doc)

    doctype = doc.get('doctype')
    if not doctype:
        frappe.throw("doctype is required")

    # Auto-assign sales_person for visit/payment if not set
    if doctype in ('SFA Visit', 'SFA Payment'):
        if not doc.get('sales_person'):
            ctx = get_user_context()
            if ctx.get('sales_person'):
                doc['sales_person'] = ctx['sales_person']

    d = frappe.get_doc(doc)
    d.insert(ignore_permissions=False)
    frappe.db.commit()
    return d.as_dict()
