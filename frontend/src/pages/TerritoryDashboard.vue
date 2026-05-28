<template>
  <div class="flex h-full flex-col overflow-hidden">

    <!-- Header -->
    <div class="flex h-[52px] shrink-0 items-center border-b border-gray-100 bg-white px-5 gap-3">
      <h1 class="text-sm font-semibold text-gray-900">Territory Dashboard</h1>
      <div class="flex-1" />

      <!-- Territory selector -->
      <select v-model="territory" @change="load"
        class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:border-gray-400 focus:outline-none">
        <option value="">Select Territory…</option>
        <option v-for="t in territories" :key="t.name" :value="t.name">{{ t.name }}</option>
      </select>

      <!-- Period selector -->
      <select v-model="period" @change="onPresetChange"
        class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:border-gray-400 focus:outline-none">
        <option value="today">Today</option>
        <option value="yesterday">Yesterday</option>
        <option value="week">This Week</option>
        <option value="last_week">Last Week</option>
        <option value="month">This Month</option>
        <option value="last_month">Last Month</option>
        <option value="quarter">This Quarter</option>
        <option value="last_quarter">Last Quarter</option>
        <option value="year">This Year</option>
        <option value="custom">Custom Range…</option>
      </select>

      <!-- Custom date inputs -->
      <template v-if="period === 'custom'">
        <input :value="customFrom" type="date" @change="setCustomFrom($event.target.value)"
          class="h-8 rounded-md border border-gray-200 px-2 text-sm focus:border-gray-400 focus:outline-none" />
        <span class="text-xs text-gray-400">→</span>
        <input :value="customTo" type="date" :min="customFrom" @change="setCustomTo($event.target.value, load)"
          class="h-8 rounded-md border border-gray-200 px-2 text-sm focus:border-gray-400 focus:outline-none" />
      </template>
      <span v-if="customDateError" class="text-xs text-red-500">{{ customDateError }}</span>

      <Btn icon="refresh-cw" :class="loading ? '[&_svg]:animate-spin' : ''" size="sm" @click="load">Refresh</Btn>
    </div>

    <!-- Empty state -->
    <div v-if="!territory" class="flex flex-1 flex-col items-center justify-center text-gray-400">
      <FeatherIcon name="map-pin" class="h-12 w-12 mb-3" />
      <p class="text-sm font-medium text-gray-600">Select a territory to view its dashboard</p>
    </div>

    <!-- Loading -->
    <div v-else-if="loading && !data" class="flex flex-1 items-center justify-center">
      <FeatherIcon name="loader" class="h-8 w-8 animate-spin text-gray-400" />
    </div>

    <!-- Content -->
    <div v-else-if="data" class="flex-1 overflow-y-auto bg-gray-50 p-5 space-y-5">

      <!-- Summary tiles -->
      <div class="grid grid-cols-2 gap-4 sm:grid-cols-3 xl:grid-cols-6">

        <!-- Coverage -->
        <div class="rounded-xl border border-gray-200 bg-white p-4">
          <div class="flex items-center justify-between mb-2">
            <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Coverage</p>
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-50">
              <FeatherIcon name="users" class="h-4 w-4 text-blue-500" />
            </div>
          </div>
          <p class="text-2xl font-bold text-gray-900">{{ data.summary.coverage_pct }}%</p>
          <p class="text-xs text-gray-400 mt-0.5">{{ data.summary.visited_customers }} / {{ data.summary.total_customers }} customers</p>
          <!-- Progress bar -->
          <div class="mt-2 h-1.5 w-full rounded-full bg-gray-100">
            <div class="h-1.5 rounded-full bg-blue-400 transition-all"
              :style="{ width: data.summary.coverage_pct + '%' }" />
          </div>
        </div>

        <!-- Visit Frequency Compliance -->
        <div class="rounded-xl border border-gray-200 bg-white p-4">
          <div class="flex items-center justify-between mb-2">
            <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Freq. Compliance</p>
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-green-50">
              <FeatherIcon name="check-circle" class="h-4 w-4 text-green-500" />
            </div>
          </div>
          <p class="text-2xl font-bold text-gray-900">{{ data.summary.freq_compliance }}%</p>
          <p class="text-xs text-gray-400 mt-0.5">{{ data.summary.freq_compliance_base }} due this period</p>
          <div class="mt-2 h-1.5 w-full rounded-full bg-gray-100">
            <div class="h-1.5 rounded-full transition-all"
              :class="data.summary.freq_compliance >= 80 ? 'bg-green-400' : data.summary.freq_compliance >= 50 ? 'bg-amber-400' : 'bg-red-400'"
              :style="{ width: data.summary.freq_compliance + '%' }" />
          </div>
        </div>

        <!-- Beat Plan Compliance -->
        <div class="rounded-xl border border-gray-200 bg-white p-4">
          <div class="flex items-center justify-between mb-2">
            <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Beat Compliance</p>
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-50">
              <FeatherIcon name="map" class="h-4 w-4 text-indigo-500" />
            </div>
          </div>
          <p class="text-2xl font-bold text-gray-900">
            {{ data.summary.beat_compliance !== null ? data.summary.beat_compliance + '%' : '—' }}
          </p>
          <p class="text-xs text-gray-400 mt-0.5">
            {{ data.summary.beat_compliance !== null ? 'vs beat plan' : 'No active beat plans' }}
          </p>
          <div class="mt-2 h-1.5 w-full rounded-full bg-gray-100">
            <div v-if="data.summary.beat_compliance !== null" class="h-1.5 rounded-full transition-all"
              :class="data.summary.beat_compliance >= 80 ? 'bg-indigo-400' : data.summary.beat_compliance >= 50 ? 'bg-amber-400' : 'bg-red-400'"
              :style="{ width: data.summary.beat_compliance + '%' }" />
          </div>
        </div>

        <!-- Revenue -->
        <div class="rounded-xl border border-gray-200 bg-white p-4">
          <div class="flex items-center justify-between mb-2">
            <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Revenue</p>
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-50">
              <FeatherIcon name="trending-up" class="h-4 w-4 text-emerald-500" />
            </div>
          </div>
          <p class="text-2xl font-bold text-gray-900">{{ fmt(data.summary.revenue) }}</p>
          <p class="text-xs text-gray-400 mt-0.5">From orders</p>
        </div>

        <!-- Overdue -->
        <div class="rounded-xl border border-gray-200 bg-white p-4">
          <div class="flex items-center justify-between mb-2">
            <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Overdue</p>
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-red-50">
              <FeatherIcon name="alert-circle" class="h-4 w-4 text-red-500" />
            </div>
          </div>
          <p class="text-2xl font-bold" :class="data.overdue.length ? 'text-red-600' : 'text-gray-900'">
            {{ data.overdue.length }}
          </p>
          <p class="text-xs text-gray-400 mt-0.5">Customers past due</p>
        </div>

        <!-- Active Reps -->
        <div class="rounded-xl border border-gray-200 bg-white p-4">
          <div class="flex items-center justify-between mb-2">
            <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Active Reps</p>
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-50">
              <FeatherIcon name="user-check" class="h-4 w-4 text-purple-500" />
            </div>
          </div>
          <p class="text-2xl font-bold text-gray-900">{{ data.summary.active_reps }}</p>
          <p class="text-xs text-gray-400 mt-0.5">With visits this period</p>
        </div>
      </div>

      <!-- Rep Activity Table -->
      <div class="rounded-xl border border-gray-200 bg-white overflow-hidden">
        <div class="border-b border-gray-100 px-4 py-3">
          <p class="text-sm font-semibold text-gray-900">Rep Activity</p>
          <p class="text-xs text-gray-400">{{ periodLabel }} · {{ territory }}</p>
        </div>

        <div v-if="data.reps.length">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 border-b border-gray-100">
              <tr>
                <th class="px-4 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Rep</th>
                <th class="px-4 py-2.5 text-center text-[10px] font-semibold uppercase tracking-wide text-gray-400">Visits</th>
                <th class="px-4 py-2.5 text-center text-[10px] font-semibold uppercase tracking-wide text-gray-400">Completed</th>
                <th class="px-4 py-2.5 text-center text-[10px] font-semibold uppercase tracking-wide text-gray-400">Customers</th>
                <th class="px-4 py-2.5 text-right text-[10px] font-semibold uppercase tracking-wide text-gray-400">Revenue</th>
                <th class="px-4 py-2.5 text-center text-[10px] font-semibold uppercase tracking-wide text-gray-400">Completion</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="rep in data.reps" :key="rep.sales_person"
                class="hover:bg-gray-50 cursor-pointer transition-colors"
                @click="goToRepMap(rep.sales_person)"
              >
                <td class="px-4 py-3">
                  <div class="flex items-center gap-2">
                    <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-xs font-semibold text-indigo-700">
                      {{ (rep.sales_person||'?').charAt(0).toUpperCase() }}
                    </div>
                    <span class="font-medium text-gray-900">{{ rep.sales_person }}</span>
                  </div>
                </td>
                <td class="px-4 py-3 text-center text-gray-700">{{ rep.total_visits }}</td>
                <td class="px-4 py-3 text-center text-gray-700">{{ rep.completed }}</td>
                <td class="px-4 py-3 text-center text-gray-700">{{ rep.customers_visited }}</td>
                <td class="px-4 py-3 text-right font-medium text-gray-900">{{ fmt(rep.revenue) }}</td>
                <td class="px-4 py-3">
                  <div class="flex items-center gap-2">
                    <div class="flex-1 h-1.5 rounded-full bg-gray-100">
                      <div class="h-1.5 rounded-full transition-all"
                        :class="completionPct(rep) >= 80 ? 'bg-green-400' : completionPct(rep) >= 50 ? 'bg-amber-400' : 'bg-red-400'"
                        :style="{ width: completionPct(rep) + '%' }"
                      />
                    </div>
                    <span class="text-xs text-gray-500 w-8 text-right">{{ completionPct(rep) }}%</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="flex flex-col items-center py-10 text-gray-400">
          <FeatherIcon name="users" class="h-8 w-8 mb-2" />
          <p class="text-sm">No rep activity this period</p>
        </div>
      </div>

      <!-- Bottom panels: Overdue + Unvisited -->
      <div class="grid grid-cols-1 gap-5 lg:grid-cols-2">

        <!-- Overdue customers -->
        <div class="rounded-xl border border-gray-200 bg-white overflow-hidden">
          <div class="flex items-center justify-between border-b border-gray-100 px-4 py-3">
            <div>
              <p class="text-sm font-semibold text-gray-900">Overdue Customers</p>
              <p class="text-xs text-gray-400">Past their next visit due date</p>
            </div>
            <span class="rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-700">
              {{ data.overdue.length }}
            </span>
          </div>
          <div v-if="data.overdue.length" class="max-h-80 overflow-y-auto divide-y divide-gray-50">
            <div v-for="c in data.overdue" :key="c.name"
              class="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors"
              @click="$router.push('/customers/'+c.name)"
            >
              <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-red-100 text-xs font-semibold text-red-600">
                {{ (c.customer_name||'?').charAt(0).toUpperCase() }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">{{ c.customer_name }}</p>
                <p class="text-xs text-gray-400">
                  {{ c.custom_sfa_rep || 'No rep' }}
                  <span v-if="c.custom_location_area"> · {{ c.custom_location_area }}</span>
                </p>
              </div>
              <div class="shrink-0 text-right">
                <p class="text-xs font-semibold text-red-600">{{ daysOverdue(c.custom_next_visit_due) }}d overdue</p>
                <p class="text-[10px] text-gray-400">Due {{ fmtDate(c.custom_next_visit_due) }}</p>
              </div>
            </div>
          </div>
          <div v-else class="flex flex-col items-center py-8 text-gray-400">
            <FeatherIcon name="check-circle" class="h-8 w-8 mb-2 text-green-400" />
            <p class="text-sm text-green-600">No overdue customers</p>
          </div>
        </div>

        <!-- Not visited this period -->
        <div class="rounded-xl border border-gray-200 bg-white overflow-hidden">
          <div class="flex items-center justify-between border-b border-gray-100 px-4 py-3">
            <div>
              <p class="text-sm font-semibold text-gray-900">Not Visited</p>
              <p class="text-xs text-gray-400">No completed visit this period</p>
            </div>
            <span class="rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-medium text-amber-700">
              {{ data.unvisited.length }}
            </span>
          </div>
          <div v-if="data.unvisited.length" class="max-h-80 overflow-y-auto divide-y divide-gray-50">
            <div v-for="c in data.unvisited" :key="c.name"
              class="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors"
              @click="$router.push('/customers/'+c.name)"
            >
              <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gray-100 text-xs font-semibold text-gray-600">
                {{ (c.customer_name||'?').charAt(0).toUpperCase() }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">{{ c.customer_name }}</p>
                <p class="text-xs text-gray-400">
                  {{ c.custom_sfa_rep || 'No rep' }}
                  <span v-if="c.custom_location_area"> · {{ c.custom_location_area }}</span>
                </p>
              </div>
              <div class="shrink-0 text-right">
                <p class="text-xs text-gray-500">
                  {{ c.custom_last_visit_date ? 'Last: ' + fmtDate(c.custom_last_visit_date) : 'Never visited' }}
                </p>
                <p v-if="c.custom_next_visit_due" class="text-[10px]"
                  :class="isOverdue(c) ? 'text-red-500 font-medium' : 'text-gray-400'">
                  Due {{ fmtDate(c.custom_next_visit_due) }}
                </p>
              </div>
            </div>
          </div>
          <div v-else class="flex flex-col items-center py-8 text-gray-400">
            <FeatherIcon name="check-circle" class="h-8 w-8 mb-2 text-green-400" />
            <p class="text-sm text-green-600">All customers visited this period</p>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDateRange } from '@/composables/useDateRange'
import { useRouter } from 'vue-router'
import { call } from '@/utils/frappe'
import { formatCurrency } from '@/utils/currency'
import Btn from '@/components/ui/Btn.vue'
import dayjs from 'dayjs'

const router = useRouter()
const territory = ref('')
const period = ref('month')
const { dateFrom: customFrom, dateTo: customTo, dateError: customDateError, setFrom: setCustomFrom, setTo: setCustomTo } = useDateRange(0)
const territories = ref([])
const data = ref(null)
const loading = ref(false)

const periodLabels = {
  today: 'Today', yesterday: 'Yesterday',
  week: 'This Week', last_week: 'Last Week',
  month: 'This Month', last_month: 'Last Month',
  quarter: 'This Quarter', last_quarter: 'Last Quarter',
  year: 'This Year', custom: 'Custom Range',
}

const periodLabel = computed(() => periodLabels[period.value] || 'This Month')

async function loadTerritories() {
  try {
    const res = await call('sfa_core.api.territory_dashboard.get_territories_list')
    territories.value = res.message || []
  } catch (e) { console.error(e) }
}

async function load() {
  if (!territory.value) return
  loading.value = true
  try {
    const args = { territory: territory.value, period: period.value }
    if (period.value === 'custom' && customFrom.value && customTo.value) {
      args.date_from = customFrom.value
      args.date_to = customTo.value
    }
    const res = await call('sfa_core.api.territory_dashboard.get_territory_dashboard', args)
    data.value = res.message
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

function onPresetChange() {
  if (period.value !== 'custom') load()
}

function goToRepMap(salesPerson) {
  router.push({ path: '/rep-activity-map', query: { rep: salesPerson } })
}

const completionPct = (rep) =>
  rep.total_visits > 0 ? Math.round(rep.completed / rep.total_visits * 100) : 0

const fmt = (v) => formatCurrency(v || 0)
const fmtDate = (d) => d ? dayjs(d).format('D MMM') : '—'
const daysOverdue = (d) => d ? dayjs().diff(dayjs(d), 'day') : 0
const isOverdue = (c) => c.custom_next_visit_due && dayjs(c.custom_next_visit_due).isBefore(dayjs(), 'day')

onMounted(loadTerritories)
</script>
