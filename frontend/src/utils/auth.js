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
  get salesPerson() { return getBoot().sales_person },
  get employee()    { return getBoot().employee },
  get territory()   { return getBoot().territory },

  canAccess(page) {
    const r = this
    const rules = {
      'dashboard':           true,
      'customers':           true,
      'visits':              true,
      'beat-plans':          true,
      'orders':              true,
      'payments':            true,
      'expenses':            true,
      'leave':               true,
      'approvals/expenses':  r.isAdmin || r.isManager,
      'approvals/leave':     r.isAdmin || r.isManager,
      'form-templates':      r.isAdmin || r.isManager,
      'gamification':        r.isAdmin || r.isManager,
      'reports':             r.isAdmin || r.isManager,
      'rep-activity-map':    r.isAdmin || r.isManager,
      'customer-map':        r.isAdmin || r.isManager,
      'territory-dashboard': r.isAdmin || r.isManager,
      'targets':             r.isAdmin || r.isManager,
      'targets/performance':  r.isAdmin || r.isManager,
      'settings':            r.isAdmin,
      'settings/team':       r.isAdmin,
      'settings/territories': r.isAdmin,
      'settings/beat-plan-permissions': r.isAdmin || r.isManager,
    }
    return rules[page] ?? r.isAdmin
  },

  can(action) {
    const r = this
    const rules = {
      'create-beat-plan':          r.isAdmin || r.isManager,
      'edit-beat-plan':            r.isAdmin || r.isManager,
      'delete-beat-plan':          r.isAdmin,
      'add-customer-to-beat':      true,
      'remove-customer-from-beat': r.isAdmin || r.isManager,
      'reorder-beat-customers':    r.isAdmin || r.isManager,
      'toggle-rep-creation':       r.isAdmin || r.isManager,
      'create-form-template':      r.isAdmin || r.isManager,
      'manage-users':              r.isAdmin,
      'view-all-reps':             r.isAdmin || r.isManager,
    }
    return rules[action] ?? r.isAdmin
  }
}
