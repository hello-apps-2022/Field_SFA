/**
 * SFA Brand store — reads from window.frappe_boot.brand
 * White-label single source of truth: logo, product/tenant name, tagline, theme.
 * Falls back to FieldPro product defaults if boot data is missing.
 */

const FALLBACK = {
  product_name: 'FieldPro',
  tenant_name: '',
  login_tagline: 'Know your field.',
  logo_login: '/assets/sfa_core/images/fieldpro-logo.svg',
  logo_navbar: '/assets/sfa_core/images/fieldpro-mark.svg',
  favicon: '/assets/sfa_core/images/fieldpro-favicon.svg',
  primary_color: '#1A1A2E',
  accent_color: '#378ADD',
  support_email: '',
}

function getBrand() {
  return { ...FALLBACK, ...(window.frappe_boot?.brand || {}) }
}

export const brand = {
  get productName() { return getBrand().product_name },
  get tenantName()  { return getBrand().tenant_name },
  get tagline()     { return getBrand().login_tagline },
  get logo()        { return getBrand().logo_navbar },
  get logoFull()    { return getBrand().logo_login },
  get favicon()     { return getBrand().favicon },
  get primary()     { return getBrand().primary_color },
  get accent()      { return getBrand().accent_color },
  get supportEmail(){ return getBrand().support_email },
}

/**
 * Apply brand to the document: theme CSS variables, tab title, favicon.
 * Call once at app mount (e.g. in main.js after the app is created).
 */
export function applyBrand() {
  const b = getBrand()
  const root = document.documentElement
  root.style.setProperty('--brand-primary', b.primary_color)
  root.style.setProperty('--brand-accent', b.accent_color)

  document.title = b.tenant_name
    ? `${b.product_name} · ${b.tenant_name}`
    : b.product_name

  if (b.favicon) {
    let link = document.querySelector("link[rel~='icon']")
    if (!link) {
      link = document.createElement('link')
      link.rel = 'icon'
      document.head.appendChild(link)
    }
    link.href = b.favicon
  }
}
