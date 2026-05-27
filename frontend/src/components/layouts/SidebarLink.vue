<template>
  <router-link
    :to="item.to"
    class="flex h-8 w-full items-center rounded px-2 text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition-colors duration-150 no-underline"
    :class="isActive ? 'bg-gray-100 text-gray-900 font-medium' : ''"
    :title="collapsed ? item.label : ''"
  >
    <FeatherIcon :name="item.icon" class="h-3.5 w-3.5 shrink-0" />
    <span
      v-show="!collapsed"
      class="ml-2 truncate text-sm"
    >
      {{ item.label }}
    </span>
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
const isActive = computed(() =>
  route.path === props.item.to ||
  (props.item.to !== '/dashboard' && route.path.startsWith(props.item.to))
)
</script>
