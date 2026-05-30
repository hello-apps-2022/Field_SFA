<template>
  <div class="flex h-full flex-col overflow-hidden bg-gray-50">
    <div class="flex h-[52px] shrink-0 items-center gap-3 border-b border-gray-100 bg-white px-5">
      <router-link to="/orders" class="text-sm text-gray-400 hover:text-gray-700">Orders</router-link>
      <FeatherIcon name="chevron-right" class="h-3.5 w-3.5 text-gray-300" />
      <span class="font-mono text-sm font-semibold text-gray-900">{{ name }}</span>
      <div class="flex-1" />
      <span v-if="doc" class="rounded px-2 py-0.5 text-xs font-medium" :class="stateColor">{{ state }}</span>
    </div>

    <div v-if="loading" class="flex flex-1 items-center justify-center">
      <FeatherIcon name="loader" class="h-6 w-6 animate-spin text-gray-400" />
    </div>

    <div v-else-if="doc" class="flex-1 overflow-y-auto p-5">
      <div class="mb-4 flex flex-wrap items-center gap-x-4 gap-y-1">
        <router-link :to="'/customers/' + doc.customer" class="text-lg font-semibold text-gray-900 hover:text-blue-600">{{ doc.customer }}</router-link>
        <span class="inline-flex items-center gap-1 rounded bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600">
          <FeatherIcon :name="doc.custom_sfa_order_type === 'Van Sale' ? 'truck' : 'clipboard'" class="h-3 w-3" />
          {{ doc.custom_sfa_order_type || 'Booking' }}
        </span>
        <span class="text-sm text-gray-500">{{ doc.total_qty || 0 }} cartons &middot; {{ fmt(doc.grand_total) }}</span>
      </div>

      <div class="grid gap-4 lg:grid-cols-3">
        <div class="lg:col-span-2">
          <div class="rounded-xl border border-gray-200 bg-white">
            <p class="border-b border-gray-100 px-4 py-2.5 text-sm font-medium text-gray-700">Items</p>
            <div class="divide-y divide-gray-50">
              <div v-for="(it, i) in (doc.items || [])" :key="i" class="flex items-center gap-2 px-4 py-2.5 text-sm">
                <span class="flex-1 truncate text-gray-800">{{ it.item_name || it.item_code }}</span>
                <span v-if="it.is_free_item" class="rounded bg-green-100 px-1.5 py-0.5 text-[10px] font-semibold uppercase text-green-700">Free</span>
                <span class="w-24 text-right text-gray-500">{{ it.qty }} &times; {{ fmt(it.rate) }}</span>
                <span class="w-24 text-right font-medium text-gray-900">{{ fmt(it.amount) }}</span>
              </div>
            </div>
            <div class="flex items-center justify-between border-t border-gray-100 px-4 py-2.5">
              <span class="text-sm text-gray-500">Total</span>
              <span class="text-sm font-semibold text-gray-900">{{ fmt(doc.grand_total) }}</span>
            </div>
          </div>
          <p v-if="doc.remarks" class="mt-3 rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm text-gray-600"><span class="text-gray-400">Remarks: </span>{{ doc.remarks }}</p>
        </div>

        <div>
          <div class="rounded-xl border border-gray-200 bg-white p-4">
            <p class="mb-4 text-sm font-medium text-gray-700">Timeline</p>
            <ol class="relative space-y-5 border-l border-gray-200 pl-5">
              <li v-for="(ev, i) in timeline" :key="i" class="relative">
                <span class="absolute -left-[27px] flex h-4 w-4 items-center justify-center rounded-full" :class="ev.done ? ev.dot : 'bg-gray-200'">
                  <span class="h-1.5 w-1.5 rounded-full bg-white" />
                </span>
                <p class="text-sm font-medium" :class="ev.done ? 'text-gray-900' : 'text-gray-400'">{{ ev.label }}</p>
                <p v-if="ev.when" class="text-xs text-gray-500">{{ ev.when }}</p>
                <p v-if="ev.who" class="text-xs text-gray-400">{{ ev.byLabel }} {{ ev.who }}</p>
                <p v-if="!ev.done && !ev.when" class="text-xs italic text-gray-300">Pending</p>
              </li>
            </ol>
          </div>

          <div v-if="state==='Draft' || state==='Confirmed'" class="mt-3 flex flex-col gap-2">
            <Btn v-if="state==='Draft'" variant="solid" icon="check" :loading="acting" @click="act('confirm_order')">Confirm Order</Btn>
            <Btn v-if="state==='Confirmed'" variant="solid" icon="truck" :loading="acting" @click="act('mark_delivered')">Mark Delivered</Btn>
            <Btn variant="ghost" icon="x-circle" :loading="acting" @click="act('cancel_order')">Cancel Order</Btn>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="flex flex-1 flex-col items-center justify-center text-gray-400">
      <FeatherIcon name="alert-circle" class="mb-2 h-8 w-8" />
      <p class="text-sm">Order not found</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getDoc, call } from '@/utils/frappe'
import { successToast, errorToast } from '@/utils/toast'
import { formatCurrency } from '@/utils/currency'
import Btn from '@/components/ui/Btn.vue'
import dayjs from 'dayjs'

const props = defineProps({ name: { type: String, required: true } })
const doc = ref(null)
const loading = ref(true)
const acting = ref(false)

const fmt = (v) => formatCurrency(v || 0)
const dt = (d) => d ? dayjs(d).format('D MMM YYYY, h:mm A') : ''

async function loadDoc() {
  loading.value = true
  try { doc.value = await getDoc('Sales Order', props.name) }
  catch (e) { doc.value = null }
  finally { loading.value = false }
}

const state = computed(() => {
  const d = doc.value
  if (!d) return ''
  if (d.docstatus === 2) return 'Cancelled'
  if (d.docstatus === 0) return 'Draft'
  return d.custom_sfa_delivery_status === 'Delivered' ? 'Delivered' : 'Confirmed'
})
const stateColor = computed(() => ({
  Draft: 'bg-amber-50 text-amber-700', Confirmed: 'bg-indigo-50 text-indigo-700',
  Delivered: 'bg-green-50 text-green-700', Cancelled: 'bg-red-50 text-red-700',
}[state.value] || 'bg-gray-100 text-gray-600'))

const timeline = computed(() => {
  const d = doc.value
  if (!d) return []
  const evs = [
    { label: 'Order placed', done: true, dot: 'bg-gray-900', when: dt(d.creation), who: d.custom_sfa_rep || d.owner, byLabel: 'by' },
  ]
  const confirmed = d.docstatus === 1
  evs.push({ label: 'Confirmed', done: confirmed, dot: 'bg-indigo-500',
    when: confirmed && d.custom_sfa_confirmed_on ? dt(d.custom_sfa_confirmed_on) : '',
    who: confirmed && d.custom_sfa_confirmed_by ? d.custom_sfa_confirmed_by : '', byLabel: 'by' })
  const delivered = d.custom_sfa_delivery_status === 'Delivered'
  evs.push({ label: 'Delivered', done: delivered, dot: 'bg-green-500',
    when: delivered ? dt(d.custom_sfa_delivered_on) : '',
    who: delivered && d.custom_sfa_delivered_by ? d.custom_sfa_delivered_by : '', byLabel: 'marked by' })
  if (d.docstatus === 2) evs.push({ label: 'Cancelled', done: true, dot: 'bg-red-500', when: dt(d.modified), who: '', byLabel: '' })
  return evs
})

async function act(method) {
  acting.value = true
  try {
    await call('sfa_core.field_sfa.api.order_actions.' + method, { name: props.name })
    successToast('Done')
    await loadDoc()
  } catch (e) {
    errorToast(e.message || 'Action failed')
  } finally { acting.value = false }
}

onMounted(loadDoc)
</script>
