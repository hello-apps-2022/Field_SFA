<template>
  <div class="flex h-full flex-col overflow-hidden">
    <div class="flex h-[52px] shrink-0 items-center border-b border-gray-100 bg-white px-5 gap-3">
      <router-link to="/settings" class="flex items-center justify-center h-7 w-7 rounded-md text-gray-400 hover:bg-gray-100 hover:text-gray-700 transition-colors">
        <FeatherIcon name="chevron-left" class="h-4 w-4" />
      </router-link>
      <h1 class="text-sm font-semibold text-gray-900">Territories</h1>
      <div class="flex-1" />
      <Btn icon="plus" variant="solid" size="sm" @click="openCreate">Add Territory</Btn>
    </div>

    <div class="flex-1 overflow-y-auto bg-gray-50 p-5">
      <div v-if="loading" class="flex h-40 items-center justify-center">
        <FeatherIcon name="loader" class="h-6 w-6 animate-spin text-gray-400" />
      </div>

      <div v-else class="max-w-2xl mx-auto space-y-2">
        <div v-for="t in territories" :key="t.name"
          class="flex items-center justify-between rounded-xl border border-gray-200 bg-white px-4 py-3">
          <div class="flex items-center gap-3">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-green-50">
              <FeatherIcon name="map-pin" class="h-4 w-4 text-green-600" />
            </div>
            <div>
              <p class="text-sm font-semibold text-gray-900">{{ t.name }}</p>
              <p class="text-xs text-gray-400">{{ t.parent_territory || 'Top level' }}</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs text-gray-400">{{ t.rep_count }} rep{{ t.rep_count !== 1 ? 's' : '' }}</span>
            <button class="h-7 w-7 flex items-center justify-center rounded text-gray-400 hover:bg-gray-100 hover:text-red-500"
              @click="confirmDelete(t)" title="Delete">
              <FeatherIcon name="trash-2" class="h-3.5 w-3.5" />
            </button>
          </div>
        </div>

        <div v-if="!territories.length" class="flex flex-col items-center py-16 text-gray-400">
          <FeatherIcon name="map-pin" class="h-10 w-10 mb-3" />
          <p class="text-sm font-medium text-gray-600">No territories yet</p>
          <Btn icon="plus" variant="solid" size="sm" class="mt-4" @click="openCreate">Add Territory</Btn>
        </div>
      </div>
    </div>
  </div>

  <!-- Create panel -->
  <SlidePanel v-model="createPanel" title="Add Territory" :saving="saving" save-label="Create" @save="createTerritory">
    <div class="space-y-4">
      <FormField v-model="form.name" label="Territory Name" required :error="errors.name"
        placeholder="e.g. Kampala North" />
      <div>
        <label class="mb-1.5 block text-xs font-medium text-gray-600">Parent Territory</label>
        <select v-model="form.parent"
          class="w-full h-9 rounded-lg border border-gray-200 bg-white px-3 text-sm focus:border-gray-400 focus:outline-none">
          <option value="All Territories">All Territories (top level)</option>
          <option v-for="t in territories" :key="t.name" :value="t.name">{{ t.name }}</option>
        </select>
      </div>
    </div>
  </SlidePanel>

  <!-- Confirm delete -->
  <Teleport to="body">
    <div v-if="deleteTarget" class="fixed inset-0 z-[70] flex items-center justify-center bg-black/30 backdrop-blur-sm">
      <div class="w-80 rounded-2xl border border-gray-200 bg-white p-6 shadow-2xl">
        <p class="text-sm font-semibold text-gray-900">Delete "{{ deleteTarget.name }}"?</p>
        <p class="mt-1.5 text-sm text-gray-500">This territory will be removed. Reps and customers assigned to it will need to be reassigned.</p>
        <div class="mt-5 flex gap-2 justify-end">
          <button class="h-8 rounded-lg border border-gray-200 px-3 text-sm text-gray-600 hover:bg-gray-50" @click="deleteTarget = null">Cancel</button>
          <button class="h-8 rounded-lg bg-red-600 px-4 text-sm font-medium text-white hover:bg-red-700" @click="doDelete">Delete</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { call, getList } from '@/utils/frappe'
import { successToast, errorToast } from '@/utils/toast'
import Btn from '@/components/ui/Btn.vue'
import SlidePanel from '@/components/ui/SlidePanel.vue'
import FormField from '@/components/ui/FormField.vue'

const territories = ref([])
const loading = ref(false)
const saving = ref(false)
const createPanel = ref(false)
const deleteTarget = ref(null)
const errors = reactive({})
const form = reactive({ name: '', parent: 'All Territories' })

async function load() {
  loading.value = true
  try {
    const res = await getList('Territory', {
      filters: { is_group: 0 },
      fields: ['name', 'parent_territory'],
      orderBy: 'name asc',
      limit: 200,
    })
    // Add rep count
    const repsRes = await call('sfa_core.api.settings.get_users')
    const reps = repsRes.message || []
    const repsByTerritory = {}
    reps.forEach(r => {
      if (r.territory) repsByTerritory[r.territory] = (repsByTerritory[r.territory] || 0) + 1
    })
    territories.value = res.map(t => ({ ...t, rep_count: repsByTerritory[t.name] || 0 }))
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

function openCreate() {
  Object.assign(form, { name: '', parent: 'All Territories' })
  Object.keys(errors).forEach(k => delete errors[k])
  createPanel.value = true
}

async function createTerritory() {
  Object.keys(errors).forEach(k => delete errors[k])
  if (!form.name) { errors.name = 'Required'; return }
  saving.value = true
  try {
    await call('frappe.client.insert', {
      doc: {
        doctype: 'Territory',
        territory_name: form.name,
        parent_territory: form.parent || 'All Territories',
      }
    })
    successToast(`Territory "${form.name}" created`)
    createPanel.value = false
    await load()
  } catch (e) { errorToast(e.message) }
  finally { saving.value = false }
}

function confirmDelete(t) { deleteTarget.value = t }

async function doDelete() {
  try {
    await call('frappe.client.delete', {
      doctype: 'Territory',
      name: deleteTarget.value.name,
    })
    successToast(`Deleted "${deleteTarget.value.name}"`)
    deleteTarget.value = null
    await load()
  } catch (e) { errorToast(e.message) }
}

onMounted(load)
</script>
