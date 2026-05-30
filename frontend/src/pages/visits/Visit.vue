<template>
  <div class="flex h-full flex-col overflow-hidden">

    <!-- Top bar -->
    <div class="flex h-[52px] shrink-0 items-center border-b border-gray-100 bg-white px-5 gap-3">
      <router-link to="/visits" class="text-sm text-gray-400 hover:text-gray-700">Visits</router-link>
      <FeatherIcon name="chevron-right" class="h-3.5 w-3.5 text-gray-300" />
      <span class="text-sm font-semibold text-gray-900 truncate">{{ doc?.customer || name }}</span>
      <div class="flex-1" />
      <StatusBadge v-if="doc" :status="doc.status" />
      <Btn variant="default" icon="edit-2" size="sm" @click="editPanel = true">Edit</Btn>
    </div>

    <!-- Visit header -->
    <div class="shrink-0 border-b border-gray-100 bg-white px-5 py-4">
      <div v-if="doc" class="flex items-center gap-4">
        <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-blue-100 text-lg font-semibold text-blue-700">
          {{ (doc.customer || '?').charAt(0).toUpperCase() }}
        </div>
        <div class="flex-1 min-w-0">
          <!-- Customer link -->
          <router-link :to="'/customers/' + doc.customer" class="text-base font-semibold text-gray-900 hover:text-blue-600 transition-colors">
            {{ doc.customer }}
          </router-link>
          <div class="flex flex-wrap items-center gap-x-4 gap-y-1 mt-1.5">
            <span class="inline-flex items-center gap-1 text-xs text-gray-500">
              <FeatherIcon name="user" class="h-3 w-3 text-gray-400" />
              {{ doc.sales_person || 'No rep' }}
            </span>
            <span class="inline-flex items-center gap-1 text-xs text-gray-500">
              <FeatherIcon name="calendar" class="h-3 w-3 text-gray-400" />
              {{ formatDate(doc.visit_date) }}
            </span>
            <span v-if="doc.visit_purpose" class="inline-flex items-center gap-1 text-xs text-gray-500">
              <FeatherIcon name="target" class="h-3 w-3 text-gray-400" />
              {{ doc.visit_purpose }}
            </span>
            <span v-if="doc.beat_plan" class="inline-flex items-center gap-1 text-xs text-gray-500">
              <FeatherIcon name="map" class="h-3 w-3 text-gray-400" />
              {{ doc.beat_plan }}
            </span>
          </div>
        </div>

        <!-- Quick stats -->
        <div class="hidden sm:flex gap-4 shrink-0 border-l border-gray-100 pl-4 text-center">
          <div v-if="doc.duration_minutes">
            <p class="text-xl font-semibold text-gray-900">{{ doc.duration_minutes }}</p>
            <p class="text-[10px] uppercase tracking-wide text-gray-400">Minutes</p>
          </div>
          <div v-if="doc.distance_from_customer != null">
            <p class="text-xl font-semibold text-gray-900">{{ doc.distance_from_customer?.toFixed(0) }}</p>
            <p class="text-[10px] uppercase tracking-wide text-gray-400">Metres away</p>
          </div>
          <div>
            <p class="text-xl font-semibold text-gray-900">{{ formResponses.length }}</p>
            <p class="text-[10px] uppercase tracking-wide text-gray-400">Forms</p>
          </div>
        </div>
      </div>
      <div v-else class="flex items-center gap-3">
        <div class="h-12 w-12 rounded-full bg-gray-200 animate-pulse" />
        <div class="space-y-2">
          <div class="h-4 w-40 rounded bg-gray-200 animate-pulse" />
          <div class="h-3 w-64 rounded bg-gray-200 animate-pulse" />
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex shrink-0 border-b border-gray-100 bg-white px-5">
      <button v-for="tab in tabs" :key="tab.id"
        class="mr-1 border-b-2 px-3 py-2.5 text-sm font-medium transition-colors"
        :class="activeTab===tab.id ? 'border-gray-900 text-gray-900' : 'border-transparent text-gray-500 hover:text-gray-700'"
        @click="activeTab=tab.id"
      >
        {{ tab.label }}
        <span v-if="tab.count" class="ml-1 rounded-full bg-gray-100 px-1.5 text-[10px] text-gray-500">{{ tab.count }}</span>
      </button>
    </div>

    <!-- Tab content -->
    <div class="flex-1 overflow-y-auto bg-gray-50">

      <!-- ── DETAILS ── -->
      <div v-show="activeTab==='details'" class="p-5 space-y-4">
        <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <!-- Left -->
          <div class="space-y-4">

            <div class="rounded-xl border border-gray-200 bg-white overflow-hidden">
              <div class="border-b border-gray-100 bg-gray-50 px-4 py-2">
                <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Visit Info</p>
              </div>
              <template v-if="doc">
                <div class="flex border-b border-gray-50 px-4 py-2.5">
                  <span class="w-36 shrink-0 text-xs text-gray-400">Customer</span>
                  <router-link :to="'/customers/'+doc.customer" class="flex-1 text-sm text-blue-600 hover:underline">{{ doc.customer }}</router-link>
                </div>
                <div class="flex border-b border-gray-50 px-4 py-2.5">
                  <span class="w-36 shrink-0 text-xs text-gray-400">Sales Person</span>
                  <span class="flex-1 text-sm text-gray-800">{{ doc.sales_person || '—' }}</span>
                </div>
                <div v-if="doc.joint_with" class="flex border-b border-gray-50 px-4 py-2.5">
                  <span class="w-36 shrink-0 text-xs text-gray-400">Joint Visit With</span>
                  <span class="flex-1 text-sm text-gray-800">{{ doc.joint_with }}</span>
                </div>
                <div class="flex border-b border-gray-50 px-4 py-2.5">
                  <span class="w-36 shrink-0 text-xs text-gray-400">Beat Plan</span>
                  <span class="flex-1 text-sm" :class="doc.beat_plan?'text-gray-800':'text-gray-400 italic'">{{ doc.beat_plan || 'Not set' }}</span>
                </div>
                <div class="flex border-b border-gray-50 px-4 py-2.5">
                  <span class="w-36 shrink-0 text-xs text-gray-400">Date</span>
                  <span class="flex-1 text-sm text-gray-800">{{ formatDate(doc.visit_date) }}</span>
                </div>
                <div class="flex px-4 py-2.5">
                  <span class="w-36 shrink-0 text-xs text-gray-400">Purpose</span>
                  <span class="flex-1 text-sm" :class="doc.visit_purpose?'text-gray-800':'text-gray-400 italic'">{{ doc.visit_purpose || 'Not set' }}</span>
                </div>
              </template>
            </div>

            <div class="rounded-xl border border-gray-200 bg-white overflow-hidden">
              <div class="border-b border-gray-100 bg-gray-50 px-4 py-2">
                <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Timing</p>
              </div>
              <template v-if="doc">
                <div class="flex border-b border-gray-50 px-4 py-2.5">
                  <span class="w-36 shrink-0 text-xs text-gray-400">Check In</span>
                  <span class="flex-1 text-sm text-gray-800">{{ doc.check_in_time ? formatDatetime(doc.check_in_time) : '—' }}</span>
                </div>
                <div class="flex border-b border-gray-50 px-4 py-2.5">
                  <span class="w-36 shrink-0 text-xs text-gray-400">Check Out</span>
                  <span class="flex-1 text-sm text-gray-800">{{ doc.check_out_time ? formatDatetime(doc.check_out_time) : '—' }}</span>
                </div>
                <div class="flex px-4 py-2.5">
                  <span class="w-36 shrink-0 text-xs text-gray-400">Duration</span>
                  <span class="flex-1 text-sm text-gray-800">{{ doc.duration_minutes ? doc.duration_minutes + ' minutes' : '—' }}</span>
                </div>
              </template>
            </div>

            <div v-if="doc?.notes" class="rounded-xl border border-gray-200 bg-white overflow-hidden">
              <div class="border-b border-gray-100 bg-gray-50 px-4 py-2">
                <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Notes</p>
              </div>
              <div class="px-4 py-3">
                <p class="text-sm text-gray-700 whitespace-pre-line">{{ doc.notes }}</p>
              </div>
            </div>
          </div>

          <!-- Right: map + location -->
          <div class="space-y-4">
            <div class="rounded-xl border border-gray-200 bg-white overflow-hidden">
              <div class="border-b border-gray-100 bg-gray-50 px-4 py-2">
                <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Location</p>
              </div>
              <div v-if="doc?.check_in_latitude">
                <div id="visit-map" class="h-56 w-full" />
                <div class="border-t border-gray-100 px-4 py-3 space-y-1">
                  <div class="flex items-center gap-3 text-xs text-gray-500">
                    <span class="flex items-center gap-1">
                      <span class="inline-block h-2.5 w-2.5 rounded-full bg-green-500" /> Check In
                      <span class="font-mono text-gray-400">{{ doc.check_in_latitude?.toFixed(5) }}, {{ doc.check_in_longitude?.toFixed(5) }}</span>
                    </span>
                  </div>
                  <div v-if="doc.check_out_latitude" class="flex items-center gap-3 text-xs text-gray-500">
                    <span class="flex items-center gap-1">
                      <span class="inline-block h-2.5 w-2.5 rounded-full bg-red-500" /> Check Out
                      <span class="font-mono text-gray-400">{{ doc.check_out_latitude?.toFixed(5) }}, {{ doc.check_out_longitude?.toFixed(5) }}</span>
                    </span>
                  </div>
                  <div v-if="doc.distance_from_customer != null" class="text-xs text-gray-400">
                    {{ doc.distance_from_customer?.toFixed(0) }}m from customer location
                    <span v-if="doc.check_in_accuracy"> · ±{{ doc.check_in_accuracy?.toFixed(0) }}m accuracy</span>
                  </div>
                </div>
              </div>
              <div v-else class="flex h-40 flex-col items-center justify-center text-gray-400">
                <FeatherIcon name="map-pin" class="h-8 w-8 mb-2" />
                <p class="text-sm text-gray-500">No GPS data</p>
                <p class="text-xs mt-1">Set from the mobile app on check-in</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ── FORMS ── -->
      <div v-show="activeTab==='forms'" class="p-5">
        <div class="mb-3 flex items-center justify-between">
          <p class="text-sm text-gray-500">{{ formResponses.length }} responses</p>
          <Btn variant="solid" icon="file-text" size="sm" @click="fillFormPanel=true">Fill Form</Btn>
        </div>
        <div v-if="formResponses.length" class="space-y-2">
          <div v-for="r in formResponses" :key="r.name"
            class="rounded-xl border border-gray-200 bg-white p-4 cursor-pointer hover:bg-gray-50 transition-colors"
            @click="selectedResponseName=r.name; responsePanel=true"
          >
            <div class="flex items-start justify-between">
              <div class="flex items-start gap-3">
                <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-50">
                  <FeatherIcon name="file-text" class="h-4 w-4 text-blue-500" />
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ r.form_template }}</p>
                  <div class="mt-1 flex gap-3 text-xs text-gray-400">
                    <span class="flex items-center gap-1"><FeatherIcon name="calendar" class="h-3 w-3" />{{ formatDatetime(r.response_date) }}</span>
                  </div>
                </div>
              </div>
              <StatusBadge :status="r.sync_status" />
            </div>
          </div>
        </div>
        <div v-else class="flex flex-col items-center py-16 text-gray-400">
          <FeatherIcon name="file-text" class="h-10 w-10 mb-3" />
          <p class="text-sm font-medium text-gray-600">No forms submitted</p>
        </div>
      </div>

      <!-- ── ORDERS ── -->
      <div v-show="activeTab==='orders'" class="p-5">
        <div v-if="orders.length" class="space-y-2">
          <div v-for="o in orders" :key="o.name"
            class="flex items-center justify-between rounded-xl border border-gray-200 bg-white p-4 cursor-pointer hover:bg-gray-50"
            @click="window.open('/app/sales-order/'+o.name,'_blank')"
          >
            <div>
              <p class="text-sm font-mono font-medium text-gray-900">{{ o.name }}</p>
              <p class="text-xs text-gray-500">{{ o.total_qty }} cartons · {{ formatDate(o.transaction_date) }}</p>
            </div>
            <div class="text-right">
              <p class="text-sm font-semibold">{{ formatCurrency(o.grand_total) }}</p>
              <StatusBadge :status="o.status" />
            </div>
          </div>
        </div>
        <div v-else class="flex flex-col items-center py-16 text-gray-400">
          <FeatherIcon name="shopping-cart" class="h-10 w-10 mb-3" />
          <p class="text-sm font-medium text-gray-600">No orders</p>
        </div>
      </div>

      <!-- ── PAYMENTS ── -->
      <div v-show="activeTab==='payments'" class="p-5">
        <div v-if="payments.length" class="space-y-2">
          <div v-for="p in payments" :key="p.name"
            class="flex items-center justify-between rounded-xl border border-gray-200 bg-white p-4">
            <div>
              <p class="text-sm font-semibold text-gray-900">{{ formatCurrency(p.amount) }}</p>
              <p class="text-xs text-gray-500">{{ p.payment_type }} · {{ formatDate(p.payment_date) }}</p>
            </div>
            <StatusBadge :status="p.status" />
          </div>
        </div>
        <div v-else class="flex flex-col items-center py-16 text-gray-400">
          <FeatherIcon name="credit-card" class="h-10 w-10 mb-3" />
          <p class="text-sm font-medium text-gray-600">No payments</p>
        </div>
      </div>
    </div>
  </div>

  <!-- Edit Panel -->
  <SlidePanel v-model="editPanel" title="Edit Visit" :saving="saving" @save="save">
    <div class="space-y-4">
      <FormField v-model="form.status" label="Status" type="select" :options="['Open','In Progress','Completed','Cancelled']" />
      <FormField v-model="form.visit_purpose" label="Visit Purpose" type="select"
        :options="['Sales Order','Payment Collection','Stock Check','Merchandising','Relationship','Other']" />
      <FormField v-model="form.notes" label="Notes" type="textarea" />
    </div>
  </SlidePanel>

  <!-- Fill Form Panel -->
  <FillFormPanel
    v-model="fillFormPanel"
    :customer-name="doc?.customer"
    :customer-doc="{ name: doc?.customer }"
    :recent-visits="[{ name: name, visit_date: doc?.visit_date, sales_person: doc?.sales_person }]"
    @submitted="load(); activeTab='forms'"
  />

  <!-- View Form Response -->
  <FormResponsePanel
    v-model="responsePanel"
    :response-name="selectedResponseName"
  />
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { getDoc, getList, saveDoc } from '@/utils/frappe'
import { formatCurrency } from '@/utils/currency'
import { successToast, errorToast } from '@/utils/toast'
import SlidePanel from '@/components/ui/SlidePanel.vue'
import FormField from '@/components/ui/FormField.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import Btn from '@/components/ui/Btn.vue'
import FillFormPanel from '@/components/ui/FillFormPanel.vue'
import FormResponsePanel from '@/components/ui/FormResponsePanel.vue'
import dayjs from 'dayjs'
import { getL, ensureLeafletCSS } from '@/utils/leaflet'

const props = defineProps({ name: String })

const doc = ref(null)
const formResponses = ref([])
const orders = ref([])
const payments = ref([])
const activeTab = ref('details')
const editPanel = ref(false)
const fillFormPanel = ref(false)
const responsePanel = ref(false)
const selectedResponseName = ref('')
const saving = ref(false)
const form = reactive({ status: '', visit_purpose: '', notes: '' })

const tabs = computed(() => [
  { id: 'details', label: 'Details' },
  { id: 'forms', label: 'Forms', count: formResponses.value.length || null },
  { id: 'orders', label: 'Orders', count: orders.value.length || null },
  { id: 'payments', label: 'Payments', count: payments.value.length || null },
])

async function load() {
  const d = await getDoc('SFA Visit', props.name)
  doc.value = d
  Object.assign(form, { status: d.status, visit_purpose: d.visit_purpose || '', notes: d.notes || '' })

  const [fr, o, p] = await Promise.all([
    getList('SFA Form Response', {
      fields: ['name', 'form_template', 'response_date', 'sync_status', 'sales_person'],
      filters: { visit: props.name }, orderBy: 'response_date desc', limit: 20,
    }),
    getList('Sales Order', {
      fields: ['name', 'transaction_date', 'status', 'grand_total', 'total_qty'],
      filters: { custom_sfa_visit: props.name }, orderBy: 'transaction_date desc', limit: 10,
    }),
    getList('SFA Payment', {
      fields: ['name', 'payment_date', 'payment_type', 'amount', 'status'],
      filters: { visit: props.name }, orderBy: 'payment_date desc', limit: 20,
    }),
  ])
  formResponses.value = fr
  orders.value = o
  payments.value = p

  if (d.check_in_latitude) { await nextTick(); initMap(d) }
}


async function initMap(d) {
  await ensureLeafletCSS()
  const L = await getL()
  const el = document.getElementById('visit-map')
  if (!el) return
  if (el._map) { el._map.invalidateSize(); return }
  const map = L.map(el)
  el._map = map
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OSM' }).addTo(map)
  window.setTimeout(() => map.invalidateSize(), 100)

  const inIcon = L.divIcon({ className: '', iconSize: [14,14], iconAnchor: [7,7], html: '<div style="background:#22c55e;width:14px;height:14px;border-radius:50%;border:2.5px solid white;box-shadow:0 1px 4px rgba(0,0,0,0.3)"></div>' })
  const outIcon = L.divIcon({ className: '', iconSize: [14,14], iconAnchor: [7,7], html: '<div style="background:#ef4444;width:14px;height:14px;border-radius:50%;border:2.5px solid white;box-shadow:0 1px 4px rgba(0,0,0,0.3)"></div>' })

  const bounds = []
  if (d.check_in_latitude) {
    const pt = [d.check_in_latitude, d.check_in_longitude]
    L.marker(pt, { icon: inIcon }).addTo(map).bindPopup('Check In')
    bounds.push(pt)
  }
  if (d.check_out_latitude) {
    const pt = [d.check_out_latitude, d.check_out_longitude]
    L.marker(pt, { icon: outIcon }).addTo(map).bindPopup('Check Out')
    bounds.push(pt)
  }
  if (bounds.length === 2) {
    L.polyline(bounds, { color: '#3b82f6', dashArray: '5,5', weight: 2 }).addTo(map)
    map.fitBounds(L.latLngBounds(bounds).pad(0.3))
  } else if (bounds.length === 1) {
    map.setView(bounds[0], 16)
  }
}

async function save() {
  saving.value = true
  try {
    await saveDoc({ doctype:'SFA Visit', name:props.name, ...form })
    successToast('Visit updated')
    editPanel.value = false
    await load()
  } catch (e) { errorToast(e.message) }
  finally { saving.value = false }
}

const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'
const formatDatetime = (d) => d ? dayjs(d).format('D MMM YYYY HH:mm') : '—'

onMounted(load)
</script>

<style>
.leaflet-tile-container img,.leaflet-marker-pane img,.leaflet-shadow-pane img{max-width:none!important;width:auto!important;height:auto!important}
.leaflet-container{z-index:0;font-family:inherit}
</style>
