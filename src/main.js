import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'

// Pages
import SFADashboard from './pages/SFADashboard.vue'
import VisitsList from './pages/VisitsList.vue'
import FormTemplates from './pages/FormTemplates.vue'

// Components (global registration)
import MetricCard from './components/MetricCard.vue'
import VisitCard from './components/VisitCard.vue'
import RepActivityCard from './components/RepActivityCard.vue'
import DataTable from './components/DataTable.vue'
import TimelineFeed from './components/TimelineFeed.vue'
import MapView from './components/MapView.vue'

// Router
const router = createRouter({
    history: createWebHashHistory(),
    routes: [
        { path: '/', redirect: '/dashboard' },
        { path: '/dashboard', component: SFADashboard },
        { path: '/visits', component: VisitsList },
        { path: '/form-templates', component: FormTemplates },
    ],
})

function mountSFAApp(selector) {
    const el = document.querySelector(selector)
    if (!el) return

    const app = createApp({
        template: '<router-view />'
    })

    app.use(router)

    // Global component registration
    app.component('MetricCard', MetricCard)
    app.component('VisitCard', VisitCard)
    app.component('RepActivityCard', RepActivityCard)
    app.component('DataTable', DataTable)
    app.component('TimelineFeed', TimelineFeed)
    app.component('MapView', MapView)

    app.mount(el)
    return app
}

// Expose globally for Frappe pages
window.SFA_Core = {
    mount: mountSFAApp,
    router,
}

export default mountSFAApp
