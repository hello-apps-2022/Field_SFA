<template>
  <button
    class="inline-flex items-center justify-center gap-1.5 rounded-md text-sm font-medium transition-colors disabled:opacity-50"
    :class="[sizeClass, variantClass]"
    :disabled="disabled || loading"
    v-bind="$attrs"
  >
    <FeatherIcon v-if="loading" name="loader" class="h-3.5 w-3.5 animate-spin" />
    <FeatherIcon v-else-if="icon" :name="icon" class="h-3.5 w-3.5" />
    <slot />
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: { type: String, default: 'default' }, // default | solid | ghost | danger
  size: { type: String, default: 'md' }, // sm | md | lg
  icon: String,
  loading: Boolean,
  disabled: Boolean,
})

const sizeClass = computed(() => ({
  sm: 'h-7 px-2.5 text-xs',
  md: 'h-8 px-3',
  lg: 'h-9 px-4',
})[props.size])

const variantClass = computed(() => ({
  default: 'border border-gray-200 bg-white text-gray-700 hover:bg-gray-50 hover:border-gray-300',
  solid:   'bg-gray-900 text-white hover:bg-gray-700 border border-transparent',
  ghost:   'text-gray-600 hover:bg-gray-100 border border-transparent',
  danger:  'bg-red-600 text-white hover:bg-red-700 border border-transparent',
  subtle:  'bg-gray-100 text-gray-700 hover:bg-gray-200 border border-transparent',
})[props.variant])
</script>
