<template>
  <div class="flex h-full flex-col overflow-hidden">
    <div class="flex h-[52px] shrink-0 items-center border-b border-gray-100 bg-white px-5 gap-3">
      <router-link to="/settings" class="flex items-center justify-center h-7 w-7 rounded-md text-gray-400 hover:bg-gray-100 hover:text-gray-700 transition-colors">
        <FeatherIcon name="chevron-left" class="h-4 w-4" />
      </router-link>
      <h1 class="text-sm font-semibold text-gray-900">Location Types</h1>
      <div class="flex-1" />
      <Btn icon="plus" variant="solid" size="sm" @click="openCreate">Add Type</Btn>
    </div>

    <div class="flex-1 overflow-y-auto bg-gray-50 p-5">
      <div v-if="loading" class="flex h-40 items-center justify-center">
        <FeatherIcon name="loader" class="h-6 w-6 animate-spin text-gray-400" />
      </div>

      <div v-else class="max-w-2xl mx-auto space-y-2">
        <p class="text-xs text-gray-400 px-1 pb-1">These drive the type dropdown when saving a location (web and mobile).</p>
        <div v-for="t in items" :key="t.name"
          class="flex items-center justify-between rounded-xl border border-gray-200 bg-white px-4 py-3"
          :class="!t.is_active ? 'opacity-60' : ''">
          <div class="flex items-center gap-3">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-green-50">
              <FeatherIcon name="tag" class="h-4 w-4 text-green-600" />
            </div>
            <div>
              <p class="text-sm font-semibold text-gray-900">{{ t.option_name }}</p>
              <p class="text-xs text-gray-400">{{ t.description || (t.is_active ? 'Active' : 'Inactive') }}</p>
            </div>
          </div>
          <div class="flex items-center gap-1">
            <button class="h-7 w-7 flex items-center justify-center rounded text-gray-400 hover:bg-gray-100 hover:text-gray-700"
              @click="openEdit(t)" title="Edit"><FeatherIcon name="edit-2" class="h-3.5 w-3.5" /></button>
            <button class="h-7 w-7 flex items-center justify-center rounded text-gray-400 hover:bg-gray-100"
              :class="t.is_active ? 'hover:text-red-500' : 'hover:text-green-600'"
              @click="toggle(t)" :title="t.is_active ? 'Deactivate' : 'Activate'">
              <FeatherIcon :name="t.is_active ? 'eye-off' : 'eye'" class="h-3.5 w-3.5" />
            </button>
          </div>
        </div>

        <div v-if="!items.length" class="flex flex-col items-center py-16 text-gray-400">
          <FeatherIcon name="tag" class="h-10 w-10 mb-3" />
          <p class="text-sm font-medium text-gray-600">No location types yet</p>
          <Btn icon="plus" variant="solid" size="sm" class="mt-4" @click="openCreate">Add Type</Btn>
        </div>
      </div>
    </div>

    <SlidePanel v-model="panel" :title="editing ? 'Edit Type' : 'Add Type'" :saving="saving"
      :save-label="editing ? 'Save' : 'Create'" @save="submit">
      <div class="space-y-4">
        <FormField v-model="form.option_name" label="Type Name" required :error="errors.option_name" placeholder="e.g. Distributor Hub" />
        <FormField v-model="form.description" type="textarea" label="Description" placeholder="optional" />
      </div>
    </SlidePanel>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { call } from '@/utils/frappe'
import { successToast, errorToast } from '@/utils/toast'
import Btn from '@/components/ui/Btn.vue'
import SlidePanel from '@/components/ui/SlidePanel.vue'
import FormField from '@/components/ui/FormField.vue'
import FeatherIcon from '@/components/ui/FeatherIcon.vue'

const items = ref([])
const loading = ref(false)
const saving = ref(false)
const panel = ref(false)
const editing = ref(null)
const errors = reactive({})
const form = reactive({ option_name: '', description: '' })

async function load() {
  loading.value = true
  try {
    const res = await call('sfa_core.api.saved_location.get_location_types', { include_inactive: 1 })
    items.value = res.message || []
  } catch (e) { errorToast(e.message || 'Failed to load') }
  finally { loading.value = false }
}

function openCreate() {
  editing.value = null
  Object.keys(errors).forEach(k => delete errors[k])
  Object.assign(form, { option_name: '', description: '' })
  panel.value = true
}

function openEdit(t) {
  editing.value = t.name
  Object.keys(errors).forEach(k => delete errors[k])
  Object.assign(form, { option_name: t.option_name, description: t.description || '' })
  panel.value = true
}

async function submit() {
  Object.keys(errors).forEach(k => delete errors[k])
  if (!form.option_name) { errors.option_name = 'Required'; return }
  saving.value = true
  try {
    if (editing.value) {
      await call('sfa_core.api.saved_location.update_location_type', { name: editing.value, option_name: form.option_name, description: form.description })
      successToast('Type updated')
    } else {
      await call('sfa_core.api.saved_location.create_location_type', { option_name: form.option_name, description: form.description })
      successToast('Type created')
    }
    panel.value = false
    await load()
  } catch (e) { errorToast(e.message) }
  finally { saving.value = false }
}

async function toggle(t) {
  try {
    await call('sfa_core.api.saved_location.update_location_type', { name: t.name, is_active: t.is_active ? 0 : 1 })
    successToast(t.is_active ? `"${t.option_name}" deactivated` : `"${t.option_name}" activated`)
    await load()
  } catch (e) { errorToast(e.message) }
}

onMounted(load)
</script>
