/**
 * Currency utilities — reads default currency from frappe_boot
 * so the app automatically adapts to ERPNext system settings.
 */

function getDefaultCurrency() {
  // frappe_boot.sysdefaults.currency comes from ERPNext system settings
  return window.frappe_boot?.sysdefaults?.currency || 'UGX'
}

function getCurrencySymbol(currency) {
  const symbols = {
    UGX: 'UGX', KES: 'KES', TZS: 'TZS', RWF: 'RWF',
    USD: '$', EUR: '€', GBP: '£', INR: '₹', NGN: '₦',
  }
  return symbols[currency] || currency
}

/**
 * Format a monetary value with the system default currency.
 * Shortens large values: 1,500,000 → "UGX 1.5M", 50,000 → "UGX 50K"
 */
export function formatCurrency(value, currency) {
  const curr = currency || getDefaultCurrency()
  const sym = getCurrencySymbol(curr)
  if (!value && value !== 0) return `${sym} 0`
  const v = Number(value)
  if (v >= 1e9) return `${sym} ${(v / 1e9).toFixed(1)}B`
  if (v >= 1e6) return `${sym} ${(v / 1e6).toFixed(1)}M`
  if (v >= 1e3) return `${sym} ${(v / 1e3).toFixed(0)}K`
  return `${sym} ${v.toLocaleString()}`
}

/**
 * Short version for stat strips — no symbol prefix, just the number
 */
export function formatCurrencyShort(value) {
  if (!value && value !== 0) return '0'
  const v = Number(value)
  if (v >= 1e9) return `${(v / 1e9).toFixed(1)}B`
  if (v >= 1e6) return `${(v / 1e6).toFixed(1)}M`
  if (v >= 1e3) return `${(v / 1e3).toFixed(0)}K`
  return v.toLocaleString()
}

/**
 * Returns the default currency label for display, e.g. "UGX" or "$"
 */
export function currencyLabel() {
  const curr = getDefaultCurrency()
  return getCurrencySymbol(curr)
}
