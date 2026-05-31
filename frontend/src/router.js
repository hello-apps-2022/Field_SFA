import { createRouter, createWebHistory } from 'vue-router'
import { auth } from '@/utils/auth'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', name: 'Dashboard', component: () => import('@/pages/Dashboard.vue') },

  { path: '/customers', name: 'Customers', component: () => import('@/pages/customers/Customers.vue') },
  { path: '/customers/:name', name: 'Customer', component: () => import('@/pages/customers/Customer.vue'), props: true },
  { path: '/orders/:name', name: 'Order', component: () => import('@/pages/orders/Order.vue'), props: true },

  { path: '/visits', name: 'Visits', component: () => import('@/pages/visits/Visits.vue') },
  { path: '/visits/:name', name: 'Visit', component: () => import('@/pages/visits/Visit.vue'), props: true },

  { path: '/beat-plans', name: 'BeatPlans', component: () => import('@/pages/BeatPlans.vue') },

  { path: '/orders', name: 'Orders', component: () => import('@/pages/Orders.vue') },
  { path: '/payments', name: 'Payments', component: () => import('@/pages/Payments.vue') },
  { path: '/catalog', name: 'Catalog', component: () => import('@/pages/catalog/Catalog.vue') },
  { path: '/schemes', name: 'FreeCartonSchemes', component: () => import('@/pages/schemes/Schemes.vue') },
  { path: '/expenses', name: 'Expenses', component: () => import('@/pages/expenses/Expenses.vue') },
  { path: '/leave', name: 'Leave', component: () => import('@/pages/leave/Leave.vue') },
  { path: "/approvals/expenses", name: "ExpenseApprovals", component: () => import("@/pages/approvals/ExpenseApprovals.vue") },
  { path: "/approvals/leave", name: "LeaveApprovals", component: () => import("@/pages/approvals/LeaveApprovals.vue") },

  { path: '/form-templates', name: 'FormTemplates', component: () => import('@/pages/forms/FormTemplates.vue') },
  { path: '/form-templates/new', name: 'NewFormTemplate', component: () => import('@/pages/forms/FormTemplateEditor.vue') },
  { path: '/form-templates/:templateId', name: 'EditFormTemplate', component: () => import('@/pages/forms/FormTemplateEditor.vue'), props: true },

  { path: '/gamification', name: 'Gamification', component: () => import('@/pages/Gamification.vue') },
  { path: '/reports', name: 'Reports', component: () => import('@/pages/Reports.vue') },
  { path: '/territory-dashboard', name: 'TerritoryDashboard', component: () => import('@/pages/TerritoryDashboard.vue') },
  { path: '/targets', name: 'Targets', component: () => import('@/pages/Targets.vue') },
  { path: '/targets/performance', name: 'TargetsPerformance', component: () => import('@/pages/TargetsPerformance.vue') },
  { path: '/settings', name: 'SettingsHub', component: () => import('@/pages/SettingsHub.vue') },
  { path: '/settings/team', name: 'SettingsTeam', component: () => import('@/pages/Settings.vue') },
  { path: '/settings/team/:sp', name: 'RepProfile', component: () => import('@/pages/team/RepProfile.vue'), props: true },
  { path: '/settings/territories', name: 'SettingsTerritories', component: () => import('@/pages/SettingsTerritories.vue') },
  { path: '/settings/import-outlets', name: 'SettingsImportOutlets', component: () => import('@/pages/SettingsImportOutlets.vue') },
  { path: '/settings/beat-plan-permissions', name: 'BeatPlanPermissions', component: () => import('@/pages/BeatPlans.vue') },

  // Maps
  { path: '/rep-activity-map', name: 'RepActivityMap', component: () => import('@/pages/RepActivityMap.vue') },
  { path: '/customer-map', name: 'CustomerMap', component: () => import('@/pages/CustomerMap.vue') },

  { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('@/pages/NotFound.vue') },
]

const router = createRouter({
  history: createWebHistory('/sfa'),
  routes,
})

router.beforeEach((to, from, next) => {
  // Extract page name from path
  const page = to.path.replace('/', '') || 'dashboard'
  if (!auth.canAccess(page)) {
    // Redirect to dashboard if no access
    next('/')
  } else {
    next()
  }
})

export default router
