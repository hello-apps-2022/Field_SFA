<template>
  <div class="flex h-full flex-col overflow-hidden">

    <!-- Header -->
    <div class="flex h-[52px] shrink-0 items-center border-b border-gray-100 bg-white px-5 gap-3">
      <h1 class="text-sm font-semibold text-gray-900">Targets</h1>
      <div class="flex-1" />
      <span class="text-xs text-gray-400">{{ filtered.length }} target sets</span>
      <Btn icon="plus" variant="solid" size="sm" @click="openCreate">New Target Set</Btn>
    </div>

    <!-- Filters -->
    <div class="flex shrink-0 flex-wrap items-center gap-2 border-b border-gray-100 bg-white px-4 py-2.5">
      <!-- Status -->
      <select v-model="statusFilter"
        class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
        <option value="">All Statuses</option>
        <option>Draft</option>
        <option>Active</option>
        <option>Closed</option>
      </select>

      <!-- Territory (admin only) -->
      <select v-if="isAdmin" v-model="territoryFilter"
        class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
        <option value="">All Territories</option>
        <option v-for="t in territories" :key="t.name" :value="t.name">{{ t.name }}</option>
      </select>

      <!-- Date quick select -->
      <select v-model="datePreset" @change="applyDatePreset"
        class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
        <option value="">Any period</option>
        <option value="this_month">This Month</option>
        <option value="last_month">Last Month</option>
        <option value="this_quarter">This Quarter</option>
        <option value="last_quarter">Last Quarter</option>
        <option value="this_year">This Year (FY)</option>
        <option value="next_month">Next Month</option>
        <option value="next_quarter">Next Quarter</option>
        <option value="custom">Custom Range…</option>
      </select>

      <!-- Custom date inputs — shown when custom is selected or preset applied -->
      <template v-if="datePreset === 'custom' || dateFrom || dateTo">
        <div class="flex items-center gap-1.5">
          <input :value="dateFrom" type="date" @change="setDateFrom($event.target.value)"
            class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:border-gray-400 focus:outline-none" />
          <span class="text-xs text-gray-400">→</span>
          <input :value="dateTo" type="date" :min="dateFrom" @change="setDateTo($event.target.value)"
            class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:border-gray-400 focus:outline-none" />
        </div>
        <span v-if="dateError" class="text-xs text-red-500">{{ dateError }}</span>
        <button v-if="dateFrom || dateTo"
          class="h-8 rounded-md border border-gray-200 px-2 text-xs text-gray-500 hover:bg-gray-50"
          @click="clearDates">
          Clear
        </button>
      </template>

      <!-- Active filter chips -->
      <div v-if="dateFrom && dateTo && datePreset !== 'custom'" class="flex items-center gap-1.5 rounded-full bg-indigo-50 border border-indigo-100 px-2.5 py-1 text-xs font-medium text-indigo-700">
        <FeatherIcon name="calendar" class="h-3 w-3" />
        {{ presetLabel }}
        <button @click="clearDates" class="ml-0.5 hover:text-indigo-900">
          <FeatherIcon name="x" class="h-3 w-3" />
        </button>
      </div>
    </div>

    <!-- Cards grid -->
    <div class="flex-1 overflow-y-auto bg-gray-50 p-5">
      <div v-if="loading" class="flex h-40 items-center justify-center">
        <FeatherIcon name="loader" class="h-6 w-6 animate-spin text-gray-400" />
      </div>

      <div v-else-if="filtered.length" class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <div v-for="ts in filtered" :key="ts.name"
          class="rounded-xl border border-gray-200 bg-white overflow-hidden cursor-pointer hover:shadow-md transition-shadow"
          @click="openDetail(ts.name)"
        >
          <!-- Card header -->
          <div class="flex items-start justify-between px-4 pt-4 pb-3">
            <div class="min-w-0 flex-1">
              <p class="text-sm font-semibold text-gray-900 truncate">{{ ts.target_set_name }}</p>
              <p class="text-xs text-gray-400 mt-0.5">{{ ts.territory }}</p>
            </div>
            <span class="ml-2 shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium"
              :class="statusColor(ts.status)">
              {{ ts.status }}
            </span>
          </div>

          <!-- Date range -->
          <div class="flex items-center gap-1.5 px-4 pb-3 text-xs text-gray-500">
            <FeatherIcon name="calendar" class="h-3.5 w-3.5 text-gray-400" />
            {{ fmtDate(ts.date_from) }} → {{ fmtDate(ts.date_to) }}
          </div>

          <!-- Footer -->
          <div class="flex items-center gap-3 border-t border-gray-50 px-4 py-2.5 text-xs text-gray-500">
            <span class="flex items-center gap-1">
              <FeatherIcon name="users" class="h-3 w-3 text-gray-400" />
              {{ ts.rep_count }} rep{{ ts.rep_count !== 1 ? 's' : '' }}
            </span>
            <span v-if="ts.notes" class="truncate text-gray-400">{{ ts.notes }}</span>
          </div>
        </div>
      </div>

      <div v-else class="flex flex-col items-center py-20 text-gray-400">
        <FeatherIcon name="target" class="h-10 w-10 mb-3" />
        <p class="text-sm font-medium text-gray-600">No target sets yet</p>
        <p class="text-xs mt-1 mb-4">Create a target set for a territory and period</p>
        <Btn icon="plus" variant="solid" size="sm" @click="openCreate">New Target Set</Btn>
      </div>
    </div>
  </div>

  <!-- Create panel -->
  <SlidePanel v-model="createPanel" title="New Target Set" width="640px"
    :saving="saving" save-label="Create" @save="createTargetSet">
    <div class="space-y-4">
      <FormField v-model="form.target_set_name" label="Name" required :error="errors.name"
        placeholder="e.g. Kampala — June 2026" />

      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="mb-1.5 block text-xs font-medium text-gray-600">Territory <span class="text-red-500">*</span></label>
          <select v-model="form.territory" @change="loadRepsForTerritory"
            class="w-full h-9 rounded-lg border border-gray-200 bg-white px-3 text-sm focus:border-gray-400 focus:outline-none">
            <option value="">Select territory…</option>
            <option v-for="t in territories" :key="t.name" :value="t.name">{{ t.name }}</option>
          </select>
        </div>
        <FormField v-model="form.status" label="Status" type="select"
          :options="['Draft','Active','Closed']" />
      </div>

      <div class="grid grid-cols-2 gap-3">
        <FormField v-model="form.date_from" label="From Date" type="date" required :error="errors.date_from" />
        <FormField v-model="form.date_to" label="To Date" type="date" required :error="errors.date_to" />
      </div>

      <FormField v-model="form.notes" label="Notes" type="textarea"
        placeholder="e.g. Focus on Cheetah push, post-Ramadan recovery…" />

      <!-- Reps table -->
      <div v-if="form.territory">
        <div class="flex items-center justify-between mb-2">
          <label class="text-xs font-medium text-gray-600">Rep Targets</label>
          <span class="text-xs text-gray-400">{{ form.reps.length }} reps in {{ form.territory }}</span>
        </div>

        <div v-if="repsLoading" class="flex justify-center py-4">
          <FeatherIcon name="loader" class="h-5 w-5 animate-spin text-gray-400" />
        </div>

        <div v-else-if="form.reps.length" class="rounded-xl border border-gray-200 overflow-hidden">
          <table class="w-full text-xs">
            <thead class="bg-gray-50 border-b border-gray-100">
              <tr>
                <th class="px-3 py-2 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Rep</th>
                <th class="px-3 py-2 text-center text-[10px] font-semibold uppercase tracking-wide text-gray-400">Visits</th>
                <th class="px-3 py-2 text-center text-[10px] font-semibold uppercase tracking-wide text-gray-400">Revenue</th>
                <th class="px-3 py-2 text-center text-[10px] font-semibold uppercase tracking-wide text-gray-400">New Custs</th>
                <th class="px-3 py-2 text-center text-[10px] font-semibold uppercase tracking-wide text-gray-400">Comp%</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="rep in form.reps" :key="rep.sales_person">
                <td class="px-3 py-2 font-medium text-gray-900">{{ rep.sales_person_name }}</td>
                <td class="px-3 py-2">
                  <input v-model.number="rep.target_visits" type="number" min="0"
                    class="w-16 h-7 rounded border border-gray-200 px-2 text-center text-xs focus:border-gray-400 focus:outline-none" />
                </td>
                <td class="px-3 py-2">
                  <input v-model.number="rep.target_revenue" type="number" min="0"
                    class="w-24 h-7 rounded border border-gray-200 px-2 text-center text-xs focus:border-gray-400 focus:outline-none" />
                </td>
                <td class="px-3 py-2">
                  <input v-model.number="rep.target_new_customers" type="number" min="0"
                    class="w-16 h-7 rounded border border-gray-200 px-2 text-center text-xs focus:border-gray-400 focus:outline-none" />
                </td>
                <td class="px-3 py-2">
                  <div class="flex items-center gap-1">
                    <input v-model.number="rep.target_compliance_pct" type="number" min="0" max="100"
                      class="w-12 h-7 rounded border border-gray-200 px-2 text-center text-xs focus:border-gray-400 focus:outline-none" />
                    <span class="text-gray-400">%</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else class="rounded-xl border border-dashed border-gray-200 py-6 text-center text-xs text-gray-400">
          No active reps in {{ form.territory }}
        </div>
      </div>
      <div v-else class="rounded-xl border border-dashed border-gray-200 py-6 text-center text-xs text-gray-400">
        Select a territory to load reps
      </div>
    </div>
  </SlidePanel>

  <!-- Detail panel -->
  <TargetSetDetail
    v-if="detailPanel && detailName"
    :key="detailKey"
    v-model="detailPanel"
    :name="detailName"
    :territories="territories"
    @updated="load"
  />
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useDateRange } from '@/composables/useDateRange'
import { call } from '@/utils/frappe'
import { auth } from '@/utils/auth'
import { successToast, errorToast } from '@/utils/toast'
import Btn from '@/components/ui/Btn.vue'
import SlidePanel from '@/components/ui/SlidePanel.vue'
import FormField from '@/components/ui/FormField.vue'
import TargetSetDetail from '@/components/ui/TargetSetDetail.vue'
import dayjs from 'dayjs'

const loading = ref(false)
const saving = ref(false)
const repsLoading = ref(false)
const targetSets = ref([])
const territories = ref([])
const statusFilter = ref('Active')
const territoryFilter = ref('')
const datePreset = ref('')
const { dateFrom, dateTo, dateError, setFrom: setDateFrom, setTo: setDateTo } = useDateRange(0)

const presetLabels = {
  this_month: 'This Month',
  last_month: 'Last Month',
  this_quarter: 'This Quarter',
  last_quarter: 'Last Quarter',
  this_year: 'This Year',
  next_month: 'Next Month',
  next_quarter: 'Next Quarter',
}
const presetLabel = computed(() => presetLabels[datePreset.value] || '')

function applyDatePreset() {
  const d = dayjs()
  switch (datePreset.value) {
    case 'this_month':
      dateFrom.value = d.startOf('month').format('YYYY-MM-DD')
      dateTo.value = d.endOf('month').format('YYYY-MM-DD')
      break
    case 'last_month':
      dateFrom.value = d.subtract(1, 'month').startOf('month').format('YYYY-MM-DD')
      dateTo.value = d.subtract(1, 'month').endOf('month').format('YYYY-MM-DD')
      break
    case 'this_quarter': {
      const qs = d.startOf('quarter')
      dateFrom.value = qs.format('YYYY-MM-DD')
      dateTo.value = qs.endOf('quarter').format('YYYY-MM-DD')
      break
    }
    case 'last_quarter': {
      const lqs = d.subtract(1, 'quarter').startOf('quarter')
      dateFrom.value = lqs.format('YYYY-MM-DD')
      dateTo.value = lqs.endOf('quarter').format('YYYY-MM-DD')
      break
    }
    case 'this_year':
      dateFrom.value = d.startOf('year').format('YYYY-MM-DD')
      dateTo.value = d.endOf('year').format('YYYY-MM-DD')
      break
    case 'next_month':
      dateFrom.value = d.add(1, 'month').startOf('month').format('YYYY-MM-DD')
      dateTo.value = d.add(1, 'month').endOf('month').format('YYYY-MM-DD')
      break
    case 'next_quarter': {
      const nqs = d.add(1, 'quarter').startOf('quarter')
      dateFrom.value = nqs.format('YYYY-MM-DD')
      dateTo.value = nqs.endOf('quarter').format('YYYY-MM-DD')
      break
    }
    case 'custom':
    default:
      // Don't clear — let user type custom dates
      break
  }
}

function clearDates() {
  dateFrom.value = ''
  dateTo.value = ''
  datePreset.value = ''
}
const createPanel = ref(false)
const detailPanel = ref(false)
const detailName = ref('')
const detailKey = ref(0)
const errors = reactive({})
const isAdmin = auth.isAdmin

const form = reactive({
  target_set_name: '', territory: '', date_from: '', date_to: '',
  status: 'Active', notes: '', reps: [],
})

const filtered = computed(() => {
  let l = targetSets.value
  if (statusFilter.value) l = l.filter(t => t.status === statusFilter.value)
  if (territoryFilter.value) l = l.filter(t => t.territory === territoryFilter.value)
  if (dateFrom.value) l = l.filter(t => t.date_to >= dateFrom.value)
  if (dateTo.value) l = l.filter(t => t.date_from <= dateTo.value)
  return l
})

const statusColor = (s) => ({
  'Draft':  'bg-gray-100 text-gray-600',
  'Active': 'bg-green-100 text-green-700',
  'Closed': 'bg-blue-100 text-blue-700',
}[s] || 'bg-gray-100 text-gray-600')

const fmtDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'

async function load() {
  loading.value = true
  try {
    const [setsRes, terrRes] = await Promise.all([
      call('sfa_core.api.targets.get_target_sets'),
      call('sfa_core.api.targets.get_territories'),
    ])
    targetSets.value = setsRes.message || []
    territories.value = terrRes.message || []
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

async function loadRepsForTerritory() {
  if (!form.territory) { form.reps = []; return }
  repsLoading.value = true
  try {
    const res = await call('sfa_core.api.targets.get_reps_for_territory', { territory: form.territory })
    form.reps = (res.message || []).map(r => ({
      sales_person: r.name,
      sales_person_name: r.sales_person_name,
      target_visits: 0,
      target_revenue: 0,
      target_new_customers: 0,
      target_compliance_pct: 80,
    }))
  } catch (e) { console.error(e) }
  finally { repsLoading.value = false }
}

function openCreate() {
  Object.assign(form, {
    target_set_name: '', territory: '', date_from: '', date_to: '',
    status: 'Active', notes: '', reps: [],
  })
  Object.keys(errors).forEach(k => delete errors[k])
  createPanel.value = true
}

function openDetail(name) {
  detailName.value = name
  detailKey.value++
  detailPanel.value = true
}

async function createTargetSet() {
  Object.keys(errors).forEach(k => delete errors[k])
  if (!form.target_set_name) { errors.name = 'Required'; return }
  if (!form.date_from) { errors.date_from = 'Required'; return }
  if (!form.date_to) { errors.date_to = 'Required'; return }
  saving.value = true
  try {
    await call('sfa_core.api.targets.create_target_set', {
      target_set_name: form.target_set_name,
      territory: form.territory || null,
      date_from: form.date_from,
      date_to: form.date_to,
      status: form.status,
      notes: form.notes || null,
      rep_targets: form.reps,
    })
    successToast('Target set created')
    createPanel.value = false
    await load()
  } catch (e) { errorToast(e.message) }
  finally { saving.value = false }
}

onMounted(load)
</script>
