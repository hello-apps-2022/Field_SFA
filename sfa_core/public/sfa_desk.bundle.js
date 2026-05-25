// SFA Core Desk Bundle - Frappe esbuild entry point
// Imports Vue app and components

import { createApp } from 'vue'

// Import pages
import SFADashboard from '../src/pages/SFADashboard.vue'
import VisitsList from '../src/pages/VisitsList.vue'
import FormTemplates from '../src/pages/FormTemplates.vue'

// Import components
import MetricCard from '../src/components/MetricCard.vue'
import VisitCard from '../src/components/VisitCard.vue'
import RepActivityCard from '../src/components/RepActivityCard.vue'
import DataTable from '../src/components/DataTable.vue'
import TimelineFeed from '../src/components/TimelineFeed.vue'
import MapView from '../src/components/MapView.vue'

// Register components globally
const app = createApp({})

app.component('SFADashboard', SFADashboard)
app.component('VisitsList', VisitsList)
app.component('FormTemplates', FormTemplates)
app.component('MetricCard', MetricCard)
app.component('VisitCard', VisitCard)
app.component('RepActivityCard', RepActivityCard)
app.component('DataTable', DataTable)
app.component('TimelineFeed', TimelineFeed)
app.component('MapView', MapView)

// Mount if element exists
const mountEl = document.getElementById('sfa-app')
if (mountEl) {
  app.mount(mountEl)
}

export default app
