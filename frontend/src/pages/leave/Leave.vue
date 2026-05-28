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

      <DateRangeFilter v-model:from="dateFrom" v-model:to="dateTo" default-preset="this_month" @change="applyFilters" />

      <button @click="clearFilters" class="h-8 rounded-md border border-gray-200 bg-white px-3 text-xs text-gray-500 hover:bg-gray-50">
        Clear
      </button>
    </div>

    <!-- Balance strip -->
    <div v-if="balances.length" class="flex shrink-0 items-center gap-6 border-b border-gray-100 bg-gray-50 px-5 py-2 text-sm">
      <span class="text-gray-400 text-xs uppercase tracking-wide">Balance</span>
      <span v-for="b in balances" :key="b.leave_type">
        <strong class="text-gray-900">{{ b.balance ?? '—' }}</strong>
        <span class="text-gray-400">{{ b.leave_type }}</span>
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
            <th class="px-5 py-2.5 text-right text-[10px] font-semibold uppercase tracking-wide text-gray-400">Actions</th>
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
              <template v-if="canManagerAct(l)">
                <button @click="act(l, 'manager_approve')" class="text-xs font-medium text-green-700 hover:underline">Approve</button>
                <button @click="act(l, 'manager_reject')" class="ml-3 text-xs font-medium text-red-600 hover:underline">Reject</button>
              </template>
              <template v-else-if="canFinanceAct(l)">
                <button @click="act(l, 'finance_approve')" class="text-xs font-medium text-green-700 hover:underline">Approve</button>
                <button @click="act(l, 'finance_reject')" class="ml-3 text-xs font-medium text-red-600 hover:underline">Reject</button>
              </template>
              <button v-else-if="l.workflow_state === 'Draft' && isOwn(l)" @click="submitLeave(l)" class="text-xs font-medium text-gray-700 hover:underline">Submit</button>
              <span v-else class="text-xs text-gray-300">—</span>
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

    <!-- Create modal -->
    <div v-if="showCreate" class="fixed inset-0 z-50 flex items-center justify-center bg-black/30 p-4" @click.self="showCreate=false">
      <div class="w-full max-w-md rounded-lg bg-white shadow-xl">
        <div class="flex h-[52px] items-center border-b border-gray-100 px-5">
          <h2 class="text-sm font-semibold text-gray-900">Apply for Leave</h2>
          <div class="flex-1" />
          <button @click="showCreate=false" class="text-gray-400 hover:text-gray-600"><FeatherIcon name="x" class="h-4 w-4" /></button>
        </div>

        <div class="p-5 space-y-3">
          <div>
            <label class="mb-1 block text-xs font-medium text-gray-500">Leave Type</label>
            <select v-model="draft.leave_type" class="h-8 w-full rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
              <option value="" disabled>Select…</option>
              <option v-for="t in leaveTypes" :key="t" :value="t">{{ t }}</option>
            </select>
          </div>
          <div class="flex gap-3">
            <div class="flex-1">
              <label class="mb-1 block text-xs font-medium text-gray-500">From</label>
              <input type="date" v-model="draft.from_date" class="h-8 w-full rounded-md border border-gray-200 px-2 text-sm focus:border-gray-400 focus:outline-none" />
            </div>
            <div class="flex-1">
              <label class="mb-1 block text-xs font-medium text-gray-500">To</label>
              <input type="date" v-model="draft.to_date" class="h-8 w-full rounded-md border border-gray-200 px-2 text-sm focus:border-gray-400 focus:outline-none" />
            </div>
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-gray-500">Reason</label>
            <textarea v-model="draft.reason" rows="2" class="w-full rounded-md border border-gray-200 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none"></textarea>
          </div>
        </div>

        <div class="flex items-center justify-end gap-3 border-t border-gray-100 px-5 py-3">
          <span v-if="createError" class="mr-auto text-xs text-red-600">{{ createError }}</span>
          <button @click="showCreate=false" class="h-8 rounded-md px-3 text-xs text-gray-500 hover:bg-gray-50">Cancel</button>
          <button @click="saveDraft" :disabled="saving" class="h-8 rounded-md bg-gray-900 px-4 text-xs font-medium text-white hover:bg-gray-700 disabled:opacity-50">
            {{ saving ? 'Saving…' : 'Save Draft' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { call } from '@/utils/frappe'
import { auth } from '@/utils/auth'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import DateRangeFilter from '@/components/ui/DateRangeFilter.vue'
import Pagination from '@/components/ui/Pagination.vue'
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

const statuses = ['Draft', 'Pending Manager Approval', 'Pending Finance Approval', 'Approved', 'Rejected']
const statusColors = {
  'Draft': 'bg-gray-100 text-gray-600',
  'Pending Manager Approval': 'bg-yellow-50 text-yellow-700',
  'Pending Finance Approval': 'bg-blue-50 text-blue-700',
  'Approved': 'bg-green-50 text-green-700',
  'Rejected': 'bg-red-50 text-red-600',
}

const leaveTypes = ref([])
const showCreate = ref(false)
const saving = ref(false)
const createError = ref('')
const draft = reactive({ leave_type: '', from_date: '', to_date: '', reason: '' })

const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'

const isOwn = (l) => auth.employee && l.employee === auth.employee
const canManagerAct = (l) => l.workflow_state === 'Pending Manager Approval' && (auth.isManager || auth.isAdmin) && !isOwn(l)
const canFinanceAct = (l) => l.workflow_state === 'Pending Finance Approval' && auth.isAdmin && !isOwn(l)

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

async function loadMeta() {
  const res = await call('sfa_core.api.leave.get_leave_meta')
  leaveTypes.value = res.message.leave_types || []
  try {
    const bal = await call('sfa_core.api.leave.get_leave_balance')
    balances.value = bal.message.balances || []
  } catch (e) { /* balance is best-effort */ }
}

function applyFilters() { page.value = 1; load() }
function clearFilters() { statusFilter.value = ''; dateFrom.value = ''; dateTo.value = ''; applyFilters() }
function onPage(p) { page.value = p; load() }

function openCreate() {
  draft.leave_type = ''
  draft.from_date = dayjs().format('YYYY-MM-DD')
  draft.to_date = dayjs().format('YYYY-MM-DD')
  draft.reason = ''
  createError.value = ''
  showCreate.value = true
}

async function saveDraft() {
  createError.value = ''
  if (!draft.leave_type) { createError.value = 'Select a leave type.'; return }
  if (!draft.from_date || !draft.to_date) { createError.value = 'Select both dates.'; return }
  if (draft.to_date < draft.from_date) { createError.value = 'To date is before From date.'; return }
  saving.value = true
  try {
    await call('sfa_core.api.leave.apply_leave', { payload: JSON.stringify({
      leave_type: draft.leave_type, from_date: draft.from_date, to_date: draft.to_date, reason: draft.reason,
    }) })
    showCreate.value = false
    load()
  } catch (e) {
    createError.value = e.message || 'Could not save leave request.'
  } finally {
    saving.value = false
  }
}

async function submitLeave(l) {
  await call('sfa_core.api.leave.submit_leave', { name: l.name })
  load()
}
async function act(l, action) {
  await call('sfa_core.api.leave.action_leave', { name: l.name, action })
  load()
}

onMounted(() => { loadMeta(); load() })
</script>
