/**
 * Frappe API client — CSRF token from window.frappe_boot
 */

export function getCsrfToken() {
  return window.frappe_boot?.csrf_token || 'fetch'
}

async function _post(method, args) {
  const res = await fetch(`/api/method/${method}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Frappe-CSRF-Token': getCsrfToken(),
      'X-Requested-With': 'XMLHttpRequest',
    },
    body: JSON.stringify(args),
    credentials: 'same-origin',
  })

  const data = await res.json()

  if (!res.ok || data.exc_type) {
    let msg = data.message || data.exception || data.exc_type || `Error ${res.status}`
    if (data._server_messages) {
      try { msg = JSON.parse(JSON.parse(data._server_messages)[0]).message || msg } catch {}
    }
    throw Object.assign(new Error(msg), { data, status: res.status })
  }

  return data
}

export const call = (method, args = {}) => _post(method, args)

export async function getList(doctype, opts = {}) {
  const data = await _post('frappe.client.get_list', {
    doctype,
    fields: opts.fields || ['name'],
    filters: opts.filters || {},
    order_by: opts.orderBy || 'modified desc',
    limit: opts.limit || 100,
    limit_start: opts.start || 0,
  })
  return data.message || []
}

export async function getDoc(doctype, name) {
  const data = await _post('frappe.client.get', { doctype, name })
  return data.message
}

export async function saveDoc(doc) {
  // Use our custom endpoint that bypasses TimestampMismatchError
  // caused by after_save hooks bumping modified between our load and save
  const data = await _post('sfa_core.api.utils.save_doc', {
    doc: JSON.stringify(doc),
  })
  return data.message
}

export async function insertDoc(doc) {
  const data = await _post('frappe.client.insert', { doc })
  return data.message
}

export async function deleteDoc(doctype, name) {
  const data = await _post('frappe.client.delete', { doctype, name })
  return data.message
}
