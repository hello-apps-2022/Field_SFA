<template>
  <router-link
    :to="item.to"
    class="flex h-8 w-full items-center gap-2.5 rounded px-2 text-ink-gray-6 hover:bg-surface-gray-2 hover:text-ink-gray-8 transition-colors"
    :class="{
      'bg-surface-gray-3 text-ink-gray-9 font-medium': isActive,
    }"
    :title="collapsed ? item.label : ''"
  >
    <FeatherIcon :name="item.icon" class="h-3.5 w-3.5 shrink-0" />
    <span v-if="!collapsed" class="text-sm truncate">{{ item.label }}</span>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  item: { type: Object, required: true },
  collapsed: { type: Boolean, default: false },
})

const route = useRoute()
const isActive = computed(() => route.path.startsWith(props.item.to) && props.item.to !== '/')
</script>
