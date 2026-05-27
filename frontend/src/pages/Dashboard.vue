<template>
  <div class="p-6 space-y-6">

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-base font-semibold text-ink-gray-9">Good {{ greeting }}, {{ firstName }}</h2>
        <p class="text-sm text-ink-gray-5 mt-0.5">{{ today }}</p>
      </div>
      <div class="flex items-center gap-2">
        <FormControl
          type="select"
          v-model="period"
          :options="periodOptions"
          size="sm"
          class="w-32"
        />
        <Button size="sm" :loading="loading" @click="refresh">
          <template #prefix><FeatherIcon name="refresh-cw" class="h-3.5 w-3.5" /></template>
          Refresh
        </Button>
      </div>
    </div>

    <!-- Metric cards -->
    <div class="grid grid-cols-2 gap-3 lg:grid-cols-4 xl:grid-cols-6">
      <MetricTile
        label="Active Visits"
        :value="metrics.active_visits ?? '—'"
        icon="map-pin"
        color="blue"
        :subtitle="'In progress'"
      />
      <MetricTile
        label="Completed Today"
        :value="metrics.completed_visits ?? '—'"
        icon="check-circle"
        color="green"
        :subtitle="'Visits closed'"
      />
      <MetricTile
        label="Orders Today"
        :value="metrics.orders_today ?? '—'"
        icon="shopping-cart"
        color="purple"
        :subtitle="'Cartons'"
      />
      <MetricTile
        label="Revenue"
        :value="formatUGX(metrics.revenue_today)"
        icon="trending-up"
        color="emerald"
        :subtitle="'UGX collected'"
      />
      <MetricTile
        label="Collections"
        :value="formatUGX(metrics.payments_today)"
        icon="credit-card"
        color="orange"
        :subtitle="'Payments'"
      />
      <MetricTile
        label="Compliance"
        :value="(metrics.compliance_rate ?? 0) + '%'"
        icon="bar-chart-2"
        color="teal"
        :subtitle="'Beat plan adherence'"
      />
    </div>

    <!-- Two column layout -->
    <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">

      <!-- Leaderboard -->
      <div class="rounded-lg border border-outline-gray-2 bg-surface-white">
        <div class="flex items-center justify-between border-b border-outline-gray-2 px-4 py-3">
          <div>
            <p class="text-sm font-medium text-ink-gray-9">Rep Leaderboard</p>
            <p class="text-xs text-ink-gray-4 mt-0.5">Ranked by visits + revenue</p>
          </div>
          <Badge
            :label="period === 'today' ? 'Today' : period === 'week' ? 'This Week' : 'This Month'"
            variant="subtle"
          />
        </div>
        <div v-if="leaderboardRows.length" class="divide-y divide-outline-gray-1">
          <div
            v-for="(rep, i) in leaderboardRows"
            :key="rep.sales_person"
            class="flex items-center gap-3 px-4 py-3"
          >
            <span class="w-5 text-center text-xs font-bold" :class="rankColor(i)">{{ i + 1 }}</span>
            <Avatar :label="rep.sales_person" size="sm" />
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-ink-gray-8 truncate">{{ rep.sales_person }}</p>
              <p class="text-xs text-ink-gray-4 truncate">{{ rep.territory || '—' }}</p>
            </div>
            <div class="flex gap-4 text-right">
              <div>
                <p class="text-sm font-semibold text-ink-gray-9">{{ rep.visits }}</p>
                <p class="text-[10px] text-ink-gray-4 uppercase tracking-wide">Visits</p>
              </div>
              <div>
                <p class="text-sm font-semibold text-ink-gray-9">{{ formatUGX(rep.revenue) }}</p>
                <p class="text-[10px] text-ink-gray-4 uppercase tracking-wide">Revenue</p>
              </div>
              <div>
                <p class="text-sm font-semibold text-ink-gray-9">{{ rep.points }}</p>
                <p class="text-[10px] text-ink-gray-4 uppercase tracking-wide">Pts</p>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="flex flex-col items-center justify-center py-12 text-ink-gray-4">
          <FeatherIcon name="users" class="h-8 w-8 mb-2" />
          <p class="text-sm">No data yet</p>
        </div>
      </div>

      <!-- Recent visits -->
      <div class="rounded-lg border border-outline-gray-2 bg-surface-white">
        <div class="flex items-center justify-between border-b border-outline-gray-2 px-4 py-3">
          <div>
            <p class="text-sm font-medium text-ink-gray-9">Recent Visits</p>
            <p class="text-xs text-ink-gray-4 mt-0.5">Live field activity</p>
          </div>
          <router-link to="/visits" class="text-xs text-ink-blue-3 hover:underline">View all →</router-link>
        </div>
        <div v-if="recentVisits.length" class="divide-y divide-outline-gray-1">
          <div
            v-for="visit in recentVisits"
            :key="visit.name"
            class="flex items-center gap-3 px-4 py-3 hover:bg-surface-gray-1 cursor-pointer"
            @click="$router.push('/visits/' + visit.name)"
          >
            <div
              class="h-2 w-2 shrink-0 rounded-full"
              :class="statusDot(visit.status)"
            />
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-ink-gray-8 truncate">{{ visit.customer }}</p>
              <p class="text-xs text-ink-gray-4 truncate">{{ visit.sales_person }} · {{ formatDate(visit.visit_date) }}</p>
            </div>
            <Badge
              :label="visit.status"
              :variant="statusVariant(visit.status)"
              size="sm"
            />
          </div>
        </div>
        <div v-else class="flex flex-col items-center justify-center py-12 text-ink-gray-4">
          <FeatherIcon name="map-pin" class="h-8 w-8 mb-2" />
          <p class="text-sm">No visits today</p>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { createResource, createListResource } from 'frappe-ui'
import MetricTile from '@/components/ui/MetricTile.vue'
import dayjs from 'dayjs'

const period = ref('today')
const loading = ref(false)
const metrics = ref({})
const leaderboardRows = ref([])

const periodOptions = [
  { label: 'Today', value: 'today' },
  { label: 'This Week', value: 'week' },
  { label: 'This Month', value: 'month' },
]

const visitsList = createListResource({
  doctype: 'SFA Visit',
  fields: ['name', 'customer', 'sales_person', 'visit_date', 'status'],
  orderBy: 'visit_date desc',
  pageLength: 10,
  auto: false,
})

const recentVisits = computed(() => visitsList.data || [])

const today = dayjs().format('dddd, D MMMM YYYY')
const hour = new Date().getHours()
const greeting = hour < 12 ? 'morning' : hour < 17 ? 'afternoon' : 'evening'
const firstName = computed(() => {
  const user = window.frappe?.session?.user || ''
  return user.split('@')[0].split('.')[0]
})

async function refresh() {
  loading.value = true
  try {
    const [dash, lb] = await Promise.all([
      frappe.call({ method: 'sfa_core.api.dashboard.get_dashboard_data', args: { period: period.value } }),
      frappe.call({ method: 'sfa_core.api.dashboard.get_leaderboard', args: { period: period.value } }),
    ])
    metrics.value = dash.message || {}
    leaderboardRows.value = lb.message || []
    await visitsList.reload()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(refresh)

const formatUGX = (val) => {
  if (!val) return 'UGX 0'
  if (val >= 1_000_000) return `UGX ${(val / 1_000_000).toFixed(1)}M`
  if (val >= 1_000) return `UGX ${(val / 1_000).toFixed(0)}K`
  return `UGX ${val}`
}

const formatDate = (d) => d ? dayjs(d).format('D MMM') : '—'

const rankColor = (i) => i === 0 ? 'text-yellow-500' : i === 1 ? 'text-slate-400' : i === 2 ? 'text-amber-600' : 'text-ink-gray-4'

const statusDot = (s) => ({
  'In Progress': 'bg-green-500',
  'Completed': 'bg-blue-500',
  'Planned': 'bg-slate-300',
  'Cancelled': 'bg-red-400',
})[s] || 'bg-slate-300'

const statusVariant = (s) => ({
  'In Progress': 'success',
  'Completed': 'info',
  'Planned': 'subtle',
  'Cancelled': 'danger',
})[s] || 'subtle'
</script>
