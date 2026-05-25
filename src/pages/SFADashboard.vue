<template>
  <div class="sfa-dashboard sfa-desk">
    <div class="dashboard-header">
      <div class="header-left">
        <h1>SFA Dashboard</h1>
        <p class="header-date">{{ today }}</p>
      </div>
      <div class="header-right">
        <div class="header-filters">
          <select v-model="periodFilter" class="period-select">
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="quarter">This Quarter</option>
          </select>
          <select v-model="territoryFilter" class="territory-select">
            <option value="">All Territories</option>
            <option v-for="t in territories" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>
        <button class="sfa-btn sfa-btn--primary" @click="refreshAll" :disabled="loading">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M1 7C1 3.686 3.686 1 7 1c2.21 0 4.21 1.07 5.42 2.79L13 2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M13 2V5M13 2H10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M13 7c0 3.314-2.686 6-6 6-2.21 0-4.21-1.07-5.42-2.79L1 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M1 12V9M1 12H4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <div class="metrics-grid">
      <MetricCard
        label="Active Visits"
        :value="activeVisits"
        subtitle="In progress now"
        :trend="visitTrend"
        :progress="visitTargetProgress"
        size="lg"
      />
      <MetricCard
        label="Orders Today"
        :value="ordersToday"
        subtitle="Carton quantities"
        :trend="orderTrend"
        :progress="orderTargetProgress"
        size="lg"
      />
      <MetricCard
        label="Revenue"
        :value="revenueToday"
        subtitle="UGX collected"
        :trend="revenueTrend"
        prefix="UGX "
        size="lg"
      />
      <MetricCard
        label="Payments"
        :value="paymentsToday"
        subtitle="Collections"
        :trend="paymentTrend"
        prefix="UGX "
        size="lg"
      />
      <MetricCard
        label="Reps Active"
        :value="repsOnline + '/' + totalReps"
        subtitle="Online now"
        :progress="repsProgress"
        size="md"
      />
      <MetricCard
        label="Compliance"
        :value="complianceRate + '%'"
        subtitle="Beat plan adherence"
        :progress="complianceRate"
        size="md"
      />
    </div>

    <div class="dashboard-grid">
      <div class="dashboard-left">
        <div class="sfa-card">
          <div class="sfa-card-header">
            <div>
              <div class="sfa-card-title">Live Activity</div>
              <div class="sfa-card-subtitle">Real-time field updates</div>
            </div>
            <div class="live-indicator">
              <span class="live-dot"></span>
              Live
            </div>
          </div>
          <div class="sfa-card-body" style="padding: 0;">
            <TimelineFeed :items="activityFeed" />
          </div>
        </div>

        <div class="sfa-card" style="margin-top: 16px;">
          <div class="sfa-card-header">
            <div>
              <div class="sfa-card-title">Rep Performance</div>
              <div class="sfa-card-subtitle">Today leaderboard</div>
            </div>
          </div>
          <div class="sfa-card-body" style="padding: 0;">
            <div class="leaderboard-list">
              <div
                v-for="(rep, index) in leaderboardData"
                :key="rep.name"
                class="leaderboard-item"
                :class="{ 'top-three': index < 3 }"
              >
                <div class="leaderboard-rank">{{ index + 1 }}</div>
                <div class="leaderboard-avatar">{{ rep.name ? rep.name.charAt(0) : '?' }}</div>
                <div class="leaderboard-info">
                  <div class="leaderboard-name">{{ rep.name }}</div>
                  <div class="leaderboard-territory">{{ rep.territory }}</div>
                </div>
                <div class="leaderboard-stats">
                  <div class="lb-stat">
                    <span class="lb-stat-value">{{ rep.visits }}</span>
                    <span class="lb-stat-label">Visits</span>
                  </div>
                  <div class="lb-stat">
                    <span class="lb-stat-value">{{ formatCurrency(rep.revenue) }}</span>
                    <span class="lb-stat-label">Revenue</span>
                  </div>
                  <div class="lb-stat">
                    <span class="lb-stat-value">{{ rep.points }}</span>
                    <span class="lb-stat-label">Points</span>
                  </div>
                </div>
                <div v-if="index < 3" class="leaderboard-badge">
                  <svg v-if="index === 0" width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <circle cx="10" cy="10" r="9" fill="#FFD700" stroke="#DAA520" stroke-width="1"/>
                    <text x="10" y="14" text-anchor="middle" fill="#333" font-size="10" font-weight="bold">1</text>
                  </svg>
                  <svg v-else-if="index === 1" width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <circle cx="10" cy="10" r="9" fill="#C0C0C0" stroke="#A0A0A0" stroke-width="1"/>
                    <text x="10" y="14" text-anchor="middle" fill="#333" font-size="10" font-weight="bold">2</text>
                  </svg>
                  <svg v-else width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <circle cx="10" cy="10" r="9" fill="#CD7F32" stroke="#B87333" stroke-width="1"/>
                    <text x="10" y="14" text-anchor="middle" fill="#333" font-size="10" font-weight="bold">3</text>
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="dashboard-right">
        <div class="sfa-card">
          <div class="sfa-card-header">
            <div>
              <div class="sfa-card-title">Field Map</div>
              <div class="sfa-card-subtitle">Live rep locations</div>
            </div>
          </div>
          <div class="sfa-card-body" style="padding: 0; height: 400px;">
            <MapView
              :markers="mapMarkers"
              @select="onMapSelect"
              @refresh="loadMapData"
            />
          </div>
        </div>

        <div class="rep-cards-scroll">
          <RepActivityCard
            v-for="rep in activeReps"
            :key="rep.name"
            :rep="rep"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import MetricCard from '../components/MetricCard.vue';
import TimelineFeed from '../components/TimelineFeed.vue';
import MapView from '../components/MapView.vue';
import RepActivityCard from '../components/RepActivityCard.vue';
import { useSFAData, useRealtime } from '../composables/useFrappe';

const { loadVisits, loadOrders, loadPayments, loadReps, loadLeaderboard, visits, orders, payments, reps, leaderboard, loading } = useSFAData();
const { subscribeToVisits, subscribeToOrders, subscribeToPayments, notifications } = useRealtime();

const periodFilter = ref('today');
const territoryFilter = ref('');
const territories = ref(['Kampala', 'Entebbe', 'Jinja', 'Mbarara', 'Gulu']);
const today = ref(new Date().toLocaleDateString('en-UG', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }));

const activeVisits = computed(() => visits.value.filter(v => v.status === 'In Progress').length);
const ordersToday = computed(() => orders.value.length);
const revenueToday = computed(() => orders.value.reduce((sum, o) => sum + (o.grand_total || 0), 0));
const paymentsToday = computed(() => payments.value.reduce((sum, p) => sum + (p.amount || 0), 0));
const repsOnline = computed(() => reps.value.filter(r => r.online_status === 'online').length);
const totalReps = computed(() => reps.value.length);
const repsProgress = computed(() => totalReps.value > 0 ? (repsOnline.value / totalReps.value) * 100 : 0);
const complianceRate = ref(87);
const visitTrend = ref(12);
const orderTrend = ref(8);
const revenueTrend = ref(15);
const paymentTrend = ref(-3);
const visitTargetProgress = ref(72);
const orderTargetProgress = ref(65);

const activityFeed = computed(() => {
  return [...notifications.value].slice(0, 20);
});

const mapMarkers = computed(() => {
  return reps.value.map(r => ({
    id: r.name,
    name: r.name,
    lat: r.current_lat,
    lng: r.current_lng,
    type: 'rep',
    status: r.online_status
  }));
});

const activeReps = computed(() => reps.value.filter(r => r.online_status !== 'offline'));
const leaderboardData = computed(() => leaderboard.value);

let refreshInterval;

onMounted(async () => {
  await refreshAll();
  subscribeToVisits();
  subscribeToOrders();
  subscribeToPayments();
  refreshInterval = setInterval(refreshAll, 30000);
});

onUnmounted(() => {
  if (refreshInterval) clearInterval(refreshInterval);
});

async function refreshAll() {
  await Promise.all([
    loadVisits(),
    loadOrders(),
    loadPayments(),
    loadReps(),
    loadLeaderboard(periodFilter.value)
  ]);
}

function onMapSelect(marker) {
  console.log('Selected marker:', marker);
}

function loadMapData() {
  loadReps();
}

function formatCurrency(val) {
  if (!val) return 'UGX 0';
  return new Intl.NumberFormat('en-UG', { style: 'currency', currency: 'UGX', maximumFractionDigits: 0 }).format(val);
}
</script>

<style scoped>
.sfa-dashboard {
  padding: 20px;
  min-height: 100vh;
}
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.header-left h1 {
  font-size: 24px;
  font-weight: 700;
  color: #1f272e;
  margin: 0;
}
.header-date {
  font-size: 13px;
  color: #687178;
  margin-top: 4px;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.header-filters {
  display: flex;
  gap: 8px;
}
.period-select, .territory-select {
  padding: 6px 12px;
  border: 1px solid #e2e6e9;
  border-radius: 6px;
  font-size: 13px;
  background: white;
}
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.dashboard-left {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.dashboard-right {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.live-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: #28a745;
  padding: 4px 10px;
  background: #e8f5e9;
  border-radius: 20px;
}
.live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #28a745;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
.leaderboard-list {
  padding: 8px 0;
}
.leaderboard-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  border-bottom: 1px solid #f0f2f4;
  transition: background 0.15s;
}
.leaderboard-item:hover {
  background: #f8f9fa;
}
.leaderboard-item.top-three {
  background: linear-gradient(90deg, rgba(255,215,0,0.05) 0%, transparent 100%);
}
.leaderboard-rank {
  width: 28px;
  text-align: center;
  font-weight: 700;
  font-size: 14px;
  color: #a0a0a0;
}
.leaderboard-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2490EF 0%, #1a7ad1 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 12px;
}
.leaderboard-info {
  flex: 1;
  min-width: 0;
}
.leaderboard-name {
  font-weight: 600;
  font-size: 13px;
  color: #1f272e;
}
.leaderboard-territory {
  font-size: 11px;
  color: #a0a0a0;
}
.leaderboard-stats {
  display: flex;
  gap: 16px;
}
.lb-stat {
  text-align: center;
}
.lb-stat-value {
  display: block;
  font-size: 13px;
  font-weight: 700;
  color: #1f272e;
}
.lb-stat-label {
  font-size: 10px;
  color: #a0a0a0;
  text-transform: uppercase;
}
.leaderboard-badge {
  margin-left: 8px;
}
.rep-cards-scroll {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 500px;
  overflow-y: auto;
}
@media (max-width: 1200px) {
  .metrics-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}
</style>
