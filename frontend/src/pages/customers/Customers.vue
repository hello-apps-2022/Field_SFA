<template>
  <ListPage
    title="Customers"
    new-label="New Customer"
    v-model:search="search"
    :columns="columns"
    :rows="filtered"
    :count="filtered.length"
    :loading="loading"
    empty-icon="users"
    empty-description="Add your first outlet to get started"
    @new="panelOpen = true"
    @row-click="(row) => $router.push('/customers/' + row.name)"
    @refresh="load"
  >
    <template #filters>
      <select v-model="groupFilter" class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
        <option value="">All Groups</option>
        <option v-for="g in groups" :key="g">{{ g }}</option>
      </select>
      <select v-model="territoryFilter" class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
        <option value="">All Territories</option>
        <option v-for="t in territories" :key="t">{{ t }}</option>
      </select>
    </template>

    <template #cell-customer_name="{ row }">
      <div class="flex items-center gap-2.5">
        <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gray-200 text-xs font-semibold text-gray-600">
          {{ (row.customer_name || row.name).charAt(0).toUpperCase() }}
        </div>
        <div>
          <p class="font-medium text-gray-900">{{ row.customer_name }}</p>
          <p class="text-xs text-gray-400">{{ row.name }}</p>
        </div>
      </div>
    </template>

    <template #cell-disabled="{ row }">
      <StatusBadge :status="row.disabled ? 'Inactive' : 'Active'" />
    </template>

    <template #row-actions="{ row }">
      <button
        class="invisible rounded px-2 py-1 text-xs text-gray-500 hover:bg-gray-200 group-hover:visible"
        @click.stop="openEdit(row)"
      >
        Edit
      </button>
    </template>
  </ListPage>

  <!-- Create / Edit panel -->
  <SlidePanel v-model="panelOpen" :title="editingName ? 'Edit Customer' : 'New Customer'" :saving="saving" @save="save">
    <div class="space-y-4">
      <FormField v-model="form.customer_name" label="Customer Name" required :error="errors.customer_name" />
      <FormField v-model="form.customer_group" label="Customer Group" type="select" :options="customerGroups" />
      <FormField v-model="form.territory" label="Territory" type="select" :options="allTerritories" />
      <FormField v-model="form.mobile_no" label="Mobile" type="tel" />
      <FormField v-model="form.email_id" label="Email" type="email" />
      <FormField v-model="form.customer_details" label="Notes" type="textarea" />
    </div>
  </SlidePanel>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { getList, insertDoc, saveDoc } from '@/utils/frappe'
import { successToast, errorToast } from '@/utils/toast'
import { useLinkedData } from '@/composables/useLinkedData'
import ListPage from '@/components/list/ListPage.vue'
import SlidePanel from '@/components/ui/SlidePanel.vue'
import FormField from '@/components/ui/FormField.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'

const { customerGroups, loadCustomerGroups } = useLinkedData()
const allTerritories = ref([])

const search = ref('')
const groupFilter = ref('')
const territoryFilter = ref('')
const loading = ref(false)
const saving = ref(false)
const panelOpen = ref(false)
const editingName = ref(null)
const customers = ref([])
const errors = reactive({})

const form = reactive({ customer_name: '', customer_group: '', territory: '', mobile_no: '', email_id: '', customer_details: '' })

const columns = [
  { key: 'customer_name', label: 'Customer Name', primary: true },
  { key: 'customer_group', label: 'Group' },
  { key: 'territory', label: 'Territory' },
  { key: 'mobile_no', label: 'Mobile' },
  { key: 'disabled', label: 'Status' },
]

const groups = computed(() => [...new Set(customers.value.map(c => c.customer_group).filter(Boolean))])
const territories = computed(() => [...new Set(customers.value.map(c => c.territory).filter(Boolean))])

const filtered = computed(() => {
  let l = customers.value
  if (search.value) { const q = search.value.toLowerCase(); l = l.filter(c => c.customer_name?.toLowerCase().includes(q) || c.name?.toLowerCase().includes(q)) }
  if (groupFilter.value) l = l.filter(c => c.customer_group === groupFilter.value)
  if (territoryFilter.value) l = l.filter(c => c.territory === territoryFilter.value)
  return l
})

async function load() {
  loading.value = true
  try {
    customers.value = await getList('Customer', {
      fields: ['name', 'customer_name', 'customer_group', 'territory', 'mobile_no', 'disabled'],
      orderBy: 'customer_name asc', limit: 500,
    })
  } catch (e) { errorToast('Failed to load customers') }
  finally { loading.value = false }
}

function openEdit(row) {
  editingName.value = row.name
  Object.assign(form, { customer_name: row.customer_name, customer_group: row.customer_group || '', territory: row.territory || '', mobile_no: row.mobile_no || '', email_id: row.email_id || '', customer_details: row.customer_details || '' })
  Object.keys(errors).forEach(k => delete errors[k])
  panelOpen.value = true
}

async function save() {
  if (!form.customer_name.trim()) { errors.customer_name = 'Required'; return }
  saving.value = true
  try {
    const doc = { doctype: 'Customer', customer_type: 'Company', ...form, customer_type: form.customer_type || 'Company' }
    if (editingName.value) { doc.name = editingName.value; await saveDoc(doc) }
    else await insertDoc(doc)
    successToast(editingName.value ? 'Customer updated' : 'Customer created')
    panelOpen.value = false
    editingName.value = null
    await load()
  } catch (e) { errorToast(e.message || 'Save failed') }
  finally { saving.value = false }
}

onMounted(async () => {
  await load()
  await loadCustomerGroups()
  allTerritories.value = territories.value
})
</script>
