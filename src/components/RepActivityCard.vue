<template>
  <div class="sfa-card rep-activity">
    <div class="rep-activity-header">
      <div class="rep-info">
        <div class="rep-avatar">
          <img v-if="rep.image" :src="rep.image" :alt="rep.name">
          <span v-else>{{ rep.name ? rep.name.charAt(0) : '?' }}</span>
        </div>
        <div class="rep-details">
          <div class="rep-name">{{ rep.name }}</div>
          <div class="rep-territory">{{ rep.territory }}</div>
        </div>
      </div>
      <div class="rep-status" :class="'rep-status--' + rep.online_status">
        <span class="rep-status-dot"></span>
        {{ rep.online_status }}
      </div>
    </div>
    <div class="rep-activity-body">
      <div class="rep-metrics">
        <div class="rep-metric">
          <span class="rep-metric-value">{{ rep.visits_today || 0 }}</span>
          <span class="rep-metric-label">Visits</span>
        </div>
        <div class="rep-metric">
          <span class="rep-metric-value">{{ rep.orders_today || 0 }}</span>
          <span class="rep-metric-label">Orders</span>
        </div>
        <div class="rep-metric">
          <span class="rep-metric-value">{{ formatCurrency(rep.revenue_today) }}</span>
          <span class="rep-metric-label">Revenue</span>
        </div>
        <div class="rep-metric">
          <span class="rep-metric-value">{{ rep.points || 0 }}</span>
          <span class="rep-metric-label">Points</span>
        </div>
      </div>
      <div class="rep-progress">
        <div class="rep-progress-header">
          <span>Daily Target</span>
          <span>{{ rep.target_progress || 0 }}%</span>
        </div>
        <div class="sfa-progress">
          <div class="sfa-progress-bar" :style="{ width: (rep.target_progress || 0) + '%' }"></div>
        </div>
      </div>
      <div v-if="rep.current_visit" class="rep-current-visit">
        <div class="current-visit-label">Current Visit</div>
        <div class="current-visit-customer">{{ rep.current_visit.customer }}</div>
        <div class="current-visit-time">Started {{ formatTime(rep.current_visit.start_time) }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  rep: { type: Object, required: true }
});

function formatCurrency(val) {
  if (!val) return 'UGX 0';
  return new Intl.NumberFormat('en-UG', { style: 'currency', currency: 'UGX', maximumFractionDigits: 0 }).format(val);
}

function formatTime(ts) {
  if (!ts) return '';
  const diff = Math.floor((Date.now() - new Date(ts).getTime()) / 60000);
  if (diff < 1) return 'just now';
  if (diff < 60) return diff + 'm ago';
  return Math.floor(diff/60) + 'h ago';
}
</script>

<style scoped>
.rep-activity {
  overflow: hidden;
}
.rep-activity-header {
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f0f2f4;
}
.rep-info {
  display: flex;
  align-items: center;
  gap: 12px;
}
.rep-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  overflow: hidden;
}
.rep-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.rep-name {
  font-weight: 600;
  font-size: 14px;
  color: #1f272e;
}
.rep-territory {
  font-size: 12px;
  color: #687178;
}
.rep-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 20px;
}
.rep-status--online {
  background: #e8f5e9;
  color: #28a745;
}
.rep-status--offline {
  background: #ffebee;
  color: #dc3545;
}
.rep-status--idle {
  background: #fff8e1;
  color: #f9a825;
}
.rep-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}
.rep-activity-body {
  padding: 16px 20px;
}
.rep-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}
.rep-metric {
  text-align: center;
}
.rep-metric-value {
  display: block;
  font-size: 18px;
  font-weight: 700;
  color: #1f272e;
}
.rep-metric-label {
  font-size: 11px;
  color: #a0a0a0;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.rep-progress {
  margin-bottom: 16px;
}
.rep-progress-header {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #687178;
  margin-bottom: 6px;
}
.rep-current-visit {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 3px solid #2490EF;
}
.current-visit-label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #a0a0a0;
  margin-bottom: 4px;
}
.current-visit-customer {
  font-weight: 600;
  font-size: 13px;
  color: #1f272e;
}
.current-visit-time {
  font-size: 11px;
  color: #687178;
  margin-top: 2px;
}
</style>
