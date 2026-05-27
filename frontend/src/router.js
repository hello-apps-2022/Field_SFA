import { createRouter, createMemoryHistory } from 'vue-router'

// Use memory history — no URL changes, so Frappe's router never intercepts
const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', redirect: '/dashboard' },
    { path: '/dashboard', name: 'Dashboard', component: () => import('@/pages/Dashboard.vue') },
    { path: '/customers', name: 'Customers', component: () => import('@/pages/Customers.vue') },
    { path: '/visits', name: 'Visits', component: () => import('@/pages/Visits.vue') },
    { path: '/visits/:visitId', name: 'Visit', component: () => import('@/pages/Visit.vue'), props: true },
    { path: '/orders', name: 'Orders', component: () => import('@/pages/Orders.vue') },
    { path: '/payments', name: 'Payments', component: () => import('@/pages/Payments.vue') },
    { path: '/beat-plans', name: 'BeatPlans', component: () => import('@/pages/BeatPlans.vue') },
    { path: '/form-templates', name: 'FormTemplates', component: () => import('@/pages/FormTemplates.vue') },
    { path: '/form-templates/new', name: 'NewFormTemplate', component: () => import('@/pages/FormTemplateEditor.vue') },
    { path: '/form-templates/:templateId', name: 'EditFormTemplate', component: () => import('@/pages/FormTemplateEditor.vue'), props: true },
    { path: '/gamification', name: 'Gamification', component: () => import('@/pages/Gamification.vue') },
    { path: '/reports', name: 'Reports', component: () => import('@/pages/Reports.vue') },
    { path: '/settings', name: 'Settings', component: () => import('@/pages/Settings.vue') },
    { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('@/pages/NotFound.vue') },
  ],
})

export default router
