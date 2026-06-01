<template>
  <div class="flex h-full flex-col overflow-hidden">

    <!-- Header -->
    <div class="flex h-[52px] shrink-0 items-center border-b border-gray-100 bg-white px-5 gap-3">
      <h1 class="text-sm font-semibold text-gray-900">Leads</h1>
      <div class="flex-1" />
      <span class="text-xs text-gray-400">{{ visible.length }} shown</span>
      <Btn icon="refresh-cw" size="sm" @click="load">Refresh</Btn>
      <Btn icon="plus" variant="solid" size="sm" @click="openCreate">Add Lead</Btn>
    </div>

    <!-- Filters -->
    <div class="flex shrink-0 flex-wrap items-center gap-2 border-b border-gray-100 bg-white px-4 py-2.5">
      <div class="relative">
        <FeatherIcon name="search" class="absolute left-2.5 top-2 h-3.5 w-3.5 text-gray-400 pointer-events-none" />
        <input v-model="search" type="text" placeholder="Search leads…"
          class="h-8 rounded-md border border-gray-200 bg-white pl-8 pr-3 text-sm focus:border-gray-400 focus:outline-none w-48" />
      </div>
      <select v-model="statusFilter" @change="load"
        class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
        <option value="">All Statuses</option>
        <option v-for="s in STATUSES" :key="s" :value="s">{{ s }}</option>
      </select>
      <select v-if="isManager" v-model="repFilter" @change="load"
        class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
        <option value="">All Reps</option>
        <option v-for="r in salesPersons" :key="r.value" :value="r.value">{{ r.label }}</option>
      </select>
      <select v-model="convertedFilter" @change="load"
        class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
        <option value="">All</option>
        <option value="0">Not converted</option>
        <option value="1">Converted</option>
      </select>
      <label class="flex items-center gap-1.5 text-xs text-gray-600 cursor-pointer select-none">
        <input type="checkbox" v-model="showNoGps" class="rounded" /> Include without GPS
      </label>
    </div>

    <!-- Map + list -->
    <div class="flex flex-1 overflow-hidden">
      <div class="relative flex-1">
        <div id="leads-map" style="height:100%;width:100%;min-height:400px" />
        <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-white/60">
          <FeatherIcon name="loader" class="h-8 w-8 animate-spin text-gray-400" />
        </div>
      </div>

      <div class="w-80 shrink-0 flex flex-col border-l border-gray-100 bg-white overflow-hidden">
        <div class="border-b border-gray-100 px-4 py-2.5">
          <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Leads</p>
          <p class="text-xs text-gray-500 mt-0.5">{{ visible.length }} matching</p>
        </div>
        <div class="flex-1 overflow-y-auto divide-y divide-gray-50">
          <div v-for="l in sidebarItems" :key="l.name"
            class="cursor-pointer px-4 py-3 hover:bg-gray-50 transition-colors"
            :class="selected?.name === l.name ? 'bg-blue-50 border-l-2 border-blue-500' : ''"
            @click="focusItem(l)">
            <div class="flex items-start justify-between gap-2">
              <div class="min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">{{ l.lead_name }}</p>
                <p class="text-xs text-gray-400 truncate">
                  {{ [l.company_name, l.territory].filter(Boolean).join(' · ') || l.mobile_no || '—' }}
                </p>
                <div class="mt-1 flex items-center gap-1.5">
                  <span class="rounded-full px-1.5 py-0.5 text-[10px] font-medium" :style="badgeStyle(l.custom_sfa_status)">{{ l.custom_sfa_status || 'New' }}</span>
                  <span v-if="l.customer" class="rounded-full bg-green-50 px-1.5 py-0.5 text-[10px] text-green-600">Customer</span>
                </div>
              </div>
              <FeatherIcon v-if="!l.custom_sfa_latitude" name="map-pin" class="h-3.5 w-3.5 shrink-0 text-gray-300" title="No GPS" />
            </div>
          </div>
          <div v-if="!visible.length" class="px-4 py-10 text-center text-xs text-gray-400">No leads</div>
          <div v-else-if="sidebarItems.length < visible.length" class="px-4 py-3 text-center text-xs text-gray-400">
            + {{ visible.length - sidebarItems.length }} more — refine filters
          </div>
        </div>
      </div>
    </div>

    <!-- Detail panel -->
    <SlidePanel v-model="detailPanel" :title="selected?.lead_name || 'Lead'" save-label="">
      <div v-if="selected" class="space-y-4">
        <div class="flex items-center gap-3">
          <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-base font-semibold text-indigo-700">
            {{ (selected.lead_name || '?').charAt(0).toUpperCase() }}
          </span>
          <div class="min-w-0">
            <p class="text-base font-semibold text-gray-900 truncate">{{ selected.lead_name }}</p>
            <p class="text-xs text-gray-500">{{ selected.company_name || selected.territory || '—' }}</p>
          </div>
        </div>

        <div class="rounded-xl border border-gray-200 bg-white overflow-hidden">
          <div class="flex border-b border-gray-50 px-4 py-2.5"><span class="w-28 text-xs text-gray-400">Mobile</span><span class="text-sm" :class="selected.mobile_no?'text-gray-800':'text-gray-400 italic'">{{ selected.mobile_no || 'Not set' }}</span></div>
          <div class="flex border-b border-gray-50 px-4 py-2.5"><span class="w-28 text-xs text-gray-400">Email</span><span class="text-sm" :class="selected.email_id?'text-gray-800':'text-gray-400 italic'">{{ selected.email_id || 'Not set' }}</span></div>
          <div class="flex border-b border-gray-50 px-4 py-2.5"><span class="w-28 text-xs text-gray-400">Territory</span><span class="text-sm text-gray-800">{{ selected.territory || '—' }}</span></div>
          <div class="flex border-b border-gray-50 px-4 py-2.5"><span class="w-28 text-xs text-gray-400">Rep</span><span class="text-sm" :class="selected.custom_sfa_rep?'text-gray-800':'text-gray-400 italic'">{{ selected.custom_sfa_rep || 'Unassigned' }}</span></div>
          <div class="flex px-4 py-2.5"><span class="w-28 text-xs text-gray-400">Source</span><span class="text-sm text-gray-800">{{ selected.source || '—' }}</span></div>
        </div>

        <!-- Converted state -->
        <div v-if="selected.customer" class="rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">
          Converted to customer <span class="font-medium">{{ selected.customer }}</span>.
        </div>

        <template v-else>
          <!-- Status progression -->
          <div>
            <label class="mb-1.5 block text-xs font-medium text-gray-600">Status</label>
            <select :value="selected.custom_sfa_status || 'New'" @change="changeStatus($event.target.value)"
              class="w-full h-9 rounded-lg border border-gray-200 bg-white px-3 text-sm focus:border-gray-400 focus:outline-none">
              <option v-for="s in STATUSES" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>

          <!-- Reassign (managers) -->
          <SearchSelect v-if="isManager" :model-value="selected.custom_sfa_rep || ''" @update:model-value="reassign"
            label="Assign Rep" :options="salesPersons" placeholder="Search reps…" />

          <div class="flex gap-2 pt-1">
            <Btn icon="edit-2" class="flex-1" @click="openEdit(selected)">Edit</Btn>
            <Btn icon="user-check" variant="solid" class="flex-1" @click="openConvert(selected)">Convert</Btn>
          </div>
        </template>
      </div>
    </SlidePanel>

    <!-- Create / edit panel -->
    <SlidePanel v-model="formPanel" :title="editing ? 'Edit Lead' : 'Add Lead'"
      :saving="saving" :save-label="editing ? 'Save' : 'Create'" @save="submit">
      <div class="space-y-4">
        <FormField v-model="form.lead_name" label="Lead / Outlet Name" required :error="errors.lead_name" placeholder="e.g. Mama Kevin's Shop" />
        <FormField v-model="form.company_name" label="Company / Business" placeholder="optional" />
        <div class="grid grid-cols-2 gap-3">
          <FormField v-model="form.mobile_no" label="Mobile" placeholder="optional" />
          <FormField v-model="form.email_id" type="email" label="Email" placeholder="optional" />
        </div>
        <FormField v-model="form.territory" type="select" label="Territory" :options="territoryOptions" placeholder="Select territory…" />
        <FormField v-model="form.source" label="Source" placeholder="e.g. Walk-in, Referral" />
        <SearchSelect v-if="isManager" v-model="form.sales_person" label="Assign Rep" :options="salesPersons" placeholder="Search reps…" />
        <div class="grid grid-cols-2 gap-3">
          <FormField v-model="form.latitude" type="number" label="Latitude" placeholder="optional" />
          <FormField v-model="form.longitude" type="number" label="Longitude" placeholder="optional" />
        </div>
      </div>
    </SlidePanel>

    <!-- Convert confirm -->
    <Teleport to="body">
      <div v-if="convertTarget" class="fixed inset-0 z-[70] flex items-center justify-center bg-black/30 backdrop-blur-sm">
        <div class="w-96 rounded-2xl border border-gray-200 bg-white p-6 shadow-2xl">
          <p class="text-sm font-semibold text-gray-900">Convert "{{ convertTarget.lead_name }}" to a customer?</p>
          <p class="mt-1.5 text-sm text-gray-500">This creates a Customer, links it back to the lead, and marks the lead Converted.</p>
          <div class="mt-4">
            <label class="mb-1.5 block text-xs font-medium text-gray-600">Customer Group</label>
            <select v-model="convertGroup"
              class="w-full h-9 rounded-lg border border-gray-200 bg-white px-3 text-sm focus:border-gray-400 focus:outline-none">
              <option value="">Default</option>
              <option v-for="g in customerGroups" :key="g" :value="g">{{ g }}</option>
            </select>
          </div>
          <div class="mt-5 flex gap-2 justify-end">
            <button class="h-8 rounded-lg border border-gray-200 px-3 text-sm text-gray-600 hover:bg-gray-50" @click="convertTarget = null">Cancel</button>
            <button class="h-8 rounded-lg bg-gray-900 px-4 text-sm font-medium text-white hover:bg-black disabled:opacity-50" :disabled="converting" @click="doConvert">
              {{ converting ? 'Converting…' : 'Convert' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
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

const STATUSES = ['New', 'Contacted', 'Qualified', 'Converted', 'Dropped']
const STATUS_COLOR = { New: '#6b7280', Contacted: '#3b82f6', Qualified: '#f59e0b', Converted: '#22c55e', Dropped: '#ef4444' }

const leads = ref([])
const salesPersons = ref([])
const customerGroups = ref([])
const loading = ref(false)
const saving = ref(false)
const search = ref('')
const statusFilter = ref('')
const repFilter = ref('')
const convertedFilter = ref('')
const showNoGps = ref(true)
const selected = ref(null)
const detailPanel = ref(false)
const formPanel = ref(false)
const editing = ref(null)
const errors = ref({})
const form = ref(blankForm())
const convertTarget = ref(null)
const convertGroup = ref('')
const converting = ref(false)

let mapInstance = null
let markersLayer = null

const isManager = computed(() => auth.isAdmin || auth.isManager)

function blankForm() {
  return { lead_name: '', company_name: '', mobile_no: '', email_id: '', territory: '', source: '', sales_person: '', latitude: '', longitude: '' }
}
function badgeStyle(s) {
  const c = STATUS_COLOR[s] || STATUS_COLOR.New
  return { background: c + '1a', color: c }
}

const territoryOptions = computed(() =>
  [...new Set(leads.value.map(l => l.territory).filter(Boolean))].sort().map(t => ({ value: t, label: t })))

const visible = computed(() => {
  let l = leads.value
  if (!showNoGps.value) l = l.filter(x => x.custom_sfa_latitude && x.custom_sfa_longitude)
  if (search.value) {
    const q = search.value.toLowerCase()
    l = l.filter(x => (x.lead_name || '').toLowerCase().includes(q) ||
      (x.company_name || '').toLowerCase().includes(q) || (x.mobile_no || '').toLowerCase().includes(q))
  }
  return l
})
const sidebarItems = computed(() => visible.value.slice(0, 100))

async function load() {
  loading.value = true
  try {
    const args = { page_length: 500 }
    if (statusFilter.value) args.status = statusFilter.value
    if (repFilter.value) args.rep = repFilter.value
    if (convertedFilter.value) args.converted = convertedFilter.value
    const res = await call('sfa_core.api.leads.get_leads', args)
    leads.value = (res.message && res.message.items) || []
    await renderMarkers()
  } catch (e) { errorToast(e.message || 'Failed to load leads') }
  finally { loading.value = false }
}

async function loadAux() {
  try {
    const sps = await getList('Sales Person', { fields: ['name', 'sales_person_name'], filters: { enabled: 1 }, orderBy: 'sales_person_name asc', limit: 500 })
    salesPersons.value = sps.map(s => ({ value: s.name, label: s.sales_person_name || s.name }))
  } catch (e) { /* non-fatal */ }
  try {
    const gs = await getList('Customer Group', { fields: ['name'], filters: { is_group: 0 }, orderBy: 'name asc', limit: 100 })
    customerGroups.value = gs.map(g => g.name)
  } catch (e) { /* non-fatal */ }
}

async function initBaseMap() {
  await ensureLeafletCSS()
  const L = await getL()
  const el = document.getElementById('leads-map')
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
  visible.value.filter(l => l.custom_sfa_latitude && l.custom_sfa_longitude).forEach(l => {
    const color = STATUS_COLOR[l.custom_sfa_status] || STATUS_COLOR.New
    const icon = L.divIcon({
      className: '', iconSize: [14, 14], iconAnchor: [7, 7],
      html: `<div style="background:${color};width:14px;height:14px;border-radius:50%;border:2px solid white;box-shadow:0 1px 4px rgba(0,0,0,0.3)"></div>`,
    })
    const marker = L.marker([l.custom_sfa_latitude, l.custom_sfa_longitude], { icon })
    marker.bindTooltip(`<b>${l.lead_name}</b><br>${l.custom_sfa_status || 'New'}`, { permanent: false })
    marker.on('click', () => { selected.value = l; detailPanel.value = true })
    group.addLayer(marker)
  })
}

function focusItem(l) {
  selected.value = l
  if (l.custom_sfa_latitude && l.custom_sfa_longitude && mapInstance) mapInstance.setView([l.custom_sfa_latitude, l.custom_sfa_longitude], 16)
  detailPanel.value = true
}

function openCreate() {
  editing.value = null
  errors.value = {}
  form.value = blankForm()
  detailPanel.value = false
  formPanel.value = true
}
function openEdit(l) {
  editing.value = l.name
  errors.value = {}
  form.value = {
    lead_name: l.lead_name, company_name: l.company_name || '', mobile_no: l.mobile_no || '',
    email_id: l.email_id || '', territory: l.territory || '', source: l.source || '',
    sales_person: l.custom_sfa_rep || '', latitude: l.custom_sfa_latitude || '', longitude: l.custom_sfa_longitude || '',
  }
  detailPanel.value = false
  formPanel.value = true
}

async function submit() {
  if (!form.value.lead_name) { errors.value = { lead_name: 'Required' }; return }
  saving.value = true
  const p = {
    lead_name: form.value.lead_name, company_name: form.value.company_name || null,
    mobile_no: form.value.mobile_no || null, email_id: form.value.email_id || null,
    territory: form.value.territory || null, source: form.value.source || null,
    latitude: form.value.latitude || null, longitude: form.value.longitude || null,
  }
  if (isManager.value && form.value.sales_person) p.sales_person = form.value.sales_person
  try {
    if (editing.value) {
      await call('sfa_core.api.leads.update_lead', { name: editing.value, ...p })
      successToast('Lead updated')
    } else {
      await call('sfa_core.api.leads.create_lead', p)
      successToast('Lead added')
    }
    formPanel.value = false
    await load()
  } catch (e) { errorToast(e.message || 'Save failed') }
  finally { saving.value = false }
}

async function changeStatus(status) {
  try {
    await call('sfa_core.api.leads.set_lead_status', { name: selected.value.name, status })
    selected.value.custom_sfa_status = status
    const row = leads.value.find(x => x.name === selected.value.name)
    if (row) row.custom_sfa_status = status
    await renderMarkers()
    successToast(`Status set to ${status}`)
  } catch (e) { errorToast(e.message || 'Failed') }
}

async function reassign(sp) {
  if (!sp || sp === selected.value.custom_sfa_rep) return
  try {
    await call('sfa_core.api.leads.reassign_lead', { name: selected.value.name, sales_person: sp })
    selected.value.custom_sfa_rep = sp
    const row = leads.value.find(x => x.name === selected.value.name)
    if (row) row.custom_sfa_rep = sp
    successToast('Lead reassigned')
  } catch (e) { errorToast(e.message || 'Failed') }
}

function openConvert(l) { convertTarget.value = l; convertGroup.value = '' }
async function doConvert() {
  converting.value = true
  try {
    const res = await call('sfa_core.api.leads.convert_lead', { name: convertTarget.value.name, customer_group: convertGroup.value || null })
    successToast(`Converted to ${res.message.customer}`)
    convertTarget.value = null
    detailPanel.value = false
    await load()
  } catch (e) { errorToast(e.message || 'Convert failed') }
  finally { converting.value = false }
}

watch([search, showNoGps], renderMarkers)

onMounted(async () => { await Promise.all([load(), loadAux()]) })
</script>

<style>
#leads-map .leaflet-tile-container img { max-width: none !important; }
#leads-map { z-index: 0; }
</style>
