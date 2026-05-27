import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/pages/Dashboard.vue'),
  },
  {
    path: '/visits',
    name: 'Visits',
    component: () => import('@/pages/Visits.vue'),
  },
  {
    path: '/visits/:visitId',
    name: 'Visit',
    component: () => import('@/pages/Visit.vue'),
    props: true,
  },
  {
    path: '/form-templates',
    name: 'FormTemplates',
    component: () => import('@/pages/FormTemplates.vue'),
  },
  {
    path: '/form-templates/new',
    name: 'NewFormTemplate',
    component: () => import('@/pages/FormTemplateEditor.vue'),
  },
  {
    path: '/form-templates/:templateId',
    name: 'EditFormTemplate',
    component: () => import('@/pages/FormTemplateEditor.vue'),
    props: true,
  },
  {
    path: '/beat-plans',
    name: 'BeatPlans',
    component: () => import('@/pages/BeatPlans.vue'),
  },
  {
    path: '/orders',
    name: 'Orders',
    component: () => import('@/pages/Orders.vue'),
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('@/pages/Reports.vue'),
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/pages/Settings.vue'),
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/pages/NotFound.vue'),
  },
]

const router = createRouter({
  history: createWebHistory('/sfa'),
  routes,
})

router.beforeEach((to, from, next) => {
  if (!window.frappe?.session?.user || window.frappe.session.user === 'Guest') {
    window.location.href = '/login?redirect-to=/sfa'
    return
  }
  next()
})

export default router
