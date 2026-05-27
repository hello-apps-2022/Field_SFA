<template>
  <div class="flex h-full flex-col overflow-hidden">

    <!-- Header -->
    <div class="flex h-[52px] shrink-0 items-center border-b border-gray-100 bg-white px-5 gap-3">
      <div class="flex-1">
        <h1 class="text-sm font-semibold text-gray-900">Dashboard</h1>
      </div>
      <!-- Period selector -->
      <div class="flex gap-1">
        <button v-for="p in periods" :key="p.value"
          class="h-7 rounded-md px-3 text-xs font-medium transition-colors border"
          :class="period === p.value
            ? 'bg-gray-900 text-white border-gray-900'
            : 'bg-white text-gray-600 border-gray-200 hover:border-gray-400'"
          @click="period = p.value; refresh()"
        >
          {{ p.label }}
        </button>
      </div>
      <Btn icon="refresh-cw" :class="loading ? '[&_svg]:animate-spin' : ''" size="sm" @click="refresh">
        Refresh
      </Btn>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto bg-gray-50 p-5 space-y-4">

      <!-- Greeting -->
      <div>
        <h2 class="text-base font-semibold text-gray-900">Good {{ greeting }}, {{ firstName }}</h2>
        <p class="text-sm text-gray-400 mt-0.5">{{ today }} · {{ periodLabel }}</p>
      </div>

      <!-- Metric cards -->
      <div class="grid grid-cols-2 gap-4 sm:grid-cols-3 xl:grid-cols-6">
        <MetricCard label="Active Visits"     :value="m.active_visits ?? '—'"        icon="map-pin"       color="blue"    sub="In progress" />
        <MetricCard label="Completed"         :value="completedStr"                   icon="check-circle"  color="green"   :sub="`of ${m.total_visits ?? 0} planned`" />
        <MetricCard label="Orders"            :value="m.orders_count ?? '—'"          icon="shopping-cart" color="purple"  sub="Submitted" />
        <MetricCard label="Revenue"           :value="fmt(m.revenue)"                 icon="trending-up"   color="emerald" sub="From orders" />
        <MetricCard label="Collections"       :value="fmt(m.payments_collected)"      icon="credit-card"   color="orange"  sub="Payments" />
        <MetricCard label="Compliance"        :value="(m.compliance_rate ?? 0) + '%'" icon="bar-chart-2"   color="teal"    sub="Beat plan" />
      </div>

      <!-- Secondary metrics row -->
      <div class="grid grid-cols-3 gap-4">
        <div class="rounded-xl border border-gray-200 bg-white px-4 py-3 flex items-center gap-3">
          <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-indigo-50">
            <FeatherIcon name="users" class="h-4 w-4 text-indigo-600" />
          </div>
          <div>
            <p class="text-xl font-semibold text-gray-900">{{ m.active_reps ?? 0 }}</p>
            <p class="text-xs text-gray-400">Active reps</p>
          </div>
        </div>
        <div class="rounded-xl border border-gray-200 bg-white px-4 py-3 flex items-center gap-3">
          <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-green-50">
            <FeatherIcon name="user-check" class="h-4 w-4 text-green-600" />
          </div>
          <div>
            <p class="text-xl font-semibold text-gray-900">{{ m.new_customers ?? 0 }}</p>
            <p class="text-xs text-gray-400">New customers</p>
          </div>
        </div>
        <div class="rounded-xl border border-gray-200 bg-white px-4 py-3 flex items-center gap-3">
          <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-50">
            <FeatherIcon name="file-text" class="h-4 w-4 text-blue-600" />
          </div>
          <div>
            <p class="text-xl font-semibold text-gray-900">{{ m.forms_submitted ?? 0 }}</p>
            <p class="text-xs text-gray-400">Forms submitted</p>
          </div>
        </div>
      </div>

      <!-- Main content: leaderboard + recent visits + overdue -->
      <div class="grid grid-cols-1 gap-4 lg:grid-cols-3">

        <!-- Leaderboard -->
        <div class="lg:col-span-1 rounded-xl border border-gray-200 bg-white overflow-hidden">
          <div class="flex items-center justify-between border-b border-gray-100 px-4 py-3">
            <div>
              <p class="text-sm font-semibold text-gray-900">Rep Leaderboard</p>
              <p class="text-xs text-gray-400">Ranked by completed visits</p>
            </div>
          </div>
          <div v-if="leaderboard.length" class="divide-y divide-gray-50">
            <div v-for="(rep, i) in leaderboard" :key="rep.sales_person"
              class="flex items-center gap-3 px-4 py-3 cursor-pointer hover:bg-gray-50 transition-colors"
              @click="$router.push('/rep-activity-map')"
            >
              <span class="w-5 text-center text-xs font-bold shrink-0"
                :class="i===0?'text-yellow-500':i===1?'text-slate-400':i===2?'text-amber-600':'text-gray-300'">
                {{ i + 1 }}
              </span>
              <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-xs font-semibold text-indigo-700">
                {{ (rep.sales_person||'?').charAt(0).toUpperCase() }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-800 truncate">{{ rep.sales_person }}</p>
                <p class="text-xs text-gray-400">{{ rep.customers_visited }} customers</p>
              </div>
              <div class="flex gap-3 shrink-0 text-right">
                <div>
                  <p class="text-sm font-semibold text-gray-900">{{ rep.completed }}<span class="text-gray-300">/{{ rep.visits }}</span></p>
                  <p class="text-[10px] text-gray-400">Visits</p>
                </div>
                <div>
                  <p class="text-sm font-semibold text-gray-900">{{ fmt(rep.revenue) }}</p>
                  <p class="text-[10px] text-gray-400">Rev</p>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="flex flex-col items-center py-10 text-gray-400">
            <FeatherIcon name="users" class="h-8 w-8 mb-2" />
            <p class="text-sm">No activity yet</p>
          </div>
        </div>

        <!-- Recent Visits -->
        <div class="lg:col-span-1 rounded-xl border border-gray-200 bg-white overflow-hidden">
          <div class="flex items-center justify-between border-b border-gray-100 px-4 py-3">
            <div>
              <p class="text-sm font-semibold text-gray-900">Recent Visits</p>
              <p class="text-xs text-gray-400">Live field activity</p>
            </div>
            <router-link to="/visits" class="text-xs text-blue-500 hover:underline">View all →</router-link>
          </div>
          <div v-if="recentVisits.length" class="divide-y divide-gray-50">
            <div v-for="v in recentVisits" :key="v.name"
              class="flex items-center gap-3 px-4 py-3 cursor-pointer hover:bg-gray-50 transition-colors"
              @click="$router.push('/visits/'+v.name)"
            >
              <div class="h-2 w-2 shrink-0 rounded-full"
                :class="v.status==='In Progress'?'bg-green-500':v.status==='Completed'?'bg-blue-400':v.status==='Open'?'bg-gray-300':'bg-red-400'" />
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-800 truncate">{{ v.customer }}</p>
                <p class="text-xs text-gray-400 truncate">
                  {{ v.sales_person }}
                  <span v-if="v.custom_location_area || v.custom_location_city">
                    · {{ [v.custom_location_area, v.custom_location_city].filter(Boolean).join(', ') }}
                  </span>
                </p>
              </div>
              <div class="shrink-0 text-right">
                <StatusBadge :status="v.status" />
                <p class="text-[10px] text-gray-400 mt-0.5">{{ fmtDate(v.visit_date) }}</p>
              </div>
            </div>
          </div>
          <div v-else class="flex flex-col items-center py-10 text-gray-400">
            <FeatherIcon name="map-pin" class="h-8 w-8 mb-2" />
            <p class="text-sm">No visits yet</p>
          </div>
        </div>

        <!-- Overdue customers -->
        <div class="lg:col-span-1 rounded-xl border border-gray-200 bg-white overflow-hidden">
          <div class="flex items-center justify-between border-b border-gray-100 px-4 py-3">
            <div>
              <p class="text-sm font-semibold text-gray-900">Overdue Visits</p>
              <p class="text-xs text-gray-400">Customers past due date</p>
            </div>
            <router-link to="/customer-map?filter=overdue" class="text-xs text-red-500 hover:underline">
              View map →
            </router-link>
          </div>
          <div v-if="overdueCustomers.length" class="divide-y divide-gray-50">
            <div v-for="c in overdueCustomers" :key="c.name"
              class="flex items-center gap-3 px-4 py-3 cursor-pointer hover:bg-gray-50 transition-colors"
              @click="$router.push('/customers/'+c.name)"
            >
              <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-red-100 text-xs font-semibold text-red-600">
                {{ (c.customer_name||'?').charAt(0).toUpperCase() }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-800 truncate">{{ c.customer_name }}</p>
                <p class="text-xs text-gray-400 truncate">
                  {{ c.custom_sfa_rep || 'No rep' }}
                  <span v-if="c.territory"> · {{ c.territory }}</span>
                </p>
              </div>
              <div class="shrink-0 text-right">
                <p class="text-xs font-medium text-red-600">{{ daysOverdue(c.custom_next_visit_due) }}d overdue</p>
                <p class="text-[10px] text-gray-400">Due {{ fmtDate(c.custom_next_visit_due) }}</p>
              </div>
            </div>
          </div>
          <div v-else class="flex flex-col items-center py-10 text-gray-400">
            <FeatherIcon name="check-circle" class="h-8 w-8 mb-2 text-green-400" />
            <p class="text-sm text-green-600">No overdue customers</p>
          </div>
        </div>
      </div>

      <!-- Live Rep Map — managers/admins only -->
      <LiveRepMap v-if="auth.isManager || auth.isAdmin" />

      <!-- Visit trend (7 days) -->
      <div class="rounded-xl border border-gray-200 bg-white overflow-hidden">
        <div class="border-b border-gray-100 px-4 py-3">
          <p class="text-sm font-semibold text-gray-900">Visit Trend</p>
          <p class="text-xs text-gray-400">Last 7 days — completed vs planned</p>
        </div>
        <div class="px-4 py-4">
          <div v-if="trend.length" class="flex items-end gap-2 h-28">
            <div v-for="d in trend" :key="d.date"
              class="group relative flex-1 flex flex-col items-center gap-1 cursor-default"
            >
              <!-- Tooltip — positioned relative to each bar column -->
              <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-20
                hidden group-hover:block pointer-events-none"
                style="white-space:nowrap"
              >
                <div class="rounded-lg bg-gray-900 text-white px-2.5 py-1.5 text-xs shadow-xl">
                  <p class="font-medium">{{ dayjsFmt(d.date, 'ddd D MMM') }}</p>
                  <p class="text-blue-300">{{ d.completed }} completed</p>
                  <p class="text-gray-400">{{ d.total }} planned</p>
                  <p v-if="d.total > 0" class="text-gray-400">
                    {{ Math.round(d.completed / d.total * 100) }}% rate
                  </p>
                </div>
                <div class="mx-auto w-0 h-0 border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-gray-900" />
              </div>

              <div class="w-full flex flex-col justify-end" style="height: 80px">
                <div class="w-full rounded-t-sm bg-gray-100 relative overflow-hidden"
                  :style="{ height: barHeight(d.total) + 'px' }"
                >
                  <div class="absolute bottom-0 left-0 right-0 bg-blue-400 rounded-t-sm transition-all"
                    :style="{ height: (d.total > 0 ? (d.completed / d.total) * 100 : 0) + '%' }"
                  />
                </div>
              </div>
              <p class="text-[9px] text-gray-400">{{ fmtDay(d.date) }}</p>
            </div>
          </div>
          <div v-else class="h-28 flex items-center justify-center text-sm text-gray-400">
            No visit data yet
          </div>
          <div class="flex items-center gap-4 mt-3 text-xs text-gray-400">
            <span class="flex items-center gap-1.5"><span class="inline-block h-2.5 w-2.5 rounded-sm bg-blue-400" /> Completed</span>
            <span class="flex items-center gap-1.5"><span class="inline-block h-2.5 w-2.5 rounded-sm bg-gray-100 border border-gray-200" /> Planned</span>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { call } from '@/utils/frappe'
import { formatCurrency } from '@/utils/currency'
import Btn from '@/components/ui/Btn.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import MetricCard from '@/components/ui/MetricCard.vue'
import dayjs from 'dayjs'
import LiveRepMap from '@/components/ui/LiveRepMap.vue'
import { auth } from '@/utils/auth'

const period = ref('today')
const loading = ref(false)
const m = ref({})
const leaderboard = ref([])
const recentVisits = ref([])
const overdueCustomers = ref([])
const trend = ref([])

const periods = [
  { label: 'Today', value: 'today' },
  { label: 'This Week', value: 'week' },
  { label: 'This Month', value: 'month' },
]

const today = dayjs().format('dddd, D MMMM YYYY')
const hour = new Date().getHours()
const greeting = hour < 12 ? 'morning' : hour < 17 ? 'afternoon' : 'evening'
const firstName = computed(() => {
  const name = window.frappe_boot?.user?.full_name || window.frappe_boot?.user?.name || ''
  return name.split(' ')[0] || 'there'
})

const periodLabel = computed(() => ({
  today: "Today's summary",
  week: 'This week',
  month: 'This month',
}[period.value]))

const completedStr = computed(() => {
  const c = m.value.completed_visits ?? 0
  const t = m.value.total_visits ?? 0
  return t > 0 ? `${c}/${t}` : String(c)
})

const maxTrend = computed(() => Math.max(...trend.value.map(d => d.total), 1))
const barHeight = (total) => Math.max(4, Math.round((total / maxTrend.value) * 72))

async function refresh() {
  loading.value = true
  try {
    const [dash, lb, rv, ov, tr] = await Promise.all([
      call('sfa_core.api.dashboard.get_dashboard_data', { period: period.value }),
      call('sfa_core.api.dashboard.get_leaderboard', { period: period.value }),
      call('sfa_core.api.dashboard.get_recent_visits', { limit: 8 }),
      call('sfa_core.api.dashboard.get_overdue_customers', { limit: 8 }),
      call('sfa_core.api.dashboard.get_visit_trend', { days: 7 }),
    ])
    m.value = dash.message || {}
    leaderboard.value = lb.message || []
    recentVisits.value = rv.message || []
    overdueCustomers.value = ov.message || []
    trend.value = tr.message || []
  } catch (e) {
    console.error('Dashboard load failed', e)
  } finally {
    loading.value = false
  }
}

const fmt = (v) => formatCurrency(v || 0)
const dayjsFmt = (d, f) => dayjs(d).format(f)
const fmtDate = (d) => d ? dayjs(d).format('D MMM') : '—'
const fmtDay = (d) => d ? dayjs(d).format('dd')[0] : ''
const daysOverdue = (d) => d ? dayjs().diff(dayjs(d), 'day') : 0

onMounted(refresh)
</script>
