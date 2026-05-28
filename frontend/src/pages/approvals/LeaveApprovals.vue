<template>
  <div class="flex h-full flex-col overflow-hidden">

    <!-- Header -->
    <div class="flex h-[52px] shrink-0 items-center border-b border-gray-100 bg-white px-5 gap-3">
      <h1 class="text-sm font-semibold text-gray-900">Leave Approvals</h1>
      <div class="flex-1" />
      <span class="text-xs text-gray-400">{{ total }} pending</span>
    </div>

    <!-- Filters -->
    <div class="flex shrink-0 flex-wrap items-center gap-2 border-b border-gray-100 bg-white px-4 py-2.5">
      <DateRangeFilter v-model:from="dateFrom" v-model:to="dateTo" default-preset="this_month" @change="applyFilters" />
      <button @click="clearFilters" class="h-8 rounded-md border border-gray-200 bg-white px-3 text-xs text-gray-500 hover:bg-gray-50">Clear</button>
      <button @click="load" class="ml-auto h-8 rounded-md border border-gray-200 bg-white px-3 text-xs text-gray-500 hover:bg-gray-50">
        <FeatherIcon name="refresh-cw" class="inline h-3 w-3 mr-1" /> Refresh
      </button>
    </div>

    <!-- Summary -->
    <div v-if="total" class="flex shrink-0 items-center gap-6 border-b border-gray-100 bg-gray-50 px-5 py-2 text-sm">
      <span><strong class="text-gray-900">{{ total }}</strong> <span class="text-gray-400">awaiting approval</span></span>
    </div>

    <!-- Table -->
    <div class="flex-1 overflow-auto">
      <div v-if="loading" class="flex h-40 items-center justify-center">
        <FeatherIcon name="loader" class="h-6 w-6 animate-spin text-gray-400" />
      </div>

      <table v-else-if="items.length" class="w-full text-sm">
        <thead class="sticky top-0 bg-white border-b border-gray-100">
          <tr>
            <th class="px-5 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Employee</th>
            <th class="px-5 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Type</th>
            <th class="px-5 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">From</th>
            <th class="px-5 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">To</th>
            <th class="px-5 py-2.5 text-right text-[10px] font-semibold uppercase tracking-wide text-gray-400">Days</th>
            <th class="px-5 py-2.5 w-8"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr v-for="l in items" :key="l.name" @click="openDrawer(l.name)" class="hover:bg-gray-50 transition-colors cursor-pointer">
            <td class="px-5 py-3 font-medium text-gray-900">{{ l.employee_name || l.employee }}</td>
            <td class="px-5 py-3 text-gray-500">{{ l.leave_type }}</td>
            <td class="px-5 py-3 text-gray-500">{{ formatDate(l.from_date) }}</td>
            <td class="px-5 py-3 text-gray-500">{{ formatDate(l.to_date) }}</td>
            <td class="px-5 py-3 text-right font-medium text-gray-900">{{ l.total_leave_days ?? '—' }}</td>
            <td class="px-3 py-3 text-right text-gray-300">
              <FeatherIcon name="chevron-right" class="h-4 w-4" />
            </td>
          </tr>
        </tbody>
      </table>

      <div v-else class="flex flex-col items-center py-20 text-gray-400">
        <FeatherIcon name="check-circle" class="h-10 w-10 mb-3" />
        <p class="text-sm font-medium text-gray-500">Nothing awaiting your approval</p>
        <p class="text-xs mt-1">You're all caught up</p>
      </div>
    </div>

    <div v-if="total > pageSize" class="shrink-0 border-t border-gray-100 bg-white px-5 py-2">
      <Pagination :page="page" :page-size="pageSize" :total="total" :loading="loading" @update:page="onPage" />
    </div>

    <!-- Drawer (queue context — shows the 'awaiting your review' banner) -->
    <LeaveClaimDrawer
      v-model="drawerOpen"
      :leave-name="drawerLeave"
      context="queue"
      @changed="load"
    />

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { call } from '@/utils/frappe'
import FeatherIcon from '@/components/ui/FeatherIcon.vue'
import DateRangeFilter from '@/components/ui/DateRangeFilter.vue'
import Pagination from '@/components/ui/Pagination.vue'
import LeaveClaimDrawer from '@/components/ui/LeaveClaimDrawer.vue'
import dayjs from 'dayjs'

const loading = ref(false)
const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 50

const dateFrom = ref('')
const dateTo = ref('')

// Drawer state — clicking a row opens it; drawer handles approve/reject + reason flow
const drawerOpen = ref(false)
const drawerLeave = ref('')

const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'

async function load() {
  loading.value = true
  try {
    // Single-tier: just fetch leaves in "Pending Approval". Both managers and
    // admins see the same queue; backend RBAC scopes by territory for managers.
    const res = await call('sfa_core.api.leave.get_leave_applications', {
      start: 0, page_length: 200, status: 'Pending Approval',
      from_date: dateFrom.value || undefined, to_date: dateTo.value || undefined,
    })
    items.value = res.message.items || []
    total.value = res.message.total || 0
  } finally {
    loading.value = false
  }
}

function applyFilters() { page.value = 1; load() }
function clearFilters() { dateFrom.value = ''; dateTo.value = ''; applyFilters() }
function onPage(p) { page.value = p; load() }

function openDrawer(name) {
  drawerLeave.value = name
  drawerOpen.value = true
}

onMounted(load)
</script>
