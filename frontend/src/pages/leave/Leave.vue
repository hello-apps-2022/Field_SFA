<template>
  <div class="flex h-full flex-col overflow-hidden">

    <!-- Header -->
    <div class="flex h-[52px] shrink-0 items-center border-b border-gray-100 bg-white px-5 gap-3">
      <h1 class="text-sm font-semibold text-gray-900">Leave</h1>
      <div class="flex-1" />
      <span class="text-xs text-gray-400">{{ total }} requests</span>
      <button @click="openCreate" class="inline-flex h-8 items-center gap-1.5 rounded-md bg-gray-900 px-3 text-xs font-medium text-white hover:bg-gray-700">
        <FeatherIcon name="plus" class="h-3.5 w-3.5" /> Apply for Leave
      </button>
    </div>

    <!-- Filters -->
    <div class="flex shrink-0 flex-wrap items-center gap-2 border-b border-gray-100 bg-white px-4 py-2.5">
      <select v-model="statusFilter" @change="applyFilters" class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
        <option value="">All Statuses</option>
        <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
      </select>

      <DateRangeFilter v-model:from="dateFrom" v-model:to="dateTo" default-preset="this_year" forward-looking @change="applyFilters" />

      <button @click="clearFilters" class="h-8 rounded-md border border-gray-200 bg-white px-3 text-xs text-gray-500 hover:bg-gray-50">
        Clear
      </button>
    </div>

    <!-- Balance strip — visible only to reps (managers/admins viewing others'
         leaves don't need their own balance polluting the header). -->
    <div v-if="balances.length" class="flex shrink-0 items-center gap-6 border-b border-gray-100 bg-gray-50 px-5 py-2 text-sm">
      <span class="text-gray-400 text-xs uppercase tracking-wide">Balance</span>
      <span v-for="b in balances" :key="b.leave_type">
        <strong class="text-gray-900">{{ b.balance ?? '—' }}</strong>
        <span class="text-gray-400 ml-1">{{ b.leave_type }}</span>
      </span>
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
            <th class="px-5 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Status</th>
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
            <td class="px-5 py-3">
              <StatusBadge :status="l.workflow_state" :color-map="statusColors" />
            </td>
            <td class="px-3 py-3 text-right text-gray-300">
              <FeatherIcon name="chevron-right" class="h-4 w-4" />
            </td>
          </tr>
        </tbody>
      </table>

      <div v-else class="flex flex-col items-center py-20 text-gray-400">
        <FeatherIcon name="calendar" class="h-10 w-10 mb-3" />
        <p class="text-sm font-medium text-gray-500">No leave requests found</p>
        <p class="text-xs mt-1">Try adjusting your filters, or apply for leave</p>
      </div>
    </div>

    <!-- Pagination footer -->
    <div v-if="total > pageSize" class="shrink-0 border-t border-gray-100 bg-white px-5 py-2">
      <Pagination :page="page" :page-size="pageSize" :total="total" :loading="loading" @update:page="onPage" />
    </div>

    <!-- Drawer — handles create/view/edit/review/approve/reject end-to-end -->
    <LeaveClaimDrawer
      v-model="drawerOpen"
      :leave-name="drawerLeave"
      :initial-mode="drawerMode"
      @changed="onDrawerChanged"
    />

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { call } from '@/utils/frappe'
import { auth } from '@/utils/auth'
import FeatherIcon from '@/components/ui/FeatherIcon.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import DateRangeFilter from '@/components/ui/DateRangeFilter.vue'
import Pagination from '@/components/ui/Pagination.vue'
import LeaveClaimDrawer from '@/components/ui/LeaveClaimDrawer.vue'
import dayjs from 'dayjs'

const loading = ref(false)
const items = ref([])
const total = ref(0)
const balances = ref([])
const page = ref(1)
const pageSize = 50

const statusFilter = ref('')
const dateFrom = ref('')
const dateTo = ref('')

const statuses = ['Draft', 'Pending Approval', 'Approved', 'Rejected']
const statusColors = {
  'Draft': 'bg-gray-100 text-gray-600',
  'Pending Approval': 'bg-yellow-50 text-yellow-700',
  'Approved': 'bg-green-50 text-green-700',
  'Rejected': 'bg-red-50 text-red-600',
}

// Drawer state
const drawerOpen = ref(false)
const drawerLeave = ref('')
const drawerMode = ref('view')

const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'

async function load() {
  loading.value = true
  try {
    const res = await call('sfa_core.api.leave.get_leave_applications', {
      start: (page.value - 1) * pageSize,
      page_length: pageSize,
      status: statusFilter.value || undefined,
      from_date: dateFrom.value || undefined,
      to_date: dateTo.value || undefined,
    })
    items.value = res.message.items || []
    total.value = res.message.total || 0
  } finally {
    loading.value = false
  }
}

async function loadBalances() {
  // Only reps need their own balance shown. Admins/managers typically don't,
  // and the API returns [] when there's no linked employee anyway.
  if (!auth.employee) return
  try {
    const bal = await call('sfa_core.api.leave.get_leave_balance')
    balances.value = bal.message.balances || []
  } catch (e) { /* balance is best-effort */ }
}

function applyFilters() { page.value = 1; load() }
function clearFilters() { statusFilter.value = ''; dateFrom.value = ''; dateTo.value = ''; applyFilters() }
function onPage(p) { page.value = p; load() }

function openCreate() {
  drawerLeave.value = ''
  drawerMode.value = 'edit'
  drawerOpen.value = true
}

function openDrawer(name) {
  drawerLeave.value = name
  drawerMode.value = 'view'
  drawerOpen.value = true
}

// Drawer emits 'changed' after save/submit/approve/reject — refresh the list
// AND balances (an approved leave consumes balance).
function onDrawerChanged() {
  load()
  loadBalances()
}

onMounted(() => { load(); loadBalances() })
</script>
