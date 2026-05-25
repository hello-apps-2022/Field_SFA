<template>
  <div class="sfa-visits-page sfa-desk">
    <div class="page-header">
      <div class="header-left">
        <h1>Visits</h1>
        <p class="header-subtitle">{{ filteredVisits.length }} visits found</p>
      </div>
      <div class="header-right">
        <div class="filter-chips">
          <button
            v-for="filter in statusFilters"
            :key="filter.value"
            class="filter-chip"
            :class="{ active: activeStatusFilter === filter.value }"
            @click="activeStatusFilter = filter.value"
          >
            {{ filter.label }}
            <span class="chip-count">{{ filter.count }}</span>
          </button>
        </div>
        <button class="sfa-btn sfa-btn--primary" @click="showAddVisit = true">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M7 2v10M2 7h10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          Add Visit
        </button>
      </div>
    </div>

    <DataTable
      :data="filteredVisits"
      :columns="visitColumns"
      @refresh="loadVisitsData"
      @select="onVisitSelect"
      @edit="onVisitEdit"
    >
      <template #cell-status="{ row, value }">
        <span class="sfa-badge" :class="'sfa-badge--' + getStatusType(value)">
          <span class="sfa-badge-dot"></span>
          {{ value }}
        </span>
      </template>
      <template #cell-duration="{ value }">
        <span :class="{ 'text-warning': value && parseDuration(value) > 120 }">
          {{ value || 'N/A' }}
        </span>
      </template>
      <template #cell-gps_accuracy="{ value }">
        <span :class="getGPSClass(value)">{{ value }}m</span>
      </template>
    </DataTable>

    <div v-if="selectedVisit" class="slide-over" @click.self="selectedVisit = null">
      <div class="slide-over-content">
        <div class="slide-header">
          <h3>Visit Details</h3>
          <button class="sfa-btn sfa-btn--ghost sfa-btn--sm" @click="selectedVisit = null">Close</button>
        </div>
        <div class="slide-body">
          <VisitCard :visit="selectedVisit" :show-details="true" />
          <div class="visit-timeline">
            <h4>Activity Timeline</h4>
            <TimelineFeed :items="visitActivities" />
          </div>
          <div v-if="selectedVisit.order_value" class="visit-order">
            <h4>Order Summary</h4>
            <div class="order-summary">
              <div class="order-row">
                <span>Order Value</span>
                <span class="order-value">{{ formatCurrency(selectedVisit.order_value) }}</span>
              </div>
              <div class="order-row">
                <span>Payment Collected</span>
                <span class="order-value">{{ formatCurrency(selectedVisit.payment_collected) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import DataTable from '../components/DataTable.vue';
import VisitCard from '../components/VisitCard.vue';
import TimelineFeed from '../components/TimelineFeed.vue';
import { useSFAData } from '../composables/useFrappe';

const { loadVisits, visits, loading } = useSFAData();

const activeStatusFilter = ref('all');
const selectedVisit = ref(null);
const visitActivities = ref([]);
const showAddVisit = ref(false);

const statusFilters = computed(() => [
  { label: 'All', value: 'all', count: visits.value.length },
  { label: 'In Progress', value: 'In Progress', count: visits.value.filter(v => v.status === 'In Progress').length },
  { label: 'Completed', value: 'Completed', count: visits.value.filter(v => v.status === 'Completed').length },
  { label: 'Missed', value: 'Missed', count: visits.value.filter(v => v.status === 'Missed').length },
  { label: 'Pending', value: 'Pending', count: visits.value.filter(v => v.status === 'Pending').length },
]);

const filteredVisits = computed(() => {
  if (activeStatusFilter.value === 'all') return visits.value;
  return visits.value.filter(v => v.status === activeStatusFilter.value);
});

const visitColumns = [
  { key: 'name', label: 'Visit ID', sortable: true, width: '120px' },
  { key: 'customer', label: 'Customer', sortable: true },
  { key: 'rep', label: 'Rep', sortable: true, width: '120px' },
  { key: 'visit_date', label: 'Date', type: 'date', sortable: true, width: '120px' },
  { key: 'status', label: 'Status', type: 'badge', sortable: true, width: '120px' },
  { key: 'check_in_time', label: 'Check In', type: 'datetime', sortable: true, width: '150px' },
  { key: 'duration', label: 'Duration', sortable: true, width: '100px' },
  { key: 'gps_accuracy', label: 'GPS', sortable: true, width: '80px' },
  { key: 'order_value', label: 'Order', type: 'currency', sortable: true, width: '120px' },
];

onMounted(() => {
  loadVisitsData();
});

async function loadVisitsData() {
  await loadVisits();
}

function onVisitSelect(row) {
  selectedVisit.value = row;
  loadVisitActivities(row.name);
}

async function loadVisitActivities(visitName) {
  try {
    const response = await frappe.call({
      method: 'sfa_core.api.dashboard.get_visit_activities',
      args: { visit_name: visitName }
    });
    visitActivities.value = response.message || [];
  } catch (e) {
    visitActivities.value = [];
  }
}

function onVisitEdit(row) {
  frappe.set_route('Form', 'SFA Visit', row.name);
}

function getStatusType(status) {
  const s = String(status).toLowerCase();
  if (['completed', 'active', 'paid', 'approved'].indexOf(s) >= 0) return 'success';
  if (['pending', 'draft', 'in progress'].indexOf(s) >= 0) return 'warning';
  if (['cancelled', 'missed', 'overdue', 'unpaid'].indexOf(s) >= 0) return 'danger';
  return 'primary';
}

function getGPSClass(acc) {
  const a = parseFloat(acc);
  if (a <= 10) return 'gps-excellent';
  if (a <= 50) return 'gps-good';
  return 'gps-poor';
}

function parseDuration(dur) {
  if (!dur) return 0;
  const match = dur.match(/([0-9]+)/);
  return match ? parseInt(match[1]) : 0;
}

function formatCurrency(val) {
  if (!val) return 'UGX 0';
  return new Intl.NumberFormat('en-UG', { style: 'currency', currency: 'UGX', maximumFractionDigits: 0 }).format(val);
}
</script>

<style scoped>
.sfa-visits-page {
  padding: 20px;
}
.page-header {
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
.header-subtitle {
  font-size: 13px;
  color: #687178;
  margin-top: 4px;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.filter-chips {
  display: flex;
  gap: 6px;
}
.filter-chip {
  padding: 6px 12px;
  border-radius: 20px;
  border: 1px solid #e2e6e9;
  background: white;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  gap: 6px;
}
.filter-chip:hover, .filter-chip.active {
  background: #2490EF;
  color: white;
  border-color: #2490EF;
}
.chip-count {
  padding: 1px 6px;
  background: rgba(0,0,0,0.1);
  border-radius: 10px;
  font-size: 10px;
  font-weight: 600;
}
.filter-chip.active .chip-count {
  background: rgba(255,255,255,0.2);
}

.slide-over {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  background: rgba(0,0,0,0.3);
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
}
.slide-over-content {
  width: 480px;
  max-width: 90vw;
  background: white;
  height: 100%;
  display: flex;
  flex-direction: column;
  animation: slideIn 0.3s ease;
}
@keyframes slideIn {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}
.slide-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #e2e6e9;
}
.slide-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}
.slide-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}
.visit-timeline, .visit-order {
  margin-top: 20px;
}
.visit-timeline h4, .visit-order h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1f272e;
  margin-bottom: 12px;
}
.order-summary {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
}
.order-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #e2e6e9;
}
.order-row:last-child {
  border-bottom: none;
}
.order-value {
  font-weight: 600;
  color: #1f272e;
}
.gps-excellent { color: #28a745; }
.gps-good { color: #ffc107; }
.gps-poor { color: #dc3545; }
.text-warning { color: #dc3545; font-weight: 600; }
</style>
