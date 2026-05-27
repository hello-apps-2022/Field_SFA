<template>
  <div class="sfa-forms-page sfa-desk">
    <div class="page-header">
      <div class="header-left">
        <h1>Form Templates</h1>
        <p class="header-subtitle">{{ filteredTemplates.length }} templates configured</p>
      </div>
      <div class="header-right">
        <div class="search-box">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <circle cx="7" cy="7" r="5.5" stroke="currentColor" stroke-width="1.5"/>
            <path d="M11.5 11.5L14.5 14.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          <input v-model="searchQuery" type="text" placeholder="Search templates..." />
        </div>
        <button class="sfa-btn sfa-btn--primary" @click="createNewTemplate">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M7 2v10M2 7h10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          New Template
        </button>
      </div>
    </div>

    <div class="templates-grid">
      <div
        v-for="template in filteredTemplates"
        :key="template.name"
        class="template-card"
        :class="{ inactive: !template.is_active }"
      >
        <div class="template-header">
          <div class="template-icon" :class="'icon--' + template.category">
            <svg v-if="template.category === 'audit'" width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M10 2l8 4v6l-8 4-8-4V6l8-4z" stroke="currentColor" stroke-width="1.5"/>
              <path d="M10 12V6" stroke="currentColor" stroke-width="1.5"/>
            </svg>
            <svg v-else-if="template.category === 'survey'" width="20" height="20" viewBox="0 0 20 20" fill="none">
              <rect x="3" y="3" width="14" height="14" rx="2" stroke="currentColor" stroke-width="1.5"/>
              <path d="M7 8h6M7 12h4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <svg v-else width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M4 10h12M10 4v12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="template-meta">
            <div class="template-name">{{ template.template_name }}</div>
            <div class="template-category">{{ template.category }}</div>
          </div>
          <div class="template-status">
            <span class="sfa-badge" :class="template.is_active ? 'sfa-badge--success' : 'sfa-badge--danger'">
              <span class="sfa-badge-dot"></span>
              {{ template.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
        </div>
        <div class="template-body">
          <div class="template-stats">
            <div class="t-stat">
              <span class="t-stat-value">{{ template.question_count || 0 }}</span>
              <span class="t-stat-label">Questions</span>
            </div>
            <div class="t-stat">
              <span class="t-stat-value">{{ template.response_count || 0 }}</span>
              <span class="t-stat-label">Responses</span>
            </div>
            <div class="t-stat">
              <span class="t-stat-value">v{{ template.version || 1 }}</span>
              <span class="t-stat-label">Version</span>
            </div>
          </div>
          <div class="template-trigger">
            <span class="trigger-label">Trigger:</span>
            <span class="trigger-value">{{ formatTrigger(template.trigger_point) }}</span>
          </div>
        </div>
        <div class="template-footer">
          <button class="sfa-btn sfa-btn--ghost sfa-btn--sm" @click="editTemplate(template)">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M2 10v2h2l8-8-2-2-8 8z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Edit
          </button>
          <button class="sfa-btn sfa-btn--ghost sfa-btn--sm" @click="duplicateTemplate(template)">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <rect x="3" y="3" width="8" height="8" rx="1" stroke="currentColor" stroke-width="1.5"/>
              <path d="M5 1h8v8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            Duplicate
          </button>
          <button class="sfa-btn sfa-btn--ghost sfa-btn--sm" @click="viewResponses(template)">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M1 7s2-4 6-4 6 4 6 4-2 4-6 4-6-4-6-4z" stroke="currentColor" stroke-width="1.5"/>
              <circle cx="7" cy="7" r="2" stroke="currentColor" stroke-width="1.5"/>
            </svg>
            Responses
          </button>
        </div>
      </div>
    </div>

    <div v-if="showCreator" class="creator-modal">
      <SurveyCreator
        :template-id="editingTemplate ? editingTemplate.name : null"
        :initial-data="editingTemplate"
        @save="onCreatorSave"
        @cancel="showCreator = false"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import SurveyCreator from '../surveyjs/SurveyCreator.vue';
import { useFrappeAPI } from '../composables/useFrappe';

const { getList, call } = useFrappeAPI();

const templates = ref([]);
const searchQuery = ref('');
const showCreator = ref(false);
const editingTemplate = ref(null);

const filteredTemplates = computed(() => {
  if (!searchQuery.value) return templates.value;
  const q = searchQuery.value.toLowerCase();
  return templates.value.filter(t =>
    (t.template_name || '').toLowerCase().includes(q) ||
    (t.category || '').toLowerCase().includes(q)
  );
});

onMounted(() => {
  loadTemplates();
});

async function loadTemplates() {
  const data = await getList('SFA Form Template', {}, [
    'name', 'template_name', 'category', 'trigger_point',
    'is_active', 'version', 'survey_json', 'modified'
  ], 100);

  data.forEach(t => {
    try {
      const json = JSON.parse(t.survey_json || '{}');
      t.question_count = (json.pages || []).reduce((sum, p) => sum + (p.elements || []).length, 0);
    } catch (e) {
      t.question_count = 0;
    }
    t.response_count = 0;
  });

  templates.value = data;
}

function createNewTemplate() {
  editingTemplate.value = null;
  showCreator.value = true;
}

function editTemplate(template) {
  editingTemplate.value = template;
  showCreator.value = true;
}

async function duplicateTemplate(template) {
  try {
    await call('sfa_core.api.forms.duplicate_form_template', {
      template_name: template.name
    });
    frappe.show_alert({ message: 'Template duplicated', indicator: 'green' });
    loadTemplates();
  } catch (e) {
    frappe.show_alert({ message: 'Failed to duplicate', indicator: 'red' });
  }
}

function viewResponses(template) {
  window.location.href = `/app/sfa-form-response?form_template=${encodeURIComponent(template.name)}`;
}

function onCreatorSave() {
  showCreator.value = false;
  loadTemplates();
}

function formatTrigger(trigger) {
  const map = {
    'visit_close': 'Visit Close (Mandatory)',
    'visit_optional': 'Visit Close (Optional)',
    'manual': 'Manual Assignment',
    'scheduled': 'Scheduled'
  };
  return map[trigger] || trigger;
}
</script>

<style scoped>
.sfa-forms-page {
  padding: 20px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.header-left h1 {
  font-size: 24px;
  font-weight: 700;
  color: #1f272e;
  margin: 0;
}
.header-subtitle {
  font-size: 13px;
  color: #687178;
  margin-top: 4px;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.search-box {
  position: relative;
}
.search-box svg {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #a0a0a0;
}
.search-box input {
  padding: 8px 12px 8px 32px;
  border: 1px solid #e2e6e9;
  border-radius: 6px;
  font-size: 13px;
  width: 240px;
}
.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}
.template-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  border: 1px solid #f0f2f4;
  transition: all 0.2s;
  overflow: hidden;
}
.template-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  transform: translateY(-2px);
}
.template-card.inactive {
  opacity: 0.7;
}
.template-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-bottom: 1px solid #f0f2f4;
}
.template-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}
.icon--audit { background: linear-gradient(135deg, #2490EF, #1a7ad1); }
.icon--survey { background: linear-gradient(135deg, #28a745, #1e7e34); }
.icon--competitor { background: linear-gradient(135deg, #dc3545, #c82333); }
.icon--merchandising { background: linear-gradient(135deg, #ffc107, #e0a800); }
.icon--feedback { background: linear-gradient(135deg, #9c27b0, #7b1fa2); }
.icon--custom { background: linear-gradient(135deg, #6c757d, #5a6268); }
.template-meta {
  flex: 1;
  min-width: 0;
}
.template-name {
  font-weight: 600;
  font-size: 14px;
  color: #1f272e;
}
.template-category {
  font-size: 11px;
  color: #a0a0a0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: 2px;
}
.template-body {
  padding: 16px;
}
.template-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 12px;
}
.t-stat {
  text-align: center;
}
.t-stat-value {
  display: block;
  font-size: 18px;
  font-weight: 700;
  color: #1f272e;
}
.t-stat-label {
  font-size: 10px;
  color: #a0a0a0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.template-trigger {
  display: flex;
  gap: 6px;
  font-size: 12px;
}
.trigger-label {
  color: #a0a0a0;
}
.trigger-value {
  color: #687178;
  font-weight: 500;
}
.template-footer {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  background: #f8f9fa;
  border-top: 1px solid #f0f2f4;
}
.creator-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  background: white;
}
</style>
