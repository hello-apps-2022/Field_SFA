<template>
  <div class="flex h-full flex-col">
    <div class="flex items-center gap-3 border-b border-outline-gray-2 bg-surface-white px-4 py-2.5">
      <TextInput v-model="search" placeholder="Search orders..." size="sm" class="w-64">
        <template #prefix><FeatherIcon name="search" class="h-3.5 w-3.5 text-ink-gray-4" /></template>
      </TextInput>
      <FormControl type="select" v-model="statusFilter" :options="statusOptions" size="sm" class="w-40" />
      <div class="flex-1" />
      <div class="text-sm font-semibold text-ink-gray-8">
        Total: {{ formatUGX(totalRevenue) }}
      </div>
      <Button size="sm" :loading="list.loading.value" @click="list.reload()">
        <template #prefix><FeatherIcon name="refresh-cw" class="h-3.5 w-3.5" /></template>
        Refresh
      </Button>
    </div>

    <div class="flex-1 overflow-auto">
      <table class="w-full text-sm">
        <thead class="sticky top-0 bg-surface-gray-1 border-b border-outline-gray-2">
          <tr>
            <th class="px-4 py-2.5 text-left text-xs font-medium text-ink-gray-5 uppercase tracking-wide">Order</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium text-ink-gray-5 uppercase tracking-wide">Customer</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium text-ink-gray-5 uppercase tracking-wide">Date</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium text-ink-gray-5 uppercase tracking-wide">Qty (Ctns)</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium text-ink-gray-5 uppercase tracking-wide">Amount</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium text-ink-gray-5 uppercase tracking-wide">Status</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-outline-gray-1">
          <tr v-for="o in filtered" :key="o.name" class="hover:bg-surface-gray-1 cursor-pointer" @click="openInDesk(o.name)">
            <td class="px-4 py-3 font-mono text-xs text-ink-blue-4">{{ o.name }}</td>
            <td class="px-4 py-3 font-medium text-ink-gray-8">{{ o.customer }}</td>
            <td class="px-4 py-3 text-ink-gray-6">{{ formatDate(o.transaction_date) }}</td>
            <td class="px-4 py-3 text-ink-gray-6">{{ o.total_qty }}</td>
            <td class="px-4 py-3 font-medium text-ink-gray-8">{{ formatUGX(o.grand_total) }}</td>
            <td class="px-4 py-3">
              <Badge :label="o.status" :variant="orderVariant(o.status)" size="sm" />
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="!list.loading.value && !filtered.length" class="flex flex-col items-center justify-center py-20 text-ink-gray-4">
        <FeatherIcon name="shopping-cart" class="h-10 w-10 mb-3" />
        <p class="text-sm font-medium">No orders found</p>
      </div>
      <div v-if="list.loading.value" class="flex justify-center py-10">
        <Spinner class="h-5 w-5 text-ink-gray-5" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { createListResource } from 'frappe-ui'
import dayjs from 'dayjs'

const search = ref('')
const statusFilter = ref('')
const statusOptions = [
  { label: 'All Statuses', value: '' },
  { label: 'Draft', value: 'Draft' },
  { label: 'To Deliver and Bill', value: 'To Deliver and Bill' },
  { label: 'Completed', value: 'Completed' },
  { label: 'Cancelled', value: 'Cancelled' },
]

const list = createListResource({
  doctype: 'Sales Order',
  fields: ['name', 'customer', 'transaction_date', 'status', 'total_qty', 'grand_total', 'owner'],
  orderBy: 'transaction_date desc',
  pageLength: 50,
  auto: true,
})

const filtered = computed(() => {
  let l = list.data || []
  if (search.value) {
    const q = search.value.toLowerCase()
    l = l.filter(o => o.customer?.toLowerCase().includes(q) || o.name?.toLowerCase().includes(q))
  }
  if (statusFilter.value) l = l.filter(o => o.status === statusFilter.value)
  return l
})

const totalRevenue = computed(() => filtered.value.reduce((s, o) => s + (o.grand_total || 0), 0))

const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'
const formatUGX = (v) => {
  if (!v) return 'UGX 0'
  if (v >= 1_000_000) return `UGX ${(v / 1_000_000).toFixed(1)}M`
  if (v >= 1_000) return `UGX ${(v / 1_000).toFixed(0)}K`
  return `UGX ${v}`
}
const orderVariant = (s) => ({ 'Completed': 'success', 'Draft': 'subtle', 'Cancelled': 'danger' })[s] || 'subtle'
const openInDesk = (name) => window.open(`/app/sales-order/${name}`, '_blank')
</script>
