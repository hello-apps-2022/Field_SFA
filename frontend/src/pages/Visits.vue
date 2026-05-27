<template>
  <div class="flex h-full flex-col">

    <!-- Toolbar -->
    <div class="flex items-center gap-3 border-b border-outline-gray-2 bg-surface-white px-4 py-2.5">
      <TextInput
        v-model="search"
        placeholder="Search visits..."
        size="sm"
        class="w-64"
      >
        <template #prefix><FeatherIcon name="search" class="h-3.5 w-3.5 text-ink-gray-4" /></template>
      </TextInput>
      <FormControl type="select" v-model="statusFilter" :options="statusOptions" size="sm" class="w-36" />
      <FormControl type="date" v-model="dateFilter" size="sm" class="w-36" />
      <div class="flex-1" />
      <Button size="sm" :loading="visitsList.loading.value" @click="visitsList.reload()">
        <template #prefix><FeatherIcon name="refresh-cw" class="h-3.5 w-3.5" /></template>
        Refresh
      </Button>
    </div>

    <!-- Table -->
    <div class="flex-1 overflow-auto">
      <table class="w-full text-sm">
        <thead class="sticky top-0 bg-surface-gray-1 border-b border-outline-gray-2">
          <tr>
            <th class="px-4 py-2.5 text-left text-xs font-medium text-ink-gray-5 uppercase tracking-wide">Visit ID</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium text-ink-gray-5 uppercase tracking-wide">Customer</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium text-ink-gray-5 uppercase tracking-wide">Sales Person</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium text-ink-gray-5 uppercase tracking-wide">Date</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium text-ink-gray-5 uppercase tracking-wide">Check In</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium text-ink-gray-5 uppercase tracking-wide">Status</th>
            <th class="px-4 py-2.5" />
          </tr>
        </thead>
        <tbody class="divide-y divide-outline-gray-1">
          <tr
            v-for="visit in filteredVisits"
            :key="visit.name"
            class="hover:bg-surface-gray-1 cursor-pointer"
            @click="$router.push('/visits/' + visit.name)"
          >
            <td class="px-4 py-3 font-mono text-xs text-ink-gray-5">{{ visit.name }}</td>
            <td class="px-4 py-3 font-medium text-ink-gray-8">{{ visit.customer }}</td>
            <td class="px-4 py-3 text-ink-gray-6">{{ visit.sales_person }}</td>
            <td class="px-4 py-3 text-ink-gray-6">{{ formatDate(visit.visit_date) }}</td>
            <td class="px-4 py-3 text-ink-gray-6">{{ visit.check_in_time ? formatTime(visit.check_in_time) : '—' }}</td>
            <td class="px-4 py-3">
              <Badge :label="visit.status" :variant="statusVariant(visit.status)" size="sm" />
            </td>
            <td class="px-4 py-3">
              <FeatherIcon name="chevron-right" class="h-4 w-4 text-ink-gray-4" />
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="!visitsList.loading.value && !filteredVisits.length" class="flex flex-col items-center justify-center py-20 text-ink-gray-4">
        <FeatherIcon name="map-pin" class="h-10 w-10 mb-3" />
        <p class="text-sm font-medium">No visits found</p>
        <p class="text-xs mt-1">Try adjusting your filters</p>
      </div>
      <div v-if="visitsList.loading.value" class="flex justify-center py-10">
        <Spinner class="h-5 w-5 text-ink-gray-5" />
      </div>
    </div>

    <!-- Pagination -->
    <div class="flex items-center justify-between border-t border-outline-gray-2 px-4 py-2.5 bg-surface-white">
      <p class="text-xs text-ink-gray-4">{{ filteredVisits.length }} visits</p>
      <div class="flex items-center gap-2">
        <Button size="sm" variant="ghost" :disabled="!visitsList.hasPreviousPage" @click="visitsList.previousPage()">Previous</Button>
        <Button size="sm" variant="ghost" :disabled="!visitsList.hasNextPage" @click="visitsList.nextPage()">Next</Button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { createListResource } from 'frappe-ui'
import dayjs from 'dayjs'

const search = ref('')
const statusFilter = ref('')
const dateFilter = ref('')

const statusOptions = [
  { label: 'All Statuses', value: '' },
  { label: 'Planned', value: 'Planned' },
  { label: 'In Progress', value: 'In Progress' },
  { label: 'Completed', value: 'Completed' },
  { label: 'Cancelled', value: 'Cancelled' },
]

const visitsList = createListResource({
  doctype: 'SFA Visit',
  fields: ['name', 'customer', 'sales_person', 'visit_date', 'check_in_time', 'check_out_time', 'status', 'beat_plan'],
  orderBy: 'visit_date desc',
  pageLength: 50,
  auto: true,
})

const filteredVisits = computed(() => {
  let list = visitsList.data || []
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(v =>
      v.customer?.toLowerCase().includes(q) ||
      v.sales_person?.toLowerCase().includes(q) ||
      v.name?.toLowerCase().includes(q)
    )
  }
  if (statusFilter.value) list = list.filter(v => v.status === statusFilter.value)
  if (dateFilter.value) list = list.filter(v => v.visit_date === dateFilter.value)
  return list
})

const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'
const formatTime = (t) => t ? dayjs(t).format('HH:mm') : '—'
const statusVariant = (s) => ({ 'In Progress': 'success', 'Completed': 'info', 'Planned': 'subtle', 'Cancelled': 'danger' })[s] || 'subtle'
</script>
