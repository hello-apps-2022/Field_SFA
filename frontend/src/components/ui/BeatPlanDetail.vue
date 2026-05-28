<template>
  <SlidePanel
    :model-value="modelValue"
    :title="doc?.plan_name || 'Beat Plan'"
    :save-label="hasChanges ? 'Save Changes' : ''"
    :cancel-label="hasChanges ? 'Discard' : 'Close'"
    :cancel-icon="hasChanges ? 'x-circle' : ''"
    width="700px"
    @update:model-value="hasChanges ? null : $emit('update:modelValue', $event)"
    @save="confirmSave"
    @cancel="hasChanges ? confirmDiscard() : $emit('update:modelValue', false)"
  >
    <div v-if="loading" class="flex h-40 items-center justify-center">
      <FeatherIcon name="loader" class="h-6 w-6 animate-spin text-gray-400" />
    </div>

    <div v-else-if="doc" class="space-y-4">

      <!-- Plan meta strip -->
      <div class="flex items-center justify-between rounded-xl border border-gray-200 bg-gray-50 px-4 py-3">
        <div class="space-y-1">
          <div class="flex items-center gap-2">
            <StatusBadge :status="doc.status" />
            <span class="text-xs text-gray-500">
              {{ doc.sales_person || 'No rep' }}
              <span v-if="doc.territory"> · {{ doc.territory }}</span>
            </span>
          </div>
          <p class="text-xs text-gray-400">
            <span v-if="doc.custom_effective_from">From {{ formatDate(doc.custom_effective_from) }}</span>
            <span v-if="doc.custom_effective_to"> → {{ formatDate(doc.custom_effective_to) }}</span>
            <span v-else-if="doc.custom_effective_from"> → ongoing</span>
          </p>
        </div>
        <div class="flex items-center gap-2">
          <span v-if="doc.custom_discovery_count" class="rounded-full bg-green-100 px-2.5 py-1 text-xs font-medium text-green-700">
            {{ doc.custom_discovery_count }} discovered
          </span>
          <button class="text-xs text-blue-500 hover:underline" @click="editPlanPanel = true">Edit</button>
        </div>
      </div>

      <!-- Beats section -->
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-semibold text-gray-900">Beats</h3>
        <Btn icon="plus" size="sm" @click="addBeatPanel = true">Add Beat</Btn>
      </div>

      <!-- Beat cards -->
      <div v-if="doc.custom_beats?.length" class="space-y-3">
        <div v-for="beat in doc.custom_beats" :key="beat.name"
          class="rounded-xl border bg-white overflow-hidden"
          :class="expandedBeat === beat.name ? 'border-gray-900' : 'border-gray-200'"
        >
          <!-- Beat header -->
          <div
            class="flex items-center gap-3 px-4 py-3 cursor-pointer hover:bg-gray-50 transition-colors"
            @click="toggleBeat(beat.name)"
          >
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <p class="text-sm font-semibold text-gray-900">{{ beat.beat_name }}</p>
                <span v-if="beat.area_name" class="text-xs text-gray-400">· {{ beat.area_name }}</span>
              </div>
              <!-- Day chips -->
              <div class="flex gap-1 mt-1.5">
                <span v-for="d in weekDays" :key="d.value"
                  class="rounded px-1.5 py-0.5 text-[10px] font-medium"
                  :class="beat[d.value] ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-300'"
                >
                  {{ d.short }}
                </span>
              </div>
            </div>
            <div class="flex items-center gap-3 shrink-0">
              <span class="text-xs text-gray-400">{{ beat.customers?.length || 0 }} customers</span>
              <FeatherIcon
                :name="expandedBeat === beat.name ? 'chevron-up' : 'chevron-down'"
                class="h-4 w-4 text-gray-400"
              />
            </div>
          </div>

          <!-- Beat customers (expanded) -->
          <div v-if="expandedBeat === beat.name" class="border-t border-gray-100 px-4 py-3 space-y-3">
            <!-- Add customer search -->
            <div class="relative">
              <FeatherIcon name="search" class="absolute left-2.5 top-2 h-3.5 w-3.5 text-gray-400 pointer-events-none" />
              <input
                v-model="customerSearch"
                type="text"
                :placeholder="`Add customer to ${beat.beat_name}…`"
                class="w-full h-8 rounded-md border border-gray-200 bg-white pl-8 pr-3 text-sm focus:border-gray-400 focus:outline-none"
                @input="onSearchInput(beat)"
                @blur="onBlurSearch"
                @focus="showResults = searchResults.length > 0"
              />
              <div v-if="showResults && searchResults.length && activeBeat === beat.name"
                class="absolute top-full left-0 right-0 z-50 mt-1 max-h-48 overflow-y-auto rounded-lg border border-gray-200 bg-white shadow-lg"
              >
                <button
                  v-for="c in searchResults" :key="c.name"
                  class="flex w-full items-center gap-2 px-3 py-2.5 text-left hover:bg-gray-50"
                  @mousedown.prevent="addCustomer(beat, c)"
                >
                  <div class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-[10px] font-bold text-indigo-700">
                    {{ (c.customer_name||'?').charAt(0).toUpperCase() }}
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ c.customer_name }}</p>
                    <p class="text-xs text-gray-400">{{ [c.custom_location_area, c.custom_location_city].filter(Boolean).join(', ') || c.territory }}</p>
                  </div>
                </button>
              </div>
            </div>

            <!-- Customer list — drag to reorder -->
            <div v-if="beat.customers?.length" class="space-y-1">
              <div v-for="(c, i) in sortedCustomers(beat)" :key="c.customer"
                class="flex items-center gap-2 rounded-lg border bg-white px-2 py-2 select-none transition-colors"
                :class="dragOverIndex === i && dragBeat === beat.name
                  ? 'border-blue-400 bg-blue-50 shadow-sm'
                  : 'border-gray-100 hover:border-gray-200'"
                draggable="true"
                @dragstart="onDragStart($event, beat, i)"
                @dragover="onDragOver($event, beat, i)"
                @dragleave="onDragLeave"
                @drop="onDrop($event, beat)"
              >
                <!-- Drag handle -->
                <div class="flex shrink-0 cursor-grab active:cursor-grabbing touch-none px-0.5">
                  <svg width="8" height="14" viewBox="0 0 8 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="2" cy="2" r="1.5" fill="#9ca3af"/>
                    <circle cx="6" cy="2" r="1.5" fill="#9ca3af"/>
                    <circle cx="2" cy="7" r="1.5" fill="#9ca3af"/>
                    <circle cx="6" cy="7" r="1.5" fill="#9ca3af"/>
                    <circle cx="2" cy="12" r="1.5" fill="#9ca3af"/>
                    <circle cx="6" cy="12" r="1.5" fill="#9ca3af"/>
                  </svg>
                </div>
                <span class="w-5 shrink-0 text-center text-[10px] font-bold text-gray-400">{{ c.visit_sequence || i+1 }}</span>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-gray-900 truncate">{{ c.customer_name || c.customer }}</p>
                  <p class="text-xs text-gray-400">
                    {{ [c.location_area, c.location_city].filter(Boolean).join(', ') }}
                    <span v-if="c.last_visit_date"> · Last: {{ formatDate(c.last_visit_date) }}</span>
                  </p>
                </div>
                <div class="flex items-center gap-1 shrink-0">
                  <router-link :to="'/customers/'+c.customer"
                    class="h-6 w-6 flex items-center justify-center rounded text-gray-400 hover:text-blue-500"
                    @click="$emit('update:modelValue', false)">
                    <FeatherIcon name="external-link" class="h-3 w-3" />
                  </router-link>
                  <button @click="removeCustomer(beat, c.customer)"
                    class="h-6 w-6 flex items-center justify-center rounded text-gray-300 hover:text-red-500">
                    <FeatherIcon name="x" class="h-3 w-3" />
                  </button>
                </div>
              </div>
            </div>
            <div v-else class="py-4 text-center text-xs text-gray-400">
              No customers yet — search above to add
            </div>

            <!-- Beat map — collapsed by default -->
            <div v-if="beat.customers?.filter(c => c.latitude).length">
              <button
                class="flex w-full items-center justify-between py-1.5 text-xs text-gray-400 hover:text-gray-700 transition-colors"
                @click="toggleMap(beat.name)"
              >
                <span class="flex items-center gap-1.5">
                  <FeatherIcon name="map" class="h-3.5 w-3.5" />
                  Route map
                </span>
                <FeatherIcon :name="expandedMaps.has(beat.name) ? 'chevron-up' : 'chevron-down'" class="h-3.5 w-3.5" />
              </button>
              <div v-if="expandedMaps.has(beat.name)"
                :id="`beat-map-${beat.name}`"
                style="height:200px;border-radius:8px;border:1px solid #e5e7eb;overflow:hidden"
              />
            </div>
          </div>
        </div>
      </div>

      <div v-else class="rounded-xl border border-dashed border-gray-200 py-12 text-center text-gray-400">
        <FeatherIcon name="map" class="h-10 w-10 mx-auto mb-3" />
        <p class="text-sm font-medium text-gray-600">No beats yet</p>
        <p class="text-xs mt-1 mb-4">Add beats — named routes that run on specific days</p>
        <Btn icon="plus" size="sm" @click="addBeatPanel = true">Add First Beat</Btn>
      </div>

    </div>
  </SlidePanel>

  <!-- Confirm dialog — inside modal -->
  <Teleport to="body">
    <div v-if="confirmDialog"
      class="fixed inset-0 z-[70] flex items-center justify-center bg-black/30 backdrop-blur-sm"
      @click.self="confirmDialog = null"
    >
      <div class="w-80 rounded-2xl border border-gray-200 bg-white p-6 shadow-2xl">
        <p class="text-sm font-semibold text-gray-900">{{ confirmDialog.title }}</p>
        <p class="mt-1.5 text-sm text-gray-500">{{ confirmDialog.message }}</p>
        <div class="mt-5 flex gap-2 justify-end">
          <button
            class="h-8 rounded-lg border border-gray-200 px-3 text-sm text-gray-600 hover:bg-gray-50"
            @click="confirmDialog = null"
          >
            Cancel
          </button>
          <button
            class="h-8 rounded-lg px-4 text-sm font-medium text-white transition-colors"
            :class="confirmDialog.destructive ? 'bg-red-600 hover:bg-red-700' : 'bg-gray-900 hover:bg-gray-700'"
            @click="confirmDialog.action(); confirmDialog = null"
          >
            {{ confirmDialog.confirm }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- Add Beat panel -->
  <SlidePanel v-model="addBeatPanel" title="Add Beat" :saving="savingBeat" save-label="Add Beat" @save="saveBeat">
    <div class="space-y-4">
      <FormField v-model="beatForm.beat_name" label="Beat Name" required :error="beatErrors.beat_name"
        placeholder="e.g. Kyebando-Kawempe Route" />

      <div>
        <label class="mb-2 block text-xs font-medium text-gray-600">
          Runs on <span class="text-red-500">*</span>
        </label>
        <div class="flex gap-2">
          <button v-for="d in weekDays" :key="d.value"
            class="flex-1 rounded-lg border py-2.5 text-xs font-semibold transition-colors"
            :class="beatForm.days.includes(d.value)
              ? 'bg-gray-900 text-white border-gray-900'
              : 'bg-white text-gray-500 border-gray-200 hover:border-gray-400'"
            @click="toggleDay(d.value)"
          >
            {{ d.short }}
          </button>
        </div>
        <p class="mt-1 text-[10px] text-gray-400">Select all days this beat runs — same customer list for all selected days</p>
      </div>

      <FormField v-model="beatForm.area_name" label="Area / Zone (optional)"
        placeholder="e.g. Kyebando, Kawempe" />
      <FormField v-model="beatForm.area_notes" label="Area Notes" type="textarea"
        placeholder="Landmarks, boundaries, key streets…" />
    </div>
  </SlidePanel>

  <!-- Edit plan panel -->
  <SlidePanel v-model="editPlanPanel" title="Edit Beat Plan" :saving="savingPlan" save-label="Save" @save="saveEditPlan">
    <div class="space-y-4">
      <FormField v-model="editForm.status" label="Status" type="select"
        :options="['Draft','Active','Completed','Cancelled']" />
      <div class="grid grid-cols-2 gap-3">
        <FormField v-model="editForm.sales_person" label="Sales Person" type="select" :options="salesPersons" />
        <FormField v-model="editForm.territory" label="Territory" type="select" :options="territories" />
      </div>
      <div class="grid grid-cols-2 gap-3">
        <FormField v-model="editForm.effective_from" label="Effective From" type="date" />
        <FormField v-model="editForm.effective_to" label="Effective To" type="date" help="Blank = ongoing" :min="editForm.effective_from" />
      </div>
    </div>
  </SlidePanel>
</template>

<script setup>
import { ref, computed, watch, reactive, nextTick, onMounted } from 'vue'
import { call, getList } from '@/utils/frappe'
import { getL, ensureLeafletCSS } from '@/utils/leaflet'
import { successToast, errorToast } from '@/utils/toast'
import SlidePanel from '@/components/ui/SlidePanel.vue'
import FormField from '@/components/ui/FormField.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import Btn from '@/components/ui/Btn.vue'
import dayjs from 'dayjs'

const props = defineProps({
  modelValue: Boolean,
  name: String,
  isManager: Boolean,
})
const emit = defineEmits(['update:modelValue', 'updated'])

const weekDays = [
  { value: 'monday',    short: 'Mon', label: 'Monday' },
  { value: 'tuesday',   short: 'Tue', label: 'Tuesday' },
  { value: 'wednesday', short: 'Wed', label: 'Wednesday' },
  { value: 'thursday',  short: 'Thu', label: 'Thursday' },
  { value: 'friday',    short: 'Fri', label: 'Friday' },
  { value: 'saturday',  short: 'Sat', label: 'Saturday' },
  { value: 'sunday',    short: 'Sun', label: 'Sunday' },
]

const doc = ref(null)
const loading = ref(false)
const expandedBeat = ref(null)
const addBeatPanel = ref(false)
const editPlanPanel = ref(false)
const savingBeat = ref(false)
const savingPlan = ref(false)
const salesPersons = ref([])
const territories = ref([])
const customerSearch = ref('')
const searchResults = ref([])
const showResults = ref(false)
const activeBeat = ref(null)
const beatMaps = {}
let searchTimer = null

const beatForm = reactive({ beat_name: '', days: [], area_name: '', area_notes: '' })
const beatErrors = reactive({})
const editForm = reactive({ status: '', sales_person: '', territory: '', effective_from: '', effective_to: '' })

function sortedCustomers(beat) {
  return [...(beat.customers || [])].sort((a, b) => (a.visit_sequence || 999) - (b.visit_sequence || 999))
}

function toggleDay(day) {
  const i = beatForm.days.indexOf(day)
  if (i >= 0) beatForm.days.splice(i, 1)
  else beatForm.days.push(day)
}

function toggleBeat(beatName) {
  if (expandedBeat.value === beatName) {
    expandedBeat.value = null
  } else {
    expandedBeat.value = beatName
    customerSearch.value = ''
    searchResults.value = []
    activeBeat.value = beatName
    // Wait for v-if content to mount before rendering map
    window.setTimeout(() => renderBeatMap(beatName), 150)
  }
}

async function reloadBeat(beat) {
  // Use our own API to reload beat data — avoids permission issues with custom doctypes
  try {
    const res = await call('sfa_core.api.beat_plans.get_beat_plan', { name: props.name })
    const freshBeat = res.message?.custom_beats?.find(b => b.name === beat.name)
    if (freshBeat) {
      beat.customers = freshBeat.customers || []
    }
  } catch (e) { console.error('Failed to reload beat', e) }
}

async function load() {
  if (!props.name) return
  loading.value = true
  try {
    const res = await call('sfa_core.api.beat_plans.get_beat_plan', { name: props.name })
    doc.value = res.message
    // Populate edit form
    const d = doc.value
    Object.assign(editForm, {
      status: d.status,
      sales_person: d.sales_person || '',
      territory: d.territory || '',
      effective_from: d.custom_effective_from || '',
      effective_to: d.custom_effective_to || '',
    })
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

async function loadMeta() {
  const [sp, tr] = await Promise.all([
    getList('Sales Person', { fields: ['name'], filters: { is_group: 0 }, limit: 200 }),
    getList('Territory', { fields: ['name'], filters: { is_group: 0 }, limit: 100 }),
  ])
  salesPersons.value = sp.map(s => s.name)
  territories.value = tr.map(t => t.name)
}

async function saveBeat() {
  Object.keys(beatErrors).forEach(k => delete beatErrors[k])
  if (!beatForm.beat_name) { beatErrors.beat_name = 'Required'; return }
  if (!beatForm.days.length) { errorToast('Select at least one day'); return }
  savingBeat.value = true
  try {
    await call('sfa_core.api.beat_plans.add_beat', {
      beat_plan: props.name,
      beat_name: beatForm.beat_name,
      days: beatForm.days,
      area_name: beatForm.area_name || null,
      area_notes: beatForm.area_notes || null,
    })
    successToast(`Beat "${beatForm.beat_name}" added`)
    addBeatPanel.value = false
    Object.assign(beatForm, { beat_name: '', days: [], area_name: '', area_notes: '' })
    await load()
    emit('updated')
  } catch (e) { errorToast(e.message) }
  finally { savingBeat.value = false }
}

async function saveEditPlan() {
  savingPlan.value = true
  try {
    await call('sfa_core.api.utils.save_doc', {
      doc: {
        doctype: 'SFA Beat Plan',
        name: props.name,
        status: editForm.status,
        sales_person: editForm.sales_person || null,
        territory: editForm.territory || null,
        custom_effective_from: editForm.effective_from || null,
        custom_effective_to: editForm.effective_to || null,
      }
    })
    successToast('Beat plan updated')
    editPlanPanel.value = false
    await load()
    emit('updated')
  } catch (e) { errorToast(e.message) }
  finally { savingPlan.value = false }
}

function onBlurSearch() {
  window.setTimeout(() => { showResults.value = false }, 150)
}

function onSearchInput(beat) {
  activeBeat.value = beat.name
  if (searchTimer) clearTimeout(searchTimer)
  if (customerSearch.value.length < 2) { searchResults.value = []; return }
  searchTimer = window.setTimeout(() => searchCustomers(beat), 300)
}

async function searchCustomers(beat) {
  try {
    const existing = new Set((beat.customers || []).map(c => c.customer))
    const results = await getList('Customer', {
      fields: ['name', 'customer_name', 'territory', 'custom_location_area', 'custom_location_city'],
      filters: { customer_name: ['like', `%${customerSearch.value}%`] },
      limit: 8,
    })
    searchResults.value = results.filter(r => !existing.has(r.name))
    showResults.value = true
  } catch (e) { console.error(e) }
}

async function addCustomer(beat, customer) {
  showResults.value = false
  customerSearch.value = ''
  searchResults.value = []
  try {
    await call('sfa_core.api.beat_plans.add_customer_to_beat', {
      beat_name: beat.name,
      customer: customer.name,
    })
    successToast(`${customer.customer_name} added to ${beat.beat_name}`)
    await reloadBeat(beat)
    markChanged()
    emit('updated')
    if (expandedMaps.value.has(beat.name)) {
      window.setTimeout(() => renderBeatMap(beat.name), 150)
    }
  } catch (e) { errorToast(e.message) }
}

async function removeCustomer(beat, customer) {
  try {
    await call('sfa_core.api.beat_plans.remove_customer_from_beat', {
      beat_name: beat.name,
      customer,
    })
    await reloadBeat(beat)
    markChanged()
    emit('updated')
    if (expandedMaps.value.has(beat.name)) {
      window.setTimeout(() => renderBeatMap(beat.name), 150)
    }
  } catch (e) { errorToast(e.message) }
}

// Unsaved changes tracking
const hasChanges = ref(false)
const confirmDialog = ref(null)

function markChanged() {
  hasChanges.value = true
}

function confirmSave() {
  confirmDialog.value = {
    title: 'Save changes?',
    message: 'Your changes to the beat plan will be saved.',
    confirm: 'Save',
    destructive: false,
    action: doSave,
  }
}

function confirmDiscard() {
  confirmDialog.value = {
    title: 'Discard changes?',
    message: 'All unsaved changes will be lost and the beat plan will reload.',
    confirm: 'Discard',
    destructive: true,
    action: doDiscard,
  }
}

async function doSave() {
  hasChanges.value = false
  successToast('Beat plan saved')
  emit('updated')
}

async function doDiscard() {
  const openMaps = new Set(expandedMaps.value)
  hasChanges.value = false
  // Clean up existing map instances before reload
  for (const beatName of openMaps) {
    if (beatMaps[beatName]) {
      try { beatMaps[beatName].remove() } catch {}
      delete beatMaps[beatName]
    }
  }
  await load()
  // Restore expanded maps state and re-render after Vue updates the DOM
  expandedMaps.value = openMaps
  window.setTimeout(async () => {
    for (const beatName of openMaps) {
      await renderBeatMap(beatName)
    }
  }, 300)
}

// Drag and drop reordering
const dragBeat = ref(null)
const dragIndex = ref(null)
const dragOverIndex = ref(null)
const expandedMaps = ref(new Set())

function onDragStart(e, beat, i) {
  dragBeat.value = beat.name
  dragIndex.value = i
  e.dataTransfer.effectAllowed = 'move'
  e.dataTransfer.setData('text/plain', String(i))
}

function onDragOver(e, beat, i) {
  e.preventDefault()
  if (dragBeat.value !== beat.name) return
  dragOverIndex.value = i
}

function onDragLeave(e) {
  // Only clear if leaving the container entirely
  if (!e.currentTarget.contains(e.relatedTarget)) {
    dragOverIndex.value = null
  }
}

async function onDrop(e, beat) {
  e.preventDefault()
  e.stopPropagation()
  const from = dragIndex.value
  const to = dragOverIndex.value
  dragOverIndex.value = null
  dragBeat.value = null
  dragIndex.value = null

  if (from === null || to === null || from === to) return

  const list = [...sortedCustomers(beat)]
  const [moved] = list.splice(from, 1)
  list.splice(to, 0, moved)

  // Update sequences locally immediately for instant feedback
  list.forEach((c, idx) => { c.visit_sequence = idx + 1 })
  beat.customers = [...list]

  try {
    await call('sfa_core.api.beat_plans.reorder_beat_customers', {
      beat_name: beat.name,
      customer_order: list.map(c => c.customer),
    })
    markChanged()
    if (expandedMaps.value.has(beat.name)) {
      window.setTimeout(() => renderBeatMap(beat.name), 100)
    }
  } catch (err) { errorToast(err.message) }
}

function toggleMap(beatName) {
  const set = new Set(expandedMaps.value)
  if (set.has(beatName)) {
    set.delete(beatName)
  } else {
    set.add(beatName)
    window.setTimeout(() => renderBeatMap(beatName), 150)
  }
  expandedMaps.value = set
}

async function renderBeatMap(beatName) {
  const beat = doc.value?.custom_beats?.find(b => b.name === beatName)
  if (!beat) return
  const customers = sortedCustomers(beat).filter(c => c.latitude && c.longitude)
  if (!customers.length) return

  await ensureLeafletCSS()
  const L = await getL()
  const el = document.getElementById(`beat-map-${beatName}`)
  if (!el) return

  if (beatMaps[beatName]) { beatMaps[beatName].remove() }
  const map = L.map(el)
  beatMaps[beatName] = map
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
  }).addTo(map)
  window.setTimeout(() => map.invalidateSize(), 100)

  const bounds = []
  customers.forEach((c, i) => {
    const pt = [c.latitude, c.longitude]
    bounds.push(pt)
    const icon = L.divIcon({
      className: '',
      iconSize: [22, 22], iconAnchor: [11, 11],
      html: `<div style="background:#111827;width:22px;height:22px;border-radius:50%;border:2px solid white;box-shadow:0 1px 4px rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:700;color:white">${i+1}</div>`
    })
    L.marker(pt, { icon }).addTo(map)
      .bindPopup(`<b>${c.customer_name || c.customer}</b>`)
  })
  if (customers.length > 1) {
    L.polyline(bounds, { color: '#3b82f6', weight: 2, dashArray: '5,4', opacity: 0.7 }).addTo(map)
  }
  map.fitBounds(L.latLngBounds(bounds).pad(0.25))
}

// Load on mount — component is remounted fresh each open via :key
onMounted(async () => {
  await Promise.all([load(), loadMeta()])
})

// Still watch name changes for navigation within open panel
watch(() => props.name, (val) => { if (val) load() })

const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'
</script>
