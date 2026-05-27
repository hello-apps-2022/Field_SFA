<template>
  <div class="p-6 space-y-5">

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-base font-semibold text-gray-900">Good {{ greeting }}, {{ firstName }}</h2>
        <p class="text-sm text-gray-400 mt-0.5">{{ today }}</p>
      </div>
      <div class="flex items-center gap-2">
        <select
          v-model="period"
          class="h-9 rounded-md border border-gray-200 bg-white px-3 text-sm focus:border-gray-400 focus:outline-none"
          @change="refresh"
        >
          <option value="today">Today</option>
          <option value="week">This Week</option>
          <option value="month">This Month</option>
        </select>
        <button
          class="flex h-9 items-center gap-1.5 rounded-md border border-gray-200 bg-white px-3 text-sm text-gray-600 hover:bg-gray-50 transition-colors"
          :disabled="loading"
          @click="refresh"
        >
          <FeatherIcon name="refresh-cw" class="h-3.5 w-3.5" :class="loading ? 'animate-spin' : ''" />
          Refresh
        </button>
      </div>
    </div>

    <!-- Metric tiles -->
    <div class="grid grid-cols-2 gap-3 lg:grid-cols-3 xl:grid-cols-6">
      <MetricTile label="Active Visits"    :value="metrics.active_visits ?? '—'"       icon="map-pin"     color="blue"    subtitle="In progress" />
      <MetricTile label="Completed Today"  :value="metrics.completed_visits ?? '—'"    icon="check-circle" color="green"   subtitle="Visits closed" />
      <MetricTile label="Orders Today"     :value="metrics.orders_today ?? '—'"         icon="shopping-cart" color="purple" subtitle="Cartons" />
      <MetricTile label="Revenue"          :value="formatUGX(metrics.revenue_today)"   icon="trending-up" color="emerald" subtitle="UGX collected" />
      <MetricTile label="Collections"      :value="formatUGX(metrics.payments_today)"  icon="credit-card" color="orange"  subtitle="Payments" />
      <MetricTile label="Compliance"       :value="(metrics.compliance_rate ?? 0) + '%'" icon="bar-chart-2" color="teal" subtitle="Beat plan adherence" />
    </div>

    <!-- Two-column -->
    <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">

      <!-- Leaderboard -->
      <div class="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden">
        <div class="flex items-center justify-between border-b border-gray-100 px-4 py-3">
          <div>
            <p class="text-sm font-semibold text-gray-900">Rep Leaderboard</p>
            <p class="text-xs text-gray-400 mt-0.5">Ranked by visits + revenue</p>
          </div>
          <span class="rounded-full bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-600">
            {{ period === 'today' ? 'Today' : period === 'week' ? 'This Week' : 'This Month' }}
          </span>
        </div>
        <div v-if="leaderboard.length" class="divide-y divide-gray-50">
          <div v-for="(rep, i) in leaderboard" :key="rep.sales_person" class="flex items-center gap-3 px-4 py-3">
            <span class="w-5 text-center text-xs font-bold" :class="rankColor(i)">{{ i + 1 }}</span>
            <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-100 text-xs font-semibold text-gray-600">
              {{ (rep.sales_person || '?').charAt(0).toUpperCase() }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-800 truncate">{{ rep.sales_person }}</p>
              <p class="text-xs text-gray-400 truncate">{{ rep.territory || '—' }}</p>
            </div>
            <div class="flex gap-4 text-right shrink-0">
              <div>
                <p class="text-sm font-semibold text-gray-900">{{ rep.visits }}</p>
                <p class="text-[10px] uppercase tracking-wide text-gray-400">Visits</p>
              </div>
              <div>
                <p class="text-sm font-semibold text-gray-900">{{ formatUGX(rep.revenue) }}</p>
                <p class="text-[10px] uppercase tracking-wide text-gray-400">Revenue</p>
              </div>
              <div>
                <p class="text-sm font-semibold text-gray-900">{{ rep.points }}</p>
                <p class="text-[10px] uppercase tracking-wide text-gray-400">Pts</p>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="flex flex-col items-center justify-center py-12 text-gray-400">
          <FeatherIcon name="users" class="h-8 w-8 mb-2" />
          <p class="text-sm">No data yet</p>
        </div>
      </div>

      <!-- Recent Visits -->
      <div class="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden">
        <div class="flex items-center justify-between border-b border-gray-100 px-4 py-3">
          <div>
            <p class="text-sm font-semibold text-gray-900">Recent Visits</p>
            <p class="text-xs text-gray-400 mt-0.5">Live field activity</p>
          </div>
          <router-link to="/visits" class="text-xs text-blue-500 hover:underline">View all →</router-link>
        </div>
        <div v-if="recentVisits.length" class="divide-y divide-gray-50">
          <div
            v-for="visit in recentVisits"
            :key="visit.name"
            class="flex items-center gap-3 px-4 py-3 cursor-pointer hover:bg-gray-50 transition-colors"
            @click="$router.push('/visits/' + visit.name)"
          >
            <div class="h-2 w-2 shrink-0 rounded-full" :class="statusDot(visit.status)" />
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-800 truncate">{{ visit.customer }}</p>
              <p class="text-xs text-gray-400 truncate">{{ visit.sales_person }} · {{ formatDate(visit.visit_date) }}</p>
            </div>
            <span class="rounded-full px-2 py-0.5 text-xs font-medium shrink-0" :class="statusClass(visit.status)">
              {{ visit.status }}
            </span>
          </div>
        </div>
        <div v-else class="flex flex-col items-center justify-center py-12 text-gray-400">
          <FeatherIcon name="map-pin" class="h-8 w-8 mb-2" />
          <p class="text-sm">No visits today</p>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import MetricTile from '@/components/ui/MetricTile.vue'
import dayjs from 'dayjs'

const period = ref('today')
const loading = ref(false)
const metrics = ref({})
const leaderboard = ref([])
const recentVisits = ref([])

const today = dayjs().format('dddd, D MMMM YYYY')
const hour = new Date().getHours()
const greeting = hour < 12 ? 'morning' : hour < 17 ? 'afternoon' : 'evening'
const firstName = computed(() => {
  const u = window.frappe?.session?.user || ''
  return u.split('@')[0].split('.')[0] || 'there'
})

async function refresh() {
  loading.value = true
  try {
    const [dashRes, lbRes, visitsRes] = await Promise.all([
      frappe.call({ method: 'sfa_core.api.dashboard.get_dashboard_data', args: { period: period.value } }),
      frappe.call({ method: 'sfa_core.api.dashboard.get_leaderboard', args: { period: period.value } }),
      frappe.call({
        method: 'frappe.client.get_list',
        args: {
          doctype: 'SFA Visit',
          fields: ['name', 'customer', 'sales_person', 'visit_date', 'status'],
          order_by: 'modified desc',
          limit: 8,
        }
      }),
    ])
    metrics.value = dashRes.message || {}
    leaderboard.value = lbRes.message || []
    recentVisits.value = visitsRes.message || []
  } catch (e) {
    console.error('Dashboard load error:', e)
  } finally {
    loading.value = false
  }
}

onMounted(refresh)

const formatUGX = (v) => {
  if (!v) return 'UGX 0'
  if (v >= 1_000_000) return `UGX ${(v / 1_000_000).toFixed(1)}M`
  if (v >= 1_000) return `UGX ${(v / 1_000).toFixed(0)}K`
  return `UGX ${v}`
}

const formatDate = (d) => d ? dayjs(d).format('D MMM') : '—'
const rankColor = (i) => i === 0 ? 'text-yellow-500' : i === 1 ? 'text-slate-400' : i === 2 ? 'text-amber-600' : 'text-gray-400'
const statusDot = (s) => ({ 'In Progress': 'bg-green-500', 'Completed': 'bg-blue-400', 'Planned': 'bg-gray-300', 'Cancelled': 'bg-red-400' })[s] || 'bg-gray-300'
const statusClass = (s) => ({ 'In Progress': 'bg-green-50 text-green-700', 'Completed': 'bg-blue-50 text-blue-700', 'Planned': 'bg-gray-100 text-gray-600', 'Cancelled': 'bg-red-50 text-red-700' })[s] || 'bg-gray-100 text-gray-600'
</script>
