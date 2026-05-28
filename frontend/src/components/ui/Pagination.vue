<template>
  <div v-if="total > 0" class="flex items-center justify-between gap-3 px-1 py-3">
    <!-- count summary (always shown when there's data) -->
    <p class="text-xs text-gray-400">
      {{ rangeStart }}–{{ rangeEnd }} of {{ total }}
    </p>

    <!-- Multi-page controls only -->
    <template v-if="total > pageSize || page > 1">
      <!-- Mobile: Load more -->
      <button v-if="hasMore"
        class="lg:hidden inline-flex items-center gap-1.5 rounded-md border border-gray-200 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
        :disabled="loading"
        @click="$emit('load-more')">
        <FeatherIcon name="chevron-down" class="h-3.5 w-3.5" />
        {{ loading ? 'Loading…' : 'Load more' }}
      </button>
      <span v-else class="lg:hidden text-xs text-gray-300">End of list</span>

      <!-- Desktop: page numbers -->
      <div class="hidden lg:flex items-center gap-1">
        <button
        class="flex h-7 w-7 items-center justify-center rounded-md border border-gray-200 text-gray-500 hover:bg-gray-50 disabled:opacity-40 disabled:hover:bg-white"
        :disabled="page <= 1 || loading"
        @click="goTo(page - 1)">
        <FeatherIcon name="chevron-left" class="h-3.5 w-3.5" />
      </button>

      <button v-for="p in visiblePages" :key="p.key"
        :disabled="p.ellipsis || loading"
        class="flex h-7 min-w-[28px] items-center justify-center rounded-md px-1.5 text-xs font-medium transition-colors"
        :class="p.num === page
          ? 'bg-gray-900 text-white'
          : p.ellipsis ? 'text-gray-300 cursor-default' : 'border border-gray-200 text-gray-600 hover:bg-gray-50'"
        @click="!p.ellipsis && goTo(p.num)">
        {{ p.ellipsis ? '…' : p.num }}
      </button>

      <button
        class="flex h-7 w-7 items-center justify-center rounded-md border border-gray-200 text-gray-500 hover:bg-gray-50 disabled:opacity-40 disabled:hover:bg-white"
        :disabled="page >= totalPages || loading"
        @click="goTo(page + 1)">
        <FeatherIcon name="chevron-right" class="h-3.5 w-3.5" />
      </button>
    </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import FeatherIcon from '@/components/ui/FeatherIcon.vue'

const props = defineProps({
  page: { type: Number, default: 1 },
  pageSize: { type: Number, default: 50 },
  total: { type: Number, default: 0 },
  loading: { type: Boolean, default: false },
})
const emit = defineEmits(['update:page', 'load-more'])

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.pageSize)))
const rangeStart = computed(() => props.total === 0 ? 0 : (props.page - 1) * props.pageSize + 1)
const rangeEnd = computed(() => Math.min(props.page * props.pageSize, props.total))
const hasMore = computed(() => props.page < totalPages.value)

function goTo(p) {
  if (p < 1 || p > totalPages.value || p === props.page) return
  emit('update:page', p)
}

// Page-number list with ellipses: 1 … 4 5 [6] 7 8 … 20
const visiblePages = computed(() => {
  const tp = totalPages.value
  const cur = props.page
  const out = []
  const push = (num, ellipsis = false) => out.push({ num, ellipsis, key: ellipsis ? `e${num}` : `p${num}` })

  if (tp <= 7) {
    for (let i = 1; i <= tp; i++) push(i)
    return out
  }
  push(1)
  if (cur > 3) push(0, true)
  const from = Math.max(2, cur - 1)
  const to = Math.min(tp - 1, cur + 1)
  for (let i = from; i <= to; i++) push(i)
  if (cur < tp - 2) push(tp, true)
  push(tp)
  return out
})
</script>
