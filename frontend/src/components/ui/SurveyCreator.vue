<template>
  <div class="sfa-creator-wrapper">

    <div class="sfa-creator-topbar">
      <div class="sfa-creator-title">
        <span>{{ isEditing ? 'Edit Form Template' : 'New Form Template' }}</span>
        <span class="sfa-creator-subtitle">{{ templateName || 'Untitled Form' }}</span>
      </div>
      <div class="sfa-creator-actions">
        <button class="sfa-btn sfa-btn--secondary" @click="previewForm">Preview</button>
        <button class="sfa-btn sfa-btn--primary" @click="saveForm" :disabled="saving">
          {{ saving ? 'Saving...' : 'Save Template' }}
        </button>
      </div>
    </div>

    <div class="sfa-creator-meta">
      <div class="sfa-meta-field sfa-meta-field--wide">
        <label>Template Name *</label>
        <input v-model="templateName" type="text" placeholder="e.g., Outlet Audit Form" />
      </div>
      <div class="sfa-meta-field">
        <label>Category</label>
        <select v-model="templateCategory">
          <option value="">Select Category</option>
          <option value="Outlet Audit">Outlet Audit</option>
          <option value="Market Survey">Market Survey</option>
          <option value="Competitor Check">Competitor Check</option>
          <option value="Merchandising">Merchandising</option>
          <option value="Customer Feedback">Customer Feedback</option>
          <option value="Custom">Custom</option>
        </select>
      </div>
      <div class="sfa-meta-field">
        <label>Trigger</label>
        <select v-model="templateTrigger">
          <option value="visit_close">Visit Close (Mandatory)</option>
          <option value="visit_optional">Visit Close (Optional)</option>
          <option value="manual">Manual Assignment</option>
          <option value="scheduled">Scheduled</option>
        </select>
      </div>
      <div class="sfa-meta-field sfa-meta-field--check">
        <label class="sfa-check-label">
          <input type="checkbox" v-model="isMandatory" true-value="1" false-value="0" />
          <span>Mandatory</span>
        </label>
      </div>
      <div class="sfa-meta-field sfa-meta-field--check">
        <label class="sfa-check-label">
          <input type="checkbox" v-model="isActive" true-value="1" false-value="0" />
          <span>Active</span>
        </label>
      </div>
    </div>

    <div class="sfa-creator-body">
      <SurveyCreatorComponent :model="creatorModel" />
    </div>

    <!-- Preview Modal -->
    <div v-if="showPreview" class="sfa-preview-overlay" @click.self="showPreview = false">
      <div class="sfa-preview-box">
        <div class="sfa-preview-header">
          <h3>Form Preview</h3>
          <button class="sfa-btn sfa-btn--ghost" @click="showPreview = false">Close</button>
        </div>
        <div class="sfa-preview-body">
          <SurveyComponent v-if="previewModel" :model="previewModel" />
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { call } from '@/utils/frappe';
import { SurveyCreatorModel } from 'survey-creator-core';
import { SurveyCreatorComponent } from 'survey-creator-vue';
import { Model as SurveyModel } from 'survey-core';
import { SurveyComponent } from 'survey-vue3-ui';

import 'survey-core/defaultV2.min.css';
import 'survey-creator-core/survey-creator-core.min.css';

const props = defineProps({
  templateId: { type: String, default: null },
  initialData: { type: Object, default: null }
});

const emit = defineEmits(['save', 'cancel']);

const templateName     = ref('');
const templateCategory = ref('');
const templateTrigger  = ref('visit_close');
const isActive         = ref('1');
const isMandatory      = ref('0');
const isEditing        = ref(false);
const saving           = ref(false);
const showPreview      = ref(false);
const previewModel     = ref(null);

// Track modified timestamp to avoid conflict errors
const docModified      = ref(null);

const creatorOptions = {
  showLogicTab: true,
  showTranslationTab: false,
  showJSONEditorTab: true,
  isAutoSave: false,
  showThemeTab: false,
  showToolbox: true,
  showSidebar: true,
  allowEditSurveyTitle: false,
};

const creatorModel = new SurveyCreatorModel(creatorOptions);

onMounted(() => {
  if (props.initialData) {
    isEditing.value        = true;
    templateName.value     = props.initialData.template_name || '';
    templateCategory.value = props.initialData.category || '';
    templateTrigger.value  = props.initialData.trigger_point || 'visit_close';
    isActive.value         = props.initialData.is_active    ? '1' : '0';
    isMandatory.value      = props.initialData.is_mandatory ? '1' : '0';
    // Store the modified timestamp to pass back on save — prevents conflict error
    docModified.value      = props.initialData.modified || null;

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
});

onBeforeUnmount(() => {
  creatorModel.dispose();
});

function previewForm() {
  previewModel.value = new SurveyModel(creatorModel.JSON);
  showPreview.value = true;
}

async function saveForm() {
  if (!templateName.value.trim()) {
    frappe.show_alert({ message: 'Please enter a template name', indicator: 'red' });
    return;
  }
  saving.value = true;
  try {
    const doc = {
      doctype:       'SFA Form Template',
      template_name: templateName.value.trim(),
      category:      templateCategory.value,
      trigger_point: templateTrigger.value,
      is_active:     isActive.value    === '1' ? 1 : 0,
      is_mandatory:  isMandatory.value === '1' ? 1 : 0,
      survey_json:   JSON.stringify(creatorModel.JSON),
      version: isEditing.value ? (props.initialData?.version || 1) + 1 : 1,
    };

    if (isEditing.value && props.templateId) {
      doc.name = props.templateId;
      // Pass modified timestamp to avoid "document modified" conflict error
      if (docModified.value) {
        doc.modified = docModified.value;
      }
      const result = await call('frappe.client.save', { doc });
      // Update our stored modified timestamp for any subsequent saves
      if (result?.message?.modified) {
        docModified.value = result.message.modified;
      }
    } else {
      await call('frappe.client.insert', { doc });
    }

    frappe.show_alert({ message: 'Saved successfully', indicator: 'green' });
    emit('save');
  } catch (err) {
    const msg = err?.message || err?.exc_type || JSON.stringify(err);
    frappe.show_alert({ message: 'Save failed: ' + msg, indicator: 'red' });
  } finally {
    saving.value = false;
  }
}
</script>

<style scoped>
.sfa-creator-wrapper {
  position: fixed;
  top: 56px;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  background: #f4f5f6;
  z-index: 100;
  overflow: hidden;
}
.sfa-creator-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 24px;
  background: #fff;
  border-bottom: 1px solid #e2e6e9;
  flex-shrink: 0;
}
.sfa-creator-title {
  display: flex;
  flex-direction: column;
}
.sfa-creator-title > span:first-child {
  font-size: 15px;
  font-weight: 600;
  color: #1f272e;
}
.sfa-creator-subtitle { font-size: 12px; color: #a0a0a0; }
.sfa-creator-actions { display: flex; gap: 8px; }
.sfa-creator-meta {
  display: flex;
  gap: 16px;
  padding: 10px 24px;
  background: #fff;
  border-bottom: 1px solid #e2e6e9;
  flex-shrink: 0;
  flex-wrap: wrap;
  align-items: flex-end;
}
.sfa-meta-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  min-width: 140px;
}
.sfa-meta-field--wide { flex: 2; min-width: 220px; }
.sfa-meta-field--check { flex: 0; padding-bottom: 4px; min-width: auto; }
.sfa-meta-field label {
  font-size: 11px;
  font-weight: 600;
  color: #687178;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.sfa-meta-field input[type="text"],
.sfa-meta-field select {
  padding: 6px 10px;
  border: 1px solid #e2e6e9;
  border-radius: 6px;
  font-size: 13px;
  background: #fff;
}
.sfa-meta-field input[type="text"]:focus,
.sfa-meta-field select:focus { outline: none; border-color: #2490ef; }
.sfa-check-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  color: #1f272e;
}
.sfa-creator-body {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.sfa-creator-body > * { flex: 1; min-height: 0; }
.sfa-preview-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.sfa-preview-box {
  background: #fff;
  border-radius: 10px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.sfa-preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 24px;
  border-bottom: 1px solid #e2e6e9;
}
.sfa-preview-header h3 { margin: 0; font-size: 15px; font-weight: 600; }
.sfa-preview-body { flex: 1; overflow-y: auto; padding: 24px; }
</style>

<style>
.svc-creator__banner { display: none !important; }
.svc-footer-bar,
.svc-creator__footer,
.svc-creator > div:last-child:empty { display: none !important; }
.svc-tabbed-menu-item--active {
  color: #2490ef !important;
  border-bottom-color: #2490ef !important;
}
</style>
