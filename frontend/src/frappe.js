/**
 * frappe.js — Frappe API shim for standalone SFA app.
 *
 * Frappe's /api/method endpoint expects:
 *   POST with Content-Type: application/json
 *   Body: args flattened to top level  e.g. {"doctype":"X","fields":[...]}
 *   Header: X-Frappe-CSRF-Token: <token>
 */

function getCsrfToken() {
  // Injected by sfa.py into window before bundle loads
  return window.csrf_token || window.__SFA_BOOT__?.csrf_token || 'fetch'
}

async function call({ method, args = {}, type } = {}) {
  const isGet = type === 'GET'
  const url = `/api/method/${method}`

  let options

  if (isGet) {
    const params = new URLSearchParams()
    for (const [k, v] of Object.entries(args)) {
      params.set(k, typeof v === 'object' ? JSON.stringify(v) : String(v))
    }
    const qs = params.toString()
    options = {
      method: 'GET',
      headers: { 'X-Frappe-CSRF-Token': getCsrfToken() },
      credentials: 'same-origin',
    }
    return _doFetch(qs ? `${url}?${qs}` : url, options)
  }

  // POST: send args FLATTENED as JSON body (not nested under "args")
  options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Frappe-CSRF-Token': getCsrfToken(),
      'X-Requested-With': 'XMLHttpRequest',
      'Accept': 'application/json',
    },
    body: JSON.stringify(args),   // ← flat, not {args: args}
    credentials: 'same-origin',
  }
  return _doFetch(url, options)
}

async function _doFetch(url, options) {
  const res = await fetch(url, options)
  const data = await res.json()

  if (!res.ok || data.exc_type) {
    let msg = data.message || data.exception || data.exc_type || `HTTP ${res.status}`
    if (data._server_messages) {
      try { msg = JSON.parse(JSON.parse(data._server_messages)[0]).message || msg } catch {}
    }
    throw Object.assign(new Error(msg), { data, status: res.status })
  }

  return data
}

function show_alert({ message, indicator = 'blue' } = {}) {
  document.querySelector('#sfa-toast')?.remove()
  const colors = { green: '#16a34a', red: '#dc2626', blue: '#2563eb', orange: '#ea580c', yellow: '#ca8a04' }
  const color = colors[indicator] || colors.blue
  const el = document.createElement('div')
  el.id = 'sfa-toast'
  Object.assign(el.style, {
    position: 'fixed', bottom: '24px', right: '24px', zIndex: '9999',
    display: 'flex', alignItems: 'center', gap: '10px',
    background: 'white', border: '1px solid #e5e7eb',
    borderLeft: `4px solid ${color}`, borderRadius: '8px',
    padding: '12px 16px', boxShadow: '0 4px 16px rgba(0,0,0,0.12)',
    fontSize: '13px', fontFamily: 'inherit', color: '#111827', maxWidth: '380px',
  })
  el.innerHTML = `<span style="flex:1;line-height:1.4">${message}</span>
    <button onclick="document.getElementById('sfa-toast')?.remove()"
      style="background:none;border:none;cursor:pointer;color:#9ca3af;font-size:18px;padding:0;line-height:1;margin-left:8px">×</button>`
  document.body.appendChild(el)
  setTimeout(() => document.getElementById('sfa-toast')?.remove(), 4500)
}

window.frappe = window.frappe || {}
if (!window.frappe.call) window.frappe.call = call
if (!window.frappe.show_alert) window.frappe.show_alert = show_alert
window.frappe.confirm = (msg) => window.confirm(msg)

export { call, show_alert }
