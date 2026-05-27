<template>
  <div v-if="visit" class="p-6 space-y-6 max-w-4xl">

    <div class="flex items-center gap-3">
      <Button variant="ghost" size="sm" @click="$router.back()">
        <template #prefix><FeatherIcon name="arrow-left" class="h-3.5 w-3.5" /></template>
        Back
      </Button>
      <span class="text-sm text-ink-gray-4">/</span>
      <span class="text-sm font-medium text-ink-gray-8">{{ visit.name }}</span>
      <Badge :label="visit.status" :variant="statusVariant(visit.status)" />
    </div>

    <div class="grid grid-cols-1 gap-4 md:grid-cols-2">

      <!-- Visit info -->
      <div class="rounded-lg border border-outline-gray-2 p-5 space-y-4">
        <p class="text-sm font-semibold text-ink-gray-9">Visit Details</p>
        <dl class="space-y-3">
          <div class="flex justify-between">
            <dt class="text-xs text-ink-gray-4 uppercase tracking-wide">Customer</dt>
            <dd class="text-sm font-medium text-ink-gray-8">{{ visit.customer }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-xs text-ink-gray-4 uppercase tracking-wide">Sales Person</dt>
            <dd class="text-sm text-ink-gray-7">{{ visit.sales_person }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-xs text-ink-gray-4 uppercase tracking-wide">Date</dt>
            <dd class="text-sm text-ink-gray-7">{{ formatDate(visit.visit_date) }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-xs text-ink-gray-4 uppercase tracking-wide">Check In</dt>
            <dd class="text-sm text-ink-gray-7">{{ visit.check_in_time ? formatTime(visit.check_in_time) : '—' }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-xs text-ink-gray-4 uppercase tracking-wide">Check Out</dt>
            <dd class="text-sm text-ink-gray-7">{{ visit.check_out_time ? formatTime(visit.check_out_time) : '—' }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-xs text-ink-gray-4 uppercase tracking-wide">Beat Plan</dt>
            <dd class="text-sm text-ink-gray-7">{{ visit.beat_plan || '—' }}</dd>
          </div>
        </dl>
      </div>

      <!-- Form responses -->
      <div class="rounded-lg border border-outline-gray-2 p-5 space-y-4">
        <p class="text-sm font-semibold text-ink-gray-9">Form Responses</p>
        <div v-if="responses.length" class="space-y-2">
          <div
            v-for="r in responses"
            :key="r.name"
            class="flex items-center justify-between rounded-md bg-surface-gray-1 px-3 py-2"
          >
            <div>
              <p class="text-sm font-medium text-ink-gray-8">{{ r.form_template }}</p>
              <p class="text-xs text-ink-gray-4">{{ formatDate(r.response_date) }}</p>
            </div>
            <Badge :label="r.sync_status" variant="subtle" size="sm" />
          </div>
        </div>
        <div v-else class="flex flex-col items-center py-6 text-ink-gray-4">
          <FeatherIcon name="file-text" class="h-7 w-7 mb-2" />
          <p class="text-xs">No forms submitted</p>
        </div>
      </div>

    </div>
  </div>
  <div v-else class="flex h-full items-center justify-center">
    <Spinner class="h-6 w-6 text-ink-gray-4" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import dayjs from 'dayjs'

const props = defineProps({ visitId: String })
const visit = ref(null)
const responses = ref([])

onMounted(async () => {
  const [v, r] = await Promise.all([
    frappe.call({ method: 'frappe.client.get', args: { doctype: 'SFA Visit', name: props.visitId } }),
    frappe.call({ method: 'frappe.client.get_list', args: {
      doctype: 'SFA Form Response',
      filters: { visit: props.visitId },
      fields: ['name', 'form_template', 'response_date', 'sync_status'],
    }}),
  ])
  visit.value = v.message
  responses.value = r.message || []
})

const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'
const formatTime = (t) => t ? dayjs(t).format('HH:mm') : '—'
const statusVariant = (s) => ({ 'In Progress': 'success', 'Completed': 'info', 'Planned': 'subtle', 'Cancelled': 'danger' })[s] || 'subtle'
</script>
