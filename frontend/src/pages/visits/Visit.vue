<template>
  <DetailLayout
    :title="doc ? doc.customer : name"
    :subtitle="doc ? formatDate(doc.visit_date) + ' · ' + (doc.sales_person || '') : ''"
    back-to="/visits"
    back-label="Visits"
    :tabs="tabs"
  >
    <template #actions>
      <StatusBadge v-if="doc" :status="doc.status" />
      <Btn variant="default" icon="edit-2" @click="editPanel = true">Edit</Btn>
    </template>

    <template #fields>
      <div v-if="doc">
        <DetailField label="Customer" :value="doc.customer" :editable="false" />
        <DetailField label="Sales Person" :value="doc.sales_person" :editable="false" />
        <DetailField label="Beat Plan" :value="doc.beat_plan" :editable="false" />
        <DetailField label="Visit Date" :value="formatDate(doc.visit_date)" :editable="false" />
        <DetailField label="Check In" :value="doc.check_in_time ? formatTime(doc.check_in_time) : '—'" :editable="false" />
        <DetailField label="Check Out" :value="doc.check_out_time ? formatTime(doc.check_out_time) : '—'" :editable="false" />
        <DetailField label="Status" :editable="false">
          <StatusBadge :status="doc.status" />
        </DetailField>
        <DetailField v-if="doc.notes" label="Notes" :value="doc.notes" :editable="false" />
      </div>
      <div v-else class="flex justify-center py-8">
        <FeatherIcon name="loader" class="h-5 w-5 animate-spin text-gray-400" />
      </div>
    </template>

    <!-- Form Responses tab -->
    <template #tab-forms>
      <div v-if="formResponses.length" class="space-y-2">
        <div v-for="r in formResponses" :key="r.name" class="rounded-lg border border-gray-100 bg-gray-50 p-3">
          <div class="flex items-center justify-between">
            <p class="text-sm font-medium text-gray-900">{{ r.form_template }}</p>
            <StatusBadge :status="r.sync_status" />
          </div>
          <p class="text-xs text-gray-500 mt-1">{{ formatDate(r.response_date) }}</p>
        </div>
      </div>
      <div v-else class="flex flex-col items-center py-12 text-gray-400">
        <FeatherIcon name="file-text" class="h-8 w-8 mb-2" />
        <p class="text-sm">No forms submitted</p>
      </div>
    </template>

    <!-- Orders tab -->
    <template #tab-orders>
      <div v-if="orders.length" class="space-y-2">
        <div v-for="o in orders" :key="o.name" class="rounded-lg border border-gray-100 bg-gray-50 p-3">
          <div class="flex items-center justify-between">
            <p class="text-sm font-mono text-gray-900">{{ o.name }}</p>
            <p class="text-sm font-semibold">{{ formatUGX(o.grand_total) }}</p>
          </div>
          <div class="flex items-center justify-between mt-1">
            <p class="text-xs text-gray-500">{{ formatDate(o.transaction_date) }}</p>
            <StatusBadge :status="o.status" />
          </div>
        </div>
      </div>
      <div v-else class="flex flex-col items-center py-12 text-gray-400">
        <FeatherIcon name="shopping-cart" class="h-8 w-8 mb-2" />
        <p class="text-sm">No orders</p>
      </div>
    </template>
  </DetailLayout>

  <SlidePanel v-model="editPanel" title="Edit Visit" :saving="saving" @save="save">
    <div v-if="doc" class="space-y-4">
      <FormField v-model="form.status" label="Status" type="select" :options="['Open','In Progress','Completed','Auto Closed','Cancelled']" />
      <FormField v-model="form.notes" label="Notes" type="textarea" />
    </div>
  </SlidePanel>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getDoc, getList, saveDoc } from '@/utils/frappe'
import { successToast, errorToast } from '@/utils/toast'
import DetailLayout from '@/components/detail/DetailLayout.vue'
import DetailField from '@/components/detail/DetailField.vue'
import SlidePanel from '@/components/ui/SlidePanel.vue'
import FormField from '@/components/ui/FormField.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import Btn from '@/components/ui/Btn.vue'
import dayjs from 'dayjs'

const props = defineProps({ name: String })
const doc = ref(null)
const formResponses = ref([])
const orders = ref([])
const editPanel = ref(false)
const saving = ref(false)
const form = reactive({ status: '', notes: '' })

const tabs = [
  { id: 'forms', label: 'Forms' },
  { id: 'orders', label: 'Orders' },
]

async function load() {
  const [d, fr, o] = await Promise.all([
    getDoc('SFA Visit', props.name),
    getList('SFA Form Response', { fields: ['name','form_template','response_date','sync_status'], filters: { visit: props.name }, orderBy: 'response_date desc', limit: 20 }),
    getList('Sales Order', { fields: ['name','transaction_date','status','grand_total'], filters: { customer: d?.customer }, orderBy: 'transaction_date desc', limit: 10 }),
  ])
  doc.value = d
  formResponses.value = fr
  orders.value = o
  Object.assign(form, { status: d.status, notes: d.notes || '' })
}

async function save() {
  saving.value = true
  try {
    await saveDoc({ doctype: 'SFA Visit', name: props.name, ...form })
    successToast('Visit updated')
    editPanel.value = false
    await load()
  } catch (e) { errorToast(e.message) }
  finally { saving.value = false }
}

const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'
const formatTime = (t) => t ? dayjs(t).format('HH:mm') : '—'
const formatUGX = (v) => v >= 1e6 ? `UGX ${(v/1e6).toFixed(1)}M` : `UGX ${(v||0).toLocaleString()}`

onMounted(load)
</script>
