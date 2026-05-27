<template>
  <DetailLayout
    :title="doc?.customer_name || name"
    :subtitle="doc?.territory || ''"
    back-to="/customers"
    back-label="Customers"
    :tabs="tabs"
  >
    <template #actions>
      <Btn variant="default" icon="edit-2" @click="editPanel = true">Edit</Btn>
    </template>

    <template #fields>
      <div v-if="doc">
        <DetailField label="Customer Name" :value="doc.customer_name" :editable="false" />
        <DetailField label="Group" :value="doc.customer_group" :editable="false" />
        <DetailField label="Territory" :value="doc.territory" :editable="false" />
        <DetailField label="Mobile" :value="doc.mobile_no" :editable="false" />
        <DetailField label="Email" :value="doc.email_id" :editable="false" />
        <DetailField label="Status" :editable="false">
          <StatusBadge :status="doc.disabled ? 'Inactive' : 'Active'" />
        </DetailField>
        <DetailField v-if="doc.customer_details" label="Notes" :value="doc.customer_details" :editable="false" />
      </div>
      <div v-else class="flex justify-center py-8">
        <FeatherIcon name="loader" class="h-5 w-5 animate-spin text-gray-400" />
      </div>
    </template>

    <template #tab-visits>
      <div v-if="visits.length" class="space-y-2">
        <div
          v-for="v in visits" :key="v.name"
          class="flex items-center justify-between rounded-lg border border-gray-100 bg-gray-50 p-3 cursor-pointer hover:bg-gray-100"
          @click="$router.push('/visits/' + v.name)"
        >
          <div>
            <p class="text-sm font-medium text-gray-900">{{ formatDate(v.visit_date) }}</p>
            <p class="text-xs text-gray-500">{{ v.sales_person }}</p>
          </div>
          <StatusBadge :status="v.status" />
        </div>
      </div>
      <div v-else class="flex flex-col items-center py-12 text-gray-400">
        <FeatherIcon name="map-pin" class="h-8 w-8 mb-2" />
        <p class="text-sm">No visits yet</p>
      </div>
    </template>

    <template #tab-orders>
      <div v-if="orders.length" class="space-y-2">
        <div v-for="o in orders" :key="o.name" class="flex items-center justify-between rounded-lg border border-gray-100 bg-gray-50 p-3">
          <div>
            <p class="text-sm font-medium font-mono text-gray-900">{{ o.name }}</p>
            <p class="text-xs text-gray-500">{{ formatDate(o.transaction_date) }}</p>
          </div>
          <div class="text-right">
            <p class="text-sm font-semibold text-gray-900">{{ formatUGX(o.grand_total) }}</p>
            <StatusBadge :status="o.status" />
          </div>
        </div>
      </div>
      <div v-else class="flex flex-col items-center py-12 text-gray-400">
        <FeatherIcon name="shopping-cart" class="h-8 w-8 mb-2" />
        <p class="text-sm">No orders yet</p>
      </div>
    </template>

    <template #tab-payments>
      <div v-if="payments.length" class="space-y-2">
        <div v-for="p in payments" :key="p.name" class="flex items-center justify-between rounded-lg border border-gray-100 bg-gray-50 p-3">
          <div>
            <p class="text-sm font-medium text-gray-900">{{ formatDate(p.payment_date) }}</p>
            <p class="text-xs text-gray-500">{{ p.payment_type }}</p>
          </div>
          <p class="text-sm font-semibold text-gray-900">{{ formatUGX(p.amount) }}</p>
        </div>
      </div>
      <div v-else class="flex flex-col items-center py-12 text-gray-400">
        <FeatherIcon name="credit-card" class="h-8 w-8 mb-2" />
        <p class="text-sm">No payments yet</p>
      </div>
    </template>
  </DetailLayout>

  <SlidePanel v-model="editPanel" title="Edit Customer" :saving="saving" @save="save">
    <div v-if="doc" class="space-y-4">
      <FormField v-model="form.customer_name" label="Customer Name" required />
      <FormField v-model="form.customer_group" label="Customer Group" type="select" :options="customerGroups" />
      <FormField v-model="form.territory" label="Territory" type="select" :options="territories" />
      <FormField v-model="form.mobile_no" label="Mobile" type="tel" />
      <FormField v-model="form.email_id" label="Email" type="email" />
      <FormField v-model="form.customer_details" label="Notes" type="textarea" />
    </div>
  </SlidePanel>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getDoc, getList, saveDoc } from '@/utils/frappe'
import { successToast, errorToast } from '@/utils/toast'
import { useLinkedData } from '@/composables/useLinkedData'
import DetailLayout from '@/components/detail/DetailLayout.vue'
import DetailField from '@/components/detail/DetailField.vue'
import SlidePanel from '@/components/ui/SlidePanel.vue'
import FormField from '@/components/ui/FormField.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import Btn from '@/components/ui/Btn.vue'
import dayjs from 'dayjs'

const props = defineProps({ name: String })
const { customerGroups, territories, loadCustomerGroups, loadTerritories } = useLinkedData()

const doc = ref(null)
const visits = ref([])
const orders = ref([])
const payments = ref([])
const editPanel = ref(false)
const saving = ref(false)
const form = reactive({
  customer_name: '', customer_group: '', territory: '',
  mobile_no: '', email_id: '', customer_details: '',
})

const tabs = [
  { id: 'visits', label: 'Visits' },
  { id: 'orders', label: 'Orders' },
  { id: 'payments', label: 'Payments' },
]

async function load() {
  const [d, v, o, p] = await Promise.all([
    getDoc('Customer', props.name),
    getList('SFA Visit', {
      fields: ['name', 'visit_date', 'sales_person', 'status'],
      filters: { customer: props.name },
      orderBy: 'visit_date desc', limit: 50,
    }),
    getList('Sales Order', {
      fields: ['name', 'transaction_date', 'status', 'grand_total'],
      filters: { customer: props.name },
      orderBy: 'transaction_date desc', limit: 50,
    }),
    getList('SFA Payment', {
      fields: ['name', 'payment_date', 'payment_type', 'amount'],
      filters: { customer: props.name },
      orderBy: 'payment_date desc', limit: 50,
    }),
  ])
  doc.value = d
  visits.value = v
  orders.value = o
  payments.value = p
  Object.assign(form, {
    customer_name: d.customer_name || '',
    customer_group: d.customer_group || '',
    territory: d.territory || '',
    mobile_no: d.mobile_no || '',
    email_id: d.email_id || '',
    customer_details: d.customer_details || '',
  })
}

async function save() {
  saving.value = true
  try {
    await saveDoc({
      doctype: 'Customer',
      name: props.name,
      customer_type: 'Company',
      ...form,
    })
    successToast('Customer updated')
    editPanel.value = false
    await load()
  } catch (e) {
    errorToast(e.message || 'Save failed')
  } finally {
    saving.value = false
  }
}

const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'
const formatUGX = (v) => v >= 1e6 ? `UGX ${(v / 1e6).toFixed(1)}M` : `UGX ${(v || 0).toLocaleString()}`

onMounted(() => {
  load()
  loadCustomerGroups()
  loadTerritories()
})
</script>
