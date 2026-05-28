<template>
  <div class="flex h-full flex-col overflow-hidden">

    <!-- Top bar -->
    <div class="flex h-11 shrink-0 items-center gap-3 border-b border-gray-200 bg-white px-4">
      <button
        class="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800 transition-colors"
        @click="$router.push('/form-templates')"
      >
        <FeatherIcon name="arrow-left" class="h-3.5 w-3.5" />
        Templates
      </button>
      <span class="text-gray-300">/</span>
      <span class="text-sm font-medium text-gray-800">
        {{ isEditing ? (templateName || 'Edit Template') : 'New Template' }}
      </span>
      <div class="flex-1" />
      <button
        class="flex h-8 items-center gap-1.5 rounded-md border border-gray-200 px-3 text-sm text-gray-600 hover:bg-gray-50 transition-colors"
        @click="previewForm"
      >
        <FeatherIcon name="eye" class="h-3.5 w-3.5" />
        Preview
      </button>
      <button
        class="flex h-8 items-center gap-1.5 rounded-md bg-gray-900 px-3 text-sm font-medium text-white hover:bg-gray-700 disabled:opacity-50 transition-colors"
        :disabled="saving"
        @click="saveForm"
      >
        <FeatherIcon v-if="saving" name="loader" class="h-3.5 w-3.5 animate-spin" />
        <FeatherIcon v-else name="check" class="h-3.5 w-3.5" />
        {{ saving ? 'Saving...' : 'Save' }}
      </button>
    </div>

    <!-- Meta bar -->
    <div class="flex shrink-0 items-end gap-4 border-b border-gray-200 bg-gray-50 px-4 py-2.5 flex-wrap">
      <div class="flex flex-col gap-1 flex-[2] min-w-[200px]">
        <label class="text-[10px] font-semibold uppercase tracking-wide text-gray-500">Template Name *</label>
        <input
          v-model="templateName"
          type="text"
          placeholder="e.g. Outlet Audit Form"
          class="h-8 rounded-md border border-gray-200 bg-white px-3 text-sm focus:border-gray-400 focus:outline-none"
        />
      </div>
      <div class="flex flex-col gap-1 flex-1 min-w-[140px]">
        <label class="text-[10px] font-semibold uppercase tracking-wide text-gray-500">Category</label>
        <select v-model="category" class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:border-gray-400 focus:outline-none">
          <option value="">Select Category</option>
          <option>Outlet Audit</option>
          <option>Market Survey</option>
          <option>Competitor Check</option>
          <option>Merchandising</option>
          <option>Customer Feedback</option>
          <option>Custom</option>
        </select>
      </div>
      <div class="flex flex-col gap-1 flex-1 min-w-[160px]">
        <label class="text-[10px] font-semibold uppercase tracking-wide text-gray-500">Trigger</label>
        <select v-model="trigger" class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:border-gray-400 focus:outline-none">
          <option value="visit_close">Visit Close (Mandatory)</option>
          <option value="visit_optional">Visit Close (Optional)</option>
          <option value="manual">Manual Assignment</option>
          <option value="scheduled">Scheduled</option>
        </select>
      </div>
      <div class="flex items-center gap-4 pb-0.5 shrink-0">
        <label class="flex items-center gap-1.5 cursor-pointer select-none text-sm text-gray-700">
          <input type="checkbox" v-model="isMandatory" class="rounded" />
          Mandatory
        </label>
        <label class="flex items-center gap-1.5 cursor-pointer select-none text-sm text-gray-700">
          <input type="checkbox" v-model="isActive" class="rounded" />
          Active
        </label>
      </div>
    </div>

    <!-- SurveyJS Creator — takes all remaining height -->
    <div class="min-h-0 flex-1">
      <SurveyCreatorComponent :model="creatorModel" />
    </div>

    <!-- Preview modal -->
    <div v-if="showPreview" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showPreview = false">
      <div class="flex h-[85vh] w-[90%] max-w-2xl flex-col rounded-xl bg-white shadow-2xl overflow-hidden">
        <div class="flex h-11 shrink-0 items-center justify-between border-b border-gray-200 px-5">
          <p class="text-sm font-semibold text-gray-900">Form Preview</p>
          <button class="text-gray-400 hover:text-gray-700" @click="showPreview = false">
            <FeatherIcon name="x" class="h-4 w-4" />
          </button>
        </div>
        <div class="flex-1 overflow-y-auto p-6">
          <SurveyComponent v-if="previewModel" :model="previewModel" />
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { call } from '@/utils/frappe'
import { useRouter } from 'vue-router'
import { SurveyCreatorModel } from 'survey-creator-core'
import { SurveyCreatorComponent } from 'survey-creator-vue'
import { Model as SurveyModel } from 'survey-core'
import { SurveyComponent } from 'survey-vue3-ui'

import 'survey-core/defaultV2.min.css'
import 'survey-creator-core/survey-creator-core.min.css'

const props = defineProps({ templateId: { type: String, default: null } })
const router = useRouter()

const templateName = ref('')
const category = ref('')
const trigger = ref('visit_close')
const isActive = ref(true)
const isMandatory = ref(false)
const saving = ref(false)
const showPreview = ref(false)
const previewModel = ref(null)
const docModified = ref(null)
const isEditing = ref(!!props.templateId)

const creatorModel = new SurveyCreatorModel({
  showLogicTab: true,
  showTranslationTab: false,
  showJSONEditorTab: true,
  isAutoSave: false,
  showThemeTab: false,
  allowEditSurveyTitle: false,
})

onMounted(async () => {
  if (props.templateId) {
    try {
      const res = await call('frappe.client.get', { doctype: 'SFA Form Template', name: props.templateId })
      const doc = res.message
      templateName.value = doc.template_name || ''
      category.value = doc.category || ''
      trigger.value = doc.trigger_point || 'visit_close'
      isActive.value = !!doc.is_active
      isMandatory.value = !!doc.is_mandatory
      docModified.value = doc.modified

      if (doc.survey_json) {
        try {
          creatorModel.JSON = typeof doc.survey_json === 'string'
            ? JSON.parse(doc.survey_json)
            : doc.survey_json
        } catch (e) { console.error('JSON parse error:', e) }
      }
    } catch (e) {
      frappe.show_alert({ message: 'Failed to load template', indicator: 'red' })
    }
  }
})

onBeforeUnmount(() => creatorModel.dispose())

function previewForm() {
  previewModel.value = new SurveyModel(creatorModel.JSON)
  showPreview.value = true
}

async function saveForm() {
  if (!templateName.value.trim()) {
    frappe.show_alert({ message: 'Template name is required', indicator: 'red' })
    return
  }
  saving.value = true
  try {
    const surveyJson = creatorModel.JSON
    // Ensure survey has at least a title
    if (!surveyJson.title) surveyJson.title = templateName.value

    const doc = {
      doctype: 'SFA Form Template',
      template_name: templateName.value.trim(),
      category: category.value,
      trigger_point: trigger.value,
      is_active: isActive.value ? 1 : 0,
      is_mandatory: isMandatory.value ? 1 : 0,
      survey_json: JSON.stringify(surveyJson),
    }

    if (isEditing.value && props.templateId) {
      doc.name = props.templateId
      // Pass modified to avoid conflict error from after_save question sync
      if (docModified.value) doc.modified = docModified.value
      const result = await call('frappe.client.save', { doc })
      // Refresh modified from server response to avoid conflict on next save
      if (result?.message?.modified) docModified.value = result.message.modified
    } else {
      doc.version = 1
      const result = await call('frappe.client.insert', { doc })
      if (result?.message?.name) {
        // Switch to edit mode after first save
        isEditing.value = true
        docModified.value = result.message.modified
        router.replace('/form-templates/' + result.message.name)
      }
    }
    frappe.show_alert({ message: 'Template saved', indicator: 'green' })
  } catch (err) {
    console.error('Save error:', err)
    const msg = err?.message || err?.exc || 'Save failed'
    frappe.show_alert({ message: msg, indicator: 'red' })
  } finally {
    saving.value = false
  }
}
</script>

<style>
/* SurveyJS overrides */
.svc-creator__banner { display: none !important; }
.svc-footer-bar { display: none !important; }
.svc-creator { height: 100% !important; }
.svc-full-container { height: 100% !important; }
</style>
