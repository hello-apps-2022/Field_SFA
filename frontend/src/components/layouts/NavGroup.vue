<template>
  <!-- Collapsed sidebar: show children as normal icon links -->
  <template v-if="sidebarCollapsed">
    <slot />
  </template>

  <!-- Expanded sidebar: collapsible group -->
  <template v-else>
    <div class="relative">
      <!-- Group header -->
      <button
        class="group flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left transition-colors"
        :class="isActive
          ? 'bg-gray-200 text-gray-900'
          : 'text-gray-600 hover:bg-gray-200 hover:text-gray-900'"
        @click="open = !open"
        @mouseenter="showPreview = true"
        @mouseleave="showPreview = false"
      >
        <!-- Icon -->
        <div class="flex h-5 w-5 shrink-0 items-center justify-center">
          <FeatherIcon :name="icon" class="h-3.5 w-3.5" :class="isActive ? 'text-gray-900' : 'text-gray-500 group-hover:text-gray-700'" />
        </div>

        <!-- Label -->
        <span class="flex-1 truncate text-sm font-medium">{{ label }}</span>

        <!-- Item count badge + chevron -->
        <div class="flex items-center gap-1.5">
          <span
            class="rounded-full bg-gray-300 px-1.5 text-[9px] font-semibold text-gray-600 transition-opacity"
            :class="open ? 'opacity-0' : 'opacity-100 group-hover:opacity-100'"
          >{{ itemCount }}</span>
          <FeatherIcon
            :name="open ? 'chevron-down' : 'chevron-right'"
            class="h-3 w-3 text-gray-400 transition-transform duration-200"
            :class="open ? 'rotate-0' : ''"
          />
        </div>
      </button>

      <!-- Hover preview tooltip — shows child items when group is closed -->
      <Transition name="preview">
        <div
          v-if="showPreview && !open"
          class="absolute left-full top-0 z-50 ml-2 min-w-[160px] rounded-lg border border-gray-200 bg-white py-1.5 shadow-lg"
        >
          <p class="px-3 pb-1 pt-0.5 text-[10px] font-semibold uppercase tracking-wide text-gray-400">{{ label }}</p>
          <slot name="preview" />
        </div>
      </Transition>
    </div>

    <!-- Children — slide open/close -->
    <div
      class="overflow-hidden transition-all duration-200 ease-in-out"
      :style="open ? `max-height: ${maxHeight}px; opacity: 1` : 'max-height: 0px; opacity: 0'"
    >
      <div class="ml-3 mt-0.5 space-y-0.5 border-l-2 border-gray-200 pl-2 pb-0.5">
        <slot />
      </div>
    </div>
  </template>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  label: String,
  icon: String,
  sidebarCollapsed: Boolean,
  paths: { type: Array, default: () => [] },
  itemCount: { type: Number, default: 2 },
})

const route = useRoute()
const open = ref(false)
const showPreview = ref(false)
const maxHeight = 240

const isActive = computed(() =>
  props.paths.some(p => route.path.startsWith(p))
)

watch(() => route.path, (path) => {
  if (props.paths.some(p => path.startsWith(p))) {
    open.value = true
  }
}, { immediate: true })
</script>

<style scoped>
.preview-enter-active { transition: opacity 0.15s ease, transform 0.15s ease; }
.preview-leave-active { transition: opacity 0.1s ease, transform 0.1s ease; }
.preview-enter-from, .preview-leave-to { opacity: 0; transform: translateX(-4px); }
</style>
