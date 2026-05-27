<template>
  <div class="flex h-full flex-col">

    <!-- Toolbar -->
    <div class="flex items-center gap-3 border-b border-outline-gray-2 bg-surface-white px-4 py-2.5">
      <TextInput v-model="search" placeholder="Search templates..." size="sm" class="w-64">
        <template #prefix><FeatherIcon name="search" class="h-3.5 w-3.5 text-ink-gray-4" /></template>
      </TextInput>
      <FormControl type="select" v-model="categoryFilter" :options="categoryOptions" size="sm" class="w-44" />
      <div class="flex-1" />
      <Button variant="solid" size="sm" @click="$router.push('/form-templates/new')">
        <template #prefix><FeatherIcon name="plus" class="h-3.5 w-3.5" /></template>
        New Template
      </Button>
    </div>

    <!-- Grid -->
    <div class="flex-1 overflow-auto p-4">
      <div v-if="templatesList.loading.value && !cards.length" class="flex justify-center py-20">
        <Spinner class="h-6 w-6 text-ink-gray-4" />
      </div>

      <div v-else-if="cards.length" class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <div
          v-for="t in cards"
          :key="t.name"
          class="group rounded-lg border border-outline-gray-2 bg-surface-white p-4 space-y-3 hover:border-outline-gray-4 hover:shadow-sm transition-all cursor-pointer"
          @click="$router.push('/form-templates/' + t.name)"
        >
          <!-- Header -->
          <div class="flex items-start justify-between">
            <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg" :class="categoryColor(t.category)">
              <FeatherIcon :name="categoryIcon(t.category)" class="h-4 w-4 text-white" />
            </div>
            <Badge
              :label="t.is_active ? 'Active' : 'Inactive'"
              :variant="t.is_active ? 'success' : 'subtle'"
              size="sm"
            />
          </div>

          <!-- Name + category -->
          <div>
            <p class="text-sm font-semibold text-ink-gray-9 truncate">{{ t.template_name }}</p>
            <p class="text-xs text-ink-gray-4 mt-0.5">{{ t.category || 'Uncategorised' }}</p>
          </div>

          <!-- Stats -->
          <div class="flex items-center gap-4 text-xs text-ink-gray-5">
            <span class="flex items-center gap-1">
              <FeatherIcon name="help-circle" class="h-3 w-3" />
              {{ t.question_count }} questions
            </span>
            <span class="flex items-center gap-1">
              <FeatherIcon name="git-branch" class="h-3 w-3" />
              v{{ t.version || 1 }}
            </span>
          </div>

          <!-- Trigger badge -->
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-medium text-ink-gray-4 uppercase tracking-wide">
              {{ triggerLabel(t.trigger_point) }}
            </span>
            <span v-if="t.is_mandatory" class="text-[10px] font-semibold text-red-500 uppercase">Required</span>
          </div>

          <!-- Actions — show on hover -->
          <div class="flex gap-2 pt-1 border-t border-outline-gray-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <Button size="sm" variant="ghost" class="flex-1" @click.stop="$router.push('/form-templates/' + t.name)">
              <template #prefix><FeatherIcon name="edit-2" class="h-3 w-3" /></template>
              Edit
            </Button>
            <Button size="sm" variant="ghost" class="flex-1" @click.stop="viewResponses(t)">
              <template #prefix><FeatherIcon name="eye" class="h-3 w-3" /></template>
              Responses
            </Button>
            <Button size="sm" variant="ghost" @click.stop="duplicate(t)">
              <FeatherIcon name="copy" class="h-3 w-3" />
            </Button>
          </div>
        </div>
      </div>

      <div v-else class="flex flex-col items-center justify-center py-20 text-ink-gray-4">
        <FeatherIcon name="file-text" class="h-10 w-10 mb-3" />
        <p class="text-sm font-medium">No form templates yet</p>
        <p class="text-xs mt-1">Create your first template to get started</p>
        <Button class="mt-4" size="sm" @click="$router.push('/form-templates/new')">New Template</Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { createListResource } from 'frappe-ui'
import { useRouter } from 'vue-router'

const router = useRouter()
const search = ref('')
const categoryFilter = ref('')

const categoryOptions = [
  { label: 'All Categories', value: '' },
  { label: 'Outlet Audit', value: 'Outlet Audit' },
  { label: 'Market Survey', value: 'Market Survey' },
  { label: 'Competitor Check', value: 'Competitor Check' },
  { label: 'Merchandising', value: 'Merchandising' },
  { label: 'Customer Feedback', value: 'Customer Feedback' },
  { label: 'Custom', value: 'Custom' },
]

const templatesList = createListResource({
  doctype: 'SFA Form Template',
  fields: ['name', 'template_name', 'category', 'trigger_point', 'is_active', 'is_mandatory', 'version', 'survey_json', 'modified'],
  orderBy: 'modified desc',
  pageLength: 100,
  auto: true,
})

const cards = computed(() => {
  let list = (templatesList.data || []).map(t => {
    let qCount = 0
    try {
      const json = typeof t.survey_json === 'string' ? JSON.parse(t.survey_json || '{}') : (t.survey_json || {})
      qCount = (json.pages || []).reduce((s, p) => s + (p.elements || []).length, 0)
    } catch {}
    return { ...t, question_count: qCount }
  })
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(t => t.template_name?.toLowerCase().includes(q))
  }
  if (categoryFilter.value) list = list.filter(t => t.category === categoryFilter.value)
  return list
})

function viewResponses(t) {
  router.push({ path: '/visits', query: { form_template: t.name } })
}

async function duplicate(t) {
  try {
    await frappe.call({ method: 'sfa_core.field_sfa.api.form.duplicate_form_template', args: { template_name: t.name } })
    frappe.show_alert({ message: 'Template duplicated', indicator: 'green' })
    templatesList.reload()
  } catch (e) {
    frappe.show_alert({ message: 'Failed to duplicate', indicator: 'red' })
  }
}

const categoryIcon = (c) => ({ 'Outlet Audit': 'clipboard', 'Market Survey': 'bar-chart', 'Competitor Check': 'target', 'Merchandising': 'package', 'Customer Feedback': 'message-square', 'Custom': 'sliders' })[c] || 'file-text'
const categoryColor = (c) => ({ 'Outlet Audit': 'bg-blue-500', 'Market Survey': 'bg-green-500', 'Competitor Check': 'bg-red-500', 'Merchandising': 'bg-yellow-500', 'Customer Feedback': 'bg-purple-500', 'Custom': 'bg-slate-500' })[c] || 'bg-slate-400'
const triggerLabel = (t) => ({ visit_close: 'Visit Close', visit_optional: 'Optional', manual: 'Manual', scheduled: 'Scheduled' })[t] || t
</script>
