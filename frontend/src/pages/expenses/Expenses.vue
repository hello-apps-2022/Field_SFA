<template>
  <div class="flex h-full flex-col overflow-hidden">

    <!-- Header -->
    <div class="flex h-[52px] shrink-0 items-center border-b border-gray-100 bg-white px-5 gap-3">
      <h1 class="text-sm font-semibold text-gray-900">Expense Claims</h1>
      <div class="flex-1" />
      <span class="text-xs text-gray-400">{{ total }} claims</span>
      <button @click="openDrawer('', 'edit')" class="inline-flex h-8 items-center gap-1.5 rounded-md bg-gray-900 px-3 text-xs font-medium text-white hover:bg-gray-700">
        <FeatherIcon name="plus" class="h-3.5 w-3.5" /> New Claim
      </button>
    </div>

    <!-- Filters -->
    <div class="flex shrink-0 flex-wrap items-center gap-2 border-b border-gray-100 bg-white px-4 py-2.5">
      <select v-model="statusFilter" @change="applyFilters" class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
        <option value="">All Statuses</option>
        <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
      </select>

      <DateRangeFilter v-model:from="dateFrom" v-model:to="dateTo" default-preset="this_year" @change="applyFilters" />

      <button @click="clearFilters" class="h-8 rounded-md border border-gray-200 bg-white px-3 text-xs text-gray-500 hover:bg-gray-50">
        Clear
      </button>
    </div>

    <!-- Summary strip -->
    <div v-if="total" class="flex shrink-0 items-center gap-6 border-b border-gray-100 bg-gray-50 px-5 py-2 text-sm">
      <span><strong class="text-gray-900">{{ total }}</strong> <span class="text-gray-400">claims</span></span>
      <span><strong class="text-gray-900">{{ fmt(totals.claimed) }}</strong> <span class="text-gray-400">claimed</span></span>
      <span><strong class="text-gray-900">{{ fmt(totals.sanctioned) }}</strong> <span class="text-gray-400">sanctioned</span></span>
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
            <th class="px-5 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Date</th>
            <th class="px-5 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Purpose</th>
            <th class="px-5 py-2.5 text-right text-[10px] font-semibold uppercase tracking-wide text-gray-400">Claimed</th>
            <th class="px-5 py-2.5 text-right text-[10px] font-semibold uppercase tracking-wide text-gray-400">Sanctioned</th>
            <th class="px-5 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Status</th>
            <th class="px-5 py-2.5 w-8"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr v-for="c in items" :key="c.name" @click="openDrawer(c.name, 'view')" class="hover:bg-gray-50 transition-colors cursor-pointer">
            <td class="px-5 py-3 font-medium text-gray-900">{{ c.employee_name || c.employee }}</td>
            <td class="px-5 py-3 text-gray-500">{{ formatDate(c.posting_date) }}</td>
            <td class="px-5 py-3">
              <div v-if="c.custom_activity_type || c.custom_purpose" class="flex flex-col gap-0.5">
                <span v-if="c.custom_activity_type" class="inline-flex w-fit items-center rounded-full bg-indigo-50 px-2 py-0.5 text-[10px] font-medium text-indigo-700">{{ c.custom_activity_type }}</span>
                <span v-if="c.custom_purpose" class="text-xs text-gray-500 line-clamp-2 max-w-xs">{{ c.custom_purpose }}</span>
              </div>
              <span v-else class="text-xs text-gray-300">—</span>
            </td>
            <td class="px-5 py-3 text-right font-medium text-gray-900">{{ fmt(c.total_claimed_amount) }}</td>
            <td class="px-5 py-3 text-right text-gray-500">{{ fmt(c.total_sanctioned_amount) }}</td>
            <td class="px-5 py-3">
              <StatusBadge :status="c.workflow_state" :color-map="statusColors" />
            </td>
            <td class="px-3 py-3 text-right text-gray-300">
              <FeatherIcon name="chevron-right" class="h-4 w-4" />
            </td>
          </tr>
        </tbody>
      </table>

      <div v-else class="flex flex-col items-center py-20 text-gray-400">
        <FeatherIcon name="receipt" class="h-10 w-10 mb-3" />
        <p class="text-sm font-medium text-gray-500">No expense claims found</p>
        <p class="text-xs mt-1">Try adjusting your filters, or create a new claim</p>
      </div>
    </div>

    <!-- Pagination footer -->
    <div v-if="total > pageSize" class="shrink-0 border-t border-gray-100 bg-white px-5 py-2">
      <Pagination :page="page" :page-size="pageSize" :total="total" :loading="loading" @update:page="onPage" />
    </div>

    <!-- Create modal -->
    <div v-if="showCreate" class="fixed inset-0 z-50 flex items-center justify-center bg-black/30 p-4" @click.self="showCreate=false">
      <div class="w-full max-w-2xl rounded-lg bg-white shadow-xl">
        <div class="flex h-[52px] items-center border-b border-gray-100 px-5">
          <h2 class="text-sm font-semibold text-gray-900">New Expense Claim</h2>
          <div class="flex-1" />
          <button @click="showCreate=false" class="text-gray-400 hover:text-gray-600"><FeatherIcon name="x" class="h-4 w-4" /></button>
        </div>

        <div class="max-h-[60vh] overflow-auto p-5 space-y-3">
          <!-- Activity grouping (header-level: applies to whole claim) -->
          <div class="flex gap-2">
            <div class="flex-1">
              <label class="mb-1 block text-xs font-medium text-gray-500">Activity Type</label>
              <select v-model="draft.activity_type" class="h-8 w-full rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
                <option value="">Select…</option>
                <option v-for="t in activityTypes" :key="t" :value="t">{{ t }}</option>
              </select>
            </div>
            <div class="flex-[2]">
              <label class="mb-1 block text-xs font-medium text-gray-500">Purpose</label>
              <input v-model="draft.purpose" placeholder="e.g. Cheetah Launch — Kayunga East door-to-door"
                class="h-8 w-full rounded-md border border-gray-200 px-2 text-sm focus:border-gray-400 focus:outline-none" />
            </div>
          </div>

          <div class="pt-2 border-t border-gray-100">
            <p class="mb-2 text-xs font-medium text-gray-500">Expense Lines</p>
          </div>

          <div v-for="(row, i) in draft.expenses" :key="i" class="flex items-center gap-2">
            <input type="date" v-model="row.expense_date" class="h-8 rounded-md border border-gray-200 px-2 text-sm focus:border-gray-400 focus:outline-none" />
            <select v-model="row.expense_type" class="h-8 flex-1 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
              <option value="" disabled>Type…</option>
              <option v-for="t in expenseTypes" :key="t" :value="t">{{ t }}</option>
            </select>
            <input type="number" v-model.number="row.amount" placeholder="Amount" class="h-8 w-32 rounded-md border border-gray-200 px-2 text-sm focus:border-gray-400 focus:outline-none" />
            <input v-model="row.description" placeholder="Description" class="h-8 flex-1 rounded-md border border-gray-200 px-2 text-sm focus:border-gray-400 focus:outline-none" />
            <button v-if="draft.expenses.length > 1" @click="draft.expenses.splice(i,1)" class="text-gray-300 hover:text-red-500"><FeatherIcon name="x" class="h-4 w-4" /></button>
          </div>
          <button @click="addLine" class="text-xs font-medium text-gray-600 hover:text-gray-900">+ Add line</button>

          <textarea v-model="draft.remark" placeholder="Remark (optional)" rows="2" class="mt-2 w-full rounded-md border border-gray-200 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none"></textarea>
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

    <!-- New unified drawer (view / edit / review + approve / reject) -->
    <ExpenseClaimDrawer
      v-model="drawerOpen"
      :claim-name="drawerClaim"
      :initial-mode="drawerMode"
      @changed="load"
    />

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { call } from '@/utils/frappe'
import { auth } from '@/utils/auth'
import { formatCurrency } from '@/utils/currency'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import DateRangeFilter from '@/components/ui/DateRangeFilter.vue'
import Pagination from '@/components/ui/Pagination.vue'
import ExpenseClaimDrawer from '@/components/ui/ExpenseClaimDrawer.vue'
import dayjs from 'dayjs'

const loading = ref(false)
const items = ref([])
const total = ref(0)
const totals = reactive({ claimed: 0, sanctioned: 0 })
const page = ref(1)
const pageSize = 50

const statusFilter = ref('')
const dateFrom = ref('')
const dateTo = ref('')

// Drawer state — opens on row click; null claimName means "new claim"
const drawerOpen = ref(false)
const drawerClaim = ref('')
const drawerMode = ref('view')

const statuses = ['Draft', 'Pending Approval', 'Approved', 'Rejected']
const statusColors = {
  'Draft': 'bg-gray-100 text-gray-600',
  'Pending Approval': 'bg-yellow-50 text-yellow-700',
  'Approved': 'bg-green-50 text-green-700',
  'Rejected': 'bg-red-50 text-red-600',
}

const expenseTypes = ref([])
const activityTypes = ref([])
const showCreate = ref(false)
const saving = ref(false)
const createError = ref('')
const draft = reactive({
  expenses: [{ expense_date: '', expense_type: '', amount: null, description: '' }],
  remark: '',
  activity_type: '',
  purpose: '',
})

const fmt = (v) => formatCurrency(v || 0)
const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'

async function load() {
  loading.value = true
  try {
    const res = await call('sfa_core.api.expenses.get_expense_claims', {
      start: (page.value - 1) * pageSize,
      page_length: pageSize,
      status: statusFilter.value || undefined,
      from_date: dateFrom.value || undefined,
      to_date: dateTo.value || undefined,
    })
    items.value = res.message.items || []
    total.value = res.message.total || 0
    Object.assign(totals, res.message.totals || { claimed: 0, sanctioned: 0 })
  } finally {
    loading.value = false
  }
}

async function loadMeta() {
  const res = await call('sfa_core.api.expenses.get_expense_claim_meta')
  expenseTypes.value = res.message.expense_types || []
  activityTypes.value = res.message.activity_types || []
}

function applyFilters() { page.value = 1; load() }
function clearFilters() { statusFilter.value = ''; dateFrom.value = ''; dateTo.value = ''; applyFilters() }
function onPage(p) { page.value = p; load() }

function openDrawer(name, mode = 'view') {
  drawerClaim.value = name || ''
  drawerMode.value = mode
  drawerOpen.value = true
}

function openCreate() {
  draft.expenses = [{ expense_date: dayjs().format('YYYY-MM-DD'), expense_type: '', amount: null, description: '' }]
  draft.remark = ''
  draft.activity_type = ''
  draft.purpose = ''
  createError.value = ''
  showCreate.value = true
}
function addLine() {
  draft.expenses.push({ expense_date: dayjs().format('YYYY-MM-DD'), expense_type: '', amount: null, description: '' })
}

async function saveDraft() {
  createError.value = ''
  const valid = draft.expenses.filter(e => e.expense_type && e.amount > 0)
  if (!valid.length) { createError.value = 'Add at least one line with a type and amount.'; return }
  saving.value = true
  try {
    await call('sfa_core.api.expenses.create_expense_claim', { payload: JSON.stringify({
      expenses: valid,
      remark: draft.remark,
      activity_type: draft.activity_type,
      purpose: draft.purpose,
    }) })
    showCreate.value = false
    load()
  } catch (e) {
    createError.value = e.message || 'Could not save claim.'
  } finally {
    saving.value = false
  }
}

onMounted(() => { loadMeta(); load() })
</script>
