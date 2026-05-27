import './index.css'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import FeatherIcon from './components/ui/FeatherIcon.vue'

// Boot data is injected by sfa.py via Jinja into window.frappe_boot
// In dev mode, fetch it from the API
async function init() {
  if (import.meta.env.DEV && !window.frappe_boot) {
    try {
      const res = await fetch('/api/method/sfa_core.www.sfa.get_context_for_dev', {
        method: 'POST',
        credentials: 'same-origin',
      })
      const data = await res.json()
      window.frappe_boot = data.message
    } catch (e) {
      console.error('Failed to fetch boot data', e)
    }
  }

  if (!window.frappe_boot?.user?.name || window.frappe_boot.user.name === 'Guest') {
    window.location.href = '/login?redirect-to=/sfa'
    return
  }

  const pinia = createPinia()
  const app = createApp(App)
  app.use(pinia)
  app.use(router)
  app.component('FeatherIcon', FeatherIcon)
  app.mount('#app')
}

init()
