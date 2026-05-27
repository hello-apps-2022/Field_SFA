<template>
  <div class="flex h-full flex-col">
    <!-- Header -->
    <PageHeader :title="title">
      <slot name="header-actions" />
      <Btn v-if="newLabel" variant="solid" icon="plus" @click="$emit('new')">
        {{ newLabel }}
      </Btn>
    </PageHeader>

    <!-- Toolbar -->
    <div class="flex shrink-0 items-center gap-2 border-b border-gray-100 bg-white px-4 py-2">
      <div class="relative">
        <FeatherIcon name="search" class="absolute left-2.5 top-2 h-3.5 w-3.5 text-gray-400" />
        <input
          :value="search"
          @input="$emit('update:search', $event.target.value)"
          type="text"
          :placeholder="searchPlaceholder || 'Search…'"
          class="h-8 rounded-md border border-gray-200 bg-white pl-8 pr-3 text-sm focus:border-gray-400 focus:outline-none w-52"
        />
      </div>
      <slot name="filters" />
      <div class="flex-1" />
      <span class="text-xs text-gray-400">{{ count }} {{ title.toLowerCase() }}</span>
      <Btn icon="refresh-cw" :class="loading ? 'animate-spin' : ''" @click="$emit('refresh')" />
    </div>

    <!-- Table -->
    <div class="flex-1 overflow-auto">
      <table class="w-full text-sm">
        <thead class="sticky top-0 z-10 border-b border-gray-100 bg-gray-50">
          <tr>
            <th
              v-for="col in columns"
              :key="col.key"
              class="px-4 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-gray-500"
              :class="col.class"
            >
              {{ col.label }}
            </th>
            <th class="w-10 px-4 py-2.5" />
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr
            v-for="row in rows"
            :key="row.name"
            class="group cursor-pointer hover:bg-gray-50 transition-colors"
            @click="$emit('row-click', row)"
          >
            <td v-for="col in columns" :key="col.key" class="px-4 py-3" :class="col.class">
              <slot :name="`cell-${col.key}`" :row="row" :col="col">
                <span :class="col.primary ? 'font-medium text-gray-900' : 'text-gray-600'">
                  {{ row[col.key] || '—' }}
                </span>
              </slot>
            </td>
            <td class="px-4 py-3 text-right">
              <slot name="row-actions" :row="row">
                <button
                  class="invisible rounded px-2 py-1 text-xs text-gray-500 hover:bg-gray-200 group-hover:visible"
                  @click.stop="$emit('row-action', row)"
                >
                  Edit
                </button>
              </slot>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty state -->
      <div v-if="!loading && rows.length === 0" class="flex flex-col items-center justify-center py-20 text-gray-400">
        <FeatherIcon :name="emptyIcon || 'inbox'" class="mb-3 h-10 w-10" />
        <p class="text-sm font-medium text-gray-600">{{ emptyTitle || `No ${title.toLowerCase()} found` }}</p>
        <p v-if="emptyDescription" class="mt-1 text-xs">{{ emptyDescription }}</p>
      </div>

      <!-- Loading -->
      <div v-if="loading && rows.length === 0" class="flex justify-center py-12">
        <FeatherIcon name="loader" class="h-6 w-6 animate-spin text-gray-400" />
      </div>
    </div>
  </div>
</template>

<script setup>
import PageHeader from '@/components/ui/PageHeader.vue'
import Btn from '@/components/ui/Btn.vue'

defineProps({
  title: String,
  newLabel: String,
  search: String,
  searchPlaceholder: String,
  columns: Array,
  rows: Array,
  count: Number,
  loading: Boolean,
  emptyIcon: String,
  emptyTitle: String,
  emptyDescription: String,
})

defineEmits(['new', 'row-click', 'row-action', 'refresh', 'update:search'])
</script>
