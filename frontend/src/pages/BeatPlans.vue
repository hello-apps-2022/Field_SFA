<template>
  <div class="flex h-full flex-col overflow-hidden">

    <!-- Header -->
    <div class="flex h-[52px] shrink-0 items-center border-b border-gray-100 bg-white px-5 gap-3">
      <h1 class="text-sm font-semibold text-gray-900">Beat Plans</h1>
      <div class="flex-1" />
      <span class="text-xs text-gray-400">{{ filtered.length }} plans</span>
      <Btn v-if="canCreate" icon="plus" variant="solid" size="sm" @click="openCreate">New Beat Plan</Btn>
    </div>

    <!-- Filters -->
    <div class="flex shrink-0 flex-wrap items-center gap-2 border-b border-gray-100 bg-white px-4 py-2.5">
      <div class="relative">
        <FeatherIcon name="search" class="absolute left-2.5 top-2 h-3.5 w-3.5 text-gray-400 pointer-events-none" />
        <input v-model="search" placeholder="Search plans, reps…"
          class="h-8 w-44 rounded-md border border-gray-200 bg-white pl-8 pr-3 text-sm focus:border-gray-400 focus:outline-none" />
      </div>

      <select v-model="statusFilter" class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
        <option value="">All Statuses</option>
        <option value="Draft">Draft</option>
        <option value="Active">Active</option>
        <option value="Completed">Completed</option>
        <option value="Cancelled">Cancelled</option>
      </select>

      <select v-model="repFilter" class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
        <option value="">All Reps</option>
        <option v-for="r in repOptions" :key="r">{{ r }}</option>
      </select>

      <!-- Manager: rep creation toggle -->
      <div v-if="isManager" class="ml-auto flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-3 py-1.5">
        <span class="text-xs text-gray-500">Reps can create</span>
        <button
          class="relative inline-flex h-5 w-9 shrink-0 rounded-full border-2 border-transparent transition-colors"
          :class="repCanCreate ? 'bg-gray-900' : 'bg-gray-200'"
          @click="toggleRepPermission"
        >
          <span class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform"
            :class="repCanCreate ? 'translate-x-4' : 'translate-x-0'" />
        </button>
      </div>
    </div>

    <!-- Cards -->
    <div class="flex-1 overflow-y-auto bg-gray-50 p-4">
      <div v-if="loading" class="flex h-40 items-center justify-center">
        <FeatherIcon name="loader" class="h-6 w-6 animate-spin text-gray-400" />
      </div>

      <div v-else-if="filtered.length" class="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
        <div v-for="plan in filtered" :key="plan.name"
          class="rounded-xl border border-gray-200 bg-white overflow-hidden cursor-pointer hover:shadow-md transition-shadow"
          @click="openDetail(plan.name)"
        >
          <!-- Plan header -->
          <div class="flex items-start justify-between px-4 pt-4 pb-3">
            <div class="min-w-0 flex-1">
              <p class="text-sm font-semibold text-gray-900 truncate">{{ plan.plan_name }}</p>
              <p class="text-xs text-gray-400 mt-0.5">
                {{ plan.sales_person || 'No rep assigned' }}
                <span v-if="plan.territory"> · {{ plan.territory }}</span>
              </p>
            </div>
            <StatusBadge :status="plan.status" />
          </div>

          <!-- Week grid — shows which days have beats -->
          <div class="px-4 pb-3">
            <div class="grid grid-cols-7 gap-1">
              <div v-for="d in weekDays" :key="d.value" class="flex flex-col items-center gap-0.5">
                <span class="text-[9px] font-medium text-gray-400">{{ d.short }}</span>
                <div class="h-2 w-full rounded-sm"
                  :class="dayHasBeat(plan, d.value) ? 'bg-gray-900' : 'bg-gray-100'" />
              </div>
            </div>
          </div>

          <!-- Stats -->
          <div class="flex items-center gap-4 border-t border-gray-50 px-4 py-2.5 text-xs text-gray-500">
            <span class="flex items-center gap-1">
              <FeatherIcon name="map" class="h-3 w-3 text-gray-400" />
              {{ plan.beat_count }} beat{{ plan.beat_count !== 1 ? 's' : '' }}
            </span>
            <span class="flex items-center gap-1">
              <FeatherIcon name="users" class="h-3 w-3 text-gray-400" />
              {{ plan.customer_count }} customers
            </span>
            <span v-if="plan.custom_discovery_count" class="flex items-center gap-1 text-green-600">
              <FeatherIcon name="plus-circle" class="h-3 w-3" />
              {{ plan.custom_discovery_count }} discovered
            </span>
            <span v-if="plan.custom_effective_from" class="ml-auto text-[10px] text-gray-300">
              From {{ formatDate(plan.custom_effective_from) }}
            </span>
          </div>
        </div>
      </div>

      <div v-else class="flex flex-col items-center py-20 text-gray-400">
        <FeatherIcon name="map" class="h-10 w-10 mb-3" />
        <p class="text-sm font-medium text-gray-500">No beat plans yet</p>
        <p class="text-xs mt-1 mb-4">Create a weekly route plan for your reps</p>
        <Btn v-if="canCreate" icon="plus" variant="solid" size="sm" @click="openCreate">Create Beat Plan</Btn>
      </div>
    </div>
  </div>

  <!-- Create panel — full plan + beats in one go -->
  <SlidePanel v-model="createPanel" title="New Beat Plan" :saving="saving" save-label="Save Beat Plan" width="640px" @save="savePlan">
    <div class="space-y-5">

      <!-- Plan details -->
      <div class="space-y-3">
        <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Plan Details</p>
        <FormField v-model="form.plan_name" label="Plan Name" required :error="errors.plan_name"
          placeholder="e.g. Moulik - Kampala North" />
        <div class="grid grid-cols-2 gap-3">
          <FormField v-model="form.sales_person" label="Sales Person" type="select" :options="salesPersons" />
          <FormField v-model="form.territory" label="Territory" type="select" :options="territories" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <FormField v-model="form.effective_from" label="Effective From" type="date" />
          <FormField v-model="form.effective_to" label="Effective To" type="date" help="Blank = ongoing" />
        </div>
      </div>

      <!-- Beats builder -->
      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Beats (Routes)</p>
          <button class="flex items-center gap-1 text-xs font-medium text-gray-600 hover:text-gray-900" @click="addNewBeat">
            <FeatherIcon name="plus" class="h-3.5 w-3.5" /> Add Beat
          </button>
        </div>

        <div v-if="!form.beats.length" class="rounded-xl border border-dashed border-gray-200 py-8 text-center text-gray-400">
          <FeatherIcon name="map" class="h-8 w-8 mx-auto mb-2" />
          <p class="text-sm">No beats yet</p>
          <p class="text-xs mt-1">A beat is a named route that runs on specific days</p>
          <button class="mt-3 text-xs font-medium text-blue-500 hover:underline" @click="addNewBeat">+ Add first beat</button>
        </div>

        <div v-for="(beat, bi) in form.beats" :key="bi" class="rounded-xl border border-gray-200 bg-gray-50 p-4 space-y-3">
          <!-- Beat name + delete -->
          <div class="flex items-center gap-2">
            <input v-model="beat.beat_name" type="text" placeholder="Beat name, e.g. Kyebando Route"
              class="flex-1 h-8 rounded-md border border-gray-200 bg-white px-3 text-sm focus:border-gray-400 focus:outline-none" />
            <button @click="form.beats.splice(bi, 1)" class="text-gray-300 hover:text-red-500 transition-colors">
              <FeatherIcon name="trash-2" class="h-4 w-4" />
            </button>
          </div>

          <!-- Day selector -->
          <div class="flex gap-1.5">
            <button v-for="d in weekDays" :key="d.value"
              class="flex-1 rounded-md border py-1.5 text-[11px] font-semibold transition-colors"
              :class="beat.days.includes(d.value)
                ? 'bg-gray-900 text-white border-gray-900'
                : 'bg-white text-gray-400 border-gray-200 hover:border-gray-400'"
              @click="toggleBeatDay(beat, d.value)"
            >{{ d.short }}</button>
          </div>

          <!-- Area -->
          <input v-model="beat.area_name" type="text" placeholder="Area / zone (optional)"
            class="w-full h-8 rounded-md border border-gray-200 bg-white px-3 text-xs focus:border-gray-400 focus:outline-none" />

          <!-- Customer search -->
          <div>
            <div class="flex items-center justify-between mb-1.5">
              <span class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Customers</span>
              <span class="text-[10px] text-gray-400">{{ beat.customers.length }} added</span>
            </div>

            <!-- Search input -->
            <div class="relative">
              <FeatherIcon name="search" class="absolute left-2.5 top-2 h-3.5 w-3.5 text-gray-400 pointer-events-none" />
              <input
                v-model="beat.customerSearch"
                type="text"
                placeholder="Search to add customers…"
                class="w-full h-8 rounded-md border border-gray-200 bg-white pl-8 pr-3 text-sm focus:border-gray-400 focus:outline-none"
                @input="onCreateSearchInput(beat)"
                @blur="onBeatBlur(beat)"
                @focus="beat.showResults = beat.searchResults?.length > 0"
              />
              <div v-if="beat.showResults && beat.searchResults?.length"
                class="absolute top-full left-0 right-0 z-50 mt-1 max-h-40 overflow-y-auto rounded-lg border border-gray-200 bg-white shadow-lg"
              >
                <button
                  v-for="c in beat.searchResults" :key="c.name"
                  class="flex w-full items-center gap-2 px-3 py-2 text-left hover:bg-gray-50"
                  @mousedown.prevent="addCustomerToBeat(beat, c)"
                >
                  <div class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-[10px] font-bold text-indigo-700">
                    {{ (c.customer_name||'?').charAt(0).toUpperCase() }}
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ c.customer_name }}</p>
                    <p class="text-[10px] text-gray-400">{{ [c.custom_location_area, c.custom_location_city].filter(Boolean).join(', ') || c.territory }}</p>
                  </div>
                </button>
              </div>
            </div>

            <!-- Added customers list -->
            <div v-if="beat.customers.length" class="mt-2 space-y-1">
              <div v-for="(c, ci) in beat.customers" :key="c.name"
                class="flex items-center gap-2 rounded-lg bg-white border border-gray-100 px-2.5 py-1.5"
              >
                <span class="text-[10px] font-bold text-gray-400 w-4 text-center">{{ ci + 1 }}</span>
                <div class="flex-1 min-w-0">
                  <p class="text-xs font-medium text-gray-900 truncate">{{ c.customer_name }}</p>
                  <p class="text-[10px] text-gray-400 truncate">{{ [c.custom_location_area, c.custom_location_city].filter(Boolean).join(', ') }}</p>
                </div>
                <button @click="beat.customers.splice(ci, 1)" class="text-gray-300 hover:text-red-500">
                  <FeatherIcon name="x" class="h-3 w-3" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <p v-if="errors.beats" class="text-xs text-red-500">{{ errors.beats }}</p>
      </div>
    </div>
  </SlidePanel>

  <!-- Detail panel -->
  <BeatPlanDetail
    v-if="detailPanel && detailName"
    :key="detailKey"
    v-model="detailPanel"
    :name="detailName"
    :is-manager="isManager"
    @updated="load"
  />
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { call, getList } from '@/utils/frappe'
import { successToast, errorToast } from '@/utils/toast'
import Btn from '@/components/ui/Btn.vue'
import SlidePanel from '@/components/ui/SlidePanel.vue'
import FormField from '@/components/ui/FormField.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import BeatPlanDetail from '@/components/ui/BeatPlanDetail.vue'
import dayjs from 'dayjs'

const weekDays = [
  { value: 'monday',    short: 'M' },
  { value: 'tuesday',   short: 'T' },
  { value: 'wednesday', short: 'W' },
  { value: 'thursday',  short: 'T' },
  { value: 'friday',    short: 'F' },
  { value: 'saturday',  short: 'S' },
  { value: 'sunday',    short: 'S' },
]

const plans = ref([])
const loading = ref(false)
const search = ref('')
const statusFilter = ref('Active')
const repFilter = ref('')
const createPanel = ref(false)
const detailPanel = ref(false)
const detailName = ref('')
const detailKey = ref(0)
const saving = ref(false)
const errors = reactive({})
const canCreate = ref(true)
const isManager = ref(false)
const repCanCreate = ref(true)
const salesPersons = ref([])
const territories = ref([])

const form = reactive({
  plan_name: '', sales_person: '', territory: '',
  status: 'Active', effective_from: dayjs().format('YYYY-MM-DD'), effective_to: '',
  beats: [], // [{beat_name, days:[], area_name}]
})

const repOptions = computed(() =>
  [...new Set(plans.value.map(p => p.sales_person).filter(Boolean))].sort()
)

const filtered = computed(() => {
  let l = plans.value
  if (search.value) {
    const q = search.value.toLowerCase()
    l = l.filter(p => p.plan_name?.toLowerCase().includes(q) ||
      p.sales_person?.toLowerCase().includes(q))
  }
  if (statusFilter.value) l = l.filter(p => p.status === statusFilter.value)
  if (repFilter.value) l = l.filter(p => p.sales_person === repFilter.value)
  return l
})

function dayHasBeat(plan, day) {
  return plan.beats_summary?.some(b => b[day])
}

function openDetail(name) {
  detailName.value = name
  detailKey.value++
  detailPanel.value = true
}

async function load() {
  loading.value = true
  try {
    const res = await call('sfa_core.api.beat_plans.get_beat_plans')
    plans.value = res.message || []
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

async function loadMeta() {
  const [sp, tr, perm] = await Promise.all([
    getList('Sales Person', { fields: ['name'], filters: { is_group: 0 }, limit: 200 }),
    getList('Territory', { fields: ['name'], filters: { is_group: 0 }, limit: 100 }),
    call('sfa_core.api.beat_plans.can_rep_create'),
  ])
  salesPersons.value = sp.map(s => s.name)
  territories.value = tr.map(t => t.name)
  canCreate.value = perm.message?.can_create ?? true
  isManager.value = perm.message?.is_manager ?? false
  repCanCreate.value = perm.message?.rep_setting ?? true
}

async function toggleRepPermission() {
  repCanCreate.value = !repCanCreate.value
  await call('sfa_core.api.beat_plans.set_rep_creation_permission', { allow: repCanCreate.value })
  successToast(repCanCreate.value ? 'Reps can now create beat plans' : 'Only managers can create beat plans')
}

function addNewBeat() {
  form.beats.push({
    beat_name: '', days: [], area_name: '',
    customers: [], customerSearch: '', showResults: false, searchResults: [],
  })
}

function toggleBeatDay(beat, day) {
  const i = beat.days.indexOf(day)
  if (i >= 0) beat.days.splice(i, 1)
  else beat.days.push(day)
}

let createSearchTimers = {}

function onBeatBlur(beat) {
  window.setTimeout(() => { beat.showResults = false }, 150)
}

function onCreateSearchInput(beat) {
  const key = form.beats.indexOf(beat)
  if (createSearchTimers[key]) clearTimeout(createSearchTimers[key])
  if (!beat.customerSearch || beat.customerSearch.length < 2) {
    beat.searchResults = []; return
  }
  createSearchTimers[key] = window.setTimeout(() => searchForBeat(beat), 300)
}

async function searchForBeat(beat) {
  try {
    const existing = new Set(beat.customers.map(c => c.name))
    const results = await getList('Customer', {
      fields: ['name', 'customer_name', 'territory', 'custom_location_area', 'custom_location_city'],
      filters: { customer_name: ['like', `%${beat.customerSearch}%`] },
      limit: 8,
    })
    beat.searchResults = results.filter(r => !existing.has(r.name))
    beat.showResults = true
  } catch (e) { console.error(e) }
}

function addCustomerToBeat(beat, customer) {
  beat.showResults = false
  beat.customerSearch = ''
  beat.searchResults = []
  if (!beat.customers.find(c => c.name === customer.name)) {
    beat.customers.push(customer)
  }
}

function openCreate() {
  Object.assign(form, {
    plan_name: '', sales_person: '', territory: '',
    status: 'Active', effective_from: dayjs().format('YYYY-MM-DD'), effective_to: '',
    beats: [],
  })
  Object.keys(errors).forEach(k => delete errors[k])
  addNewBeat() // start with one empty beat
  createPanel.value = true
}

async function savePlan() {
  Object.keys(errors).forEach(k => delete errors[k])
  if (!form.plan_name) { errors.plan_name = 'Required'; return }

  // Validate beats
  const validBeats = form.beats.filter(b => b.beat_name.trim())
  for (const b of validBeats) {
    if (!b.days.length) { errors.beats = `"${b.beat_name}" needs at least one day selected`; return }
  }

  saving.value = true
  try {
    // 1. Create the beat plan
    const res = await call('frappe.client.insert', {
      doc: {
        doctype: 'SFA Beat Plan',
        plan_name: form.plan_name,
        date: form.effective_from || dayjs().format('YYYY-MM-DD'),
        sales_person: form.sales_person || null,
        territory: form.territory || null,
        status: form.status,
        custom_effective_from: form.effective_from || null,
        custom_effective_to: form.effective_to || null,
      }
    })
    const planName = res.message?.name

    // 2. Add each beat with its customers
    for (const beat of validBeats) {
      await call('sfa_core.api.beat_plans.add_beat', {
        beat_plan: planName,
        beat_name: beat.beat_name.trim(),
        days: beat.days,
        area_name: beat.area_name || null,
      })
    }

    // 3. Add customers to each beat
    // Re-fetch plan to get beat names/IDs
    const planRes = await call('sfa_core.api.beat_plans.get_beat_plan', { name: planName })
    const createdBeats = planRes.message?.custom_beats || []

    for (let i = 0; i < validBeats.length; i++) {
      const beat = validBeats[i]
      const createdBeat = createdBeats[i]
      if (!createdBeat || !beat.customers.length) continue
      for (const customer of beat.customers) {
        await call('sfa_core.api.beat_plans.add_customer_to_beat', {
          beat_name: createdBeat.name,
          customer: customer.name,
        })
      }
    }

    successToast('Beat plan created')
    createPanel.value = false
    await load()
    // Auto-open the new plan
    openDetail(planName)
  } catch (e) { errorToast(e.message || 'Failed') }
  finally { saving.value = false }
}

const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'

onMounted(() => Promise.all([load(), loadMeta()]))
</script>
