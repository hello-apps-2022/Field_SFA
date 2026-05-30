<template>
  <div class="flex h-full flex-col overflow-hidden">
    <!-- Top bar -->
    <div class="flex h-[52px] shrink-0 items-center border-b border-gray-100 bg-white px-5 gap-3">
      <button class="text-sm text-gray-400 hover:text-gray-700" @click="goBack">Team</button>
      <FeatherIcon name="chevron-right" class="h-3.5 w-3.5 text-gray-300" />
      <span class="text-sm font-semibold text-gray-900 truncate">{{ p.full_name || sp }}</span>
      <div class="flex-1" />
      <span v-if="data" class="inline-flex items-center gap-1 text-xs" :class="p.sfa_active ? 'text-green-600' : 'text-gray-400'">
        <span class="h-1.5 w-1.5 rounded-full" :class="p.sfa_active ? 'bg-green-500' : 'bg-gray-300'" />
        {{ p.sfa_active ? 'Active' : 'Inactive' }}
      </span>
      <Btn v-if="data && auth.isAdmin" variant="default" icon="edit-2" size="sm" @click="editPanel = true">Edit</Btn>
    </div>

    <div v-if="loading" class="flex flex-1 items-center justify-center text-gray-400">
      <FeatherIcon name="loader" class="h-5 w-5 animate-spin mr-2" /> Loading profile…
    </div>
    <div v-else-if="error" class="m-5 rounded-xl border border-red-200 bg-red-50 p-6 text-sm text-red-700">{{ error }}</div>

    <template v-else-if="data">
      <!-- Header -->
      <div class="shrink-0 border-b border-gray-100 bg-white px-5 py-4">
        <div class="flex items-center gap-4">
          <div class="flex h-12 w-12 shrink-0 items-center justify-center overflow-hidden rounded-full bg-indigo-100 text-lg font-semibold text-indigo-700">
            <img v-if="p.user_image" :src="p.user_image" class="h-full w-full object-cover" />
            <span v-else>{{ initials(p.full_name) }}</span>
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex flex-wrap items-center gap-2">
              <h2 class="truncate text-base font-semibold text-gray-900">{{ p.full_name }}</h2>
              <span class="rounded-full px-2 py-0.5 text-xs font-medium" :class="roleBadge(p.role)">{{ p.role || 'No role' }}</span>
            </div>
            <div class="mt-1.5 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-gray-500">
              <span class="inline-flex items-center gap-1"><FeatherIcon name="mail" class="h-3 w-3 text-gray-400" />{{ p.email || '—' }}</span>
              <span class="text-gray-200">|</span>
              <span class="inline-flex items-center gap-1"><FeatherIcon name="globe" class="h-3 w-3 text-gray-400" />{{ p.territory || 'No territory' }}</span>
              <span v-if="p.manager_name" class="inline-flex items-center gap-1"><FeatherIcon name="user" class="h-3 w-3 text-gray-400" />Reports to {{ p.manager_name }}</span>
              <span class="inline-flex items-center gap-1"><FeatherIcon name="award" class="h-3 w-3 text-gray-400" />{{ p.points }} pts</span>
              <span v-if="p.last_seen" class="inline-flex items-center gap-1"><FeatherIcon name="clock" class="h-3 w-3 text-gray-400" />Seen {{ fmtDateTime(p.last_seen) }}</span>
            </div>
          </div>
          <!-- Quick stats (selected range) -->
          <div class="hidden shrink-0 gap-5 border-l border-gray-100 pl-5 text-center sm:flex">
            <div><p class="text-xl font-semibold text-gray-900">{{ k.visits || 0 }}</p><p class="text-[10px] uppercase tracking-wide text-gray-400">Visits</p></div>
            <div><p class="text-xl font-semibold text-gray-900">{{ k.orders || 0 }}</p><p class="text-[10px] uppercase tracking-wide text-gray-400">Orders</p></div>
            <div><p class="text-xl font-semibold text-gray-900">{{ fmtShort(k.revenue) }}</p><p class="text-[10px] uppercase tracking-wide text-gray-400">Revenue</p></div>
            <div><p class="text-xl font-semibold text-gray-900">{{ fmtShort(k.payments) }}</p><p class="text-[10px] uppercase tracking-wide text-gray-400">Payments</p></div>
          </div>
        </div>
      </div>

      <!-- Tabs + date filter -->
      <div class="flex shrink-0 items-center border-b border-gray-100 bg-white px-5">
        <button v-for="t in tabs" :key="t" @click="tab = t"
          class="mr-1 whitespace-nowrap border-b-2 px-3 py-2.5 text-sm font-medium transition-colors"
          :class="tab === t ? 'border-gray-900 text-gray-900' : 'border-transparent text-gray-500 hover:text-gray-700'">
          {{ t }}
        </button>
        <div class="flex-1" />
        <div v-if="showFilter" class="flex items-center gap-2">
          <FeatherIcon v-if="refreshing" name="loader" class="h-3.5 w-3.5 animate-spin text-gray-400" />
          <DateRangeFilter v-model:from="dateFrom" v-model:to="dateTo" default-preset="this_month" @change="onRange" />
        </div>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto bg-gray-50 p-5">

        <!-- OVERVIEW -->
        <div v-if="tab === 'Overview'" class="space-y-5">
          <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <div v-for="kk in kpiTiles" :key="kk.label" class="rounded-xl border border-gray-200 bg-white p-4">
              <p class="text-xs text-gray-400">{{ kk.label }}</p>
              <p class="mt-1 text-lg font-semibold text-gray-900">{{ kk.value }}</p>
              <p v-if="kk.sub" class="text-xs text-gray-400">{{ kk.sub }}</p>
            </div>
          </div>
          <div class="overflow-hidden rounded-xl border border-gray-200 bg-white">
            <div class="border-b border-gray-100 bg-gray-50 px-4 py-2">
              <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Details</p>
            </div>
            <dl class="grid grid-cols-1 gap-y-3 p-4 text-sm sm:grid-cols-2">
              <div><dt class="text-xs text-gray-400">Role</dt><dd class="text-gray-800">{{ p.role || '—' }}</dd></div>
              <div><dt class="text-xs text-gray-400">Territory</dt><dd class="text-gray-800">{{ p.territory || '—' }}</dd></div>
              <div><dt class="text-xs text-gray-400">Manager</dt><dd class="text-gray-800">{{ p.manager_name || '—' }}</dd></div>
              <div><dt class="text-xs text-gray-400">Mobile</dt><dd class="text-gray-800">{{ p.mobile_no || '—' }}</dd></div>
              <div><dt class="text-xs text-gray-400">HR Employee</dt><dd class="text-gray-800">{{ p.employee_name || p.employee || '—' }}</dd></div>
              <div><dt class="text-xs text-gray-400">Companies</dt>
                <dd class="text-gray-800">
                  <span v-if="!p.companies.length" class="text-gray-400">All products</span>
                  <span v-for="c in p.companies" :key="c" class="mr-1 inline-block rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">{{ c }}</span>
                </dd>
              </div>
            </dl>
          </div>
          <div v-if="p.badges.length" class="overflow-hidden rounded-xl border border-gray-200 bg-white">
            <div class="border-b border-gray-100 bg-gray-50 px-4 py-2">
              <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Badges</p>
            </div>
            <div class="flex flex-wrap gap-2 p-4">
              <span v-for="b in p.badges" :key="b.badge" class="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2.5 py-1 text-xs text-amber-700">
                <FeatherIcon name="award" class="h-3.5 w-3.5" />{{ b.badge }}
              </span>
            </div>
          </div>
        </div>

        <!-- ACTIVITY -->
        <div v-else-if="tab === 'Activity'" class="space-y-2">
          <div v-if="!data.visits.length" class="rounded-xl border border-dashed border-gray-200 bg-white py-10 text-center text-sm text-gray-400">No visits in this period.</div>
          <div v-for="v in data.visits" :key="v.name" class="rounded-xl border border-gray-200 bg-white px-4 py-3">
            <div class="flex items-center justify-between">
              <div class="min-w-0">
                <p class="truncate text-sm font-medium text-gray-900">{{ v.customer }}</p>
                <p class="text-xs text-gray-400">{{ fmtDate(v.visit_date) }}<span v-if="v.visit_purpose"> · {{ v.visit_purpose }}</span><span v-if="v.duration_minutes"> · {{ v.duration_minutes }} min</span></p>
              </div>
              <span class="rounded-full px-2 py-0.5 text-xs" :class="visitBadge(v.status)">{{ v.status }}</span>
            </div>
          </div>
        </div>

        <!-- ORDERS -->
        <div v-else-if="tab === 'Orders'" class="space-y-2">
          <div v-if="!data.orders.length" class="rounded-xl border border-dashed border-gray-200 bg-white py-10 text-center text-sm text-gray-400">No orders in this period.</div>
          <div v-for="o in data.orders" :key="o.name" class="rounded-xl border border-gray-200 bg-white px-4 py-3">
            <div class="flex items-center justify-between gap-3">
              <div class="min-w-0">
                <p class="truncate text-sm font-medium text-gray-900">{{ o.customer }}</p>
                <p class="text-xs text-gray-400">{{ fmtDate(o.transaction_date) }} · {{ o.name }}</p>
              </div>
              <div class="shrink-0 text-right">
                <p class="text-sm font-semibold text-gray-900">{{ money(o.paid_total) }}</p>
                <div class="flex items-center justify-end gap-1.5">
                  <span v-if="o.free_qty" class="rounded-full bg-green-50 px-2 py-0.5 text-xs text-green-700">+{{ o.free_qty }} free</span>
                  <span class="rounded-full px-2 py-0.5 text-xs" :class="orderBadge(o.doc_status)">{{ o.doc_status }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- PERFORMANCE -->
        <div v-else-if="tab === 'Performance'">
          <div v-if="!perf.has_targets" class="rounded-xl border border-dashed border-gray-200 bg-white py-10 text-center text-sm text-gray-400">No targets assigned to this rep yet.</div>
          <div v-else class="space-y-4">
            <p class="text-sm text-gray-500">{{ perf.period_name }} · {{ fmtDate(perf.date_from) }} – {{ fmtDate(perf.date_to) }}
              <span class="ml-1 rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">{{ perf.status }}</span></p>
            <div v-for="m in perfMetrics" :key="m.label" class="rounded-xl border border-gray-200 bg-white p-4">
              <div class="mb-2 flex items-center justify-between text-sm">
                <span class="font-medium text-gray-700">{{ m.label }}</span>
                <span class="text-gray-500">{{ m.actualText }} <span class="text-gray-300">/</span> {{ m.targetText }}</span>
              </div>
              <div class="h-2 w-full overflow-hidden rounded-full bg-gray-100">
                <div class="h-full rounded-full" :class="m.pct >= 100 ? 'bg-green-500' : m.pct >= 60 ? 'bg-amber-400' : 'bg-red-400'" :style="{ width: Math.min(m.pct, 100) + '%' }" />
              </div>
              <p class="mt-1 text-right text-xs text-gray-400">{{ m.pct }}%</p>
            </div>
            <div class="rounded-xl border border-gray-200 bg-white p-4 text-sm">
              <div class="flex items-center justify-between">
                <span class="font-medium text-gray-700">Visit compliance</span>
                <span class="text-gray-600">{{ perf.actual_compliance_pct }}% <span class="text-gray-300">/</span> target {{ perf.target_compliance_pct }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- LEAVE & EXPENSES -->
        <div v-else-if="tab === 'Leave & Expenses'" class="space-y-6">
          <div v-if="!p.employee" class="rounded-xl border border-dashed border-gray-200 bg-white py-10 text-center text-sm text-gray-400">No HR employee is linked to this rep, so leave and expenses aren't available.</div>
          <template v-else>
            <div>
              <div class="mb-2 flex items-center justify-between">
                <h3 class="text-sm font-semibold text-gray-700">Leave</h3>
                <span class="text-xs text-gray-400">{{ data.leave.pending }} pending · {{ data.leave.approved }} approved</span>
              </div>
              <div v-if="!data.leave.items.length" class="rounded-xl border border-dashed border-gray-200 bg-white py-10 text-center text-sm text-gray-400">No leave in this period.</div>
              <div v-for="l in data.leave.items" :key="l.name" class="mb-2 rounded-xl border border-gray-200 bg-white px-4 py-3">
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ l.leave_type }}</p>
                    <p class="text-xs text-gray-400">{{ fmtDate(l.from_date) }} – {{ fmtDate(l.to_date) }} · {{ l.total_leave_days }} day(s)</p>
                  </div>
                  <span class="rounded-full px-2 py-0.5 text-xs" :class="hrBadge(l.workflow_state || l.status)">{{ l.workflow_state || l.status }}</span>
                </div>
              </div>
            </div>
            <div>
              <div class="mb-2 flex items-center justify-between">
                <h3 class="text-sm font-semibold text-gray-700">Expenses</h3>
                <span class="text-xs text-gray-400">{{ money(data.expenses.claimed) }} claimed · {{ money(data.expenses.sanctioned) }} sanctioned</span>
              </div>
              <div v-if="!data.expenses.items.length" class="rounded-xl border border-dashed border-gray-200 bg-white py-10 text-center text-sm text-gray-400">No expense claims in this period.</div>
              <div v-for="e in data.expenses.items" :key="e.name" class="mb-2 rounded-xl border border-gray-200 bg-white px-4 py-3">
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ e.name }}</p>
                    <p class="text-xs text-gray-400">{{ fmtDate(e.posting_date) }}</p>
                  </div>
                  <div class="text-right">
                    <p class="text-sm font-semibold text-gray-900">{{ money(e.total_claimed_amount) }}</p>
                    <span class="rounded-full px-2 py-0.5 text-xs" :class="hrBadge(e.approval_status)">{{ e.approval_status }}</span>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>

      </div>
    </template>

    <SlidePanel v-model="editPanel" title="Edit Profile" :saving="saving" save-label="Save changes" @save="saveEdit" width="520px">
      <div class="space-y-4">
        <div class="grid grid-cols-2 gap-3">
          <FormField v-model="ed.first_name" label="First Name" />
          <FormField v-model="ed.last_name" label="Last Name" />
        </div>
        <FormField v-model="ed.mobile_no" label="Mobile" />
        <FormField v-model="ed.territory" label="Territory" type="select" :options="territoryOpts" placeholder="—" />
        <FormField v-model="ed.role" label="Role" type="select" :options="roleOpts" />
        <FormField v-model="ed.reports_to" label="Reports To" type="select" :options="managerOpts" placeholder="—" />
        <div>
          <label class="mb-1.5 block text-sm font-medium text-gray-700">Companies</label>
          <p class="mb-2 text-xs text-gray-400">No selection = sees all products.</p>
          <div class="space-y-1.5">
            <label v-for="c in companyOpts" :key="c.value" class="flex items-center gap-2 text-sm text-gray-700">
              <input type="checkbox" :value="c.value" v-model="ed.companies" class="rounded border-gray-300" />
              {{ c.label }}
            </label>
            <p v-if="!companyOpts.length" class="text-xs text-gray-400">No companies defined.</p>
          </div>
        </div>
        <label class="flex items-center gap-2 text-sm text-gray-700">
          <input type="checkbox" v-model="ed.sfa_active" class="rounded border-gray-300" /> Active
        </label>
        <label class="flex items-center gap-2 text-sm text-gray-700">
          <input type="checkbox" v-model="ed.can_export_reports" class="rounded border-gray-300" /> Can export reports
        </label>
      </div>
    </SlidePanel>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { call, getList } from '@/utils/frappe'
import { auth } from '@/utils/auth'
import FeatherIcon from '@/components/ui/FeatherIcon.vue'
import FormField from '@/components/ui/FormField.vue'
import Btn from '@/components/ui/Btn.vue'
import SlidePanel from '@/components/ui/SlidePanel.vue'
import DateRangeFilter from '@/components/ui/DateRangeFilter.vue'
import { successToast, errorToast } from '@/utils/toast'
import dayjs from 'dayjs'

const props = defineProps({ sp: { type: String, required: true } })
const router = useRouter()

const data = ref(null)
const loading = ref(true)
const refreshing = ref(false)
const error = ref('')
const tab = ref('Overview')
const saving = ref(false)
const editPanel = ref(false)

const dateFrom = ref(dayjs().startOf('month').format('YYYY-MM-DD'))
const dateTo = ref(dayjs().format('YYYY-MM-DD'))

const territoryOpts = ref([])
const managerOpts = ref([])
const companyOpts = ref([])
const roleOpts = ['SFA Rep', 'SFA Manager', 'SFA Admin']

const ed = reactive({
  first_name: '', last_name: '', mobile_no: '', territory: '', role: '',
  reports_to: '', companies: [], sfa_active: true, can_export_reports: false,
})

const p = computed(() => data.value?.profile || { companies: [], badges: [] })
const k = computed(() => data.value?.kpis || {})
const perf = computed(() => data.value?.performance || { has_targets: false })

const tabs = computed(() => ['Overview', 'Activity', 'Orders', 'Performance', 'Leave & Expenses'])
const showFilter = computed(() => tab.value !== 'Performance' && tab.value !== 'Edit')

function initials(n) { return (n || '?').split(' ').map(s => s[0]).slice(0, 2).join('').toUpperCase() }
function fmtDate(d) { return d ? dayjs(d).format('D MMM YYYY') : '—' }
function fmtDateTime(d) { return d ? dayjs(d).format('D MMM, h:mm A') : '—' }
const ugx = new Intl.NumberFormat('en-UG', { style: 'currency', currency: 'UGX', maximumFractionDigits: 0 })
function money(v) { try { return ugx.format(Number(v) || 0) } catch (e) { return 'UGX ' + (Number(v) || 0).toLocaleString() } }
function fmtShort(v) {
  const n = Number(v) || 0
  if (n >= 1e9) return (n / 1e9).toFixed(1).replace(/\.0$/, '') + 'B'
  if (n >= 1e6) return (n / 1e6).toFixed(1).replace(/\.0$/, '') + 'M'
  if (n >= 1e3) return (n / 1e3).toFixed(1).replace(/\.0$/, '') + 'K'
  return String(n)
}

function roleBadge(r) { return r === 'SFA Admin' ? 'bg-purple-100 text-purple-700' : r === 'SFA Manager' ? 'bg-blue-100 text-blue-700' : r === 'SFA Rep' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500' }
function visitBadge(s) { return s === 'Completed' ? 'bg-green-100 text-green-700' : s === 'Cancelled' ? 'bg-red-100 text-red-600' : s === 'In Progress' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600' }
function orderBadge(s) { return s === 'Submitted' ? 'bg-green-100 text-green-700' : s === 'Cancelled' ? 'bg-red-100 text-red-600' : 'bg-amber-100 text-amber-700' }
function hrBadge(s) { const x = (s || '').toLowerCase(); return x === 'approved' ? 'bg-green-100 text-green-700' : (x.includes('reject') || x === 'cancelled') ? 'bg-red-100 text-red-600' : 'bg-amber-100 text-amber-700' }

const kpiTiles = computed(() => {
  const kk = k.value
  return [
    { label: 'Visits', value: kk.visits || 0, sub: (kk.visits_completed || 0) + ' completed' },
    { label: 'Orders', value: kk.orders || 0 },
    { label: 'Revenue', value: money(kk.revenue) },
    { label: 'Payments', value: money(kk.payments) },
    { label: 'New Customers', value: kk.new_customers || 0 },
    { label: 'Free Cartons', value: kk.free_qty || 0 },
    { label: 'Points', value: p.value.points || 0 },
  ]
})

const perfMetrics = computed(() => {
  const pf = perf.value
  if (!pf.has_targets) return []
  const pct = (a, t) => t > 0 ? Math.round(a / t * 100) : 0
  return [
    { label: 'Visits', actualText: pf.actual_visits, targetText: pf.target_visits, pct: pct(pf.actual_visits, pf.target_visits) },
    { label: 'Revenue', actualText: money(pf.actual_revenue), targetText: money(pf.target_revenue), pct: pct(pf.actual_revenue, pf.target_revenue) },
    { label: 'New Customers', actualText: pf.actual_new_customers, targetText: pf.target_new_customers, pct: pct(pf.actual_new_customers, pf.target_new_customers) },
  ]
})

function goBack() { if (window.history.length > 1) router.back(); else router.push('/settings') }

async function fetchData(initial) {
  if (initial) loading.value = true; else refreshing.value = true
  error.value = ''
  try {
    const res = await call('sfa_core.api.rep_profile.get_rep_profile', { sales_person: props.sp, date_from: dateFrom.value, date_to: dateTo.value })
    data.value = res.message || res
    if (initial) seedEditForm()
  } catch (e) {
    if (initial) error.value = e?.message || 'Could not load this profile.'
    else errorToast(e?.message || 'Could not refresh.')
  } finally {
    loading.value = false; refreshing.value = false
  }
}

function seedEditForm() {
  const pr = data.value.profile
  const parts = (pr.full_name || '').trim().split(' ')
  ed.first_name = parts.shift() || ''
  ed.last_name = parts.join(' ')
  ed.mobile_no = pr.mobile_no || ''
  ed.territory = pr.territory || ''
  ed.role = pr.role || ''
  ed.reports_to = pr.reports_to || ''
  ed.companies = [...(pr.companies || [])]
  ed.sfa_active = !!pr.sfa_active
  ed.can_export_reports = !!pr.can_export_reports
}

function onRange(r) {
  const nf = r.from || '', nt = r.to || ''
  if (nf === dateFrom.value && nt === dateTo.value) return
  dateFrom.value = nf; dateTo.value = nt
  fetchData(false)
}

async function loadEditOptions() {
  if (!auth.isAdmin) return
  try {
    const [terr, reps, comps] = await Promise.all([
      getList('Territory', { fields: ['name'], filters: { is_group: 0 }, limit: 200 }),
      getList('Sales Person', { fields: ['name', 'sales_person_name'], filters: { is_group: 0 }, limit: 500 }),
      call('sfa_core.field_sfa.api.catalog.get_companies'),
    ])
    territoryOpts.value = (terr || []).map(t => t.name)
    managerOpts.value = (reps || []).filter(r => r.name !== props.sp).map(r => ({ value: r.name, label: r.sales_person_name || r.name }))
    const cl = comps?.message || comps || []
    companyOpts.value = cl.map(c => ({ value: c.name, label: c.company_name || c.name }))
  } catch (e) { /* options best-effort */ }
}

async function saveEdit() {
  saving.value = true
  try {
    await call('sfa_core.api.settings.update_user', {
      sales_person: props.sp,
      first_name: ed.first_name,
      last_name: ed.last_name,
      mobile_no: ed.mobile_no,
      territory: ed.territory || null,
      role: ed.role || null,
      reports_to: ed.reports_to || '',
      sfa_active: ed.sfa_active ? 1 : 0,
      can_export_reports: ed.can_export_reports ? 1 : 0,
      companies: JSON.stringify(ed.companies),
    })
    successToast('Profile updated')
    await fetchData(true)
    editPanel.value = false
  } catch (e) {
    errorToast(e?.message || 'Update failed')
  } finally {
    saving.value = false
  }
}

onMounted(async () => { await fetchData(true); loadEditOptions() })
</script>
