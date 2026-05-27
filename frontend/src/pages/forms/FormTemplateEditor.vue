<template>
  <div class="flex h-full flex-col overflow-hidden">
    <PageHeader :title="isNew ? 'New Form Template' : (templateName || 'Edit Template')" back-to="/form-templates" back-label="Templates">
      <Btn icon="eye" @click="preview">Preview</Btn>
      <Btn variant="solid" :loading="saving" icon="check" @click="saveForm">Save</Btn>
    </PageHeader>

    <!-- Meta bar -->
    <div class="flex shrink-0 items-end gap-3 border-b border-gray-100 bg-gray-50 px-4 py-2.5 flex-wrap">
      <div class="flex flex-col gap-1 flex-[2] min-w-[200px]">
        <label class="text-[10px] font-semibold uppercase tracking-wide text-gray-500">Template Name *</label>
        <input v-model="templateName" type="text" placeholder="e.g. Outlet Audit Form" class="h-8 rounded-md border border-gray-200 bg-white px-3 text-sm focus:border-gray-400 focus:outline-none" />
      </div>
      <div class="flex flex-col gap-1 flex-1 min-w-[140px]">
        <label class="text-[10px] font-semibold uppercase tracking-wide text-gray-500">Category</label>
        <select v-model="category" class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
          <option value="">Select…</option>
          <option>Outlet Audit</option><option>Market Survey</option><option>Competitor Check</option>
          <option>Merchandising</option><option>Customer Feedback</option><option>Custom</option>
        </select>
      </div>
      <div class="flex flex-col gap-1 flex-1 min-w-[160px]">
        <label class="text-[10px] font-semibold uppercase tracking-wide text-gray-500">Trigger</label>
        <select v-model="trigger" class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
          <option value="visit_close">Visit Close (Mandatory)</option>
          <option value="visit_optional">Visit Close (Optional)</option>
          <option value="manual">Manual</option>
          <option value="scheduled">Scheduled</option>
        </select>
      </div>
      <div class="flex items-center gap-4 pb-0.5 shrink-0">
        <label class="flex items-center gap-1.5 cursor-pointer text-sm text-gray-700 select-none">
          <input type="checkbox" v-model="isMandatory" class="rounded" /> Mandatory
        </label>
        <label class="flex items-center gap-1.5 cursor-pointer text-sm text-gray-700 select-none">
          <input type="checkbox" v-model="isActive" class="rounded" /> Active
        </label>
      </div>
    </div>

    <!-- SurveyJS Creator -->
    <div class="min-h-0 flex-1">
      <SurveyCreatorComponent :model="creator" />
    </div>

    <!-- Preview modal -->
    <div v-if="showPreview" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showPreview=false">
      <div class="flex h-[85vh] w-[90%] max-w-2xl flex-col overflow-hidden rounded-xl bg-white shadow-2xl">
        <div class="flex h-12 shrink-0 items-center justify-between border-b px-5">
          <p class="text-sm font-semibold">Form Preview</p>
          <button @click="showPreview=false" class="text-gray-400 hover:text-gray-700"><FeatherIcon name="x" class="h-4 w-4" /></button>
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
import { useRouter } from 'vue-router'
import { SurveyCreatorModel } from 'survey-creator-core'
import { SurveyCreatorComponent } from 'survey-creator-vue'
import { Model as SurveyModel } from 'survey-core'
import { SurveyComponent } from 'survey-vue3-ui'
import { getDoc, insertDoc, saveDoc } from '@/utils/frappe'
import { successToast, errorToast } from '@/utils/toast'
import PageHeader from '@/components/ui/PageHeader.vue'
import Btn from '@/components/ui/Btn.vue'

import 'survey-core/defaultV2.min.css'
import 'survey-creator-core/survey-creator-core.min.css'

const props = defineProps({ name: { type: String, default: null } })
const router = useRouter()
const isNew = !props.name

const templateName = ref('')
const category = ref('')
const trigger = ref('visit_close')
const isActive = ref(true)
const isMandatory = ref(false)
const saving = ref(false)
const showPreview = ref(false)
const previewModel = ref(null)
const docModified = ref(null)

const creator = new SurveyCreatorModel({ showLogicTab: true, showJSONEditorTab: true, isAutoSave: false, showThemeTab: false, allowEditSurveyTitle: false })

onMounted(async () => {
  if (!isNew) {
    try {
      const doc = await getDoc('SFA Form Template', props.name)
      templateName.value = doc.template_name || ''
      category.value = doc.category || ''
      trigger.value = doc.trigger_point || 'visit_close'
      isActive.value = !!doc.is_active
      isMandatory.value = !!doc.is_mandatory
      docModified.value = doc.modified
      if (doc.survey_json) {
        try { creator.JSON = typeof doc.survey_json === 'string' ? JSON.parse(doc.survey_json) : doc.survey_json } catch {}
      }
    } catch (e) { errorToast('Failed to load template') }
  }
})

onBeforeUnmount(() => creator.dispose())

function preview() {
  previewModel.value = new SurveyModel(creator.JSON)
  showPreview.value = true
}

async function saveForm() {
  if (!templateName.value.trim()) { errorToast('Template name is required'); return }
  saving.value = true
  try {
    const doc = {
      doctype: 'SFA Form Template',
      template_name: templateName.value.trim(),
      category: category.value, trigger_point: trigger.value,
      is_active: isActive.value ? 1 : 0, is_mandatory: isMandatory.value ? 1 : 0,
      survey_json: JSON.stringify(creator.JSON),
    }
    if (!isNew) {
      doc.name = props.name
      if (docModified.value) doc.modified = docModified.value
      const res = await saveDoc(doc)
      if (res?.modified) docModified.value = res.modified
    } else {
      doc.version = 1
      const res = await insertDoc(doc)
      if (res?.name) router.replace('/form-templates/' + res.name)
    }
    successToast('Template saved')
  } catch (e) { errorToast(e.message || 'Save failed') }
  finally { saving.value = false }
}
</script>

<style>
.svc-creator__banner { display: none !important; }
.svc-footer-bar { display: none !important; }
</style>
