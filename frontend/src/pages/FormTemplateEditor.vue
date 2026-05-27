<template>
  <div class="flex h-full flex-col overflow-hidden">

    <!-- Top bar -->
    <div class="flex items-center gap-3 border-b border-outline-gray-2 bg-surface-white px-4 py-2.5 shrink-0">
      <Button variant="ghost" size="sm" @click="$router.push('/form-templates')">
        <template #prefix><FeatherIcon name="arrow-left" class="h-3.5 w-3.5" /></template>
        Templates
      </Button>
      <span class="text-ink-gray-3">/</span>
      <span class="text-sm font-medium text-ink-gray-8">
        {{ isEditing ? (templateName || 'Edit Template') : 'New Template' }}
      </span>
      <div class="flex-1" />
      <Button variant="ghost" size="sm" @click="previewForm">
        <template #prefix><FeatherIcon name="eye" class="h-3.5 w-3.5" /></template>
        Preview
      </Button>
      <Button variant="solid" size="sm" :loading="saving" @click="saveForm">
        <template #prefix><FeatherIcon name="check" class="h-3.5 w-3.5" /></template>
        {{ saving ? 'Saving...' : 'Save' }}
      </Button>
    </div>

    <!-- Meta bar -->
    <div class="flex items-end gap-4 border-b border-outline-gray-2 bg-surface-gray-1 px-4 py-2.5 shrink-0 flex-wrap">
      <div class="flex flex-col gap-1 flex-[2] min-w-[200px]">
        <label class="text-[10px] font-semibold text-ink-gray-5 uppercase tracking-wide">Template Name *</label>
        <TextInput v-model="templateName" placeholder="e.g. Outlet Audit Form" size="sm" />
      </div>
      <div class="flex flex-col gap-1 flex-1 min-w-[140px]">
        <label class="text-[10px] font-semibold text-ink-gray-5 uppercase tracking-wide">Category</label>
        <FormControl type="select" v-model="category" :options="categoryOptions" size="sm" />
      </div>
      <div class="flex flex-col gap-1 flex-1 min-w-[160px]">
        <label class="text-[10px] font-semibold text-ink-gray-5 uppercase tracking-wide">Trigger</label>
        <FormControl type="select" v-model="trigger" :options="triggerOptions" size="sm" />
      </div>
      <div class="flex items-center gap-4 pb-0.5">
        <label class="flex items-center gap-1.5 cursor-pointer select-none">
          <input type="checkbox" v-model="isMandatory" class="rounded border-outline-gray-3" />
          <span class="text-sm text-ink-gray-7">Mandatory</span>
        </label>
        <label class="flex items-center gap-1.5 cursor-pointer select-none">
          <input type="checkbox" v-model="isActive" class="rounded border-outline-gray-3" />
          <span class="text-sm text-ink-gray-7">Active</span>
        </label>
      </div>
    </div>

    <!-- Survey Creator -->
    <div class="flex-1 overflow-hidden min-h-0">
      <SurveyCreatorComponent :model="creatorModel" />
    </div>

    <!-- Preview Dialog -->
    <Dialog v-model="showPreview" :options="{ title: 'Form Preview', size: 'xl' }">
      <template #body-content>
        <div class="max-h-[70vh] overflow-y-auto p-2">
          <SurveyComponent v-if="previewModel" :model="previewModel" />
        </div>
      </template>
    </Dialog>

  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
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

const categoryOptions = [
  { label: 'Select Category', value: '' },
  { label: 'Outlet Audit', value: 'Outlet Audit' },
  { label: 'Market Survey', value: 'Market Survey' },
  { label: 'Competitor Check', value: 'Competitor Check' },
  { label: 'Merchandising', value: 'Merchandising' },
  { label: 'Customer Feedback', value: 'Customer Feedback' },
  { label: 'Custom', value: 'Custom' },
]

const triggerOptions = [
  { label: 'Visit Close (Mandatory)', value: 'visit_close' },
  { label: 'Visit Close (Optional)', value: 'visit_optional' },
  { label: 'Manual Assignment', value: 'manual' },
  { label: 'Scheduled', value: 'scheduled' },
]

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
      const res = await frappe.call({
        method: 'frappe.client.get',
        args: { doctype: 'SFA Form Template', name: props.templateId },
      })
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
        } catch {}
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
    frappe.show_alert({ message: 'Please enter a template name', indicator: 'red' })
    return
  }
  saving.value = true
  try {
    const doc = {
      doctype: 'SFA Form Template',
      template_name: templateName.value.trim(),
      category: category.value,
      trigger_point: trigger.value,
      is_active: isActive.value ? 1 : 0,
      is_mandatory: isMandatory.value ? 1 : 0,
      survey_json: JSON.stringify(creatorModel.JSON),
    }
    if (isEditing.value && props.templateId) {
      doc.name = props.templateId
      if (docModified.value) doc.modified = docModified.value
      const res = await frappe.call({ method: 'frappe.client.save', args: { doc } })
      if (res?.message?.modified) docModified.value = res.message.modified
    } else {
      doc.version = 1
      await frappe.call({ method: 'frappe.client.insert', args: { doc } })
    }
    frappe.show_alert({ message: 'Saved successfully', indicator: 'green' })
    router.push('/form-templates')
  } catch (err) {
    frappe.show_alert({ message: 'Save failed: ' + (err?.message || err), indicator: 'red' })
  } finally {
    saving.value = false
  }
}
</script>

<style>
.svc-creator__banner { display: none !important; }
.svc-footer-bar { display: none !important; }
</style>
