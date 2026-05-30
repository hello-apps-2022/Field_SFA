/**
 * SFA Auth store — reads from window.frappe_boot.sfa
 * Single source of truth for role-based UI decisions.
 */

function getBoot() {
  return window.frappe_boot?.sfa || {}
}

export const auth = {
  get role()        { return getBoot().role },
  get isAdmin()     { return getBoot().is_admin || false },
  get isManager()   { return getBoot().is_manager || false },
  get isRep()       { return getBoot().is_rep || false },
  get isSupervisor(){ return getBoot().is_supervisor || false },
  get isHelper()    { return getBoot().is_helper || false },
  get salesPerson() { return getBoot().sales_person },
  get employee()    { return getBoot().employee },
  get territory()   { return getBoot().territory },
  get companies()   { return getBoot().companies || [] },
  get allowDiscretionaryFree() { return getBoot().allow_discretionary_free || false },

  canAccess(page) {
    const r = this
    const rules = {
      'dashboard':           true,
      'customers':           true,
      'visits':              true,
      'beat-plans':          true,
      'orders':              true,
      'payments':            true,
      'catalog':             r.isAdmin || r.isManager,
      'schemes':             true,
      'expenses':            true,
      'leave':               true,
      'approvals/expenses':  r.isAdmin || r.isManager,
      'approvals/leave':     r.isAdmin || r.isManager,
      'form-templates':      r.isAdmin || r.isManager,
      'gamification':        r.isAdmin || r.isManager,
      'reports':             r.isAdmin || r.isManager || r.isSupervisor,
      'rep-activity-map':    r.isAdmin || r.isManager || r.isSupervisor,
      'customer-map':        r.isAdmin || r.isManager || r.isSupervisor,
      'territory-dashboard': r.isAdmin || r.isManager || r.isSupervisor,
      'targets':             r.isAdmin || r.isManager || r.isSupervisor,
      'targets/performance':  r.isAdmin || r.isManager || r.isSupervisor,
      'settings':            r.isAdmin || r.isManager,
      'settings/team':       r.isAdmin || r.isManager,
      'settings/territories': r.isAdmin || r.isManager,
      'settings/beat-plan-permissions': r.isAdmin || r.isManager || r.isSupervisor,
    }
    if (page.startsWith('settings/team/')) return r.isAdmin || r.isManager || r.isRep || r.isSupervisor
    // Exact match first, then match the longest rule key that is a path-segment
    // prefix of the page (so "customers/<name>" resolves to the "customers" rule).
    if (page in rules) return rules[page]
    const parts = page.split('/')
    for (let n = parts.length - 1; n >= 1; n--) {
      const key = parts.slice(0, n).join('/')
      if (key in rules) return rules[key]
    }
    return r.isAdmin
  },

  can(action) {
    const r = this
    const rules = {
      'create-beat-plan':          r.isAdmin || r.isManager || r.isSupervisor,
      'edit-beat-plan':            r.isAdmin || r.isManager || r.isSupervisor,
      'delete-beat-plan':          r.isAdmin,
      'add-customer-to-beat':      true,
      'remove-customer-from-beat': r.isAdmin || r.isManager || r.isSupervisor,
      'reorder-beat-customers':    r.isAdmin || r.isManager || r.isSupervisor,
      'toggle-rep-creation':       r.isAdmin || r.isManager || r.isSupervisor,
      'create-form-template':      r.isAdmin || r.isManager,
      'manage-users':              r.isAdmin || r.isManager,
      'view-all-reps':             r.isAdmin || r.isManager,
    }
    return rules[action] ?? r.isAdmin
  }
}
