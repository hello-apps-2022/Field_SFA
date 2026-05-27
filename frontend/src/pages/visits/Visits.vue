<template>
  <ListPage
    title="Visits"
    new-label="New Visit"
    v-model:search="search"
    :columns="columns"
    :rows="filtered"
    :count="filtered.length"
    :loading="loading"
    empty-icon="map-pin"
    empty-description="No visits recorded yet"
    @new="panelOpen = true"
    @row-click="(row) => $router.push('/visits/' + row.name)"
    @refresh="load"
  >
    <template #filters>
      <select v-model="statusFilter" class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
        <option value="">All Statuses</option>
        <option>Planned</option><option>In Progress</option><option>Completed</option><option>Cancelled</option>
      </select>
      <input v-model="dateFilter" type="date" class="h-8 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none" />
    </template>

    <template #cell-customer="{ row }">
      <p class="font-medium text-gray-900">{{ row.customer }}</p>
    </template>

    <template #cell-status="{ row }">
      <StatusBadge :status="row.status" />
    </template>

    <template #cell-visit_date="{ row }">
      <span class="text-gray-600">{{ formatDate(row.visit_date) }}</span>
    </template>

    <template #row-actions="{ row }">
      <button class="invisible rounded px-2 py-1 text-xs text-gray-500 hover:bg-gray-200 group-hover:visible" @click.stop="openEdit(row)">Edit</button>
    </template>
  </ListPage>

  <SlidePanel v-model="panelOpen" :title="editingName ? 'Edit Visit' : 'New Visit'" :saving="saving" @save="save">
    <div class="space-y-4">
      <FormField v-model="form.customer" label="Customer" type="select" :options="customers" required :error="errors.customer" />
      <FormField v-model="form.sales_person" label="Sales Person" type="select" :options="salesPersons" required :error="errors.sales_person" />
      <FormField v-model="form.beat_plan" label="Beat Plan" type="select" :options="beatPlans" />
      <FormField v-model="form.visit_date" label="Visit Date" type="date" required :error="errors.visit_date" />
      <FormField v-model="form.status" label="Status" type="select" :options="['Open','In Progress','Completed','Auto Closed','Cancelled']" />
      <FormField v-model="form.notes" label="Notes" type="textarea" />
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
import dayjs from 'dayjs'

const { customers, salesPersons, beatPlans, loadCustomers, loadSalesPersons, loadBeatPlans } = useLinkedData()

const search = ref('')
const statusFilter = ref('')
const dateFilter = ref('')
const loading = ref(false)
const saving = ref(false)
const panelOpen = ref(false)
const editingName = ref(null)
const visits = ref([])
const errors = reactive({})

const form = reactive({ customer: '', sales_person: '', beat_plan: '', visit_date: dayjs().format('YYYY-MM-DD'), status: 'Open', notes: '' })

const columns = [
  { key: 'customer', label: 'Customer', primary: true },
  { key: 'sales_person', label: 'Sales Person' },
  { key: 'visit_date', label: 'Date' },
  { key: 'status', label: 'Status' },
]

const filtered = computed(() => {
  let l = visits.value
  if (search.value) { const q = search.value.toLowerCase(); l = l.filter(v => v.customer?.toLowerCase().includes(q) || v.sales_person?.toLowerCase().includes(q)) }
  if (statusFilter.value) l = l.filter(v => v.status === statusFilter.value)
  if (dateFilter.value) l = l.filter(v => v.visit_date === dateFilter.value)
  return l
})

async function load() {
  loading.value = true
  try { visits.value = await getList('SFA Visit', { fields: ['name','customer','sales_person','visit_date','check_in_time','status','beat_plan'], orderBy: 'visit_date desc', limit: 200 }) }
  catch (e) { errorToast('Failed to load visits') }
  finally { loading.value = false }
}

function openEdit(row) {
  editingName.value = row.name
  Object.assign(form, { customer: row.customer, sales_person: row.sales_person, beat_plan: row.beat_plan || '', visit_date: row.visit_date, status: row.status, notes: row.notes || '' })
  Object.keys(errors).forEach(k => delete errors[k])
  panelOpen.value = true
}

async function save() {
  let ok = true
  if (!form.customer) { errors.customer = 'Required'; ok = false }
  if (!form.sales_person) { errors.sales_person = 'Required'; ok = false }
  if (!ok) return
  saving.value = true
  try {
    const doc = { doctype: 'SFA Visit', ...form }
    if (editingName.value) { doc.name = editingName.value; await saveDoc(doc) } else await insertDoc(doc)
    successToast(editingName.value ? 'Visit updated' : 'Visit created')
    panelOpen.value = false; editingName.value = null; await load()
  } catch (e) { errorToast(e.message || 'Save failed') }
  finally { saving.value = false }
}

const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'
onMounted(() => { load(); loadCustomers(); loadSalesPersons(); loadBeatPlans() })
</script>
