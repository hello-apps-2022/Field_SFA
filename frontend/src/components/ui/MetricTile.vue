<template>
  <div class="rounded-lg border border-outline-gray-2 bg-surface-white p-4 space-y-2">
    <div class="flex items-center justify-between">
      <p class="text-xs font-medium text-ink-gray-5 uppercase tracking-wide">{{ label }}</p>
      <div class="flex h-7 w-7 items-center justify-center rounded-md" :class="iconBg">
        <FeatherIcon :name="icon" class="h-3.5 w-3.5" :class="iconColor" />
      </div>
    </div>
    <p class="text-2xl font-semibold text-ink-gray-9 leading-none">{{ value }}</p>
    <p class="text-xs text-ink-gray-4">{{ subtitle }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: String,
  value: [String, Number],
  icon: String,
  color: { type: String, default: 'blue' },
  subtitle: String,
})

const colorMap = {
  blue:    { bg: 'bg-blue-50',    icon: 'text-blue-500' },
  green:   { bg: 'bg-green-50',   icon: 'text-green-500' },
  purple:  { bg: 'bg-purple-50',  icon: 'text-purple-500' },
  emerald: { bg: 'bg-emerald-50', icon: 'text-emerald-500' },
  orange:  { bg: 'bg-orange-50',  icon: 'text-orange-500' },
  teal:    { bg: 'bg-teal-50',    icon: 'text-teal-500' },
}

const iconBg = computed(() => colorMap[props.color]?.bg || colorMap.blue.bg)
const iconColor = computed(() => colorMap[props.color]?.icon || colorMap.blue.icon)
</script>
