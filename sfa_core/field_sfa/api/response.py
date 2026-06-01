import functools

import frappe
from frappe.utils import strip_html_tags


def _clean(exc, default):
    try:
        text = strip_html_tags(str(exc) or "").strip()
    except Exception:
        text = (str(exc) or "").strip()
    return text or default


def _envelope(code, message, http_status):
    frappe.local.response["http_status_code"] = http_status
    return {"error": {"code": code, "message": message}}


def mobile_api(fn):
    """Wrap a whitelisted mobile endpoint so failures return a uniform JSON
    error envelope -- {"error": {"code", "message"}} -- with a matching HTTP
    status, instead of Frappe's default HTML / _server_messages payload.

    Only the OUTERMOST wrapped call in a request produces an envelope. When one
    wrapped endpoint calls another internally (e.g. sync push routes through the
    typed create endpoints), the inner call is transparent: it raises normally
    so the caller's own per-record error handling and savepoints still work.
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        depth = getattr(frappe.local, "_mobile_api_depth", 0)
        if depth:
            return fn(*args, **kwargs)
        frappe.local._mobile_api_depth = 1
        try:
            return fn(*args, **kwargs)
        except frappe.PermissionError as e:
            frappe.db.rollback()
            return _envelope("PERMISSION", _clean(e, "You are not permitted to do this."), 403)
        except frappe.DoesNotExistError as e:
            frappe.db.rollback()
            return _envelope("NOT_FOUND", _clean(e, "Not found."), 404)
        except frappe.DuplicateEntryError as e:
            frappe.db.rollback()
            return _envelope("CONFLICT", _clean(e, "This record already exists."), 409)
        except frappe.ValidationError as e:
            frappe.db.rollback()
            return _envelope("VALIDATION", _clean(e, "Validation failed."), 417)
        except Exception:
            frappe.db.rollback()
            frappe.log_error(title="Field SFA mobile API error", message=frappe.get_traceback())
            return _envelope("SERVER", "Something went wrong. Please try again.", 500)
        finally:
            frappe.local._mobile_api_depth = 0
    return wrapper
