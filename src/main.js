import { createApp } from 'vue'

// Import pages
import SFADashboard from './pages/SFADashboard.vue'
import VisitsList from './pages/VisitsList.vue'
import FormTemplates from './pages/FormTemplates.vue'

// Import components
import MetricCard from './components/MetricCard.vue'
import VisitCard from './components/VisitCard.vue'
import RepActivityCard from './components/RepActivityCard.vue'
import DataTable from './components/DataTable.vue'
import TimelineFeed from './components/TimelineFeed.vue'
import MapView from './components/MapView.vue'

// Make components available globally
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

// Mount if target element exists
const mountEl = document.getElementById('sfa-app')
if (mountEl) {
  app.mount(mountEl)
}

export default app
