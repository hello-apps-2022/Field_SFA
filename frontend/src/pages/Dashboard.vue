<template>
  <div class="flex h-full flex-col">
    <PageHeader title="Dashboard">
      <select v-model="period" class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none" @change="refresh">
        <option value="today">Today</option>
        <option value="week">This Week</option>
        <option value="month">This Month</option>
      </select>
      <Btn icon="refresh-cw" :class="loading ? '[&_svg]:animate-spin' : ''" @click="refresh">Refresh</Btn>
    </PageHeader>

    <div class="flex-1 overflow-auto p-5 space-y-5">
      <!-- Greeting -->
      <div>
        <h2 class="text-base font-semibold text-gray-900">Good {{ greeting }}, {{ firstName }}</h2>
        <p class="text-sm text-gray-400 mt-0.5">{{ today }}</p>
      </div>

      <!-- Metrics -->
      <div class="grid grid-cols-2 gap-3 lg:grid-cols-3 xl:grid-cols-6">
        <MetricCard label="Active Visits"    :value="m.active_visits ?? '—'"       icon="map-pin"      color="blue"    sub="In progress" />
        <MetricCard label="Completed Today"  :value="m.completed_visits ?? '—'"    icon="check-circle" color="green"   sub="Visits closed" />
        <MetricCard label="Orders Today"     :value="m.orders_today ?? '—'"         icon="shopping-cart" color="purple" sub="Cartons" />
        <MetricCard label="Revenue"          :value="fmt(m.revenue_today)"          icon="trending-up"  color="emerald" sub="UGX collected" />
        <MetricCard label="Collections"      :value="fmt(m.payments_today)"         icon="credit-card"  color="orange"  sub="Payments" />
        <MetricCard label="Compliance"       :value="(m.compliance_rate ?? 0) + '%'" icon="bar-chart-2" color="teal"   sub="Beat plan" />
      </div>

      <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <!-- Leaderboard -->
        <div class="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden">
          <div class="flex items-center justify-between border-b border-gray-100 px-4 py-3">
            <div><p class="text-sm font-semibold text-gray-900">Rep Leaderboard</p><p class="text-xs text-gray-400">Ranked by visits + revenue</p></div>
          </div>
          <div v-if="leaderboard.length" class="divide-y divide-gray-50">
            <div v-for="(rep, i) in leaderboard" :key="rep.sales_person" class="flex items-center gap-3 px-4 py-3">
              <span class="w-5 text-center text-xs font-bold" :class="['text-yellow-500','text-slate-400','text-amber-600'][i] || 'text-gray-400'">{{ i+1 }}</span>
              <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gray-200 text-xs font-semibold text-gray-600">{{ (rep.sales_person||'?').charAt(0).toUpperCase() }}</div>
              <div class="flex-1 min-w-0"><p class="text-sm font-medium text-gray-800 truncate">{{ rep.sales_person }}</p></div>
              <div class="flex gap-3 text-right shrink-0">
                <div><p class="text-sm font-semibold text-gray-900">{{ rep.visits }}</p><p class="text-[10px] text-gray-400">Visits</p></div>
                <div><p class="text-sm font-semibold text-gray-900">{{ fmt(rep.revenue) }}</p><p class="text-[10px] text-gray-400">Rev</p></div>
              </div>
            </div>
          </div>
          <div v-else class="flex flex-col items-center py-12 text-gray-400">
            <FeatherIcon name="users" class="h-8 w-8 mb-2" />
            <p class="text-sm">No data yet</p>
          </div>
        </div>

        <!-- Recent visits -->
        <div class="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden">
          <div class="flex items-center justify-between border-b border-gray-100 px-4 py-3">
            <div><p class="text-sm font-semibold text-gray-900">Recent Visits</p><p class="text-xs text-gray-400">Live activity</p></div>
            <router-link to="/visits" class="text-xs text-blue-500 hover:underline">View all →</router-link>
          </div>
          <div v-if="recentVisits.length" class="divide-y divide-gray-50">
            <div v-for="v in recentVisits" :key="v.name" class="flex items-center gap-3 px-4 py-3 cursor-pointer hover:bg-gray-50" @click="$router.push('/visits/'+v.name)">
              <div class="h-2 w-2 shrink-0 rounded-full" :class="{'bg-green-500':v.status==='In Progress','bg-blue-400':v.status==='Completed','bg-gray-300':v.status==='Planned'}"></div>
              <div class="flex-1 min-w-0"><p class="text-sm font-medium text-gray-800 truncate">{{ v.customer }}</p><p class="text-xs text-gray-400">{{ v.sales_person }} · {{ fmtDate(v.visit_date) }}</p></div>
              <StatusBadge :status="v.status" />
            </div>
          </div>
          <div v-else class="flex flex-col items-center py-12 text-gray-400">
            <FeatherIcon name="map-pin" class="h-8 w-8 mb-2" /><p class="text-sm">No visits today</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { call, getList } from '@/utils/frappe'
import PageHeader from '@/components/ui/PageHeader.vue'
import Btn from '@/components/ui/Btn.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import MetricCard from '@/components/ui/MetricCard.vue'
import dayjs from 'dayjs'
import { formatCurrency } from '@/utils/currency'

const period = ref('today')
const loading = ref(false)
const m = ref({})
const leaderboard = ref([])
const recentVisits = ref([])

const today = dayjs().format('dddd, D MMMM YYYY')
const hour = new Date().getHours()
const greeting = hour < 12 ? 'morning' : hour < 17 ? 'afternoon' : 'evening'
const firstName = computed(() => (window.frappe_boot?.user?.name || '').split('@')[0].split('.')[0] || 'there')

async function refresh() {
  loading.value = true
  try {
    const [dash, lb, v] = await Promise.all([
      call('sfa_core.api.dashboard.get_dashboard_data', { period: period.value }),
      call('sfa_core.api.dashboard.get_leaderboard', { period: period.value }),
      getList('SFA Visit', { fields: ['name','customer','sales_person','visit_date','status'], orderBy: 'modified desc', limit: 8 }),
    ])
    m.value = dash.message || {}
    leaderboard.value = lb.message || []
    recentVisits.value = v
  } catch(e) { console.error(e) }
  finally { loading.value = false }
}

const fmt = (v) => !v ? 'UGX 0' : v >= 1e6 ? `UGX ${(v/1e6).toFixed(1)}M` : v >= 1e3 ? `UGX ${(v/1e3).toFixed(0)}K` : `UGX ${v}`
const fmtDate = (d) => d ? dayjs(d).format('D MMM') : '—'

onMounted(refresh)
</script>
