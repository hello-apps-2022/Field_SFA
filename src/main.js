import { createApp } from 'vue'

// Pages
import SFADashboard from './pages/SFADashboard.vue'
import VisitsList from './pages/VisitsList.vue'
import FormTemplates from './pages/FormTemplates.vue'

// Components
import MetricCard from './components/MetricCard.vue'
import VisitCard from './components/VisitCard.vue'
import RepActivityCard from './components/RepActivityCard.vue'
import DataTable from './components/DataTable.vue'
import TimelineFeed from './components/TimelineFeed.vue'
import MapView from './components/MapView.vue'

function createSFAApp() {
    const app = createApp({})
    app.component('SfaDashboard', SFADashboard)
    app.component('VisitsList', VisitsList)
    app.component('FormTemplates', FormTemplates)
    app.component('MetricCard', MetricCard)
    app.component('VisitCard', VisitCard)
    app.component('RepActivityCard', RepActivityCard)
    app.component('DataTable', DataTable)
    app.component('TimelineFeed', TimelineFeed)
    app.component('MapView', MapView)
    return app
}

// Expose a mount function for Frappe pages to call
window.SFA_Core = {
    mount: function(selector) {
        const el = document.querySelector(selector)
        if (el) {
            createSFAApp().mount(el)
        }
    }
}

export default createSFAApp
