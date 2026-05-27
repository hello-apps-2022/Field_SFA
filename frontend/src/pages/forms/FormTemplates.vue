<template>
  <ListPage
    title="Form Templates"
    new-label="New Template"
    v-model:search="search"
    :columns="columns"
    :rows="filtered"
    :count="filtered.length"
    :loading="loading"
    empty-icon="file-text"
    empty-description="Create your first form template"
    @new="$router.push('/form-templates/new')"
    @row-click="(row) => $router.push('/form-templates/' + row.name)"
    @refresh="load"
  >
    <template #filters>
      <select v-model="categoryFilter" class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
        <option value="">All Categories</option>
        <option>Outlet Audit</option><option>Market Survey</option><option>Competitor Check</option>
        <option>Merchandising</option><option>Customer Feedback</option><option>Custom</option>
      </select>
    </template>

    <template #cell-template_name="{ row }">
      <div class="flex items-center gap-2.5">
        <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg" :class="catColor(row.category)">
          <FeatherIcon :name="catIcon(row.category)" class="h-3.5 w-3.5 text-white" />
        </div>
        <div>
          <p class="font-medium text-gray-900">{{ row.template_name }}</p>
          <p class="text-xs text-gray-400">{{ row.category || 'Uncategorised' }}</p>
        </div>
      </div>
    </template>

    <template #cell-is_active="{ row }">
      <StatusBadge :status="row.is_active ? 'Active' : 'Inactive'" />
    </template>

    <template #cell-is_mandatory="{ row }">
      <span v-if="row.is_mandatory" class="text-xs font-semibold text-red-500">Required</span>
      <span v-else class="text-xs text-gray-400">Optional</span>
    </template>

    <template #row-actions="{ row }">
      <button class="invisible rounded px-2 py-1 text-xs text-gray-500 hover:bg-gray-200 group-hover:visible" @click.stop="$router.push('/form-templates/'+row.name)">Edit</button>
    </template>
  </ListPage>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getList } from '@/utils/frappe'
import { errorToast } from '@/utils/toast'
import ListPage from '@/components/list/ListPage.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'

const search = ref('')
const categoryFilter = ref('')
const loading = ref(false)
const templates = ref([])

const columns = [
  { key: 'template_name', label: 'Template Name', primary: true },
  { key: 'trigger_point', label: 'Trigger' },
  { key: 'is_mandatory', label: 'Required' },
  { key: 'is_active', label: 'Status' },
]

const filtered = computed(() => {
  let l = templates.value
  if (search.value) { const q = search.value.toLowerCase(); l = l.filter(t => t.template_name?.toLowerCase().includes(q)) }
  if (categoryFilter.value) l = l.filter(t => t.category === categoryFilter.value)
  return l
})

async function load() {
  loading.value = true
  try { templates.value = await getList('SFA Form Template', { fields: ['name','template_name','category','trigger_point','is_active','is_mandatory','version'], orderBy: 'modified desc', limit: 200 }) }
  catch (e) { errorToast('Failed to load templates') }
  finally { loading.value = false }
}

const catIcon = (c) => ({'Outlet Audit':'clipboard','Market Survey':'bar-chart-2','Competitor Check':'target','Merchandising':'package','Customer Feedback':'message-square','Custom':'sliders'})[c] || 'file-text'
const catColor = (c) => ({'Outlet Audit':'bg-blue-500','Market Survey':'bg-green-500','Competitor Check':'bg-red-500','Merchandising':'bg-yellow-500','Customer Feedback':'bg-purple-500','Custom':'bg-slate-400'})[c] || 'bg-slate-400'

onMounted(load)
</script>
