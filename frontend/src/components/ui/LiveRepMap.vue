<template>
  <div class="rounded-xl border border-gray-200 bg-white overflow-hidden">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-gray-100 px-4 py-3">
      <div class="flex items-center gap-2">
        <p class="text-sm font-semibold text-gray-900">Live Rep Locations</p>
        <!-- Live pulse indicator -->
        <span class="flex items-center gap-1.5">
          <span class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
          </span>
          <span class="text-xs text-gray-400">Live · updates every 60s</span>
        </span>
      </div>
      <div class="flex items-center gap-2">
        <!-- Rep count pills -->
        <span v-if="visiting.length" class="rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-700">
          {{ visiting.length }} visiting
        </span>
        <span v-if="active.length" class="rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-700">
          {{ active.length }} active
        </span>
        <button @click="load" class="flex h-7 w-7 items-center justify-center rounded-md text-gray-400 hover:bg-gray-100 hover:text-gray-700">
          <FeatherIcon name="refresh-cw" class="h-3.5 w-3.5" :class="loading ? 'animate-spin' : ''" />
        </button>
        <router-link to="/rep-activity-map"
          class="flex items-center gap-1 text-xs text-blue-500 hover:underline">
          Full map →
        </router-link>
      </div>
    </div>

    <!-- Map + sidebar -->
    <div class="flex" style="height: 320px">

      <!-- Map -->
      <div class="relative flex-1">
        <div id="dashboard-live-map" style="height:100%;width:100%" />

        <!-- Empty state -->
        <div v-if="!loading && reps.length === 0"
          class="absolute inset-0 flex flex-col items-center justify-center bg-white/90">
          <FeatherIcon name="map-pin" class="h-10 w-10 text-gray-300 mb-3" />
          <p class="text-sm font-medium text-gray-500">No rep locations available</p>
          <p class="text-xs text-gray-400 mt-1">Locations update when reps check in via mobile app</p>
        </div>

        <!-- Loading -->
        <div v-if="loading && reps.length === 0"
          class="absolute inset-0 flex items-center justify-center bg-white/60">
          <FeatherIcon name="loader" class="h-6 w-6 animate-spin text-gray-400" />
        </div>
      </div>

      <!-- Rep list sidebar -->
      <div class="w-56 shrink-0 border-l border-gray-100 overflow-y-auto">
        <div v-if="reps.length" class="divide-y divide-gray-50">
          <div
            v-for="rep in repsSorted" :key="rep.name"
            class="flex items-start gap-2.5 px-3 py-2.5 cursor-pointer hover:bg-gray-50 transition-colors"
            @click="focusRep(rep)"
          >
            <!-- Status dot -->
            <div class="mt-0.5 shrink-0 flex flex-col items-center gap-1">
              <div class="h-2.5 w-2.5 rounded-full border-2 border-white shadow-sm"
                :class="{
                  'bg-green-500': rep.status === 'visiting',
                  'bg-blue-400': rep.status === 'active',
                  'bg-gray-300': rep.status === 'inactive',
                }" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-xs font-medium text-gray-900 truncate">{{ rep.name }}</p>
              <p v-if="rep.active_visit" class="text-[10px] text-green-600 truncate">
                @ {{ rep.active_visit.customer }}
              </p>
              <p v-else class="text-[10px] text-gray-400">
                {{ rep.completed_today }}/{{ rep.visits_today }} visits
              </p>
              <p class="text-[10px] text-gray-300">{{ lastSeenLabel(rep.last_seen) }}</p>
            </div>
          </div>
        </div>
        <div v-else class="flex flex-col items-center py-8 text-gray-400">
          <p class="text-xs text-center px-3">No rep data yet</p>
        </div>
      </div>
    </div>

    <!-- Legend -->
    <div class="flex items-center gap-4 border-t border-gray-100 px-4 py-2">
      <span class="flex items-center gap-1.5 text-xs text-gray-400">
        <span class="h-2.5 w-2.5 rounded-full bg-green-500 border-2 border-white shadow-sm" />
        At customer
      </span>
      <span class="flex items-center gap-1.5 text-xs text-gray-400">
        <span class="h-2.5 w-2.5 rounded-full bg-blue-400 border-2 border-white shadow-sm" />
        Moving / active
      </span>
      <span class="flex items-center gap-1.5 text-xs text-gray-400">
        <span class="h-2.5 w-2.5 rounded-full bg-gray-300 border-2 border-white shadow-sm" />
        Inactive today
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { call } from '@/utils/frappe'
import dayjs from 'dayjs'
import { getL, ensureLeafletCSS } from '@/utils/leaflet'
import relativeTime from 'dayjs/plugin/relativeTime'
dayjs.extend(relativeTime)

const reps = ref([])
const loading = ref(false)
let mapInstance = null
let markersLayer = null
let refreshTimer = null

const visiting = computed(() => reps.value.filter(r => r.status === 'visiting'))
const active = computed(() => reps.value.filter(r => r.status === 'active'))
const repsSorted = computed(() => [...reps.value].sort((a, b) => {
  const order = { visiting: 0, active: 1, inactive: 2 }
  return order[a.status] - order[b.status]
}))

async function load() {
  loading.value = true
  try {
    const res = await call('sfa_core.api.dashboard.get_live_reps')
    const msg = res.message
    // Handle both array and object responses
    reps.value = Array.isArray(msg) ? msg : (msg ? Object.values(msg) : [])
    await renderMarkers()
  } catch (e) {
    console.error('Failed to load live reps', e)
  } finally {
    loading.value = false
  }
}


async function initMap() {
  await ensureLeafletCSS()
  const L = await getL()
  const el = document.getElementById('dashboard-live-map')
  if (!el) return null
  if (mapInstance) return mapInstance
  const map = L.map(el, { zoomControl: true })
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
  }).addTo(map)
  map.setView([1.3733, 32.2903], 8)
  mapInstance = map
  return map
}

function repIcon(L, rep) {
  const colors = {
    visiting: { bg: '#22c55e', border: '#16a34a' },
    active: { bg: '#60a5fa', border: '#2563eb' },
    inactive: { bg: '#d1d5db', border: '#9ca3af' },
  }
  const c = colors[rep.status] || colors.inactive
  const initial = (rep.name || '?').charAt(0).toUpperCase()
  return L.divIcon({
    className: '',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    html: `<div style="background:${c.bg};border:2.5px solid ${c.border};width:32px;height:32px;border-radius:50%;box-shadow:0 2px 6px rgba(0,0,0,0.25);display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:white;font-family:inherit">${initial}</div>`
  })
}

async function renderMarkers() {
  const map = await initMap()
  if (!map) return
  
  if (markersLayer) { map.removeLayer(markersLayer); markersLayer = null }
  const group = L.layerGroup().addTo(map)
  markersLayer = group

  const bounds = []
  reps.value.forEach(rep => {
    if (!rep.latitude || !rep.longitude) return
    const pt = [rep.latitude, rep.longitude]
    bounds.push(pt)

    const marker = L.marker(pt, { icon: repIcon(L, rep) })

    const visitInfo = rep.active_visit
      ? `<p style="font-size:11px;color:#16a34a;margin:2px 0 0">@ ${rep.active_visit.customer}</p>`
      : ''
    const statsInfo = `<p style="font-size:11px;color:#6b7280;margin:2px 0 0">${rep.completed_today}/${rep.visits_today} visits today</p>`
    const lastSeen = rep.last_seen
      ? `<p style="font-size:10px;color:#9ca3af;margin:2px 0 0">${lastSeenLabel(rep.last_seen)}</p>`
      : ''
    const speedInfo = rep.speed > 0.5
      ? `<p style="font-size:10px;color:#6b7280;margin:2px 0 0">Moving · ${(rep.speed * 3.6).toFixed(1)} km/h</p>`
      : ''

    marker.bindPopup(`
      <div style="min-width:160px;font-family:inherit">
        <p style="font-weight:600;font-size:13px;margin:0">${rep.name}</p>
        ${rep.territory ? `<p style="font-size:11px;color:#6b7280;margin:2px 0 0">${rep.territory}</p>` : ''}
        ${visitInfo}
        ${statsInfo}
        ${speedInfo}
        ${lastSeen}
      </div>
    `, { maxWidth: 220 })

    group.addLayer(marker)
  })

  if (bounds.length > 0) {
    if (bounds.length === 1) {
      map.setView(bounds[0], 13)
    } else {
      map.fitBounds(L.latLngBounds(bounds).pad(0.2))
    }
  }
}

function focusRep(rep) {
  if (mapInstance && rep.latitude && rep.longitude) {
    mapInstance.setView([rep.latitude, rep.longitude], 14)
  }
}

function lastSeenLabel(ts) {
  if (!ts) return 'Never'
  return dayjs(ts).fromNow()
}

onMounted(async () => {
  await load()
  // Auto-refresh every 60 seconds
  refreshTimer = window.setInterval(load, 60000)
})

onUnmounted(() => {
  if (refreshTimer) window.clearInterval(refreshTimer)
  if (mapInstance) { mapInstance.remove(); mapInstance = null }
})
</script>

<style>
#dashboard-live-map .leaflet-tile-container img { max-width: none !important; }
#dashboard-live-map { z-index: 0; }
</style>
