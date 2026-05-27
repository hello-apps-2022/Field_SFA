<template>
  <div class="flex h-full flex-col">
    <div class="flex items-center gap-3 border-b border-outline-gray-2 bg-surface-white px-4 py-2.5">
      <TextInput v-model="search" placeholder="Search beat plans..." size="sm" class="w-64">
        <template #prefix><FeatherIcon name="search" class="h-3.5 w-3.5 text-ink-gray-4" /></template>
      </TextInput>
      <FormControl type="select" v-model="statusFilter" :options="statusOptions" size="sm" class="w-36" />
      <div class="flex-1" />
      <Button size="sm" :loading="list.loading.value" @click="list.reload()">
        <template #prefix><FeatherIcon name="refresh-cw" class="h-3.5 w-3.5" /></template>
        Refresh
      </Button>
    </div>

    <div class="flex-1 overflow-auto">
      <table class="w-full text-sm">
        <thead class="sticky top-0 bg-surface-gray-1 border-b border-outline-gray-2">
          <tr>
            <th class="px-4 py-2.5 text-left text-xs font-medium text-ink-gray-5 uppercase tracking-wide">Plan Name</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium text-ink-gray-5 uppercase tracking-wide">Territory</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium text-ink-gray-5 uppercase tracking-wide">Sales Person</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium text-ink-gray-5 uppercase tracking-wide">Date</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium text-ink-gray-5 uppercase tracking-wide">Status</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-outline-gray-1">
          <tr v-for="bp in filtered" :key="bp.name" class="hover:bg-surface-gray-1">
            <td class="px-4 py-3 font-medium text-ink-gray-8">{{ bp.plan_name }}</td>
            <td class="px-4 py-3 text-ink-gray-6">{{ bp.territory || '—' }}</td>
            <td class="px-4 py-3 text-ink-gray-6">{{ bp.sales_person || '—' }}</td>
            <td class="px-4 py-3 text-ink-gray-6">{{ formatDate(bp.date) }}</td>
            <td class="px-4 py-3">
              <Badge :label="bp.status || 'Draft'" variant="subtle" size="sm" />
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="!list.loading.value && !filtered.length" class="flex flex-col items-center justify-center py-20 text-ink-gray-4">
        <FeatherIcon name="map" class="h-10 w-10 mb-3" />
        <p class="text-sm font-medium">No beat plans found</p>
      </div>
      <div v-if="list.loading.value" class="flex justify-center py-10">
        <Spinner class="h-5 w-5 text-ink-gray-5" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { createListResource } from 'frappe-ui'
import dayjs from 'dayjs'

const search = ref('')
const statusFilter = ref('')
const statusOptions = [
  { label: 'All Statuses', value: '' },
  { label: 'Draft', value: 'Draft' },
  { label: 'Active', value: 'Active' },
  { label: 'Completed', value: 'Completed' },
]

const list = createListResource({
  doctype: 'SFA Beat Plan',
  fields: ['name', 'plan_name', 'territory', 'sales_person', 'date', 'status'],
  orderBy: 'date desc',
  pageLength: 50,
  auto: true,
})

const filtered = computed(() => {
  let l = list.data || []
  if (search.value) {
    const q = search.value.toLowerCase()
    l = l.filter(b => b.plan_name?.toLowerCase().includes(q) || b.territory?.toLowerCase().includes(q))
  }
  if (statusFilter.value) l = l.filter(b => b.status === statusFilter.value)
  return l
})

const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'
</script>
