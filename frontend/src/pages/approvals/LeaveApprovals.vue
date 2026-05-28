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
      <select v-if="isAdmin" v-model="tierFilter" @change="applyFilters" class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
        <option value="">All Pending Tiers</option>
        <option value="Pending Manager Approval">Manager Tier</option>
        <option value="Pending Finance Approval">Finance Tier</option>
      </select>
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
            <th class="px-5 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Awaiting</th>
            <th class="px-5 py-2.5 text-right text-[10px] font-semibold uppercase tracking-wide text-gray-400">Action</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr v-for="l in items" :key="l.name" class="hover:bg-gray-50 transition-colors">
            <td class="px-5 py-3 font-medium text-gray-900">{{ l.employee_name || l.employee }}</td>
            <td class="px-5 py-3 text-gray-500">{{ l.leave_type }}</td>
            <td class="px-5 py-3 text-gray-500">{{ formatDate(l.from_date) }}</td>
            <td class="px-5 py-3 text-gray-500">{{ formatDate(l.to_date) }}</td>
            <td class="px-5 py-3 text-right font-medium text-gray-900">{{ l.total_leave_days ?? '—' }}</td>
            <td class="px-5 py-3">
              <StatusBadge :status="l.workflow_state" :color-map="statusColors" />
            </td>
            <td class="px-5 py-3 text-right whitespace-nowrap">
              <template v-if="canAct(l) && !isOwn(l)">
                <button @click="act(l, approveAction(l))" class="text-xs font-medium text-green-700 hover:underline">Approve</button>
                <button @click="act(l, rejectAction(l))" class="ml-3 text-xs font-medium text-red-600 hover:underline">Reject</button>
              </template>
              <span v-else-if="isOwn(l)" class="text-xs text-gray-300">Your request</span>
              <span v-else class="text-xs text-gray-300">—</span>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { call } from '@/utils/frappe'
import { auth } from '@/utils/auth'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import DateRangeFilter from '@/components/ui/DateRangeFilter.vue'
import Pagination from '@/components/ui/Pagination.vue'
import dayjs from 'dayjs'

const loading = ref(false)
const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 50

const isAdmin = auth.isAdmin
const isManager = auth.isManager
const tierFilter = ref('')
const dateFrom = ref('')
const dateTo = ref('')

const statusColors = {
  'Pending Manager Approval': 'bg-yellow-50 text-yellow-700',
  'Pending Finance Approval': 'bg-blue-50 text-blue-700',
}

const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'
const isOwn = (l) => auth.employee && l.employee === auth.employee

function pendingStatesForUser() {
  if (isAdmin) return ['Pending Manager Approval', 'Pending Finance Approval']
  if (isManager) return ['Pending Manager Approval']
  return []
}
const canAct = (l) => pendingStatesForUser().includes(l.workflow_state)
const approveAction = (l) => l.workflow_state === 'Pending Finance Approval' ? 'finance_approve' : 'manager_approve'
const rejectAction = (l) => l.workflow_state === 'Pending Finance Approval' ? 'finance_reject' : 'manager_reject'

async function load() {
  loading.value = true
  try {
    const states = tierFilter.value ? [tierFilter.value] : pendingStatesForUser()
    let all = [], t = 0
    for (const st of states) {
      const res = await call('sfa_core.api.leave.get_leave_applications', {
        start: 0, page_length: 200, status: st,
        from_date: dateFrom.value || undefined, to_date: dateTo.value || undefined,
      })
      all = all.concat(res.message.items || [])
      t += res.message.total || 0
    }
    items.value = all
    total.value = t
  } finally {
    loading.value = false
  }
}

function applyFilters() { page.value = 1; load() }
function clearFilters() { tierFilter.value = ''; dateFrom.value = ''; dateTo.value = ''; applyFilters() }
function onPage(p) { page.value = p; load() }

async function act(l, action) {
  await call('sfa_core.api.leave.action_leave', { name: l.name, action })
  load()
}

onMounted(load)
</script>
