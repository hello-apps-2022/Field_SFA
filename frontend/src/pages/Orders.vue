<template>
  <div class="flex h-full flex-col">
    <div class="flex items-center gap-3 border-b border-gray-200 bg-white px-4 py-2.5">
      <div class="relative">
        <FeatherIcon name="search" class="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-gray-400" />
        <input v-model="search" type="text" placeholder="Search orders..."
          class="h-9 rounded-md border border-gray-200 bg-white pl-8 pr-3 text-sm focus:border-gray-400 focus:outline-none w-56" />
      </div>
      <select v-model="statusFilter" class="h-9 rounded-md border border-gray-200 bg-white px-3 text-sm">
        <option value="">All Statuses</option>
        <option>Draft</option><option>To Deliver and Bill</option><option>Completed</option><option>Cancelled</option>
      </select>
      <div class="flex-1" />
      <div class="text-sm font-semibold text-gray-800">Total: {{ formatUGX(totalRevenue) }}</div>
      <button class="flex h-9 items-center gap-1.5 rounded-md border border-gray-200 bg-white px-3 text-sm text-gray-600 hover:bg-gray-50" @click="load">
        <FeatherIcon name="refresh-cw" class="h-3.5 w-3.5" :class="loading ? 'animate-spin' : ''" />
        Refresh
      </button>
      <button class="flex h-9 items-center gap-1.5 rounded-md bg-gray-900 px-3 text-sm font-medium text-white hover:bg-gray-700" @click="openNew">
        <FeatherIcon name="plus" class="h-3.5 w-3.5" />
        New Order
      </button>
    </div>

    <div class="flex-1 overflow-auto">
      <table class="w-full text-sm">
        <thead class="sticky top-0 border-b border-gray-200 bg-gray-50">
          <tr>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Order</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Customer</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Date</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Qty</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Amount</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Status</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="o in filtered" :key="o.name" class="cursor-pointer hover:bg-gray-50 transition-colors" @click="window.open('/app/sales-order/' + o.name, '_blank')">
            <td class="px-4 py-3 font-mono text-xs text-blue-500">{{ o.name }}</td>
            <td class="px-4 py-3 font-medium text-gray-900">{{ o.customer }}</td>
            <td class="px-4 py-3 text-gray-600">{{ formatDate(o.transaction_date) }}</td>
            <td class="px-4 py-3 text-gray-600">{{ o.total_qty }}</td>
            <td class="px-4 py-3 font-medium text-gray-900">{{ formatUGX(o.grand_total) }}</td>
            <td class="px-4 py-3">
              <span class="rounded-full px-2 py-0.5 text-xs font-medium" :class="statusClass(o.status)">{{ o.status }}</span>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="!loading && !filtered.length" class="flex flex-col items-center justify-center py-20 text-gray-400">
        <FeatherIcon name="shopping-cart" class="h-10 w-10 mb-3" />
        <p class="text-sm font-medium">No orders found</p>
      </div>
      <div v-if="loading" class="flex justify-center py-12">
        <FeatherIcon name="loader" class="h-6 w-6 animate-spin text-gray-400" />
      </div>
    </div>

    <!-- Slide Panel - wider for order items -->
    <SlidePanel v-model="panelOpen" title="New Order" :saving="saving" @save="save" width="560px">
      <div class="space-y-4">
        <FormField v-model="form.customer" label="Customer" type="select" :options="customers" required :error="errors.customer" />
        <FormField v-model="form.transaction_date" label="Order Date" type="date" required />
        <FormField v-model="form.delivery_date" label="Delivery Date" type="date" />

        <!-- Items -->
        <div>
          <div class="flex items-center justify-between mb-2">
            <label class="text-xs font-medium text-gray-600">Items <span class="text-red-500">*</span></label>
            <button class="text-xs text-gray-500 hover:text-gray-800 flex items-center gap-1" @click="addItem">
              <FeatherIcon name="plus" class="h-3 w-3" /> Add Item
            </button>
          </div>
          <div class="space-y-2">
            <div v-for="(row, i) in form.items" :key="i" class="grid grid-cols-12 gap-2 items-center">
              <select v-model="row.item_code" @change="onItemChange(row)" class="col-span-5 rounded-md border border-gray-200 bg-white px-2 py-1.5 text-xs focus:border-gray-400 focus:outline-none">
                <option value="">Select item...</option>
                <option v-for="it in items" :key="it.value" :value="it.value">{{ it.label }}</option>
              </select>
              <input v-model.number="row.qty" type="number" placeholder="Qty" min="1" class="col-span-2 rounded-md border border-gray-200 px-2 py-1.5 text-xs focus:outline-none" />
              <input v-model.number="row.rate" type="number" placeholder="Rate" class="col-span-3 rounded-md border border-gray-200 px-2 py-1.5 text-xs focus:outline-none" />
              <div class="col-span-1 text-xs text-gray-500 text-right">{{ formatUGX(row.qty * row.rate) }}</div>
              <button class="col-span-1 flex justify-center text-gray-400 hover:text-red-500" @click="removeItem(i)">
                <FeatherIcon name="x" class="h-3.5 w-3.5" />
              </button>
            </div>
            <div v-if="!form.items.length" class="rounded-md bg-gray-50 px-3 py-2 text-xs text-gray-400">No items added yet</div>
          </div>
          <!-- Total -->
          <div v-if="form.items.length" class="mt-2 flex justify-end">
            <span class="text-sm font-semibold text-gray-900">Order Total: {{ formatUGX(orderTotal) }}</span>
          </div>
        </div>

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

const { customers, items, loadCustomers, loadItems } = useLinkedData()

const search = ref('')
const statusFilter = ref('')
const loading = ref(false)
const saving = ref(false)
const panelOpen = ref(false)
const orders = ref([])
const errors = reactive({})

const form = reactive({ customer: '', transaction_date: dayjs().format('YYYY-MM-DD'), delivery_date: '', items: [], remarks: '' })
const orderTotal = computed(() => form.items.reduce((s, i) => s + (i.qty || 0) * (i.rate || 0), 0))

async function load() {
  loading.value = true
  try {
    const res = await frappe.call({ method: 'frappe.client.get_list', args: { doctype: 'Sales Order', fields: ['name','customer','transaction_date','status','total_qty','grand_total'], order_by: 'transaction_date desc', limit: 200 } })
    orders.value = res.message || []
  } catch (e) { console.error(e) } finally { loading.value = false }
}

function openNew() {
  Object.assign(form, { customer: '', transaction_date: dayjs().format('YYYY-MM-DD'), delivery_date: '', items: [], remarks: '' })
  Object.keys(errors).forEach(k => delete errors[k])
  panelOpen.value = true
}

function addItem() { form.items.push({ item_code: '', qty: 1, rate: 0, item_name: '' }) }
function removeItem(i) { form.items.splice(i, 1) }
function onItemChange(row) {
  const item = items.value.find(i => i.value === row.item_code)
  if (item) { row.item_name = item.label; row.rate = item.rate || 0 }
}

async function save() {
  if (!form.customer) { errors.customer = 'Required'; return }
  if (!form.items.length || !form.items.some(i => i.item_code)) {
    frappe.show_alert({ message: 'Add at least one item', indicator: 'red' }); return
  }
  saving.value = true
  try {
    const doc = {
      doctype: 'Sales Order',
      customer: form.customer,
      transaction_date: form.transaction_date,
      delivery_date: form.delivery_date || form.transaction_date,
      remarks: form.remarks,
      items: form.items.filter(i => i.item_code).map(i => ({
        doctype: 'Sales Order Item',
        item_code: i.item_code, item_name: i.item_name,
        qty: i.qty, rate: i.rate, delivery_date: form.delivery_date || form.transaction_date,
      })),
    }
    await frappe.call({ method: 'frappe.client.insert', args: { doc } })
    frappe.show_alert({ message: 'Order created', indicator: 'green' })
    panelOpen.value = false; load()
  } catch (e) { frappe.show_alert({ message: e.message || 'Save failed', indicator: 'red' }) }
  finally { saving.value = false }
}

const filtered = computed(() => {
  let l = orders.value
  if (search.value) { const q = search.value.toLowerCase(); l = l.filter(o => o.customer?.toLowerCase().includes(q) || o.name?.toLowerCase().includes(q)) }
  if (statusFilter.value) l = l.filter(o => o.status === statusFilter.value)
  return l
})

const totalRevenue = computed(() => filtered.value.reduce((s, o) => s + (o.grand_total || 0), 0))
const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'
const formatUGX = (v) => { if (!v) return 'UGX 0'; if (v >= 1_000_000) return `UGX ${(v/1_000_000).toFixed(1)}M`; if (v >= 1_000) return `UGX ${(v/1_000).toFixed(0)}K`; return `UGX ${v}` }
const statusClass = (s) => ({ 'Completed': 'bg-green-50 text-green-700', 'Draft': 'bg-gray-100 text-gray-600', 'Cancelled': 'bg-red-50 text-red-700' })[s] || 'bg-gray-100 text-gray-600'

onMounted(() => { load(); loadCustomers(); loadItems() })
</script>
