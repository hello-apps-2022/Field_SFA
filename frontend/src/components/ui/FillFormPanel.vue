<template>
  <SlidePanel
    :model-value="modelValue"
    :title="panelTitle"
    :saving="submitting"
    :save-label="panelSaveLabel"
    width="600px"
    @update:model-value="$emit('update:modelValue', $event)"
    @save="handleSave"
  >
    <!-- Back button in header area via subtitle slot workaround -->
    <template v-if="step === 'fill'">
      <button
        class="mb-4 flex items-center gap-1.5 text-xs text-gray-400 hover:text-gray-700 transition-colors"
        @click="step = 'select'; surveyModel = null; submitError = ''"
      >
        <FeatherIcon name="arrow-left" class="h-3.5 w-3.5" /> Back to template selection
      </button>
    </template>

    <template v-if="step === 'review'">
      <button
        class="mb-4 flex items-center gap-1.5 text-xs text-gray-400 hover:text-gray-700 transition-colors"
        @click="step = 'fill'; submitError = ''"
      >
        <FeatherIcon name="arrow-left" class="h-3.5 w-3.5" /> Back to edit answers
      </button>
    </template>

    <!-- Step 1: Select template -->
    <div v-if="step === 'select'" class="space-y-4">
      <p class="text-sm text-gray-500">Filling form for <strong>{{ customerName }}</strong>.</p>

      <div>
        <label class="mb-1.5 block text-xs font-medium text-gray-600">
          Form Template <span class="text-red-500">*</span>
        </label>

        <div v-if="loadingTemplates" class="flex h-10 items-center gap-2 rounded-md border border-gray-200 bg-gray-50 px-3 text-sm text-gray-400">
          <FeatherIcon name="loader" class="h-3.5 w-3.5 animate-spin" /> Loading...
        </div>

        <div v-else-if="!templates.length" class="flex h-10 items-center gap-2 rounded-md border border-gray-200 bg-gray-50 px-3 text-sm text-gray-400">
          No active templates —
          <router-link to="/form-templates" class="text-blue-500 hover:underline">create one</router-link>
        </div>

        <div v-else class="relative">
          <div class="relative">
            <FeatherIcon name="search" class="absolute left-3 top-2.5 h-3.5 w-3.5 text-gray-400 pointer-events-none" />
            <input
              v-model="templateSearch"
              type="text"
              placeholder="Search templates..."
              class="w-full border border-gray-200 bg-white py-2 pl-8 pr-3 text-sm focus:border-gray-400 focus:outline-none"
              :class="dropdownOpen ? 'rounded-t-md' : 'rounded-md'"
              @focus="dropdownOpen = true"
              @blur="onSearchBlur"
            />
            <div
              v-if="selectedTemplate && !dropdownOpen"
              class="absolute inset-0 flex cursor-pointer items-center gap-2 rounded-md border border-gray-200 bg-white px-3"
              @click="dropdownOpen = true; templateSearch = ''"
            >
              <div class="flex h-6 w-6 shrink-0 items-center justify-center rounded" :class="catColor(selectedTemplate.category)">
                <FeatherIcon :name="catIcon(selectedTemplate.category)" class="h-3 w-3 text-white" />
              </div>
              <span class="flex-1 truncate text-sm font-medium text-gray-900">{{ selectedTemplate.template_name }}</span>
              <span class="text-xs text-gray-400">{{ selectedTemplate.category || 'General' }}</span>
              <button class="shrink-0 text-gray-400 hover:text-gray-700" @click.stop="selectedTemplate = null; templateSearch = ''; dropdownOpen = true">
                <FeatherIcon name="x" class="h-3.5 w-3.5" />
              </button>
            </div>
          </div>

          <div v-if="dropdownOpen" class="absolute z-50 max-h-60 w-full overflow-y-auto rounded-b-md border border-t-0 border-gray-200 bg-white shadow-lg">
            <div
              v-for="t in filteredTemplates" :key="t.name"
              class="flex cursor-pointer items-center gap-3 px-3 py-2.5 hover:bg-gray-50"
              @mousedown.prevent="selectTemplate(t)"
            >
              <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded" :class="catColor(t.category)">
                <FeatherIcon :name="catIcon(t.category)" class="h-3.5 w-3.5 text-white" />
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900">{{ t.template_name }}</p>
                <p class="text-xs text-gray-400">{{ t.category || 'General' }} · {{ t.trigger_point_label }}</p>
              </div>
              <span v-if="t.is_mandatory" class="shrink-0 rounded-full bg-red-50 px-2 py-0.5 text-xs text-red-600">Required</span>
            </div>
            <div v-if="!filteredTemplates.length" class="px-3 py-3 text-sm italic text-gray-400">
              No templates match "{{ templateSearch }}"
            </div>
          </div>
        </div>
      </div>

      <FormField
        v-model="visitLink"
        label="Link to Visit (optional)"
        type="select"
        :options="visitOptions"
        help="Associate this response with a recent visit"
      />

      <p v-if="submitError" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{{ submitError }}</p>
    </div>

    <!-- Step 2: Fill the survey -->
    <div v-else-if="step === 'fill'" class="space-y-4">
      <!-- Context strip -->
      <div class="flex flex-wrap items-center gap-2 rounded-lg border border-gray-200 bg-gray-50 px-3 py-2.5 text-sm text-gray-600">
        <div class="flex h-6 w-6 items-center justify-center rounded" :class="catColor(selectedTemplate?.category)">
          <FeatherIcon :name="catIcon(selectedTemplate?.category)" class="h-3 w-3 text-white" />
        </div>
        <span class="font-medium">{{ selectedTemplate?.template_name }}</span>
        <span class="text-gray-300">·</span>
        <span>{{ customerName }}</span>
        <span class="text-gray-300">·</span>
        <span class="text-gray-500">{{ currentSalesPerson || currentUserFullName }}</span>
      </div>

      <div v-if="surveyModel" class="survey-wrapper">
        <SurveyComponent :model="surveyModel" />
      </div>
      <div v-else class="flex justify-center py-8">
        <FeatherIcon name="loader" class="h-5 w-5 animate-spin text-gray-400" />
      </div>

      <p v-if="submitError" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{{ submitError }}</p>
    </div>

    <!-- Step 3: Review before submit -->
    <div v-else-if="step === 'review'" class="space-y-4">
      <div class="rounded-xl border border-green-100 bg-green-50 px-4 py-3">
        <p class="text-sm font-medium text-green-800">Review your answers before submitting</p>
        <p class="text-xs text-green-600 mt-0.5">Click "Back to edit answers" above if you need to make changes.</p>
      </div>

      <!-- Summary card -->
      <div class="rounded-xl border border-gray-200 bg-white overflow-hidden">
        <div class="border-b border-gray-100 bg-gray-50 px-4 py-2.5">
          <div class="flex items-center gap-2">
            <div class="flex h-6 w-6 items-center justify-center rounded" :class="catColor(selectedTemplate?.category)">
              <FeatherIcon :name="catIcon(selectedTemplate?.category)" class="h-3 w-3 text-white" />
            </div>
            <p class="text-sm font-semibold text-gray-900">{{ selectedTemplate?.template_name }}</p>
          </div>
          <div class="mt-1 flex flex-wrap gap-3 text-xs text-gray-400">
            <span class="flex items-center gap-1"><FeatherIcon name="user" class="h-3 w-3" />{{ customerName }}</span>
            <span class="flex items-center gap-1"><FeatherIcon name="user-check" class="h-3 w-3" />{{ currentSalesPerson || currentUserFullName }}</span>
            <span class="flex items-center gap-1"><FeatherIcon name="calendar" class="h-3 w-3" />{{ formattedNow }}</span>
            <span v-if="visitLink" class="flex items-center gap-1"><FeatherIcon name="map-pin" class="h-3 w-3" />{{ visitLink }}</span>
          </div>
        </div>
        <!-- Answers -->
        <div class="divide-y divide-gray-50 max-h-80 overflow-y-auto">
          <div v-for="(val, key) in reviewData" :key="key" class="flex items-start gap-3 px-4 py-2.5">
            <span class="w-40 shrink-0 text-xs text-gray-400 pt-0.5">{{ questionLabel(key) }}</span>
            <span class="flex-1 text-sm text-gray-800">{{ Array.isArray(val) ? val.join(', ') : String(val ?? '—') }}</span>
          </div>
          <div v-if="!Object.keys(reviewData).length" class="px-4 py-3 text-sm italic text-gray-400">No answers recorded</div>
        </div>
      </div>

      <p v-if="submitError" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{{ submitError }}</p>
    </div>
  </SlidePanel>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Model as SurveyModel } from 'survey-core'
import { SurveyComponent } from 'survey-vue3-ui'
import { getList, insertDoc } from '@/utils/frappe'
import SlidePanel from '@/components/ui/SlidePanel.vue'
import FormField from '@/components/ui/FormField.vue'
import dayjs from 'dayjs'
import 'survey-core/defaultV2.min.css'

const props = defineProps({
  modelValue: Boolean,
  customerName: String,
  customerDoc: Object,
  recentVisits: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:modelValue', 'submitted'])

const currentUser = window.frappe_boot?.user?.name || ''
const currentUserFullName = window.frappe_boot?.user?.full_name || currentUser
const currentSalesPerson = ref('')

const step = ref('select') // 'select' | 'fill' | 'review'
const templates = ref([])
const selectedTemplate = ref(null)
const templateSearch = ref('')
const dropdownOpen = ref(false)
const loadingTemplates = ref(false)
const surveyModel = ref(null)
const submitting = ref(false)
const submitError = ref('')
const visitLink = ref('')
const reviewData = ref({})

const formattedNow = dayjs().format('D MMM YYYY HH:mm')

const panelTitle = computed(() => ({
  select: 'Fill Form',
  fill: selectedTemplate.value?.template_name || 'Fill Form',
  review: 'Review & Submit',
}[step.value] || 'Fill Form'))

const panelSaveLabel = computed(() => ({
  select: 'Next →',
  fill: 'Preview & Review →',
  review: 'Submit Form',
}[step.value] || 'Next'))

const filteredTemplates = computed(() => {
  const q = templateSearch.value.toLowerCase()
  if (!q) return templates.value
  return templates.value.filter(t =>
    t.template_name.toLowerCase().includes(q) ||
    (t.category || '').toLowerCase().includes(q)
  )
})

const visitOptions = computed(() => [
  { value: '', label: 'No visit' },
  ...props.recentVisits.map(v => ({
    value: v.name,
    label: `${dayjs(v.visit_date).format('D MMM')} · ${v.sales_person}`,
  })),
])

function questionLabel(name) {
  if (!surveyModel.value) return name
  const q = surveyModel.value.getQuestionByName(name)
  return q?.title || q?.name || name
}

function onSearchBlur() {
  window.setTimeout(() => { dropdownOpen.value = false }, 150)
}

function selectTemplate(t) {
  selectedTemplate.value = t
  templateSearch.value = ''
  dropdownOpen.value = false
}

const triggerLabels = {
  visit_close: 'Visit Close', visit_optional: 'Visit (Optional)',
  manual: 'Manual', scheduled: 'Scheduled',
}

async function loadTemplates() {
  loadingTemplates.value = true
  try {
    const data = await getList('SFA Form Template', {
      fields: ['name', 'template_name', 'category', 'trigger_point', 'is_mandatory', 'survey_json', 'version'],
      filters: { is_active: 1 },
      orderBy: 'is_mandatory desc, template_name asc',
      limit: 100,
    })
    templates.value = data.map(t => ({
      ...t,
      trigger_point_label: triggerLabels[t.trigger_point] || t.trigger_point || '',
    }))
  } catch (e) {
    console.error('Failed to load templates', e)
  } finally {
    loadingTemplates.value = false
  }
}

async function loadCurrentSalesPerson() {
  try {
    const emailPrefix = currentUser.split('@')[0].toLowerCase()
    const data = await getList('Sales Person', {
      fields: ['name'],
      filters: { is_group: 0 },
      limit: 200,
    })
    const match = data.find(sp => {
      const n = sp.name.toLowerCase()
      return n === currentUserFullName.toLowerCase() || n.includes(emailPrefix)
    })
    if (match) currentSalesPerson.value = match.name
  } catch {}
}

function buildSurvey(template) {
  try {
    const json = typeof template.survey_json === 'string'
      ? JSON.parse(template.survey_json)
      : template.survey_json || {
          pages: [{ elements: [{ type: 'text', name: 'q1', title: 'No questions defined yet' }] }]
        }
    const model = new SurveyModel(json)
    model.showCompletedPage = false
    return model
  } catch (e) {
    console.error('Survey build error', e)
    return null
  }
}

async function handleSave() {
  submitError.value = ''

  if (step.value === 'select') {
    if (!selectedTemplate.value) {
      submitError.value = 'Please select a form template'
      return
    }
    surveyModel.value = buildSurvey(selectedTemplate.value)
    step.value = 'fill'
    return
  }

  if (step.value === 'fill') {
    if (!surveyModel.value) return
    const valid = surveyModel.value.validate()
    if (!valid) { submitError.value = 'Please fill in all required fields'; return }
    // Capture current answers for review display
    reviewData.value = { ...surveyModel.value.data }
    step.value = 'review'
    return
  }

  if (step.value === 'review') {
    submitting.value = true
    try {
      const responseData = surveyModel.value.data
      const responseItems = Object.entries(responseData).map(([key, value]) => ({
        doctype: 'SFA Response Item',
        question_name: key,
        answer_value: Array.isArray(value) ? value.join(', ') : String(value ?? ''),
      }))

      await insertDoc({
        doctype: 'SFA Form Response',
        form_template: selectedTemplate.value.name,
        customer: props.customerDoc?.name || props.customerName,
        sales_person: currentSalesPerson.value || null,
        visit: visitLink.value || null,
        response_date: dayjs().format('YYYY-MM-DD HH:mm:ss'),
        sync_status: 'Synced',
        survey_version: selectedTemplate.value.version || 1,
        survey_response_json: JSON.stringify(responseData),
        response_items: responseItems,
      })

      emit('submitted')
      emit('update:modelValue', false)
    } catch (e) {
      submitError.value = e.message || 'Submission failed'
    } finally {
      submitting.value = false
    }
  }
}

watch(() => props.modelValue, (val) => {
  if (!val) {
    window.setTimeout(() => {
      step.value = 'select'
      selectedTemplate.value = null
      templateSearch.value = ''
      dropdownOpen.value = false
      surveyModel.value = null
      submitError.value = ''
      visitLink.value = ''
      reviewData.value = {}
    }, 300)
  } else if (!templates.value.length) {
    loadTemplates()
  }
})

const catIcon = (c) => ({ 'Outlet Audit': 'clipboard', 'Market Survey': 'bar-chart-2', 'Competitor Check': 'target', 'Merchandising': 'package', 'Customer Feedback': 'message-square' })[c] || 'file-text'
const catColor = (c) => ({ 'Outlet Audit': 'bg-blue-500', 'Market Survey': 'bg-green-500', 'Competitor Check': 'bg-red-500', 'Merchandising': 'bg-yellow-500', 'Customer Feedback': 'bg-purple-500' })[c] || 'bg-gray-400'

onMounted(() => loadCurrentSalesPerson())
</script>

<style>
.survey-wrapper .sd-root-modern { --sd-base-padding: 0; font-family: inherit !important; }
.survey-wrapper .sd-container-modern { box-shadow: none !important; border: 1px solid #e5e7eb; border-radius: 12px; overflow: hidden; }
.survey-wrapper .sd-title { display: none !important; }
.survey-wrapper .sd-body { padding: 16px !important; }
.survey-wrapper .sd-question__title { font-size: 13px !important; font-weight: 500 !important; color: #374151 !important; }
.survey-wrapper .sd-input { border-radius: 8px !important; border-color: #e5e7eb !important; font-size: 13px !important; }
.survey-wrapper .sd-btn--action { background: #111827 !important; border-radius: 8px !important; }
</style>
