<template>
  <div class="flex h-full flex-col">

    <!-- Toolbar -->
    <div class="flex items-center gap-3 border-b border-gray-200 bg-white px-4 py-2.5">
      <div class="relative">
        <FeatherIcon name="search" class="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-gray-400" />
        <input
          v-model="search"
          type="text"
          placeholder="Search templates..."
          class="h-9 rounded-md border border-gray-200 bg-white pl-8 pr-3 text-sm focus:border-gray-400 focus:outline-none w-56"
        />
      </div>
      <select
        v-model="categoryFilter"
        class="h-9 rounded-md border border-gray-200 bg-white px-3 text-sm focus:border-gray-400 focus:outline-none"
      >
        <option value="">All Categories</option>
        <option>Outlet Audit</option>
        <option>Market Survey</option>
        <option>Competitor Check</option>
        <option>Merchandising</option>
        <option>Customer Feedback</option>
        <option>Custom</option>
      </select>
      <div class="flex-1" />
      <button
        class="flex h-9 items-center gap-1.5 rounded-md bg-gray-900 px-3 text-sm font-medium text-white hover:bg-gray-700 transition-colors"
        @click="$router.push('/form-templates/new')"
      >
        <FeatherIcon name="plus" class="h-3.5 w-3.5" />
        New Template
      </button>
    </div>

    <!-- Grid -->
    <div class="flex-1 overflow-auto p-4">
      <div v-if="loading" class="flex justify-center py-16">
        <FeatherIcon name="loader" class="h-6 w-6 animate-spin text-gray-400" />
      </div>

      <div v-else-if="cards.length" class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <div
          v-for="t in cards"
          :key="t.name"
          class="group flex flex-col rounded-xl border border-gray-200 bg-white p-4 shadow-sm hover:border-gray-300 hover:shadow-md transition-all cursor-pointer"
        >
          <!-- Card header -->
          <div class="flex items-start justify-between mb-3">
            <div
              class="flex h-9 w-9 items-center justify-center rounded-lg"
              :class="categoryBg(t.category)"
            >
              <FeatherIcon :name="categoryIcon(t.category)" class="h-4 w-4 text-white" />
            </div>
            <span
              class="rounded-full px-2 py-0.5 text-xs font-medium"
              :class="t.is_active ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-500'"
            >
              {{ t.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>

          <!-- Name -->
          <p class="text-sm font-semibold text-gray-900 truncate mb-0.5">{{ t.template_name }}</p>
          <p class="text-xs text-gray-400 mb-3">{{ t.category || 'Uncategorised' }}</p>

          <!-- Stats row -->
          <div class="flex items-center gap-3 text-xs text-gray-500 mb-3">
            <span class="flex items-center gap-1">
              <FeatherIcon name="help-circle" class="h-3 w-3" />
              {{ t.question_count }} questions
            </span>
            <span class="flex items-center gap-1">
              <FeatherIcon name="git-branch" class="h-3 w-3" />
              v{{ t.version || 1 }}
            </span>
            <span v-if="t.is_mandatory" class="ml-auto text-red-500 font-semibold uppercase">Required</span>
          </div>

          <!-- Actions -->
          <div class="mt-auto flex gap-2 pt-3 border-t border-gray-100">
            <button
              class="flex flex-1 items-center justify-center gap-1.5 rounded-md border border-gray-200 px-2 py-1.5 text-xs text-gray-600 hover:bg-gray-50 transition-colors"
              @click="$router.push('/form-templates/' + t.name)"
            >
              <FeatherIcon name="edit-2" class="h-3 w-3" />
              Edit
            </button>
            <button
              class="flex flex-1 items-center justify-center gap-1.5 rounded-md border border-gray-200 px-2 py-1.5 text-xs text-gray-600 hover:bg-gray-50 transition-colors"
              @click.stop="viewResponses(t)"
            >
              <FeatherIcon name="eye" class="h-3 w-3" />
              Responses
            </button>
            <button
              class="flex items-center justify-center rounded-md border border-gray-200 px-2 py-1.5 text-xs text-gray-600 hover:bg-gray-50 transition-colors"
              @click.stop="duplicate(t)"
              title="Duplicate"
            >
              <FeatherIcon name="copy" class="h-3 w-3" />
            </button>
          </div>
        </div>
      </div>

      <div v-else class="flex flex-col items-center justify-center py-20 text-gray-400">
        <FeatherIcon name="file-text" class="h-10 w-10 mb-3" />
        <p class="text-sm font-medium text-gray-600">No form templates yet</p>
        <p class="text-xs mt-1 mb-4">Create your first template to get started</p>
        <button
          class="rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-700 transition-colors"
          @click="$router.push('/form-templates/new')"
        >
          New Template
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { call } from '@/utils/frappe'
import { successToast, errorToast } from '@/utils/toast'
import { useRouter } from 'vue-router'

const router = useRouter()
const search = ref('')
const categoryFilter = ref('')
const loading = ref(false)
const templates = ref([])

async function load() {
  loading.value = true
  try {
    const res = await call('frappe.client.get_list', {
        doctype: 'SFA Form Template',
        fields: ['name', 'template_name', 'category', 'trigger_point', 'is_active', 'is_mandatory', 'version', 'survey_json', 'modified'],
        order_by: 'modified desc',
        limit: 200,
      })
    templates.value = (res.message || []).map(t => {
      let qCount = 0
      try {
        const json = typeof t.survey_json === 'string' ? JSON.parse(t.survey_json || '{}') : (t.survey_json || {})
        qCount = (json.pages || []).reduce((s, p) => s + (p.elements || []).length, 0)
      } catch {}
      return { ...t, question_count: qCount }
    })
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)

const cards = computed(() => {
  let list = templates.value
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(t => t.template_name?.toLowerCase().includes(q))
  }
  if (categoryFilter.value) list = list.filter(t => t.category === categoryFilter.value)
  return list
})

async function duplicate(t) {
  try {
    await call('sfa_core.field_sfa.api.form.duplicate_form_template', { template_name: t.name })
    successToast('Template duplicated')
    load()
  } catch {
    errorToast('Failed to duplicate')
  }
}

function viewResponses(t) {
  window.open(`/app/sfa-form-response?form_template=${encodeURIComponent(t.name)}`, '_blank')
}

const categoryIcon = (c) => ({ 'Outlet Audit': 'clipboard', 'Market Survey': 'bar-chart', 'Competitor Check': 'target', 'Merchandising': 'package', 'Customer Feedback': 'message-square', 'Custom': 'sliders' })[c] || 'file-text'
const categoryBg = (c) => ({ 'Outlet Audit': 'bg-blue-500', 'Market Survey': 'bg-green-500', 'Competitor Check': 'bg-red-500', 'Merchandising': 'bg-yellow-500', 'Customer Feedback': 'bg-purple-500', 'Custom': 'bg-slate-400' })[c] || 'bg-slate-400'
</script>
