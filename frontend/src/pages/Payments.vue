<template>
  <div class="flex h-full flex-col">
    <div class="flex items-center gap-3 border-b border-gray-200 bg-white px-4 py-2.5">
      <div class="relative">
        <FeatherIcon name="search" class="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-gray-400" />
        <input v-model="search" type="text" placeholder="Search payments..."
          class="h-9 rounded-md border border-gray-200 bg-white pl-8 pr-3 text-sm focus:border-gray-400 focus:outline-none w-56" />
      </div>
      <select v-model="typeFilter" class="h-9 rounded-md border border-gray-200 bg-white px-3 text-sm">
        <option value="">All Types</option>
        <option v-for="t in paymentTypeOptions" :key="t">{{ t }}</option>
      </select>
      <div class="flex-1" />
      <div class="text-sm font-semibold text-gray-800">Total: {{ formatUGX(totalAmount) }}</div>
      <button class="flex h-9 items-center gap-1.5 rounded-md border border-gray-200 bg-white px-3 text-sm text-gray-600 hover:bg-gray-50" @click="load">
        <FeatherIcon name="refresh-cw" class="h-3.5 w-3.5" :class="loading ? 'animate-spin' : ''" />
        Refresh
      </button>
      <button class="flex h-9 items-center gap-1.5 rounded-md bg-gray-900 px-3 text-sm font-medium text-white hover:bg-gray-700" @click="openNew">
        <FeatherIcon name="plus" class="h-3.5 w-3.5" />
        Record Payment
      </button>
    </div>

    <div class="flex-1 overflow-auto">
      <table class="w-full text-sm">
        <thead class="sticky top-0 border-b border-gray-200 bg-gray-50">
          <tr>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Payment ID</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Customer</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Sales Person</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Date</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Type</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Amount</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Reference</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="p in filtered" :key="p.name" class="hover:bg-gray-50 transition-colors">
            <td class="px-4 py-3 font-mono text-xs text-gray-400">{{ p.name }}</td>
            <td class="px-4 py-3 font-medium text-gray-900">{{ p.customer }}</td>
            <td class="px-4 py-3 text-gray-600">{{ p.sales_person }}</td>
            <td class="px-4 py-3 text-gray-600">{{ formatDate(p.payment_date) }}</td>
            <td class="px-4 py-3">
              <span class="rounded-full bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700">{{ p.payment_type || '—' }}</span>
            </td>
            <td class="px-4 py-3 font-semibold text-gray-900">{{ formatUGX(p.amount) }}</td>
            <td class="px-4 py-3 text-gray-500 text-xs">{{ p.reference_no || p.cheque_no || '—' }}</td>
          </tr>
        </tbody>
      </table>
      <div v-if="!loading && !filtered.length" class="flex flex-col items-center justify-center py-20 text-gray-400">
        <FeatherIcon name="credit-card" class="h-10 w-10 mb-3" />
        <p class="text-sm font-medium">No payments found</p>
      </div>
      <div v-if="loading" class="flex justify-center py-12">
        <FeatherIcon name="loader" class="h-6 w-6 animate-spin text-gray-400" />
      </div>
    </div>

    <div class="flex items-center justify-between border-t border-gray-200 bg-white px-4 py-2">
      <p class="text-xs text-gray-400">{{ filtered.length }} payments</p>
    </div>

    <!-- Slide Panel -->
    <SlidePanel v-model="panelOpen" title="Record Payment" :saving="saving" save-label="Record Payment" @save="save">
      <div class="space-y-4">
        <FormField v-model="form.customer" label="Customer" type="select" :options="customers" required :error="errors.customer" />
        <FormField v-model="form.sales_person" label="Sales Person" type="select" :options="salesPersons" required :error="errors.sales_person" />
        <FormField v-model="form.visit" label="Visit (optional)" type="text" placeholder="SFA-VISIT-2026-00001" help="Link to the visit this payment relates to" />
        <FormField v-model="form.payment_date" label="Payment Date" type="date" required :error="errors.payment_date" />
        <FormField v-model="form.payment_type" label="Payment Type" type="select" :options="paymentTypes" required :error="errors.payment_type" />
        <FormField v-model="form.amount" label="Amount (UGX)" type="number" required :error="errors.amount" />
        <FormField v-model="form.reference_no" label="Reference / Receipt No" />
        <FormField v-model="form.cheque_no" label="Cheque No" help="If payment by cheque" />
        <FormField v-model="form.mobile_money_provider" label="Mobile Money Provider" help="e.g. MTN MoMo, Airtel Money" />
        <FormField v-model="form.remarks" label="Remarks" type="textarea" />
      </div>
    </SlidePanel>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import SlidePanel from '@/components/ui/SlidePanel.vue'
import FormField from '@/components/ui/FormField.vue'
import { useLinkedData } from '@/composables/useLinkedData'
import dayjs from 'dayjs'

const { customers, salesPersons, paymentTypes, loadCustomers, loadSalesPersons, loadPaymentTypes } = useLinkedData()

const search = ref('')
const typeFilter = ref('')
const loading = ref(false)
const saving = ref(false)
const panelOpen = ref(false)
const payments = ref([])
const errors = reactive({})

const paymentTypeOptions = computed(() => [...new Set(payments.value.map(p => p.payment_type).filter(Boolean))])
const totalAmount = computed(() => filtered.value.reduce((s, p) => s + (p.amount || 0), 0))

const form = reactive({ customer: '', sales_person: '', visit: '', payment_date: dayjs().format('YYYY-MM-DD'), payment_type: '', amount: '', reference_no: '', cheque_no: '', mobile_money_provider: '', remarks: '' })

async function load() {
  loading.value = true
  try {
    const res = await frappe.call({ method: 'frappe.client.get_list', args: { doctype: 'SFA Payment', fields: ['name','customer','sales_person','payment_date','payment_type','amount','reference_no','cheque_no'], order_by: 'payment_date desc', limit: 200 } })
    payments.value = res.message || []
  } catch (e) { console.error(e) } finally { loading.value = false }
}

function openNew() {
  Object.assign(form, { customer: '', sales_person: '', visit: '', payment_date: dayjs().format('YYYY-MM-DD'), payment_type: '', amount: '', reference_no: '', cheque_no: '', mobile_money_provider: '', remarks: '' })
  Object.keys(errors).forEach(k => delete errors[k])
  panelOpen.value = true
}

async function save() {
  let valid = true
  if (!form.customer) { errors.customer = 'Required'; valid = false }
  if (!form.sales_person) { errors.sales_person = 'Required'; valid = false }
  if (!form.payment_date) { errors.payment_date = 'Required'; valid = false }
  if (!form.payment_type) { errors.payment_type = 'Required'; valid = false }
  if (!form.amount || Number(form.amount) <= 0) { errors.amount = 'Enter a valid amount'; valid = false }
  if (!valid) return
  saving.value = true
  try {
    const doc = { doctype: 'SFA Payment', currency: 'UGX', ...form, amount: Number(form.amount) }
    await frappe.call({ method: 'frappe.client.insert', args: { doc } })
    frappe.show_alert({ message: 'Payment recorded', indicator: 'green' })
    panelOpen.value = false; load()
  } catch (e) { frappe.show_alert({ message: e.message || 'Save failed', indicator: 'red' }) }
  finally { saving.value = false }
}

const filtered = computed(() => {
  let l = payments.value
  if (search.value) { const q = search.value.toLowerCase(); l = l.filter(p => p.customer?.toLowerCase().includes(q) || p.sales_person?.toLowerCase().includes(q)) }
  if (typeFilter.value) l = l.filter(p => p.payment_type === typeFilter.value)
  return l
})

const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'
const formatUGX = (v) => { if (!v) return 'UGX 0'; if (v >= 1_000_000) return `UGX ${(v/1_000_000).toFixed(1)}M`; if (v >= 1_000) return `UGX ${(v/1_000).toFixed(0)}K`; return `UGX ${v}` }

onMounted(() => { load(); loadCustomers(); loadSalesPersons(); loadPaymentTypes() })
</script>
