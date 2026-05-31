// Pure order payment-status helpers. No Vue state: pass the order, the
// payments array, and (where money is formatted) a currency formatter.
// Shared by the customer peek panel and the standalone /orders/:name page.

const COLLECTED = ['Submitted', 'Reconciled']

export function orderIsCarton(o) {
  return (Number(o.grand_total) || 0) <= 0 && (Number(o.total_qty) || 0) > 0
}

export function orderPaid(o, payments = []) {
  let sum = 0
  for (const p of payments) {
    if (p.custom_sales_order === o.name && COLLECTED.includes(p.status)) sum += Number(p.amount) || 0
  }
  return sum
}

export function orderCartonsPaid(o, payments = []) {
  let sum = 0
  for (const p of payments) {
    if (p.custom_sales_order === o.name && COLLECTED.includes(p.status)) sum += Number(p.custom_carton_total) || 0
  }
  return sum
}

export function orderOutstanding(o, payments = []) {
  return Math.max(0, (Number(o.grand_total) || 0) - orderPaid(o, payments))
}

export function orderCartonsOutstanding(o, payments = []) {
  return Math.max(0, (Number(o.total_qty) || 0) - orderCartonsPaid(o, payments))
}

export function orderNeedsCollection(o, payments = []) {
  return orderIsCarton(o) ? orderCartonsOutstanding(o, payments) > 0 : orderOutstanding(o, payments) > 0
}

export function orderPayStatus(o, payments = []) {
  if (orderIsCarton(o)) {
    const ordered = Number(o.total_qty) || 0
    const paid = orderCartonsPaid(o, payments)
    if (paid <= 0) return 'Unpaid'
    return paid >= ordered ? 'Paid' : 'Partial'
  }
  const total = Number(o.grand_total) || 0
  if (total <= 0) return 'Paid'
  const paid = orderPaid(o, payments)
  if (paid <= 0) return 'Unpaid'
  return paid >= total ? 'Paid' : 'Partial'
}

export function orderPayBadge(o, payments = [], fmt = (n) => n) {
  const s = orderPayStatus(o, payments)
  if (s !== 'Partial') return s
  return orderIsCarton(o) ? (orderCartonsOutstanding(o, payments) + ' ctns left') : (fmt(orderOutstanding(o, payments)) + ' left')
}

export function orderPayColor(o, payments = []) {
  const s = orderPayStatus(o, payments)
  return s === 'Paid' ? 'text-green-600' : s === 'Partial' ? 'text-amber-600' : 'text-gray-400'
}

export function orderPayLabel(o, payments = [], fmt = (n) => n) {
  const s = orderPayStatus(o, payments)
  if (orderIsCarton(o)) {
    const ordered = Number(o.total_qty) || 0
    const paid = orderCartonsPaid(o, payments)
    if (s === 'Paid') return 'Cartons collected in full'
    if (s === 'Partial') return paid + ' of ' + ordered + ' cartons · ' + orderCartonsOutstanding(o, payments) + ' left'
    return 'Uncollected · ' + ordered + ' cartons due'
  }
  if (s === 'Paid') return 'Paid in full'
  if (s === 'Partial') return fmt(orderPaid(o, payments)) + ' of ' + fmt(o.grand_total) + ' · ' + fmt(orderOutstanding(o, payments)) + ' left'
  return 'Unpaid · ' + fmt(o.grand_total) + ' due'
}
