<template>
  <div v-if="hasData" class="rounded-xl border border-gray-200 bg-white p-4">
    <p class="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">{{ title }}</p>

    <!-- Bar chart -->
    <svg v-if="type === 'bar'" :viewBox="`0 0 ${width} ${height}`" class="w-full" :style="{ maxHeight: '280px' }">
      <g v-for="(d, i) in bars" :key="i">
        <rect :x="d.x" :y="d.y" :width="barWidth" :height="d.h" rx="3" fill="#378ADD" />
        <text :x="d.x + barWidth / 2" :y="height - 18" text-anchor="middle" font-size="9" fill="#6b7280">{{ d.label }}</text>
        <text :x="d.x + barWidth / 2" :y="d.y - 4" text-anchor="middle" font-size="9" font-weight="600" fill="#374151">{{ d.valueLabel }}</text>
      </g>
      <line :x1="pad" :y1="height - 30" :x2="width - pad" :y2="height - 30" stroke="#e5e7eb" stroke-width="1" />
    </svg>

    <!-- Pie chart -->
    <svg v-else-if="type === 'pie'" viewBox="0 0 240 160" class="w-full" :style="{ maxHeight: '280px' }">
      <g transform="translate(80,80)">
        <path v-for="(s, i) in slices" :key="i" :d="s.path" :fill="s.color" />
      </g>
      <g transform="translate(170,30)">
        <g v-for="(s, i) in slices" :key="'l' + i" :transform="`translate(0,${i * 18})`">
          <rect width="11" height="11" rx="2" :fill="s.color" />
          <text x="16" y="10" font-size="10" fill="#374151">{{ s.label }} ({{ s.pct }}%)</text>
        </g>
      </g>
    </svg>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: { type: String, default: 'Chart' },
  type: { type: String, default: 'bar' },
  rows: { type: Array, default: () => [] },
  xField: String,
  yField: String,
})

const width = 480
const height = 240
const pad = 30

const cleanRows = computed(() =>
  (props.rows || [])
    .filter((r) => r && r[props.yField] != null && Number(r[props.yField]) === Number(r[props.yField]))
    .slice(0, 12)
)

const hasData = computed(() => cleanRows.value.length > 0)

const maxVal = computed(() => Math.max(1, ...cleanRows.value.map((r) => Number(r[props.yField]) || 0)))

const barWidth = computed(() => {
  const n = cleanRows.value.length || 1
  return Math.max(8, (width - pad * 2) / n - 10)
})

function fmtVal(v) {
  const n = Number(v) || 0
  if (n >= 1000) return (n / 1000).toFixed(1) + 'k'
  return Math.round(n * 100) / 100
}

function shortLabel(v) {
  const s = String(v ?? '')
  return s.length > 10 ? s.slice(0, 9) + '…' : s
}

const bars = computed(() => {
  const n = cleanRows.value.length || 1
  const slot = (width - pad * 2) / n
  const chartH = height - 60
  return cleanRows.value.map((r, i) => {
    const val = Number(r[props.yField]) || 0
    const h = Math.max(1, (val / maxVal.value) * chartH)
    return {
      x: pad + i * slot + (slot - barWidth.value) / 2,
      y: height - 30 - h,
      h,
      label: shortLabel(r[props.xField]),
      valueLabel: fmtVal(val),
    }
  })
})

const PALETTE = ['#378ADD', '#5DCAA5', '#D85A30', '#7F77DD', '#EF9F27', '#D4537E', '#639922', '#888780']

const slices = computed(() => {
  const rows = cleanRows.value
  const total = rows.reduce((s, r) => s + (Number(r[props.yField]) || 0), 0) || 1
  let angle = -Math.PI / 2
  return rows.map((r, i) => {
    const val = Number(r[props.yField]) || 0
    const frac = val / total
    const start = angle
    const end = angle + frac * Math.PI * 2
    angle = end
    const r0 = 70
    const x1 = Math.cos(start) * r0
    const y1 = Math.sin(start) * r0
    const x2 = Math.cos(end) * r0
    const y2 = Math.sin(end) * r0
    const large = end - start > Math.PI ? 1 : 0
    return {
      path: `M0 0 L ${x1.toFixed(2)} ${y1.toFixed(2)} A ${r0} ${r0} 0 ${large} 1 ${x2.toFixed(2)} ${y2.toFixed(2)} Z`,
      color: PALETTE[i % PALETTE.length],
      label: shortLabel(r[props.xField]),
      pct: Math.round(frac * 100),
    }
  })
})
</script>
