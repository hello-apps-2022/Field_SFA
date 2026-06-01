<template>
  <div class="flex h-full flex-col overflow-hidden">

    <!-- Header -->
    <div class="flex h-[52px] shrink-0 items-center border-b border-gray-100 bg-white px-5 gap-3">
      <h1 class="text-sm font-semibold text-gray-900">Saved Locations</h1>
      <div class="flex-1" />
      <span class="text-xs text-gray-400">{{ visible.length }} shown</span>
      <Btn icon="refresh-cw" size="sm" @click="load">Refresh</Btn>
      <Btn v-if="canCreate" icon="plus" variant="solid" size="sm" @click="openCreate">Add Location</Btn>
    </div>

    <!-- Filters -->
    <div class="flex shrink-0 flex-wrap items-center gap-2 border-b border-gray-100 bg-white px-4 py-2.5">
      <div class="relative">
        <FeatherIcon name="search" class="absolute left-2.5 top-2 h-3.5 w-3.5 text-gray-400 pointer-events-none" />
        <input v-model="search" type="text" placeholder="Search locations…"
          class="h-8 rounded-md border border-gray-200 bg-white pl-8 pr-3 text-sm focus:border-gray-400 focus:outline-none w-48" />
      </div>
      <select v-model="typeFilter"
        class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
        <option value="">All Types</option>
        <option v-for="t in types" :key="t.option_name" :value="t.option_name">{{ t.option_name }}</option>
      </select>
      <label class="flex items-center gap-1.5 text-xs text-gray-600 cursor-pointer select-none">
        <input type="checkbox" v-model="showInactive" @change="load" class="rounded" />
        Include inactive
      </label>
    </div>

    <!-- Map + list -->
    <div class="flex flex-1 overflow-hidden">
      <div class="relative flex-1">
        <div id="saved-locations-map" style="height:100%;width:100%;min-height:400px" />
        <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-white/60">
          <FeatherIcon name="loader" class="h-8 w-8 animate-spin text-gray-400" />
        </div>
      </div>

      <div class="w-72 shrink-0 flex flex-col border-l border-gray-100 bg-white overflow-hidden">
        <div class="border-b border-gray-100 px-4 py-2.5">
          <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Locations</p>
          <p class="text-xs text-gray-500 mt-0.5">{{ visible.length }} matching</p>
        </div>
        <div class="flex-1 overflow-y-auto divide-y divide-gray-50">
          <div v-for="l in sidebarItems" :key="l.name"
            class="cursor-pointer px-4 py-3 hover:bg-gray-50 transition-colors"
            :class="selected?.name === l.name ? 'bg-blue-50 border-l-2 border-blue-500' : ''"
            @click="focusItem(l)">
            <div class="flex items-start gap-2.5">
              <span class="mt-1 h-2.5 w-2.5 shrink-0 rounded-full" :style="{ background: typeColor(l.location_type) }" />
              <div class="min-w-0 flex-1">
                <p class="text-sm font-medium text-gray-900 truncate" :class="!l.is_active ? 'text-gray-400 line-through' : ''">{{ l.location_name }}</p>
                <p class="text-xs text-gray-400 truncate">{{ l.location_type }}<span v-if="l.linked_customer"> · {{ l.linked_customer }}</span></p>
              </div>
            </div>
          </div>
          <div v-if="!visible.length" class="px-4 py-10 text-center text-xs text-gray-400">No saved locations</div>
          <div v-else-if="sidebarItems.length < visible.length" class="px-4 py-3 text-center text-xs text-gray-400">
            + {{ visible.length - sidebarItems.length }} more — refine filters
          </div>
        </div>
      </div>
    </div>

    <!-- Detail panel (view) -->
    <SlidePanel v-model="detailPanel" :title="selected?.location_name || 'Location'" save-label="">
      <div v-if="selected" class="space-y-4">
        <div class="flex items-center gap-3">
          <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full"
            :style="{ background: typeColor(selected.location_type) + '22' }">
            <FeatherIcon name="map-pin" class="h-5 w-5" :style="{ color: typeColor(selected.location_type) }" />
          </span>
          <div>
            <p class="text-base font-semibold text-gray-900">{{ selected.location_name }}</p>
            <p class="text-xs text-gray-500">{{ selected.location_type }}</p>
          </div>
        </div>
        <div class="rounded-xl border border-gray-200 bg-white overflow-hidden">
          <div class="flex border-b border-gray-50 px-4 py-2.5"><span class="w-28 text-xs text-gray-400">Coordinates</span><span class="text-sm text-gray-800">{{ selected.latitude }}, {{ selected.longitude }}</span></div>
          <div class="flex border-b border-gray-50 px-4 py-2.5"><span class="w-28 text-xs text-gray-400">Accuracy</span><span class="text-sm text-gray-800">{{ selected.accuracy ? selected.accuracy + ' m' : '—' }}</span></div>
          <div class="flex border-b border-gray-50 px-4 py-2.5"><span class="w-28 text-xs text-gray-400">Address</span><span class="text-sm" :class="selected.address ? 'text-gray-800' : 'text-gray-400 italic'">{{ selected.address || 'Not set' }}</span></div>
          <div v-if="selected.linked_customer" class="flex border-b border-gray-50 px-4 py-2.5"><span class="w-28 text-xs text-gray-400">Customer</span><span class="text-sm text-gray-800">{{ selected.linked_customer }}</span></div>
          <div class="flex px-4 py-2.5"><span class="w-28 text-xs text-gray-400">Status</span>
            <span class="text-sm" :class="selected.is_active ? 'text-green-600' : 'text-gray-400'">{{ selected.is_active ? 'Active' : 'Inactive' }}</span>
          </div>
        </div>
        <div v-if="canWrite(selected)" class="flex gap-2">
          <Btn icon="edit-2" class="flex-1" @click="openEdit(selected)">Edit</Btn>
          <Btn :icon="selected.is_active ? 'eye-off' : 'eye'" :variant="selected.is_active ? 'danger' : 'default'"
            class="flex-1" @click="toggleActive(selected)">{{ selected.is_active ? 'Deactivate' : 'Activate' }}</Btn>
        </div>
      </div>
    </SlidePanel>

    <!-- Create / edit panel -->
    <SlidePanel v-model="formPanel" :title="editing ? 'Edit Location' : 'Add Location'"
      :saving="saving" :save-label="editing ? 'Save' : 'Create'" @save="submit">
      <div class="space-y-4">
        <FormField v-model="form.location_name" label="Location Name" required :error="errors.location_name" placeholder="e.g. Nakawa depot gate" />
        <FormField v-model="form.location_type" type="select" label="Type" required :error="errors.location_type"
          :options="types.map(t => ({ value: t.option_name, label: t.option_name }))" placeholder="Select type…" />
        <SearchSelect v-if="form.location_type === 'Customer'" v-model="form.linked_customer"
          label="Linked Customer" :options="customerOptions" placeholder="Search customers…" />
        <div class="grid grid-cols-2 gap-3">
          <FormField v-model="form.latitude" type="number" label="Latitude" required :error="errors.latitude" placeholder="0.3476" />
          <FormField v-model="form.longitude" type="number" label="Longitude" required :error="errors.longitude" placeholder="32.5825" />
        </div>
        <div class="flex items-center gap-2">
          <Btn icon="crosshair" size="sm" @click="useMapCenter">Use map center</Btn>
          <span class="text-xs text-gray-400">Pan the map, then drop the pin at its center.</span>
        </div>
        <FormField v-model="form.accuracy" type="number" label="Accuracy (m)" placeholder="optional" />
        <FormField v-model="form.address" type="textarea" label="Address" placeholder="optional" />
      </div>
    </SlidePanel>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { call, getList } from '@/utils/frappe'
import { auth } from '@/utils/auth'
import { successToast, errorToast } from '@/utils/toast'
import Btn from '@/components/ui/Btn.vue'
import SlidePanel from '@/components/ui/SlidePanel.vue'
import FormField from '@/components/ui/FormField.vue'
import SearchSelect from '@/components/ui/SearchSelect.vue'
import FeatherIcon from '@/components/ui/FeatherIcon.vue'
import { getL, ensureLeafletCSS } from '@/utils/leaflet'

const locations = ref([])
const types = ref([])
const customerOptions = ref([])
const loading = ref(false)
const saving = ref(false)
const search = ref('')
const typeFilter = ref('')
const showInactive = ref(false)
const selected = ref(null)
const detailPanel = ref(false)
const formPanel = ref(false)
const editing = ref(null)
const errors = ref({})
const form = ref({ location_name: '', location_type: '', latitude: '', longitude: '', accuracy: '', address: '', linked_customer: '' })

let mapInstance = null
let markersLayer = null

const canCreate = computed(() => auth.isAdmin || auth.isManager || auth.isRep)
const canWrite = () => auth.isAdmin || auth.isManager || auth.isRep || auth.isSupervisor

const PALETTE = ['#3b82f6', '#8b5cf6', '#ef4444', '#f59e0b', '#14b8a6', '#ec4899', '#6366f1']
const FIXED = { Customer: '#22c55e', Warehouse: '#3b82f6', Office: '#8b5cf6', Competitor: '#ef4444', Other: '#6b7280' }
function typeColor(t) {
  if (FIXED[t]) return FIXED[t]
  let h = 0
  for (const ch of (t || '')) h = (h * 31 + ch.charCodeAt(0)) >>> 0
  return PALETTE[h % PALETTE.length]
}

const visible = computed(() => {
  let l = locations.value
  if (typeFilter.value) l = l.filter(x => x.location_type === typeFilter.value)
  if (search.value) {
    const q = search.value.toLowerCase()
    l = l.filter(x => (x.location_name || '').toLowerCase().includes(q) || (x.address || '').toLowerCase().includes(q))
  }
  return l
})
const sidebarItems = computed(() => visible.value.slice(0, 100))

async function load() {
  loading.value = true
  try {
    const [locRes, typeRes] = await Promise.all([
      call('sfa_core.api.saved_location.get_saved_locations', { is_active: showInactive.value ? 'all' : 1, page_length: 1000 }),
      call('sfa_core.api.saved_location.get_location_types'),
    ])
    locations.value = (locRes.message && locRes.message.items) || []
    types.value = typeRes.message || []
    await renderMarkers()
  } catch (e) { errorToast(e.message || 'Failed to load') }
  finally { loading.value = false }
}

async function initBaseMap() {
  await ensureLeafletCSS()
  const L = await getL()
  const el = document.getElementById('saved-locations-map')
  if (!el) return null
  if (mapInstance) { mapInstance.invalidateSize(); return mapInstance }
  const map = L.map(el)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OpenStreetMap contributors' }).addTo(map)
  map.setView([1.3733, 32.2903], 7)
  mapInstance = map
  window.setTimeout(() => map.invalidateSize(), 100)
  return map
}

async function renderMarkers() {
  const L = await getL()
  const map = await initBaseMap()
  if (!map) return
  if (markersLayer) { map.removeLayer(markersLayer); markersLayer = null }
  const group = L.layerGroup().addTo(map)
  markersLayer = group
  visible.value.filter(l => l.latitude && l.longitude).forEach(l => {
    const color = typeColor(l.location_type)
    const icon = L.divIcon({
      className: '', iconSize: [14, 14], iconAnchor: [7, 7],
      html: `<div style="background:${color};width:14px;height:14px;border-radius:50%;border:2px solid white;box-shadow:0 1px 4px rgba(0,0,0,0.3);opacity:${l.is_active ? 1 : 0.4}"></div>`,
    })
    const marker = L.marker([l.latitude, l.longitude], { icon })
    marker.bindTooltip(`<b>${l.location_name}</b><br>${l.location_type || ''}`, { permanent: false })
    marker.on('click', () => { selected.value = l; detailPanel.value = true })
    group.addLayer(marker)
  })
}

function focusItem(l) {
  selected.value = l
  if (l.latitude && l.longitude && mapInstance) mapInstance.setView([l.latitude, l.longitude], 16)
  detailPanel.value = true
}

function blankForm() {
  return { location_name: '', location_type: '', latitude: '', longitude: '', accuracy: '', address: '', linked_customer: '' }
}

async function ensureCustomers() {
  if (customerOptions.value.length) return
  try {
    const rows = await getList('Customer', { fields: ['name', 'customer_name'], orderBy: 'customer_name asc', limit: 500 })
    customerOptions.value = rows.map(r => ({ value: r.name, label: r.customer_name || r.name }))
  } catch (e) { /* non-fatal */ }
}

function openCreate() {
  editing.value = null
  errors.value = {}
  form.value = blankForm()
  if (mapInstance) {
    const c = mapInstance.getCenter()
    form.value.latitude = +c.lat.toFixed(6)
    form.value.longitude = +c.lng.toFixed(6)
  }
  ensureCustomers()
  detailPanel.value = false
  formPanel.value = true
}

function openEdit(l) {
  editing.value = l.name
  errors.value = {}
  form.value = {
    location_name: l.location_name, location_type: l.location_type,
    latitude: l.latitude, longitude: l.longitude, accuracy: l.accuracy || '',
    address: l.address || '', linked_customer: l.linked_customer || '',
  }
  ensureCustomers()
  detailPanel.value = false
  formPanel.value = true
}

function useMapCenter() {
  if (!mapInstance) return
  const c = mapInstance.getCenter()
  form.value.latitude = +c.lat.toFixed(6)
  form.value.longitude = +c.lng.toFixed(6)
}

function validate() {
  const e = {}
  if (!form.value.location_name) e.location_name = 'Required'
  if (!form.value.location_type) e.location_type = 'Required'
  if (form.value.latitude === '' || form.value.latitude === null) e.latitude = 'Required'
  if (form.value.longitude === '' || form.value.longitude === null) e.longitude = 'Required'
  errors.value = e
  return !Object.keys(e).length
}

async function submit() {
  if (!validate()) return
  saving.value = true
  const payload = {
    location_name: form.value.location_name,
    location_type: form.value.location_type,
    latitude: form.value.latitude,
    longitude: form.value.longitude,
    accuracy: form.value.accuracy || null,
    address: form.value.address || null,
    linked_customer: form.value.location_type === 'Customer' ? (form.value.linked_customer || null) : null,
  }
  try {
    if (editing.value) {
      await call('sfa_core.api.saved_location.update_saved_location', { name: editing.value, ...payload })
      successToast('Location updated')
    } else {
      await call('sfa_core.api.saved_location.create_saved_location', payload)
      successToast('Location added')
    }
    formPanel.value = false
    await load()
  } catch (e) { errorToast(e.message || 'Save failed') }
  finally { saving.value = false }
}

async function toggleActive(l) {
  try {
    await call('sfa_core.api.saved_location.set_saved_location_active', { name: l.name, is_active: l.is_active ? 0 : 1 })
    successToast(l.is_active ? 'Location deactivated' : 'Location activated')
    detailPanel.value = false
    await load()
  } catch (e) { errorToast(e.message || 'Failed') }
}

watch([search, typeFilter], renderMarkers)

onMounted(load)
</script>

<style>
#saved-locations-map .leaflet-tile-container img { max-width: none !important; }
#saved-locations-map { z-index: 0; }
</style>
