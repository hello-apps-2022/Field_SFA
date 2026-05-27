import './index.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import { Button, Badge, Avatar, LoadingIndicator, Dialog, Alert, Input, FeatherIcon } from 'frappe-ui'
import 'frappe-ui/src/style.css'

function mountSFAApp(selector) {
  const el = document.querySelector(selector)
  if (!el) {
    console.error('SFA: mount element not found:', selector)
    return
  }

  // frappe.call, frappe.session etc are all available here
  // because we're inside the Frappe desk context

  const pinia = createPinia()
  const app = createApp(App)
  app.use(pinia)
  app.use(router)
  app.component('Button', Button)
  app.component('Badge', Badge)
  app.component('Avatar', Avatar)
  app.component('LoadingIndicator', LoadingIndicator)
  app.component('Dialog', Dialog)
  app.component('Alert', Alert)
  app.component('Input', Input)
  app.component('FeatherIcon', FeatherIcon)
  app.mount(el)
  return app
}

// Expose for Frappe Page to call
window.SFA_Core = {
  mount: mountSFAApp,
  router,
}
