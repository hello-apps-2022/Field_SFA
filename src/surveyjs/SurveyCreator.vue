<template>
  <div class="survey-creator-container sfa-desk survey-creator-theme">
    <div class="creator-header">
      <div class="creator-title">
        <h2>{{ isEditing ? 'Edit Form Template' : 'New Form Template' }}</h2>
        <span class="creator-subtitle">{{ templateName || 'Untitled Form' }}</span>
      </div>
      <div class="creator-actions">
        <button class="sfa-btn sfa-btn--secondary" @click="previewForm">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M1 7s2-5 6-5 6 5 6 5-2 5-6 5-6-5-6-5z" stroke="currentColor" stroke-width="1.5"/>
            <circle cx="7" cy="7" r="2" stroke="currentColor" stroke-width="1.5"/>
          </svg>
          Preview
        </button>
        <button class="sfa-btn sfa-btn--primary" @click="saveForm" :disabled="saving">
          <svg v-if="saving" class="spinner" width="14" height="14" viewBox="0 0 14 14">
            <circle cx="7" cy="7" r="6" stroke="currentColor" stroke-width="1.5" fill="none" stroke-dasharray="20" stroke-dashoffset="10"/>
          </svg>
          <svg v-else width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M2 7l4 4 6-8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          {{ saving ? 'Saving...' : 'Save Template' }}
        </button>
      </div>
    </div>

    <div class="creator-meta">
      <div class="meta-field">
        <label>Template Name</label>
        <input v-model="templateName" type="text" placeholder="e.g., Outlet Audit Form" />
      </div>
      <div class="meta-field">
        <label>Category</label>
        <select v-model="templateCategory">
          <option value="">Select Category</option>
          <option value="audit">Outlet Audit</option>
          <option value="survey">Market Survey</option>
          <option value="competitor">Competitor Check</option>
          <option value="merchandising">Merchandising</option>
          <option value="feedback">Customer Feedback</option>
          <option value="custom">Custom</option>
        </select>
      </div>
      <div class="meta-field">
        <label>Trigger</label>
        <select v-model="templateTrigger">
          <option value="visit_close">Visit Close (Mandatory)</option>
          <option value="visit_optional">Visit Close (Optional)</option>
          <option value="manual">Manual Assignment</option>
          <option value="scheduled">Scheduled</option>
        </select>
      </div>
      <div class="meta-field meta-field--checkbox">
        <label class="checkbox-label">
          <input v-model="isActive" type="checkbox" />
          <span>Active</span>
        </label>
      </div>
    </div>

    <div class="creator-body">
      <div ref="creatorElement" class="survey-creator"></div>
    </div>

    <!-- Preview Modal -->
    <div v-if="showPreview" class="preview-modal" @click.self="showPreview = false">
      <div class="preview-content">
        <div class="preview-header">
          <h3>Form Preview</h3>
          <button class="sfa-btn sfa-btn--ghost sfa-btn--sm" @click="showPreview = false">Close</button>
        </div>
        <div ref="previewElement" class="survey-preview"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue';
import { Model } from 'survey-core';
import { SurveyCreatorModel } from 'survey-creator-core';

// Import mobile renderer mappings (for reference, not for Creator registration)
import { mobileRenderers } from './customQuestions';

const props = defineProps({
  templateId: { type: String, default: null },
  initialData: { type: Object, default: null }
});

const emit = defineEmits(['save', 'cancel']);

const creatorElement = ref(null);
const previewElement = ref(null);
const creator = ref(null);

const templateName = ref('');
const templateCategory = ref('');
const templateTrigger = ref('visit_close');
const isActive = ref(true);
const isEditing = ref(false);
const saving = ref(false);
const showPreview = ref(false);

// SurveyJS Creator options - uses ALL standard question types
// No custom types registered - SurveyJS Creator has them all built-in
const creatorOptions = {
    showLogicTab: true,
    showTranslationTab: true,
    showJSONEditorTab: true,
    showTestSurveyTab: false,
    isAutoSave: false,
    showThemeTab: false,
    allowChangeThemeInPreview: false,
    showPagesInTestSurveyTab: true,
    showSimulatorInTestSurveyTab: false,
    showInvisibleElementsInPreview: true,
    showToolbox: true,
    showSidebar: true,
    allowEditSurveyTitle: false,
    allowEditSurveyDescription: false,
    // No custom questionTypes specified - uses all SurveyJS defaults
};

onMounted(() => {
    const creatorModel = new SurveyCreatorModel(creatorOptions);

    // Load existing template if editing
    if (props.initialData) {
        isEditing.value = true;
        templateName.value = props.initialData.template_name || '';
        templateCategory.value = props.initialData.category || '';
        templateTrigger.value = props.initialData.trigger_point || 'visit_close';
        isActive.value = props.initialData.is_active !== 0;

        if (props.initialData.survey_json) {
            try {
                const json = typeof props.initialData.survey_json === 'string' 
                    ? JSON.parse(props.initialData.survey_json) 
                    : props.initialData.survey_json;
                creatorModel.JSON = json;
            } catch (e) {
                console.error('Failed to parse survey JSON', e);
            }
        }
    }

    creatorModel.render(creatorElement.value);
    creator.value = creatorModel;
});

onBeforeUnmount(() => {
    if (creator.value) {
        creator.value.dispose();
    }
});

function previewForm() {
    if (!creator.value) return;
    const json = creator.value.JSON;
    const survey = new Model(json);
    showPreview.value = true;
    nextTick(() => {
        if (previewElement.value) {
            survey.render(previewElement.value);
        }
    });
}

async function saveForm() {
    if (!creator.value) return;
    if (!templateName.value.trim()) {
        frappe.show_alert({ message: 'Please enter a template name', indicator: 'red' });
        return;
    }

    saving.value = true;
    try {
        const surveyJson = JSON.stringify(creator.value.JSON);
        const doc = {
            doctype: 'SFA Form Template',
            template_name: templateName.value,
            category: templateCategory.value,
            trigger_point: templateTrigger.value,
            is_active: isActive.value ? 1 : 0,
            survey_json: surveyJson,
            version: isEditing.value ? (props.initialData.version || 1) + 1 : 1
        };

        if (isEditing.value && props.templateId) {
            doc.name = props.templateId;
            await frappe.call({
                method: 'frappe.client.save',
                args: { doc }
            });
        } else {
            await frappe.call({
                method: 'frappe.client.insert',
                args: { doc }
            });
        }

        frappe.show_alert({ message: 'Form template saved successfully', indicator: 'green' });
        emit('save');
    } catch (err) {
        console.error('Save failed', err);
        frappe.show_alert({ message: 'Failed to save template', indicator: 'red' });
    } finally {
        saving.value = false;
    }
}
</script>

<style scoped>
.survey-creator-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px);
  background: #f4f5f6;
}
.creator-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e2e6e9;
}
.creator-title h2 {
  font-size: 18px;
  font-weight: 600;
  color: #1f272e;
  margin: 0;
}
.creator-subtitle {
  font-size: 12px;
  color: #a0a0a0;
  margin-top: 2px;
}
.creator-actions {
  display: flex;
  gap: 8px;
}
.creator-meta {
  display: flex;
  gap: 16px;
  padding: 12px 24px;
  background: white;
  border-bottom: 1px solid #e2e6e9;
  align-items: flex-end;
}
.meta-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}
.meta-field label {
  font-size: 11px;
  font-weight: 600;
  color: #687178;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.meta-field input,
.meta-field select {
  padding: 6px 10px;
  border: 1px solid #e2e6e9;
  border-radius: 6px;
  font-size: 13px;
  background: white;
}
.meta-field input:focus,
.meta-field select:focus {
  outline: none;
  border-color: #2490EF;
}
.meta-field--checkbox {
  flex: 0;
  padding-bottom: 6px;
}
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  cursor: pointer;
}
.creator-body {
  flex: 1;
  overflow: hidden;
}
.survey-creator {
  height: 100%;
}

/* Preview Modal */
.preview-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.preview-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #e2e6e9;
}
.preview-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}
.survey-preview {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.spinner {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>

<!-- Global styles for SurveyJS overrides -->
<style>
.survey-creator-theme .svc-creator__banner {
  display: none !important;
}
.survey-creator-theme .svc-tabbed-menu-item--active {
  color: #2490EF !important;
  border-bottom-color: #2490EF !important;
}
.survey-creator-theme .svc-btn {
  background: #2490EF !important;
}
</style>
