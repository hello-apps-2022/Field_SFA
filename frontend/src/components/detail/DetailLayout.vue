<template>
  <div class="flex h-full flex-col">
    <!-- Header -->
    <PageHeader :title="title" :back-to="backTo" :back-label="backLabel">
      <slot name="actions" />
    </PageHeader>

    <!-- Body: left panel + right panel -->
    <div class="flex flex-1 overflow-hidden">

      <!-- Left: record details (resizable) -->
      <div
        class="flex h-full flex-col overflow-hidden border-r border-gray-100"
        :style="{ width: leftWidth + 'px', minWidth: '280px', maxWidth: '480px' }"
      >
        <!-- Avatar + name area -->
        <div class="shrink-0 border-b border-gray-100 p-5">
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gray-200 text-sm font-semibold text-gray-600">
              {{ initials }}
            </div>
            <div class="min-w-0">
              <p class="truncate text-base font-semibold text-gray-900">{{ title }}</p>
              <p v-if="subtitle" class="truncate text-xs text-gray-500">{{ subtitle }}</p>
            </div>
          </div>
          <slot name="quick-actions" />
        </div>

        <!-- Scrollable fields -->
        <div class="flex-1 overflow-y-auto p-5">
          <slot name="fields" />
        </div>
      </div>

      <!-- Resize handle -->
      <div
        class="w-1 shrink-0 cursor-col-resize bg-gray-100 hover:bg-gray-300 active:bg-blue-400 transition-colors"
        @mousedown="startResize"
      />

      <!-- Right: tabs + activity -->
      <div class="flex flex-1 flex-col overflow-hidden">
        <!-- Tabs -->
        <div class="flex shrink-0 border-b border-gray-100 bg-white px-4">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            class="mr-1 border-b-2 px-3 py-3 text-sm font-medium transition-colors"
            :class="activeTab === tab.id
              ? 'border-gray-900 text-gray-900'
              : 'border-transparent text-gray-500 hover:text-gray-700'"
            @click="activeTab = tab.id"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- Tab content -->
        <div class="flex-1 overflow-y-auto p-5">
          <slot :name="`tab-${activeTab}`" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import PageHeader from '@/components/ui/PageHeader.vue'

const props = defineProps({
  title: String,
  subtitle: String,
  backTo: String,
  backLabel: String,
  tabs: { type: Array, default: () => [{ id: 'details', label: 'Details' }] },
})

const activeTab = ref(props.tabs[0]?.id || 'details')
const leftWidth = ref(320)

const initials = computed(() => {
  if (!props.title) return '?'
  return props.title.split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase()
})

// Resize logic
let startX = 0
let startWidth = 0

function startResize(e) {
  startX = e.clientX
  startWidth = leftWidth.value
  document.addEventListener('mousemove', onResize)
  document.addEventListener('mouseup', stopResize)
}

function onResize(e) {
  const delta = e.clientX - startX
  leftWidth.value = Math.max(280, Math.min(480, startWidth + delta))
}

function stopResize() {
  document.removeEventListener('mousemove', onResize)
  document.removeEventListener('mouseup', stopResize)
}
</script>
