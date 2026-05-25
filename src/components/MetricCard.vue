<template>
  <div class="sfa-card sfa-metric" :class="'sfa-metric--' + size">
    <div class="sfa-metric-header">
      <span class="sfa-metric-label">{{ label }}</span>
      <span v-if="trend !== null" class="sfa-metric-change" :class="trend >= 0 ? 'positive' : 'negative'">
        <svg v-if="trend >= 0" width="12" height="12" viewBox="0 0 12 12" fill="none">
          <path d="M6 2L10 7H2L6 2Z" fill="currentColor"/>
        </svg>
        <svg v-else width="12" height="12" viewBox="0 0 12 12" fill="none">
          <path d="M6 10L2 5H10L6 10Z" fill="currentColor"/>
        </svg>
        {{ Math.abs(trend) }}%
      </span>
    </div>
    <div class="sfa-metric-value">{{ formattedValue }}</div>
    <div v-if="subtitle" class="sfa-metric-subtitle">{{ subtitle }}</div>
    <div v-if="progress !== null" class="sfa-progress" style="margin-top: 8px;">
      <div class="sfa-progress-bar" :class="progressClass" :style="{ width: progress + '%' }"></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  label: { type: String, required: true },
  value: { type: [Number, String], required: true },
  subtitle: { type: String, default: '' },
  trend: { type: Number, default: null },
  progress: { type: Number, default: null },
  size: { type: String, default: 'md' },
  prefix: { type: String, default: '' },
  suffix: { type: String, default: '' },
  decimals: { type: Number, default: 0 }
});

const formattedValue = computed(() => {
  if (typeof props.value === 'number') {
    const val = props.value.toFixed(props.decimals);
    return props.prefix + val + props.suffix;
  }
  return props.prefix + props.value + props.suffix;
});

const progressClass = computed(() => {
  if (props.progress >= 80) return 'sfa-progress-bar--success';
  if (props.progress >= 50) return 'sfa-progress-bar--warning';
  return 'sfa-progress-bar--danger';
});
</script>

<style scoped>
.sfa-metric {
  padding: 16px 20px;
}
.sfa-metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.sfa-metric-label {
  font-size: 12px;
  font-weight: 500;
  color: #687178;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.sfa-metric-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f272e;
  line-height: 1.2;
}
.sfa-metric--sm .sfa-metric-value {
  font-size: 20px;
}
.sfa-metric--lg .sfa-metric-value {
  font-size: 36px;
}
.sfa-metric-subtitle {
  font-size: 12px;
  color: #a0a0a0;
  margin-top: 4px;
}
.sfa-metric-change {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
}
.sfa-metric-change.positive {
  color: #28a745;
  background: #e8f5e9;
}
.sfa-metric-change.negative {
  color: #dc3545;
  background: #ffebee;
}
</style>
