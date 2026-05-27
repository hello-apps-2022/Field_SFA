<template>
  <SlidePanel
    :model-value="modelValue"
    :title="response?.form_template || 'Form Response'"
    width="600px"
    save-label=""
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <!-- Hide the save button by overriding footer -->
    <template #default>
      <div v-if="loading" class="flex justify-center py-12">
        <FeatherIcon name="loader" class="h-6 w-6 animate-spin text-gray-400" />
      </div>

      <div v-else-if="response" class="space-y-4">
        <!-- Meta -->
        <div class="rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 space-y-1.5">
          <div class="flex items-center gap-2 text-xs text-gray-500">
            <FeatherIcon name="file-text" class="h-3.5 w-3.5" />
            <span class="font-medium text-gray-700">{{ response.form_template }}</span>
          </div>
          <div class="flex flex-wrap gap-4 text-xs text-gray-400">
            <span class="flex items-center gap-1">
              <FeatherIcon name="user" class="h-3 w-3" />
              {{ response.sales_person || 'Unknown' }}
            </span>
            <span class="flex items-center gap-1">
              <FeatherIcon name="users" class="h-3 w-3" />
              {{ response.customer }}
            </span>
            <span class="flex items-center gap-1">
              <FeatherIcon name="calendar" class="h-3 w-3" />
              {{ formatDatetime(response.response_date) }}
            </span>
            <router-link
              v-if="response.visit"
              :to="'/visits/' + response.visit"
              class="flex items-center gap-1 text-blue-400 hover:text-blue-600 hover:underline"
              @click="$emit('update:modelValue', false)"
            >
              <FeatherIcon name="map-pin" class="h-3 w-3" />
              {{ response.visit }}
            </router-link>
          </div>
          <div class="flex items-center gap-1.5">
            <StatusBadge :status="response.sync_status" />
            <span class="text-xs text-gray-400">v{{ response.survey_version || 1 }}</span>
          </div>
        </div>

        <!-- Answers -->
        <div>
          <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-400">Responses</p>

          <!-- From response_items if available -->
          <div v-if="responseItems.length" class="rounded-xl border border-gray-200 bg-white overflow-hidden divide-y divide-gray-50">
            <div v-for="item in responseItems" :key="item.question_name" class="flex items-start px-4 py-3 gap-3">
              <span class="w-44 shrink-0 text-xs text-gray-400 pt-0.5 leading-relaxed">{{ item.question_name }}</span>
              <span class="flex-1 text-sm text-gray-800 break-words">{{ item.answer_value || '—' }}</span>
            </div>
          </div>

          <!-- Fallback: parse survey_response_json -->
          <div v-else-if="parsedJson && Object.keys(parsedJson).length" class="rounded-xl border border-gray-200 bg-white overflow-hidden divide-y divide-gray-50">
            <div v-for="(val, key) in parsedJson" :key="key" class="flex items-start px-4 py-3 gap-3">
              <span class="w-44 shrink-0 text-xs text-gray-400 pt-0.5">{{ key }}</span>
              <span class="flex-1 text-sm text-gray-800 break-words">{{ Array.isArray(val) ? val.join(', ') : String(val ?? '—') }}</span>
            </div>
          </div>

          <div v-else class="rounded-xl border border-dashed border-gray-200 py-8 text-center text-sm text-gray-400">
            No response data found
          </div>
        </div>
      </div>
    </template>
  </SlidePanel>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { call } from '@/utils/frappe'
import SlidePanel from '@/components/ui/SlidePanel.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import dayjs from 'dayjs'

const props = defineProps({
  modelValue: Boolean,
  responseName: String,
})
const emit = defineEmits(['update:modelValue'])

const response = ref(null)
const loading = ref(false)

const responseItems = computed(() => response.value?.response_items || [])

const parsedJson = computed(() => {
  if (!response.value?.survey_response_json) return {}
  try {
    return JSON.parse(response.value.survey_response_json)
  } catch { return {} }
})

async function load() {
  if (!props.responseName) return
  loading.value = true
  try {
    const data = await call('frappe.client.get', {
      doctype: 'SFA Form Response',
      name: props.responseName,
    })
    response.value = data.message
  } catch (e) {
    console.error('Failed to load response', e)
  } finally {
    loading.value = false
  }
}

watch(() => props.responseName, (val) => { if (val && props.modelValue) load() })
watch(() => props.modelValue, (val) => { if (val && props.responseName) load() })

const formatDatetime = (d) => d ? dayjs(d).format('D MMM YYYY HH:mm') : '—'
</script>
