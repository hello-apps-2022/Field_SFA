import './index.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

import {
  FrappeUI,
  Button,
  Input,
  TextInput,
  FormControl,
  ErrorMessage,
  Dialog,
  Alert,
  Badge,
  Avatar,
  Tooltip,
  Spinner,
  setConfig,
  frappeRequest,
  FeatherIcon,
} from 'frappe-ui'

const globalComponents = {
  Button,
  Input,
  TextInput,
  FormControl,
  ErrorMessage,
  Dialog,
  Alert,
  Badge,
  Avatar,
  Tooltip,
  Spinner,
  FeatherIcon,
}

const pinia = createPinia()
const app = createApp(App)

setConfig('resourceFetcher', frappeRequest)

app.use(FrappeUI)
app.use(pinia)
app.use(router)

for (const key in globalComponents) {
  app.component(key, globalComponents[key])
}

// Mount — in production boot data is injected by sfa.py via Jinja
if (import.meta.env.DEV) {
  frappeRequest({ url: '/api/method/sfa_core.www.sfa.get_context_for_dev' }).then(
    (values) => {
      for (const key in values) window[key] = values[key]
      app.mount('#app')
    }
  )
} else {
  app.mount('#app')
}
