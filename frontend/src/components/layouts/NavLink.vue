<template>
  <router-link
    :to="item.to"
    class="flex h-8 w-full items-center rounded-md px-2 text-sm text-gray-600 hover:bg-gray-200 hover:text-gray-900 transition-colors"
    :class="isActive ? 'bg-white text-gray-900 font-medium shadow-sm border border-gray-200' : ''"
    :title="collapsed ? item.label : ''"
  >
    <FeatherIcon :name="item.icon" class="h-3.5 w-3.5 shrink-0" />
    <Transition name="fade-left">
      <span v-if="!collapsed" class="ml-2 truncate">{{ item.label }}</span>
    </Transition>
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

<style scoped>
.fade-left-enter-active, .fade-left-leave-active { transition: opacity 0.12s ease; }
.fade-left-enter-from, .fade-left-leave-to { opacity: 0; }
</style>
