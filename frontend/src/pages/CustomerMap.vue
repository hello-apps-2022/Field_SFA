<template>
  <div class="flex h-full flex-col overflow-hidden">

    <!-- Header -->
    <div class="flex h-[52px] shrink-0 items-center border-b border-gray-100 bg-white px-5 gap-3">
      <h1 class="text-sm font-semibold text-gray-900">Customer Map</h1>
      <div class="flex-1" />
      <span class="text-xs text-gray-400">{{ visibleCustomers.length }} customers shown</span>
      <Btn icon="refresh-cw" size="sm" @click="load">Refresh</Btn>
    </div>

    <!-- Filters -->
    <div class="flex shrink-0 flex-wrap items-center gap-2 border-b border-gray-100 bg-white px-4 py-2.5">
      <div class="relative">
        <FeatherIcon name="search" class="absolute left-2.5 top-2 h-3.5 w-3.5 text-gray-400 pointer-events-none" />
        <input v-model="search" type="text" placeholder="Search customers…"
          class="h-8 rounded-md border border-gray-200 bg-white pl-8 pr-3 text-sm focus:border-gray-400 focus:outline-none w-48" />
      </div>

      <select v-model="territoryFilter" @change="applyFilters"
        class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
        <option value="">All Territories</option>
        <option v-for="t in territories" :key="t">{{ t }}</option>
      </select>

      <select v-model="groupFilter" @change="applyFilters"
        class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
        <option value="">All Groups</option>
        <option value="General Trade" style="font-weight:600">── General Trade</option>
        <option value="Kiosk / Duka">  Kiosk / Duka</option>
        <option value="Retailer">  Retailer</option>
        <option value="Wholesaler / Stockist">  Wholesaler / Stockist</option>
        <option value="Dealer">  Dealer</option>
        <option value="Distributor">  Distributor</option>
        <option value="Modern Trade" style="font-weight:600">── Modern Trade</option>
        <option value="Supermarket">  Supermarket</option>
        <option value="Convenience Store">  Convenience Store</option>
        <option value="Petrol Forecourt">  Petrol Forecourt</option>
        <option value="Horeca" style="font-weight:600">── Horeca</option>
        <option value="Hotel / Lodge">  Hotel / Lodge</option>
        <option value="Restaurant / Café">  Restaurant / Café</option>
        <option value="Bar / Club">  Bar / Club</option>
        <option v-for="g in groups" :key="g">{{ g }}</option>
      </select>

      <select v-model="repFilter" @change="applyFilters"
        class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
        <option value="">All Reps</option>
        <option v-for="r in repsList" :key="r">{{ r }}</option>
      </select>

      <select v-model="visitFilter" @change="applyFilters"
        class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
        <option value="">All Visit Status</option>
        <option value="overdue">Overdue</option>
        <option value="due_soon">Due Soon (7 days)</option>
        <option value="visited">Visited This Week</option>
        <option value="never">Never Visited</option>
      </select>

      <select v-model="tierFilter" @change="applyFilters"
        class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
        <option value="">All Tiers</option>
        <option value="Tier 1">Tier 1</option>
        <option value="Tier 2">Tier 2</option>
        <option value="Tier 3">Tier 3</option>
        <option value="Tier 4">Tier 4</option>
        <option value="Tier 5">Tier 5</option>
      </select>

      <label class="flex items-center gap-1.5 text-xs text-gray-600 cursor-pointer select-none">
        <input type="checkbox" v-model="showNoLocation" class="rounded" />
        Include without GPS
      </label>
    </div>

    <!-- Map + list -->
    <div class="flex flex-1 overflow-hidden">

      <!-- Map -->
      <div class="relative flex-1">
        <div id="customer-map-view" style="height:100%;width:100%;min-height:400px" />

        <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-white/60">
          <FeatherIcon name="loader" class="h-8 w-8 animate-spin text-gray-400" />
        </div>
      </div>

      <!-- Sidebar -->
      <div class="w-72 shrink-0 flex flex-col border-l border-gray-100 bg-white overflow-hidden">
        <div class="border-b border-gray-100 px-4 py-2.5">
          <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Customers</p>
          <p class="text-xs text-gray-500 mt-0.5">{{ visibleCustomers.length }} matching filters</p>
        </div>
        <div class="flex-1 overflow-y-auto divide-y divide-gray-50">
          <div
            v-for="c in sidebarCustomers" :key="c.name"
            class="cursor-pointer px-4 py-3 hover:bg-gray-50 transition-colors"
            :class="selectedCustomer?.name === c.name ? 'bg-blue-50 border-l-2 border-blue-500' : ''"
            @click="focusCustomer(c)"
          >
            <div class="flex items-start justify-between gap-2">
              <div class="min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">{{ c.customer_name }}</p>
                <p class="text-xs text-gray-400 truncate">
                  {{ [c.custom_location_area, c.custom_location_city].filter(Boolean).join(', ') || c.territory || 'No location' }}
                </p>
                <div class="mt-1 flex items-center gap-2">
                  <span v-if="c.custom_last_visit_date" class="text-[10px] text-gray-400">
                    Last: {{ formatDate(c.custom_last_visit_date) }}
                  </span>
                  <span v-if="isOverdue(c)" class="rounded-full bg-red-50 px-1.5 py-0.5 text-[10px] text-red-600">Overdue</span>
                </div>
              </div>
              <div v-if="!c.custom_latitude" class="shrink-0">
                <FeatherIcon name="map-pin" class="h-3.5 w-3.5 text-gray-300" title="No GPS" />
              </div>
            </div>
          </div>
          <div v-if="sidebarCustomers.length < visibleCustomers.length" class="px-4 py-3 text-center text-xs text-gray-400">
            + {{ visibleCustomers.length - sidebarCustomers.length }} more — zoom in or refine filters
          </div>
        </div>
      </div>
    </div>

    <!-- Customer popup panel -->
    <SlidePanel
      v-model="customerPanel"
      :title="selectedCustomer?.customer_name || 'Customer'"
      save-label=""
    >
      <div v-if="selectedCustomer" class="space-y-4">
        <div class="flex items-center gap-3">
          <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-lg font-semibold text-indigo-700">
            {{ (selectedCustomer.customer_name || '?').charAt(0).toUpperCase() }}
          </div>
          <div>
            <p class="text-base font-semibold text-gray-900">{{ selectedCustomer.customer_name }}</p>
            <p class="text-xs text-gray-500">{{ selectedCustomer.territory }} · {{ selectedCustomer.customer_group }}</p>
          </div>
        </div>

        <div class="rounded-xl border border-gray-200 bg-white overflow-hidden">
          <div class="flex border-b border-gray-50 px-4 py-2.5">
            <span class="w-32 text-xs text-gray-400">Mobile</span>
            <span class="text-sm" :class="selectedCustomer.mobile_no?'text-gray-800':'text-gray-400 italic'">{{ selectedCustomer.mobile_no || 'Not set' }}</span>
          </div>
          <div class="flex border-b border-gray-50 px-4 py-2.5">
            <span class="w-32 text-xs text-gray-400">Primary Rep</span>
            <span class="text-sm" :class="selectedCustomer.custom_sfa_rep?'text-gray-800':'text-gray-400 italic'">{{ selectedCustomer.custom_sfa_rep || 'Not assigned' }}</span>
          </div>
          <div class="flex border-b border-gray-50 px-4 py-2.5">
            <span class="w-32 text-xs text-gray-400">Last Visit</span>
            <span class="text-sm" :class="isOverdue(selectedCustomer)?'text-red-600 font-medium':'text-gray-800'">
              {{ formatDate(selectedCustomer.custom_last_visit_date) }}
              <span v-if="isOverdue(selectedCustomer)" class="ml-1 text-xs">(Overdue)</span>
            </span>
          </div>
          <div class="flex border-b border-gray-50 px-4 py-2.5">
            <span class="w-32 text-xs text-gray-400">Next Due</span>
            <span class="text-sm text-gray-800">{{ formatDate(selectedCustomer.custom_next_visit_due) }}</span>
          </div>
          <div class="flex border-b border-gray-50 px-4 py-2.5">
            <span class="w-32 text-xs text-gray-400">Total Orders</span>
            <span class="text-sm text-gray-800">{{ selectedCustomer.custom_total_orders || 0 }}</span>
          </div>
          <div class="flex px-4 py-2.5">
            <span class="w-32 text-xs text-gray-400">Revenue</span>
            <span class="text-sm text-gray-800">{{ formatCurrency(selectedCustomer.custom_total_revenue) }}</span>
          </div>
        </div>

        <div class="flex gap-2">
          <router-link
            :to="'/customers/' + selectedCustomer.name"
            class="flex-1 inline-flex h-9 items-center justify-center rounded-lg border border-gray-200 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
            @click="customerPanel = false"
          >
            <FeatherIcon name="eye" class="h-3.5 w-3.5 mr-1.5" /> View Details
          </router-link>
        </div>
      </div>
    </SlidePanel>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { call } from '@/utils/frappe'
import { formatCurrency } from '@/utils/currency'
import Btn from '@/components/ui/Btn.vue'
import SlidePanel from '@/components/ui/SlidePanel.vue'
import dayjs from 'dayjs'
import { getL, ensureLeafletCSS } from '@/utils/leaflet'

const customers = ref([])
const loading = ref(false)
const search = ref('')
const territoryFilter = ref('')
const groupFilter = ref('')
const repFilter = ref('')
const visitFilter = ref('')
const tierFilter = ref('')
const showNoLocation = ref(false)
const selectedCustomer = ref(null)
const customerPanel = ref(false)
let mapInstance = null
let markersLayer = null

const territories = computed(() => [...new Set(customers.value.map(c => c.territory).filter(Boolean))].sort())
const groups = computed(() => [...new Set(customers.value.map(c => c.customer_group).filter(Boolean))].sort())
const repsList = computed(() => [...new Set(customers.value.map(c => c.custom_sfa_rep).filter(Boolean))].sort())

const visibleCustomers = computed(() => {
  let l = customers.value
  if (!showNoLocation.value) l = l.filter(c => c.custom_latitude && c.custom_longitude)
  if (search.value) {
    const q = search.value.toLowerCase()
    l = l.filter(c => c.customer_name?.toLowerCase().includes(q) || c.name?.toLowerCase().includes(q))
  }
  if (territoryFilter.value) l = l.filter(c => c.territory === territoryFilter.value)
  if (groupFilter.value) l = l.filter(c => c.customer_group === groupFilter.value)
  if (repFilter.value) l = l.filter(c => c.custom_sfa_rep === repFilter.value)
  if (tierFilter.value) l = l.filter(c => c.custom_outlet_tier === tierFilter.value)
  if (visitFilter.value === 'overdue') l = l.filter(c => isOverdue(c))
  if (visitFilter.value === 'due_soon') l = l.filter(c => isDueSoon(c))
  if (visitFilter.value === 'visited') l = l.filter(c => {
    if (!c.custom_last_visit_date) return false
    return dayjs(c.custom_last_visit_date).isAfter(dayjs().subtract(7, 'day'))
  })
  if (visitFilter.value === 'never') l = l.filter(c => !c.custom_last_visit_date)
  return l
})

// Show max 100 in sidebar, all on map
const sidebarCustomers = computed(() => visibleCustomers.value.slice(0, 100))

async function load() {
  loading.value = true
  try {
    const res = await call('sfa_core.api.maps.get_customers_map', { has_location_only: 0 })
    customers.value = res.message || []
    await renderMarkers()
  } catch (e) {
    console.error('Failed to load customers', e)
  } finally {
    loading.value = false
  }
}


async function initBaseMap() {
  await ensureLeafletCSS()
  const L = await getL()
  const el = document.getElementById('customer-map-view')
  if (!el) return null
  if (mapInstance) { mapInstance.invalidateSize(); return mapInstance }
  const map = L.map(el)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map)
  map.setView([1.3733, 32.2903], 8)
  mapInstance = map
  window.setTimeout(() => map.invalidateSize(), 100)
  return map
}

function markerColor(c) {
  if (isOverdue(c)) return '#ef4444'      // red — overdue
  if (!c.custom_last_visit_date) return '#9ca3af'  // gray — never visited
  if (isDueSoon(c)) return '#f59e0b'      // amber — due soon
  return '#22c55e'                         // green — visited recently
}

async function renderMarkers() {
  const L = await getL()
  const map = await initBaseMap()
  if (!map) return
  
  if (markersLayer) { map.removeLayer(markersLayer); markersLayer = null }
  const group = L.layerGroup().addTo(map)
  markersLayer = group

  const toRender = visibleCustomers.value.filter(c => c.custom_latitude && c.custom_longitude)

  toRender.forEach(c => {
    const color = markerColor(c)
    const icon = L.divIcon({
      className: '',
      iconSize: [12, 12],
      iconAnchor: [6, 6],
      html: `<div style="background:${color};width:12px;height:12px;border-radius:50%;border:2px solid white;box-shadow:0 1px 4px rgba(0,0,0,0.3)" title="${c.customer_name}"></div>`
    })
    const marker = L.marker([c.custom_latitude, c.custom_longitude], { icon })
    marker.bindTooltip(`<b>${c.customer_name}</b><br>${c.territory || ''}`, { permanent: false })
    marker.on('click', () => { selectedCustomer.value = c; customerPanel.value = true })
    group.addLayer(marker)
  })
}

function focusCustomer(c) {
  selectedCustomer.value = c
  if (c.custom_latitude && c.custom_longitude && mapInstance) {
    mapInstance.setView([c.custom_latitude, c.custom_longitude], 16)
  }
  customerPanel.value = true
}

function applyFilters() {
  renderMarkers()
}

watch([search, territoryFilter, groupFilter, repFilter, visitFilter, showNoLocation], () => {
  renderMarkers()
})

const isOverdue = (c) => c.custom_next_visit_due && dayjs(c.custom_next_visit_due).isBefore(dayjs(), 'day')
const isDueSoon = (c) => c.custom_next_visit_due && dayjs(c.custom_next_visit_due).isBefore(dayjs().add(7, 'day'), 'day') && !isOverdue(c)
const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'

onMounted(async () => {
  await load()
})
</script>

<style>
#customer-map-view .leaflet-tile-container img { max-width: none !important; }
#customer-map-view { z-index: 0; }
</style>
