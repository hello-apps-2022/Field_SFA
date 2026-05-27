<template>
  <div class="flex h-full flex-col overflow-hidden">

    <!-- Header -->
    <div class="flex h-[52px] shrink-0 items-center border-b border-gray-100 bg-white px-5 gap-3">
      <h1 class="text-sm font-semibold text-gray-900">Performance</h1>
      <div class="flex-1" />

      <!-- Target set selector -->
      <select v-model="selectedSet" @change="loadPerformance"
        class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none min-w-[200px]">
        <option value="">Select target set…</option>
        <option v-for="ts in targetSets" :key="ts.name" :value="ts.name">
          {{ ts.target_set_name }} — {{ ts.territory }}
        </option>
      </select>

      <select v-if="isAdmin" v-model="territoryFilter" @change="loadSets"
        class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
        <option value="">All Territories</option>
        <option v-for="t in territories" :key="t.name" :value="t.name">{{ t.name }}</option>
      </select>

      <Btn icon="refresh-cw" size="sm" :class="loading ? '[&_svg]:animate-spin' : ''" @click="loadPerformance">Refresh</Btn>
    </div>

    <!-- Empty state -->
    <div v-if="!selectedSet" class="flex flex-1 flex-col items-center justify-center text-gray-400">
      <FeatherIcon name="target" class="h-12 w-12 mb-3" />
      <p class="text-sm font-medium text-gray-600">Select a target set to view performance</p>
      <p class="text-xs mt-1 text-gray-400">Or <router-link to="/targets" class="text-blue-500 hover:underline">create a target set</router-link> first</p>
    </div>

    <div v-else-if="loading" class="flex flex-1 items-center justify-center">
      <FeatherIcon name="loader" class="h-8 w-8 animate-spin text-gray-400" />
    </div>

    <div v-else-if="data" class="flex-1 overflow-y-auto bg-gray-50 p-5 space-y-5">

      <!-- Period info bar -->
      <div class="flex items-center justify-between rounded-xl border border-gray-200 bg-white px-4 py-3">
        <div class="flex items-center gap-4">
          <div>
            <p class="text-sm font-semibold text-gray-900">{{ data.target_set_name }}</p>
            <p class="text-xs text-gray-400">{{ data.territory }} · {{ fmtDate(data.date_from) }} → {{ fmtDate(data.date_to) }}</p>
          </div>
          <span class="rounded-full px-2.5 py-0.5 text-xs font-medium"
            :class="statusColor(data.status)">{{ data.status }}</span>
        </div>
        <div class="flex items-center gap-2 text-xs text-gray-400">
          <FeatherIcon name="calendar" class="h-3.5 w-3.5" />
          {{ daysRemaining }} days remaining
        </div>
      </div>

      <!-- Team summary -->
      <div class="grid grid-cols-4 gap-4">
        <div v-for="m in teamSummary" :key="m.label"
          class="rounded-xl border border-gray-200 bg-white p-4">
          <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">{{ m.label }}</p>
          <div class="mt-1.5 flex items-end gap-2">
            <p class="text-2xl font-bold text-gray-900">{{ m.actual }}</p>
            <p class="text-sm text-gray-400 mb-0.5">/ {{ m.target }}</p>
          </div>
          <div class="mt-2 h-2 w-full rounded-full bg-gray-100">
            <div class="h-2 rounded-full transition-all"
              :class="m.pct >= 100 ? 'bg-green-400' : m.pct >= 70 ? 'bg-amber-400' : 'bg-red-400'"
              :style="{ width: Math.min(m.pct, 100) + '%' }" />
          </div>
          <p class="mt-1.5 text-xs font-semibold"
            :class="m.pct >= 100 ? 'text-green-600' : m.pct >= 70 ? 'text-amber-600' : 'text-red-600'">
            {{ m.pct }}% achieved
          </p>
        </div>
      </div>

      <!-- Rep performance cards -->
      <div>
        <p class="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-3">Rep Breakdown</p>
        <div class="space-y-3">
          <div v-for="rep in data.rep_targets" :key="rep.sales_person"
            class="rounded-xl border border-gray-200 bg-white overflow-hidden">

            <!-- Rep header -->
            <div class="flex items-center justify-between px-4 py-3 border-b border-gray-50">
              <div class="flex items-center gap-3">
                <div class="flex h-9 w-9 items-center justify-center rounded-full text-sm font-bold"
                  :class="overallPct(rep) >= 100 ? 'bg-green-100 text-green-700' : overallPct(rep) >= 70 ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-600'">
                  {{ (rep.sales_person_name||'?').charAt(0).toUpperCase() }}
                </div>
                <div>
                  <p class="text-sm font-semibold text-gray-900">{{ rep.sales_person_name }}</p>
                  <p class="text-xs text-gray-400">{{ data.territory }}</p>
                </div>
              </div>
              <div class="text-right">
                <p class="text-xs text-gray-400">Overall Achievement</p>
                <p class="text-lg font-bold"
                  :class="overallPct(rep) >= 100 ? 'text-green-600' : overallPct(rep) >= 70 ? 'text-amber-600' : 'text-red-600'">
                  {{ overallPct(rep) }}%
                </p>
              </div>
            </div>

            <!-- Metrics -->
            <div class="grid grid-cols-4 divide-x divide-gray-50">
              <div v-for="m in repMetrics(rep)" :key="m.key" class="px-4 py-3">
                <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400 mb-2">{{ m.label }}</p>
                <div class="flex items-end gap-1.5 mb-2">
                  <span class="text-xl font-bold text-gray-900">{{ m.actual }}</span>
                  <span class="text-xs text-gray-400 mb-0.5">/ {{ m.target }}</span>
                </div>
                <div class="h-2 w-full rounded-full bg-gray-100 mb-1.5">
                  <div class="h-2 rounded-full"
                    :class="m.pct >= 100 ? 'bg-green-400' : m.pct >= 70 ? 'bg-amber-400' : 'bg-red-400'"
                    :style="{ width: Math.min(m.pct, 100) + '%' }" />
                </div>
                <p class="text-xs font-semibold"
                  :class="m.pct >= 100 ? 'text-green-600' : m.pct >= 70 ? 'text-amber-600' : 'text-red-600'">
                  {{ m.pct }}%
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { call } from '@/utils/frappe'
import { auth } from '@/utils/auth'
import Btn from '@/components/ui/Btn.vue'
import dayjs from 'dayjs'

const loading = ref(false)
const targetSets = ref([])
const territories = ref([])
const selectedSet = ref('')
const territoryFilter = ref('')
const data = ref(null)
const isAdmin = auth.isAdmin

const fmtDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'

const statusColor = (s) => ({
  'Draft': 'bg-gray-100 text-gray-600',
  'Active': 'bg-green-100 text-green-700',
  'Closed': 'bg-blue-100 text-blue-700',
}[s] || 'bg-gray-100 text-gray-600')

const daysRemaining = computed(() => {
  if (!data.value?.date_to) return 0
  const diff = dayjs(data.value.date_to).diff(dayjs(), 'day')
  return diff > 0 ? diff : 0
})

function pct(actual, target) {
  return target > 0 ? Math.round((actual || 0) / target * 100) : 0
}

function fmtNum(n) {
  if (!n) return '0'
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return (n / 1000).toFixed(0) + 'K'
  return String(Math.round(n))
}

function overallPct(rep) {
  return pct(rep.actual_visits, rep.target_visits)
}

function repMetrics(rep) {
  return [
    { key: 'visits', label: 'Visits', target: rep.target_visits, actual: rep.actual_visits, pct: pct(rep.actual_visits, rep.target_visits) },
    { key: 'revenue', label: 'Revenue', target: fmtNum(rep.target_revenue), actual: fmtNum(rep.actual_revenue), pct: pct(rep.actual_revenue, rep.target_revenue) },
    { key: 'new_customers', label: 'New Customers', target: rep.target_new_customers, actual: rep.actual_new_customers, pct: pct(rep.actual_new_customers, rep.target_new_customers) },
    { key: 'compliance', label: 'Compliance', target: (rep.target_compliance_pct || 0) + '%', actual: (rep.actual_compliance_pct || 0) + '%', pct: pct(rep.actual_compliance_pct, rep.target_compliance_pct) },
  ]
}

const teamSummary = computed(() => {
  if (!data.value?.rep_targets?.length) return []
  const reps = data.value.rep_targets
  const tot = key => reps.reduce((s, r) => s + (r[key] || 0), 0)
  return [
    { label: 'Visits', target: tot('target_visits'), actual: tot('actual_visits'), pct: pct(tot('actual_visits'), tot('target_visits')) },
    { label: 'Revenue', target: fmtNum(tot('target_revenue')), actual: fmtNum(tot('actual_revenue')), pct: pct(tot('actual_revenue'), tot('target_revenue')) },
    { label: 'New Customers', target: tot('target_new_customers'), actual: tot('actual_new_customers'), pct: pct(tot('actual_new_customers'), tot('target_new_customers')) },
    { label: 'Compliance', target: Math.round(tot('target_compliance_pct') / reps.length) + '%', actual: Math.round(tot('actual_compliance_pct') / reps.length) + '%', pct: pct(tot('actual_compliance_pct'), tot('target_compliance_pct')) },
  ]
})

async function loadSets() {
  try {
    const [setsRes, terrRes] = await Promise.all([
      call('sfa_core.api.targets.get_target_sets', { territory: territoryFilter.value || null }),
      isAdmin ? call('sfa_core.api.targets.get_territories') : Promise.resolve({ message: [] }),
    ])
    targetSets.value = setsRes.message || []
    territories.value = terrRes.message || []
    // Auto-select the first active set
    const active = targetSets.value.find(ts => ts.status === 'Active')
    if (active && !selectedSet.value) {
      selectedSet.value = active.name
      await loadPerformance()
    }
  } catch (e) { console.error(e) }
}

async function loadPerformance() {
  if (!selectedSet.value) return
  loading.value = true
  try {
    const res = await call('sfa_core.api.targets.get_target_set', { name: selectedSet.value })
    data.value = res.message
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

onMounted(loadSets)
</script>
