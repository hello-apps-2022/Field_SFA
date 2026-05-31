<template>
  <span class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium" :class="colorClass">
    {{ label || status }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: String,
  label: String,
  colorMap: { type: Object, default: () => ({}) },
})

const defaultColors = {
  'Active': 'bg-green-50 text-green-700',
  'Inactive': 'bg-gray-100 text-gray-500',
  'Completed': 'bg-blue-50 text-blue-700',
  'Confirmed': 'bg-blue-50 text-blue-700',
  'Delivered': 'bg-green-50 text-green-700',
  'In Progress': 'bg-green-50 text-green-700',
  'Planned': 'bg-gray-100 text-gray-600',
  'Cancelled': 'bg-red-50 text-red-600',
  'Draft': 'bg-yellow-50 text-yellow-700',
  'Synced': 'bg-green-50 text-green-700',
  'Pending': 'bg-yellow-50 text-yellow-700',
  'Failed': 'bg-red-50 text-red-600',
}

const colorClass = computed(() =>
  props.colorMap[props.status] || defaultColors[props.status] || 'bg-gray-100 text-gray-600'
)
</script>
