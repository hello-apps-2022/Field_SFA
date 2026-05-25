<template>
  <div class="sfa-timeline">
    <div
      v-for="item in items"
      :key="item.name"
      class="sfa-timeline-item"
      :class="'timeline-item--' + item.type"
    >
      <div class="sfa-timeline-time">{{ formatTime(item.timestamp) }}</div>
      <div class="sfa-timeline-content">
        <div class="timeline-header">
          <span class="timeline-badge" :class="'badge--' + item.type">
            {{ item.type }}
          </span>
          <span class="timeline-actor">{{ item.actor }}</span>
        </div>
        <div class="timeline-body">{{ item.description }}</div>
        <div v-if="item.metadata" class="timeline-meta">
          <span v-for="(val, key) in item.metadata" :key="key" class="meta-tag">
            {{ key }}: {{ val }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  items: { type: Array, required: true }
});

function formatTime(ts) {
  if (!ts) return '';
  const date = new Date(ts);
  const now = new Date();
  const diff = Math.floor((now - date) / 60000);
  if (diff < 1) return 'Just now';
  if (diff < 60) return diff + 'm ago';
  if (diff < 1440) return Math.floor(diff/60) + 'h ago';
  return date.toLocaleDateString('en-UG', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}
</script>

<style scoped>
.timeline-item--visit .timeline-badge { background: #e8f4fd; color: #2490EF; }
.timeline-item--order .timeline-badge { background: #e8f5e9; color: #28a745; }
.timeline-item--payment .timeline-badge { background: #fff8e1; color: #f9a825; }
.timeline-item--form .timeline-badge { background: #f3e5f5; color: #9c27b0; }
.timeline-item--alert .timeline-badge { background: #ffebee; color: #dc3545; }

.timeline-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.timeline-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.timeline-actor {
  font-size: 12px;
  font-weight: 600;
  color: #1f272e;
}
.timeline-body {
  font-size: 13px;
  color: #687178;
  line-height: 1.5;
}
.timeline-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}
.meta-tag {
  padding: 2px 8px;
  background: #f4f5f6;
  border-radius: 4px;
  font-size: 11px;
  color: #687178;
}
</style>
