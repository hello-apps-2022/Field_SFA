<template>
  <div class="sfa-card visit-card" :class="'visit-card--' + (visit.status ? visit.status.toLowerCase() : '')">
    <div class="visit-card-header">
      <div class="visit-card-customer">
        <div class="visit-card-avatar">
          {{ visit.customer ? visit.customer.charAt(0) : '?' }}
        </div>
        <div class="visit-card-info">
          <div class="visit-card-name">{{ visit.customer }}</div>
          <div class="visit-card-meta">
            <span class="sfa-badge" :class="badgeClass">
              <span class="sfa-badge-dot"></span>
              {{ visit.status }}
            </span>
            <span class="visit-card-time">{{ formatTime(visit.check_in_time) }}</span>
          </div>
        </div>
      </div>
      <div class="visit-card-actions">
        <button class="sfa-btn sfa-btn--ghost sfa-btn--sm" @click="$emit('view', visit)">
          View
        </button>
      </div>
    </div>
    <div class="visit-card-body" v-if="showDetails">
      <div class="visit-card-stats">
        <div class="visit-stat">
          <span class="visit-stat-label">Duration</span>
          <span class="visit-stat-value">{{ visit.duration || 'N/A' }}</span>
        </div>
        <div class="visit-stat">
          <span class="visit-stat-label">Order Value</span>
          <span class="visit-stat-value">{{ formatCurrency(visit.order_value) }}</span>
        </div>
        <div class="visit-stat">
          <span class="visit-stat-label">Payment</span>
          <span class="visit-stat-value">{{ formatCurrency(visit.payment_collected) }}</span>
        </div>
        <div class="visit-stat">
          <span class="visit-stat-label">GPS</span>
          <span class="visit-stat-value" :class="gpsClass">{{ visit.gps_accuracy }}m</span>
        </div>
      </div>
      <div v-if="visit.form_responses" class="visit-card-forms">
        <div v-for="form in visit.form_responses" :key="form.name" class="visit-form-tag">
          {{ form.form_template }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  visit: { type: Object, required: true },
  showDetails: { type: Boolean, default: true }
});

defineEmits(['view']);

const badgeClass = computed(() => {
  const status = props.visit.status ? props.visit.status.toLowerCase() : '';
  if (status === 'completed') return 'sfa-badge--success';
  if (status === 'in progress') return 'sfa-badge--primary';
  if (status === 'missed') return 'sfa-badge--danger';
  if (status === 'pending') return 'sfa-badge--warning';
  return 'sfa-badge--primary';
});

const gpsClass = computed(() => {
  const acc = parseFloat(props.visit.gps_accuracy);
  if (acc <= 10) return 'gps-excellent';
  if (acc <= 50) return 'gps-good';
  return 'gps-poor';
});

function formatTime(ts) {
  if (!ts) return '';
  return new Date(ts).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

function formatCurrency(val) {
  if (!val) return 'UGX 0';
  return new Intl.NumberFormat('en-UG', { style: 'currency', currency: 'UGX', maximumFractionDigits: 0 }).format(val);
}
</script>

<style scoped>
.visit-card {
  transition: all 0.2s ease;
}
.visit-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.08);
}
.visit-card-header {
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.visit-card-customer {
  display: flex;
  align-items: center;
  gap: 12px;
}
.visit-card-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2490EF 0%, #1a7ad1 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}
.visit-card-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.visit-card-name {
  font-weight: 600;
  font-size: 14px;
  color: #1f272e;
}
.visit-card-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}
.visit-card-time {
  font-size: 12px;
  color: #a0a0a0;
}
.visit-card-body {
  padding: 0 20px 16px;
  border-top: 1px solid #f0f2f4;
  margin-top: 0;
  padding-top: 12px;
}
.visit-card-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}
.visit-stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.visit-stat-label {
  font-size: 11px;
  color: #a0a0a0;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.visit-stat-value {
  font-size: 13px;
  font-weight: 600;
  color: #1f272e;
}
.gps-excellent { color: #28a745; }
.gps-good { color: #ffc107; }
.gps-poor { color: #dc3545; }
.visit-card-forms {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 12px;
}
.visit-form-tag {
  padding: 4px 10px;
  background: #e8f4fd;
  color: #2490EF;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}
</style>
