import frappe
from frappe import _
from frappe.utils import cint
from sfa_core.api.auth import resolve_sales_person
from sfa_core.field_sfa.api.response import mobile_api

# Sync doctypes that carry custom_client_uuid and a rep field to authorize against.
_REP_FIELD = {
    "SFA Visit": "sales_person",
    "SFA Form Response": "sales_person",
    "Sales Order": "custom_sfa_rep",
    "SFA Payment": "sales_person",
}


@frappe.whitelist()
@mobile_api
def upload_image(parent_doctype, parent_client_uuid, file_name, content, is_private=1):
    """Attach a base64-encoded image to a synced record, located by the
    parent's offline client id (custom_client_uuid).

    parent_doctype      one of the sync doctypes in _REP_FIELD
    parent_client_uuid  offline client id of the record the photo belongs to
    file_name           stable per-image name (used for idempotent retries)
    content             base64-encoded file bytes
    is_private          1 (default) keeps the file private

    Idempotent on (parent, file_name): a retry with the same file_name returns
    the existing file instead of creating a duplicate, so the app should use a
    stable name (e.g. embed the image's local id).
    """
    if parent_doctype not in _REP_FIELD:
        frappe.throw(_("Cannot attach images to {0}.").format(parent_doctype),
                     frappe.PermissionError)

    rep = resolve_sales_person(None)
    rep_field = _REP_FIELD[parent_doctype]
    parent = frappe.db.get_value(
        parent_doctype, {"custom_client_uuid": parent_client_uuid},
        ["name", rep_field], as_dict=True)
    if not parent:
        frappe.throw(
            _("{0} for client id {1} not found.").format(parent_doctype, parent_client_uuid),
            frappe.DoesNotExistError)
    if rep and parent.get(rep_field) != rep:
        frappe.throw(_("You can only attach images to your own records."),
                     frappe.PermissionError)

    dupe = frappe.db.get_value(
        "File",
        {"attached_to_doctype": parent_doctype, "attached_to_name": parent.name,
         "file_name": file_name},
        ["name", "file_url"], as_dict=True)
    if dupe:
        return {"name": dupe.name, "file_url": dupe.file_url, "status": "duplicate"}

    f = frappe.get_doc({
        "doctype": "File",
        "file_name": file_name,
        "attached_to_doctype": parent_doctype,
        "attached_to_name": parent.name,
        "is_private": cint(is_private),
        "content": content,
        "decode": True,
    })
    f.insert(ignore_permissions=True)
    return {"name": f.name, "file_url": f.file_url, "status": "uploaded"}
