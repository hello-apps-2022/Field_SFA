<template>
  <div class="flex h-full flex-col overflow-hidden">

    <!-- Header -->
    <div class="flex h-[52px] shrink-0 items-center border-b border-gray-100 bg-white px-5 gap-3">
      <h1 class="text-sm font-semibold text-gray-900">Orders</h1>
      <div class="flex-1" />
      <span class="text-xs text-gray-400">{{ total }} orders</span>
      <button @click="searchModal=true" class="inline-flex h-8 items-center gap-1.5 rounded-md bg-gray-900 px-3 text-xs font-medium text-white hover:bg-gray-700">
        <FeatherIcon name="plus" class="h-3.5 w-3.5" /> New Order
      </button>
    </div>

    <CustomerSearchModal v-model="searchModal" action="order" />

    <!-- Filters -->
    <div class="flex shrink-0 flex-wrap items-center gap-2 border-b border-gray-100 bg-white px-4 py-2.5">
      <div class="relative">
        <FeatherIcon name="search" class="absolute left-2.5 top-2 h-3.5 w-3.5 text-gray-400 pointer-events-none" />
        <input v-model="search" @input="onSearchInput" placeholder="Customer, order ID…"
          class="h-8 w-44 rounded-md border border-gray-200 bg-white pl-8 pr-3 text-sm focus:border-gray-400 focus:outline-none" />
      </div>

      <select v-model="repFilter" @change="applyFilters" class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
        <option value="">All Reps</option>
        <option v-for="r in repOptions" :key="r">{{ r }}</option>
      </select>

      <select v-model="statusFilter" @change="applyFilters" class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
        <option value="">All Statuses</option>
        <option value="Draft">Draft</option>
        <option value="To Deliver and Bill">To Deliver and Bill</option>
        <option value="To Bill">To Bill</option>
        <option value="Completed">Completed</option>
        <option value="Cancelled">Cancelled</option>
      </select>

      <DateRangeFilter v-model:from="dateFrom" v-model:to="dateTo" default-preset="this_month" @change="applyFilters" />

      <button @click="clearFilters" class="h-8 rounded-md border border-gray-200 bg-white px-3 text-xs text-gray-500 hover:bg-gray-50">
        Clear
      </button>
    </div>

    <!-- Summary strip -->
    <div v-if="total" class="flex shrink-0 items-center gap-6 border-b border-gray-100 bg-gray-50 px-5 py-2 text-sm">
      <span><strong class="text-gray-900">{{ total }}</strong> <span class="text-gray-400">orders</span></span>
      <span><strong class="text-gray-900">{{ fmt(totalRevenue) }}</strong> <span class="text-gray-400">total value</span></span>
      <span><strong class="text-gray-900">{{ totalCartons }}</strong> <span class="text-gray-400">cartons</span></span>
    </div>

    <!-- Table -->
    <div class="flex-1 overflow-auto">
      <div v-if="loading" class="flex h-40 items-center justify-center">
        <FeatherIcon name="loader" class="h-6 w-6 animate-spin text-gray-400" />
      </div>

      <table v-else-if="filtered.length" class="w-full text-sm">
        <thead class="sticky top-0 bg-white border-b border-gray-100">
          <tr>
            <th class="px-5 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Order ID</th>
            <th class="px-5 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Customer</th>
            <th class="px-5 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Rep</th>
            <th class="px-5 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Date</th>
            <th class="px-5 py-2.5 text-right text-[10px] font-semibold uppercase tracking-wide text-gray-400">Cartons</th>
            <th class="px-5 py-2.5 text-right text-[10px] font-semibold uppercase tracking-wide text-gray-400">Amount</th>
            <th class="px-5 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Status</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr v-for="o in filtered" :key="o.name"
            class="cursor-pointer hover:bg-gray-50 transition-colors"
            @click="$router.push('/orders/' + o.name)"
          >
            <td class="px-5 py-3 font-mono text-xs text-blue-600">{{ o.name }}</td>
            <td class="px-5 py-3 font-medium text-gray-900">{{ o.customer }}</td>
            <td class="px-5 py-3 text-gray-500">{{ o.sales_person || '—' }}</td>
            <td class="px-5 py-3 text-gray-500">{{ formatDate(o.transaction_date) }}</td>
            <td class="px-5 py-3 text-right text-gray-700">{{ o.total_qty || '—' }}</td>
            <td class="px-5 py-3 text-right font-medium text-gray-900">{{ fmt(o.grand_total) }}</td>
            <td class="px-5 py-3">
              <StatusBadge :status="o.status" />
            </td>
          </tr>
        </tbody>
      </table>

      <div v-else class="flex flex-col items-center py-20 text-gray-400">
        <FeatherIcon name="shopping-cart" class="h-10 w-10 mb-3" />
        <p class="text-sm font-medium text-gray-500">No orders found</p>
        <p class="text-xs mt-1">Try adjusting your filters</p>
      </div>
    </div>

    <!-- Pagination footer -->
    <div v-if="total" class="shrink-0 border-t border-gray-100 bg-white px-5">
      <Pagination :page="page" :page-size="pageSize" :total="total" :loading="loading"
        @update:page="goToPage" @load-more="loadMore" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDateRange } from '@/composables/useDateRange'
import { useLinkedData } from '@/composables/useLinkedData'
import { getList, call } from '@/utils/frappe'
import { formatCurrency } from '@/utils/currency'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import DateRangeFilter from '@/components/ui/DateRangeFilter.vue'
import Pagination from '@/components/ui/Pagination.vue'
import dayjs from 'dayjs'
import CustomerSearchModal from '@/components/ui/CustomerSearchModal.vue'

const orders = ref([])
const searchModal = ref(false)
const loading = ref(false)
const search = ref('')
const repFilter = ref('')
const statusFilter = ref('')
const { dateFrom, dateTo, dateError, setFrom, setTo, reset: resetDates } = useDateRange(30)

// Pagination + server-side totals
const page = ref(1)
const pageSize = 50
const total = ref(0)
const sumRevenue = ref(0)
const sumCartons = ref(0)

// Rep options come from all sales persons (not just the current page).
const repOptions = ref([])
const linked = useLinkedData()

// List as-is — filtering/search happen server-side now.
const filtered = computed(() => orders.value)
const totalRevenue = computed(() => sumRevenue.value)
const totalCartons = computed(() => sumCartons.value)

let searchTimer = null
function onSearchInput() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { page.value = 1; load() }, 350)
}

async function load(append = false) {
  loading.value = true
  try {
    const res = (await call('sfa_core.api.list.get_orders', {
      search: search.value || null,
      rep: repFilter.value || null,
      status: statusFilter.value || null,
      date_from: dateFrom.value || null,
      date_to: dateTo.value || null,
      start: (page.value - 1) * pageSize,
      page_length: pageSize,
    })).message || {}
    const items = res.items || []
    orders.value = append ? [...orders.value, ...items] : items
    total.value = res.total || 0
    sumRevenue.value = res.sum_revenue || 0
    sumCartons.value = res.sum_qty || 0
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

// Desktop: jump to a page (replace). Mobile: load-more (append).
function goToPage(p) { page.value = p; load(false) }
function loadMore() { page.value += 1; load(true) }

// Re-load page 1 when a server-side filter changes.
function applyFilters() { page.value = 1; load(false) }

function clearFilters() {
  search.value = ''
  repFilter.value = ''
  statusFilter.value = ''
  resetDates()
  page.value = 1
  load()
}

const fmt = (v) => formatCurrency(v || 0)
const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'

onMounted(async () => {
  await linked.loadSalesPersons()
  repOptions.value = linked.salesPersons.value
  // Initial load is triggered by DateRangeFilter emitting its default range on mount.
})
</script>
