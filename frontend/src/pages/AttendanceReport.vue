<template>
  <div class="flex h-full flex-col overflow-hidden">
    <div class="flex h-[52px] shrink-0 items-center border-b border-gray-100 bg-white px-5 gap-3">
      <h1 class="text-sm font-semibold text-gray-900">Attendance Report</h1>
      <div class="flex-1" />
      <span class="text-xs text-gray-400">{{ summary.records }} day records</span>
    </div>

    <!-- Filters -->
    <div class="flex shrink-0 flex-wrap items-center gap-2 border-b border-gray-100 bg-white px-4 py-2.5">
      <div class="relative">
        <FeatherIcon name="search" class="absolute left-2.5 top-2 h-3.5 w-3.5 text-gray-400 pointer-events-none" />
        <input v-model="search" placeholder="Rep name…"
          class="h-8 w-44 rounded-md border border-gray-200 bg-white pl-8 pr-3 text-sm focus:border-gray-400 focus:outline-none" />
      </div>
      <DateRangeFilter v-model:from="dateFrom" v-model:to="dateTo" default-preset="today" @change="load" />
      <button @click="load" class="h-8 rounded-md border border-gray-200 bg-white px-3 text-xs text-gray-500 hover:bg-gray-50">Refresh</button>
    </div>

    <!-- Summary -->
    <div v-if="summary.records" class="flex shrink-0 items-center gap-6 border-b border-gray-100 bg-gray-50 px-5 py-2 text-sm">
      <span v-if="summary.working_now" class="inline-flex items-center gap-1.5">
        <span class="relative flex h-2 w-2">
          <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-400 opacity-75"></span>
          <span class="relative inline-flex h-2 w-2 rounded-full bg-green-500"></span>
        </span>
        <strong class="text-gray-900">{{ summary.working_now }}</strong> <span class="text-gray-400">on the clock</span>
      </span>
      <span><strong class="text-gray-900">{{ summary.present }}</strong> <span class="text-gray-400">present</span></span>
      <span><strong class="text-gray-900">{{ summary.records }}</strong> <span class="text-gray-400">day records</span></span>
    </div>

    <!-- Table -->
    <div class="flex-1 overflow-auto">
      <div v-if="loading" class="flex h-40 items-center justify-center">
        <FeatherIcon name="loader" class="h-6 w-6 animate-spin text-gray-400" />
      </div>
      <table v-else-if="filtered.length" class="w-full text-sm">
        <thead class="sticky top-0 z-10 bg-white border-b border-gray-100">
          <tr>
            <th class="w-8"></th>
            <th class="px-3 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Date</th>
            <th class="px-3 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Rep</th>
            <th class="px-3 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Status</th>
            <th class="px-3 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Start</th>
            <th class="px-3 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">End</th>
            <th class="px-3 py-2.5 text-right text-[10px] font-semibold uppercase tracking-wide text-gray-400">Hours</th>
            <th class="px-3 py-2.5 text-center text-[10px] font-semibold uppercase tracking-wide text-gray-400">Sessions</th>
            <th class="px-3 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Focus &amp; priorities</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <template v-for="r in filtered" :key="rowKey(r)">
            <tr class="hover:bg-gray-50 align-top cursor-pointer" @click="toggle(r)">
              <td class="pl-4 py-2.5 text-gray-400">
                <FeatherIcon :name="expanded.has(rowKey(r)) ? 'chevron-down' : 'chevron-right'" class="h-4 w-4" />
              </td>
              <td class="px-3 py-2.5 text-gray-500 whitespace-nowrap">{{ r.date }}</td>
              <td class="px-3 py-2.5 font-medium text-gray-900 whitespace-nowrap">{{ r.employee_name }}</td>
              <td class="px-3 py-2.5 whitespace-nowrap">
                <span class="inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs font-medium" :class="badge(r.status).cls">
                  <span v-if="r.status === 'working'" class="relative flex h-1.5 w-1.5">
                    <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-400 opacity-75"></span>
                    <span class="relative inline-flex h-1.5 w-1.5 rounded-full bg-green-500"></span>
                  </span>
                  {{ badge(r.status).label }}
                </span>
              </td>
              <td class="px-3 py-2.5 whitespace-nowrap">
                <span v-if="r.check_in" class="text-gray-700">{{ fmtTime(r.check_in) }}</span>
                <FeatherIcon v-if="r.check_in_lat" name="map-pin" class="ml-1 inline h-3 w-3 text-gray-400" />
                <span v-if="!r.check_in" class="text-gray-300">—</span>
              </td>
              <td class="px-3 py-2.5 whitespace-nowrap">
                <span v-if="r.check_out" class="text-gray-700">{{ fmtTime(r.check_out) }}</span>
                <FeatherIcon v-if="r.check_out_lat" name="map-pin" class="ml-1 inline h-3 w-3 text-gray-400" />
                <span v-else-if="r.status === 'working'" class="text-green-600">active</span>
                <span v-else-if="r.status === 'open'" class="text-amber-600">no clock-out</span>
                <span v-else class="text-gray-300">—</span>
              </td>
              <td class="px-3 py-2.5 text-right text-gray-700 whitespace-nowrap">{{ r.hours != null ? r.hours : '—' }}</td>
              <td class="px-3 py-2.5 text-center text-gray-500">{{ r.session_count || '—' }}</td>
              <td class="px-3 py-2.5 text-gray-600">
                <div v-if="focusOf(r).length" class="mb-1 flex flex-wrap gap-1">
                  <span v-for="f in focusOf(r)" :key="f" class="rounded-full bg-gray-100 px-2 py-0.5 text-[11px] text-gray-600">{{ f }}</span>
                </div>
                <span v-if="r.priorities" class="whitespace-pre-line text-xs">{{ r.priorities }}</span>
                <span v-if="!r.priorities && !focusOf(r).length" class="text-gray-300">—</span>
              </td>
            </tr>
            <!-- Expanded: map + session breakdown -->
            <tr v-if="expanded.has(rowKey(r))" class="bg-gray-50/60">
              <td></td>
              <td colspan="8" class="px-3 pb-3 pt-1">
                <div class="grid gap-3 md:grid-cols-2">
                  <!-- Where attendance was marked -->
                  <div class="rounded-lg border border-gray-200 bg-white overflow-hidden">
                    <div class="flex items-center justify-between border-b border-gray-100 px-3 py-1.5">
                      <span class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Where it was marked</span>
                      <span v-if="places[rowKey(r)]" class="truncate pl-2 text-[11px] text-gray-500">{{ places[rowKey(r)] }}</span>
                    </div>
                    <div v-if="hasGps(r)" :id="'att-map-' + rowKey(r)" class="h-48 w-full bg-gray-100"></div>
                    <div v-else class="flex h-48 flex-col items-center justify-center px-4 text-center text-gray-400">
                      <FeatherIcon name="map-pin" class="h-6 w-6" />
                      <p class="mt-2 text-xs">No GPS captured for these punches</p>
                      <p class="mt-0.5 text-[11px] text-gray-300">Location needs HTTPS or the mobile app to be recorded.</p>
                    </div>
                  </div>

                  <!-- Sessions -->
                  <div class="rounded-lg border border-gray-200 bg-white">
                    <div class="border-b border-gray-100 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-wide text-gray-400">
                      Sessions ({{ r.sessions.length }})
                    </div>
                    <ul class="max-h-[220px] divide-y divide-gray-50 overflow-y-auto">
                      <li v-for="(s, si) in r.sessions" :key="si" class="flex items-center gap-2.5 px-3 py-2 text-sm">
                        <span class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-gray-100 text-[11px] font-medium text-gray-500">{{ si + 1 }}</span>
                        <span class="font-medium text-gray-900 whitespace-nowrap">{{ fmtTime(s.in_time) }}</span>
                        <a v-if="s.in_lat" :href="mapUrl(s.in_lat, s.in_lng)" target="_blank" class="text-xs text-blue-600 hover:underline" @click.stop>map</a>
                        <FeatherIcon name="arrow-right" class="h-3.5 w-3.5 text-gray-300" />
                        <template v-if="s.open">
                          <span class="inline-flex items-center gap-1 whitespace-nowrap font-medium text-green-600">
                            <span class="relative flex h-1.5 w-1.5">
                              <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-400 opacity-75"></span>
                              <span class="relative inline-flex h-1.5 w-1.5 rounded-full bg-green-500"></span>
                            </span>
                            on the clock
                          </span>
                        </template>
                        <template v-else>
                          <span class="font-medium text-gray-900 whitespace-nowrap">{{ fmtTime(s.out_time) }}</span>
                          <a v-if="s.out_lat" :href="mapUrl(s.out_lat, s.out_lng)" target="_blank" class="text-xs text-blue-600 hover:underline" @click.stop>map</a>
                        </template>
                        <div class="flex-1" />
                        <span v-if="!s.open" class="whitespace-nowrap text-gray-400">{{ s.hours }}h</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
      <div v-else class="flex h-40 flex-col items-center justify-center text-gray-400">
        <FeatherIcon name="calendar" class="h-8 w-8" />
        <p class="mt-2 text-sm">No attendance in this range</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { call } from '@/utils/frappe'
import { show_alert } from '@/frappe'
import { getL, ensureLeafletCSS } from '@/utils/leaflet'
import FeatherIcon from '@/components/ui/FeatherIcon.vue'
import DateRangeFilter from '@/components/ui/DateRangeFilter.vue'

const rows = ref([])
const summary = ref({ records: 0, present: 0, working_now: 0 })
const loading = ref(false)
const search = ref('')
const dateFrom = ref('')
const dateTo = ref('')
const expanded = ref(new Set())
const places = ref({})
const mapInstances = {}

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return rows.value
  return rows.value.filter(r => (r.employee_name || '').toLowerCase().includes(q))
})

const BADGES = {
  working: { label: 'On the clock', cls: 'bg-green-50 text-green-700' },
  open: { label: 'No clock-out', cls: 'bg-amber-50 text-amber-700' },
  ended: { label: 'Done', cls: 'bg-gray-100 text-gray-500' },
}
function badge(s) { return BADGES[s] || BADGES.ended }
function rowKey(r) { return r.employee + '|' + r.date }
function focusOf(r) { return (r.focus || '').split(',').map(s => s.trim()).filter(Boolean) }
function hasGps(r) { return (r.sessions || []).some(s => s.in_lat != null || s.out_lat != null) }
function fmtTime(t) {
  if (!t) return ''
  return new Date(String(t).replace(' ', 'T')).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })
}
function mapUrl(lat, lng) { return `https://www.google.com/maps?q=${lat},${lng}` }

function destroyMap(key) {
  if (mapInstances[key]) { mapInstances[key].remove(); delete mapInstances[key] }
}
function destroyAllMaps() { Object.keys(mapInstances).forEach(destroyMap) }

async function toggle(r) {
  const key = rowKey(r)
  const next = new Set(expanded.value)
  if (next.has(key)) {
    next.delete(key)
    expanded.value = next
    destroyMap(key)
  } else {
    next.add(key)
    expanded.value = next
    if (hasGps(r)) {
      await nextTick()
      drawMap(r, key)
    }
  }
}

async function drawMap(r, key) {
  await ensureLeafletCSS()
  const L = await getL()
  const el = document.getElementById('att-map-' + key)
  if (!el || mapInstances[key]) return

  const icon = (color) => L.divIcon({
    className: '', iconSize: [16, 16], iconAnchor: [8, 8],
    html: `<div style="background:${color};width:16px;height:16px;border-radius:50%;border:3px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.4)"></div>`,
  })

  const map = L.map(el, { scrollWheelZoom: false })
  mapInstances[key] = map
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OSM' }).addTo(map)

  const pts = []
  r.sessions.forEach((s, i) => {
    if (s.in_lat != null) {
      L.marker([s.in_lat, s.in_lng], { icon: icon('#16a34a') }).addTo(map)
        .bindPopup(`<b>Session ${i + 1} · start</b><br>${fmtTime(s.in_time)}`)
      pts.push([s.in_lat, s.in_lng])
    }
    if (!s.open && s.out_lat != null) {
      L.marker([s.out_lat, s.out_lng], { icon: icon('#dc2626') }).addTo(map)
        .bindPopup(`<b>Session ${i + 1} · end</b><br>${fmtTime(s.out_time)}`)
      pts.push([s.out_lat, s.out_lng])
    }
  })

  if (pts.length === 1) map.setView(pts[0], 16)
  else if (pts.length > 1) map.fitBounds(pts, { padding: [30, 30], maxZoom: 17 })
  window.setTimeout(() => map.invalidateSize(), 100)

  if (pts.length && !places.value[key]) reverseGeocode(pts[0][0], pts[0][1], key)
}

async function reverseGeocode(lat, lng, key) {
  try {
    const res = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=16&addressdetails=1`,
      { headers: { 'Accept-Language': 'en' } }
    )
    const data = await res.json()
    const a = data.address || {}
    const label = [a.suburb || a.neighbourhood || a.village || a.hamlet, a.city || a.town || a.county].filter(Boolean).join(', ')
    places.value = { ...places.value, [key]: label || data.display_name || `${(+lat).toFixed(5)}, ${(+lng).toFixed(5)}` }
  } catch (e) {
    places.value = { ...places.value, [key]: `${(+lat).toFixed(5)}, ${(+lng).toFixed(5)}` }
  }
}

async function load() {
  loading.value = true
  destroyAllMaps()
  expanded.value = new Set()
  places.value = {}
  try {
    const res = (await call('sfa_core.api.attendance.get_attendance_report', {
      date_from: dateFrom.value || null,
      date_to: dateTo.value || null,
    })).message
    rows.value = (res && res.rows) || []
    summary.value = (res && res.summary) || { records: 0, present: 0, working_now: 0 }
  } catch (e) {
    show_alert({ message: e.message || 'Could not load report', indicator: 'red' })
  } finally {
    loading.value = false
  }
}

onMounted(load)
onBeforeUnmount(destroyAllMaps)
</script>
