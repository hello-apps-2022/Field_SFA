<template>
  <div class="flex h-full flex-col overflow-hidden">

    <!-- Header -->
    <div class="flex h-[52px] shrink-0 items-center border-b border-gray-100 bg-white px-5 gap-3">
      <h1 class="text-sm font-semibold text-gray-900">Rep Activity Map</h1>
      <div class="flex-1" />
      <Btn icon="refresh-cw" :class="loading ? '[&_svg]:animate-spin' : ''" size="sm" @click="load">Refresh</Btn>
    </div>

    <!-- Controls -->
    <div class="flex shrink-0 flex-wrap items-center gap-2 border-b border-gray-100 bg-white px-4 py-2.5">

      <!-- Rep selector -->
      <select v-model="selectedRep" @change="load"
        class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:border-gray-400 focus:outline-none">
        <option value="">Select Rep…</option>
        <option v-for="r in reps" :key="r.name" :value="r.name">{{ r.name }}</option>
      </select>

      <!-- Date range -->
      <div class="flex items-center gap-1.5">
        <span class="text-xs text-gray-400">From</span>
        <input v-model="dateFrom" type="date" @change="load"
          class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:border-gray-400 focus:outline-none" />
        <span class="text-xs text-gray-400">to</span>
        <input v-model="dateTo" type="date" @change="load"
          class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:border-gray-400 focus:outline-none" />
      </div>

      <!-- Time range -->
      <div class="flex items-center gap-1.5">
        <FeatherIcon name="clock" class="h-3.5 w-3.5 text-gray-400" />
        <input v-model="timeFrom" type="time" @change="load"
          class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:border-gray-400 focus:outline-none" />
        <span class="text-xs text-gray-400">–</span>
        <input v-model="timeTo" type="time" @change="load"
          class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:border-gray-400 focus:outline-none" />
      </div>

      <!-- Quick presets -->
      <div class="flex gap-1">
        <button
          v-for="p in presets" :key="p.label"
          class="h-7 rounded-md px-2.5 text-xs font-medium transition-colors border"
          :class="activePreset === p.label
            ? 'bg-gray-900 text-white border-gray-900'
            : 'bg-white text-gray-600 border-gray-200 hover:border-gray-400'"
          @click="applyPreset(p)"
        >
          {{ p.label }}
        </button>
      </div>

      <div class="flex-1" />

      <!-- Legend -->
      <div class="hidden sm:flex items-center gap-3 text-xs text-gray-400">
        <span class="flex items-center gap-1"><span class="inline-block h-2.5 w-2.5 rounded-full bg-green-500" /> Check-in</span>
        <span class="flex items-center gap-1"><span class="inline-block h-2.5 w-2.5 rounded-full bg-red-500" /> Check-out</span>
        <span class="flex items-center gap-1"><span class="inline-block h-2.5 w-2.5 rounded-full bg-blue-400" /> GPS trail</span>
      </div>
    </div>

    <!-- Summary strip -->
    <div v-if="data" class="flex shrink-0 items-center gap-4 border-b border-gray-100 bg-gray-50 px-5 py-2">
      <div class="flex gap-4 text-sm">
        <span><strong class="text-gray-900">{{ data.visits.length }}</strong> <span class="text-gray-400">visits</span></span>
        <span><strong class="text-green-600">{{ completedCount }}</strong> <span class="text-gray-400">completed</span></span>
        <span><strong class="text-gray-900">{{ data.track_points.length }}</strong> <span class="text-gray-400">GPS points</span></span>
        <span v-if="dateRangeDays > 1"><strong class="text-gray-900">{{ dateRangeDays }}</strong> <span class="text-gray-400">days</span></span>
      </div>
      <div class="flex-1" />
      <!-- Day filter when multi-day -->
      <div v-if="dateRangeDays > 1" class="flex items-center gap-2">
        <span class="text-xs text-gray-400">View day:</span>
        <select v-model="focusDay" @change="renderMap"
          class="h-7 rounded-md border border-gray-200 bg-white px-2 text-xs focus:outline-none">
          <option value="">All days</option>
          <option v-for="d in dayOptions" :key="d.value" :value="d.value">{{ d.label }}</option>
        </select>
      </div>
    </div>

    <!-- Map + sidebar -->
    <div class="flex flex-1 overflow-hidden">

      <!-- Map -->
      <div class="relative flex-1">
        <div id="rep-activity-map" style="height:100%;width:100%;min-height:400px" />

        <!-- Empty / loading overlays -->
        <div v-if="!selectedRep" class="absolute inset-0 flex flex-col items-center justify-center bg-white/90">
          <FeatherIcon name="user" class="h-12 w-12 text-gray-300 mb-3" />
          <p class="text-sm font-medium text-gray-600">Select a rep to view their activity</p>
          <p class="text-xs text-gray-400 mt-1">GPS trail and visits will appear on the map</p>
        </div>
        <div v-else-if="loading" class="absolute inset-0 flex items-center justify-center bg-white/60">
          <FeatherIcon name="loader" class="h-8 w-8 animate-spin text-gray-400" />
        </div>
        <div v-else-if="selectedRep && data && !data.track_points.length && !data.visits.length"
          class="absolute inset-0 flex flex-col items-center justify-center bg-white/80">
          <FeatherIcon name="map-pin" class="h-12 w-12 text-gray-300 mb-3" />
          <p class="text-sm font-medium text-gray-600">No activity in this period</p>
          <p class="text-xs text-gray-400 mt-1">Try a wider date range or different time window</p>
        </div>
      </div>

      <!-- Sidebar: visit timeline -->
      <div class="w-72 shrink-0 flex flex-col overflow-hidden border-l border-gray-100 bg-white">
        <div class="border-b border-gray-100 px-4 py-2.5">
          <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Visit Timeline</p>
          <p v-if="selectedRep" class="text-sm font-medium text-gray-800 mt-0.5">{{ selectedRep }}</p>
          <p class="text-xs text-gray-400">
            {{ formatDate(dateFrom) }}{{ dateTo !== dateFrom ? ' – ' + formatDate(dateTo) : '' }}
            {{ timeFrom !== '00:00' || timeTo !== '23:59' ? ` · ${timeFrom}–${timeTo}` : '' }}
          </p>
        </div>

        <div v-if="sidebarVisits.length" class="flex-1 overflow-y-auto divide-y divide-gray-50">
          <!-- Group by date when multi-day -->
          <template v-if="dateRangeDays > 1">
            <div v-for="group in visitsByDay" :key="group.date">
              <div class="sticky top-0 bg-gray-50 border-b border-gray-100 px-4 py-1.5">
                <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-500">
                  {{ formatDate(group.date) }} · {{ group.visits.length }} visits
                </p>
              </div>
              <div
                v-for="v in group.visits" :key="v.name"
                class="cursor-pointer px-4 py-3 hover:bg-gray-50 transition-colors"
                :class="highlightedVisit === v.name ? 'bg-blue-50 border-l-2 border-blue-500' : ''"
                @click="focusVisit(v)"
              >
                <VisitCard :visit="v" />
              </div>
            </div>
          </template>

          <!-- Single day list -->
          <template v-else>
            <div
              v-for="v in sidebarVisits" :key="v.name"
              class="cursor-pointer px-4 py-3 hover:bg-gray-50 transition-colors"
              :class="highlightedVisit === v.name ? 'bg-blue-50 border-l-2 border-blue-500' : ''"
              @click="focusVisit(v)"
            >
              <VisitCard :visit="v" />
            </div>
          </template>
        </div>

        <div v-else-if="selectedRep && !loading" class="flex flex-1 flex-col items-center justify-center py-12 text-gray-400">
          <FeatherIcon name="calendar" class="h-8 w-8 mb-2" />
          <p class="text-sm">No visits in this period</p>
        </div>

        <div v-else-if="!selectedRep" class="flex flex-1 flex-col items-center justify-center py-12 text-gray-400">
          <p class="text-xs text-center px-4">Select a rep to see their visit timeline</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, defineComponent, h } from 'vue'
import { call } from '@/utils/frappe'
import Btn from '@/components/ui/Btn.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import dayjs from 'dayjs'
import { getL, ensureLeafletCSS } from '@/utils/leaflet'

// Inline VisitCard component
const VisitCard = defineComponent({
  props: { visit: Object },
  setup(props) {
    return () => h('div', { class: 'space-y-0.5' }, [
      h('div', { class: 'flex items-start justify-between gap-2' }, [
        h('div', { class: 'min-w-0 flex-1' }, [
          h('p', { class: 'text-sm font-medium text-gray-900 truncate' }, props.visit.customer),
          props.visit.custom_location_area || props.visit.custom_location_city
            ? h('p', { class: 'text-xs text-gray-400 truncate' },
                [props.visit.custom_location_area, props.visit.custom_location_city].filter(Boolean).join(', '))
            : null,
          h('div', { class: 'flex items-center gap-2 mt-0.5 text-xs text-gray-400' }, [
            props.visit.check_in_time ? h('span', {}, dayjs(props.visit.check_in_time).format('HH:mm')) : null,
            props.visit.check_in_time && props.visit.check_out_time ? h('span', {}, '→') : null,
            props.visit.check_out_time ? h('span', {}, dayjs(props.visit.check_out_time).format('HH:mm')) : null,
            props.visit.duration_minutes ? h('span', { class: 'text-gray-300' }, '·') : null,
            props.visit.duration_minutes ? h('span', {}, `${props.visit.duration_minutes}min`) : null,
          ]),
          props.visit.visit_purpose ? h('p', { class: 'text-xs text-gray-400' }, props.visit.visit_purpose) : null,
        ]),
        h(StatusBadge, { status: props.visit.status }),
      ]),
    ])
  }
})

// State
const selectedRep = ref('')
const dateFrom = ref(dayjs().format('YYYY-MM-DD'))
const dateTo = ref(dayjs().format('YYYY-MM-DD'))
const timeFrom = ref('00:00')
const timeTo = ref('23:59')
const focusDay = ref('')
const reps = ref([])
const data = ref(null)
const loading = ref(false)
const highlightedVisit = ref('')
let mapInstance = null
let layerGroup = null

// Presets
const presets = [
  { label: 'Today', df: () => dayjs().format('YYYY-MM-DD'), dt: () => dayjs().format('YYYY-MM-DD'), tf: '00:00', tt: '23:59' },
  { label: 'Yesterday', df: () => dayjs().subtract(1,'day').format('YYYY-MM-DD'), dt: () => dayjs().subtract(1,'day').format('YYYY-MM-DD'), tf: '00:00', tt: '23:59' },
  { label: 'This Week', df: () => dayjs().startOf('week').format('YYYY-MM-DD'), dt: () => dayjs().format('YYYY-MM-DD'), tf: '00:00', tt: '23:59' },
  { label: 'Last 7 Days', df: () => dayjs().subtract(6,'day').format('YYYY-MM-DD'), dt: () => dayjs().format('YYYY-MM-DD'), tf: '00:00', tt: '23:59' },
  { label: 'Morning', df: () => dateFrom.value, dt: () => dateTo.value, tf: '06:00', tt: '12:00' },
  { label: 'Afternoon', df: () => dateFrom.value, dt: () => dateTo.value, tf: '12:00', tt: '18:00' },
]

const activePreset = ref('Today')

function applyPreset(p) {
  dateFrom.value = p.df()
  dateTo.value = p.dt()
  timeFrom.value = p.tf
  timeTo.value = p.tt
  activePreset.value = p.label
  load()
}

// Computed
const dateRangeDays = computed(() => {
  if (!dateFrom.value || !dateTo.value) return 1
  return dayjs(dateTo.value).diff(dayjs(dateFrom.value), 'day') + 1
})

const completedCount = computed(() =>
  data.value?.visits.filter(v => v.status === 'Completed').length || 0
)

const dayOptions = computed(() => {
  const days = []
  let d = dayjs(dateFrom.value)
  const end = dayjs(dateTo.value)
  while (d.isBefore(end) || d.isSame(end, 'day')) {
    days.push({ value: d.format('YYYY-MM-DD'), label: d.format('ddd D MMM') })
    d = d.add(1, 'day')
  }
  return days
})

const sidebarVisits = computed(() => {
  if (!data.value) return []
  if (focusDay.value) return data.value.visits.filter(v => v.visit_date === focusDay.value)
  return data.value.visits
})

const visitsByDay = computed(() => {
  const grouped = {}
  sidebarVisits.value.forEach(v => {
    const d = v.visit_date
    if (!grouped[d]) grouped[d] = { date: d, visits: [] }
    grouped[d].visits.push(v)
  })
  return Object.values(grouped).sort((a, b) => a.date.localeCompare(b.date))
})

// Load data
async function loadReps() {
  try {
    const res = await call('sfa_core.api.maps.get_active_sales_persons')
    reps.value = res.message || []
  } catch (e) { console.error(e) }
}

async function load() {
  if (!selectedRep.value) return
  loading.value = true
  try {
    const res = await call('sfa_core.api.maps.get_rep_activity', {
      sales_person: selectedRep.value,
      date_from: dateFrom.value,
      date_to: dateTo.value,
      time_from: timeFrom.value,
      time_to: timeTo.value,
    })
    data.value = res.message
    focusDay.value = ''
    await renderMap()
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

// Map

async function initBaseMap() {
  await ensureLeafletCSS()
  const L = await getL()
  const el = document.getElementById('rep-activity-map')
  if (!el) return null
  if (mapInstance) { mapInstance.invalidateSize(); return mapInstance }
  const map = L.map(el)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
  }).addTo(map)
  map.setView([1.3733, 32.2903], 7)
  mapInstance = map
  window.setTimeout(() => map.invalidateSize(), 100)
  return map
}

// Day colors for multi-day view
const DAY_COLORS = ['#3b82f6','#8b5cf6','#f59e0b','#10b981','#ef4444','#ec4899','#06b6d4']

async function renderMap() {
    const map = await initBaseMap()
  if (!map || !data.value) return

  if (layerGroup) { map.removeLayer(layerGroup); layerGroup = null }
  const group = L.layerGroup().addTo(map)
  layerGroup = group

  const visitsToShow = focusDay.value
    ? data.value.visits.filter(v => v.visit_date === focusDay.value)
    : data.value.visits

  const trackToShow = focusDay.value
    ? data.value.track_points.filter(p => p.timestamp?.startsWith(focusDay.value))
    : data.value.track_points

  const allPoints = []
  const isMultiDay = dateRangeDays.value > 1

  // Group track points by day for color coding
  const trackByDay = {}
  trackToShow.forEach(p => {
    const d = p.timestamp ? p.timestamp.substring(0, 10) : 'unknown'
    if (!trackByDay[d]) trackByDay[d] = []
    trackByDay[d].push(p)
  })

  Object.entries(trackByDay).forEach(([day, points], dayIdx) => {
    if (points.length < 2) return
    const color = isMultiDay ? DAY_COLORS[dayIdx % DAY_COLORS.length] : '#3b82f6'
    const coords = points.map(p => [p.latitude, p.longitude])
    L.polyline(coords, { color, weight: 3, opacity: 0.65 }).addTo(group)
    coords.forEach(c => allPoints.push(c))

    // Trail dots
    const step = Math.max(1, Math.floor(points.length / 20))
    for (let i = 0; i < points.length; i += step) {
      const p = points[i]
      const dot = L.circleMarker([p.latitude, p.longitude], {
        radius: 3, fillColor: color, color: 'white', weight: 1, fillOpacity: 0.9,
      })
      const time = p.timestamp ? dayjs(p.timestamp).format('HH:mm') : ''
      const speed = p.speed ? ` · ${(p.speed * 3.6).toFixed(1)}km/h` : ''
      dot.bindTooltip(`${time}${speed}`, { permanent: false })
      group.addLayer(dot)
    }
  })

  // Visit markers
  visitsToShow.forEach((v, i) => {
    if (!v.check_in_latitude || !v.check_in_longitude) return
    const pt = [v.check_in_latitude, v.check_in_longitude]
    allPoints.push(pt)

    const dayIdx = isMultiDay ? dayOptions.value.findIndex(d => d.value === v.visit_date) : 0
    const color = isMultiDay ? DAY_COLORS[dayIdx % DAY_COLORS.length] : '#22c55e'

    const icon = L.divIcon({
      className: '',
      iconSize: [28, 28], iconAnchor: [14, 14],
      html: `<div style="background:${color};width:28px;height:28px;border-radius:50%;border:3px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;color:white">${i + 1}</div>`
    })

    const marker = L.marker(pt, { icon })
    const checkin = v.check_in_time ? dayjs(v.check_in_time).format('HH:mm') : ''
    const checkout = v.check_out_time ? dayjs(v.check_out_time).format('HH:mm') : ''
    marker.bindPopup(`
      <div style="min-width:180px;font-family:inherit">
        <p style="font-weight:600;font-size:13px;margin:0 0 2px">${v.customer}</p>
        <p style="font-size:11px;color:#6b7280;margin:0">${v.visit_purpose || 'Visit'}</p>
        ${isMultiDay ? `<p style="font-size:11px;color:#6b7280;margin:2px 0 0">${dayjs(v.visit_date).format('D MMM')}</p>` : ''}
        <p style="font-size:11px;color:#6b7280;margin:2px 0 0">${checkin}${checkout ? ' → ' + checkout : ''}${v.duration_minutes ? ' · ' + v.duration_minutes + 'min' : ''}</p>
        <p style="margin:6px 0 0"><span style="background:${v.status==='Completed'?'#dcfce7':'#f3f4f6'};color:${v.status==='Completed'?'#166534':'#374151'};padding:2px 8px;border-radius:999px;font-size:11px">${v.status}</span></p>
      </div>
    `, { maxWidth: 240 })
    marker.on('click', () => { highlightedVisit.value = v.name })
    group.addLayer(marker)

    // Check-out dot
    if (v.check_out_latitude && v.check_out_longitude) {
      const outIcon = L.divIcon({
        className: '', iconSize: [10, 10], iconAnchor: [5, 5],
        html: `<div style="background:#ef4444;width:10px;height:10px;border-radius:50%;border:2px solid white;box-shadow:0 1px 3px rgba(0,0,0,0.3)"></div>`
      })
      group.addLayer(L.marker([v.check_out_latitude, v.check_out_longitude], { icon: outIcon }))
    }
  })

  if (allPoints.length > 0) {
    map.fitBounds(L.latLngBounds(allPoints).pad(0.15))
  }
}

function focusVisit(v) {
  highlightedVisit.value = v.name
  if (mapInstance && v.check_in_latitude) {
    mapInstance.setView([v.check_in_latitude, v.check_in_longitude], 16)
  }
}

const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'

onMounted(async () => {
  await loadReps()
  initBaseMap()
})
</script>

<style>
#rep-activity-map .leaflet-tile-container img { max-width: none !important; }
#rep-activity-map { z-index: 0; }
</style>
