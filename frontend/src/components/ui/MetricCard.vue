<template>
  <div class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm space-y-2">
    <div class="flex items-center justify-between">
      <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-500">{{ label }}</p>
      <div class="flex h-7 w-7 items-center justify-center rounded-lg" :class="bgColor">
        <FeatherIcon :name="icon" class="h-3.5 w-3.5 text-white" />
      </div>
    </div>
    <p class="text-2xl font-semibold leading-none text-gray-900">{{ value }}</p>
    <p class="text-xs text-gray-400">{{ sub }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ label: String, value: [String, Number], icon: String, color: String, sub: String })
const colors = { blue: 'bg-blue-500', green: 'bg-green-500', purple: 'bg-purple-500', emerald: 'bg-emerald-500', orange: 'bg-orange-500', teal: 'bg-teal-500' }
const bgColor = computed(() => colors[props.color] || 'bg-gray-500')
</script>
