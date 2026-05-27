<template>
  <div class="flex h-full flex-col">
    <div class="flex items-center gap-3 border-b border-gray-200 bg-white px-4 py-2.5">
      <div class="relative">
        <FeatherIcon name="search" class="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-gray-400" />
        <input v-model="search" type="text" placeholder="Search visits..."
          class="h-9 rounded-md border border-gray-200 bg-white pl-8 pr-3 text-sm focus:border-gray-400 focus:outline-none w-56" />
      </div>
      <select v-model="statusFilter" class="h-9 rounded-md border border-gray-200 bg-white px-3 text-sm focus:border-gray-400 focus:outline-none">
        <option value="">All Statuses</option>
        <option>Planned</option><option>In Progress</option><option>Completed</option><option>Cancelled</option>
      </select>
      <input v-model="dateFilter" type="date" class="h-9 rounded-md border border-gray-200 bg-white px-3 text-sm focus:border-gray-400 focus:outline-none" />
      <div class="flex-1" />
      <span class="text-xs text-gray-400">{{ filtered.length }} visits</span>
      <button class="flex h-9 items-center gap-1.5 rounded-md border border-gray-200 bg-white px-3 text-sm text-gray-600 hover:bg-gray-50 transition-colors" @click="load">
        <FeatherIcon name="refresh-cw" class="h-3.5 w-3.5" :class="loading ? 'animate-spin' : ''" />
        Refresh
      </button>
      <button class="flex h-9 items-center gap-1.5 rounded-md bg-gray-900 px-3 text-sm font-medium text-white hover:bg-gray-700 transition-colors" @click="openNew">
        <FeatherIcon name="plus" class="h-3.5 w-3.5" />
        New Visit
      </button>
    </div>

    <div class="flex-1 overflow-auto">
      <table class="w-full text-sm">
        <thead class="sticky top-0 border-b border-gray-200 bg-gray-50">
          <tr>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Visit ID</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Customer</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Sales Person</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Date</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Check In</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Status</th>
            <th class="px-4 py-2.5" />
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="v in filtered" :key="v.name"
            class="cursor-pointer hover:bg-gray-50 transition-colors group"
            @click="$router.push('/visits/' + v.name)">
            <td class="px-4 py-3 font-mono text-xs text-gray-400">{{ v.name }}</td>
            <td class="px-4 py-3 font-medium text-gray-900">{{ v.customer }}</td>
            <td class="px-4 py-3 text-gray-600">{{ v.sales_person }}</td>
            <td class="px-4 py-3 text-gray-600">{{ formatDate(v.visit_date) }}</td>
            <td class="px-4 py-3 text-gray-600">{{ v.check_in_time ? formatTime(v.check_in_time) : '—' }}</td>
            <td class="px-4 py-3">
              <span class="rounded-full px-2 py-0.5 text-xs font-medium" :class="statusClass(v.status)">{{ v.status }}</span>
            </td>
            <td class="px-4 py-3" @click.stop>
              <button class="opacity-0 group-hover:opacity-100 rounded-md border border-gray-200 px-2 py-1 text-xs text-gray-600 hover:bg-gray-100 transition-all" @click="openEdit(v)">
                Edit
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="!loading && !filtered.length" class="flex flex-col items-center justify-center py-20 text-gray-400">
        <FeatherIcon name="map-pin" class="h-10 w-10 mb-3" />
        <p class="text-sm font-medium">No visits found</p>
      </div>
      <div v-if="loading" class="flex justify-center py-12">
        <FeatherIcon name="loader" class="h-6 w-6 animate-spin text-gray-400" />
      </div>
    </div>

    <!-- Slide Panel -->
    <SlidePanel v-model="panelOpen" :title="editing ? 'Edit Visit' : 'New Visit'" :saving="saving" @save="save">
      <div class="space-y-4">
        <FormField v-model="form.customer" label="Customer" type="select" :options="customers" required :error="errors.customer" />
        <FormField v-model="form.sales_person" label="Sales Person" type="select" :options="salesPersons" required :error="errors.sales_person" />
        <FormField v-model="form.beat_plan" label="Beat Plan" type="select" :options="beatPlans" />
        <FormField v-model="form.visit_date" label="Visit Date" type="date" required :error="errors.visit_date" />
        <FormField v-model="form.status" label="Status" type="select" :options="['Planned','In Progress','Completed','Cancelled']" />
        <FormField v-model="form.notes" label="Notes" type="textarea" />
      </div>
    </SlidePanel>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import SlidePanel from '@/components/ui/SlidePanel.vue'
import FormField from '@/components/ui/FormField.vue'
import { useLinkedData } from '@/composables/useLinkedData'
import dayjs from 'dayjs'

const { customers, salesPersons, beatPlans, loadCustomers, loadSalesPersons, loadBeatPlans } = useLinkedData()

const search = ref('')
const statusFilter = ref('')
const dateFilter = ref('')
const loading = ref(false)
const saving = ref(false)
const panelOpen = ref(false)
const editing = ref(null)
const visits = ref([])
const errors = reactive({})

const form = reactive({ customer: '', sales_person: '', beat_plan: '', visit_date: dayjs().format('YYYY-MM-DD'), status: 'Planned', notes: '' })

async function load() {
  loading.value = true
  try {
    const res = await frappe.call({ method: 'frappe.client.get_list', args: { doctype: 'SFA Visit', fields: ['name','customer','sales_person','visit_date','check_in_time','status','beat_plan','notes'], order_by: 'visit_date desc', limit: 200 } })
    visits.value = res.message || []
  } catch (e) { console.error(e) } finally { loading.value = false }
}

function openNew() {
  editing.value = null
  Object.assign(form, { customer: '', sales_person: '', beat_plan: '', visit_date: dayjs().format('YYYY-MM-DD'), status: 'Planned', notes: '' })
  Object.keys(errors).forEach(k => delete errors[k])
  panelOpen.value = true
}

function openEdit(v) {
  editing.value = v.name
  Object.assign(form, { customer: v.customer, sales_person: v.sales_person, beat_plan: v.beat_plan || '', visit_date: v.visit_date, status: v.status, notes: v.notes || '' })
  Object.keys(errors).forEach(k => delete errors[k])
  panelOpen.value = true
}

async function save() {
  let valid = true
  if (!form.customer) { errors.customer = 'Required'; valid = false }
  if (!form.sales_person) { errors.sales_person = 'Required'; valid = false }
  if (!form.visit_date) { errors.visit_date = 'Required'; valid = false }
  if (!valid) return
  saving.value = true
  try {
    const doc = { doctype: 'SFA Visit', ...form }
    if (editing.value) { doc.name = editing.value; await frappe.call({ method: 'frappe.client.save', args: { doc } }) }
    else { await frappe.call({ method: 'frappe.client.insert', args: { doc } }) }
    frappe.show_alert({ message: editing.value ? 'Visit updated' : 'Visit created', indicator: 'green' })
    panelOpen.value = false
    load()
  } catch (e) { frappe.show_alert({ message: e.message || 'Save failed', indicator: 'red' }) }
  finally { saving.value = false }
}

const filtered = computed(() => {
  let l = visits.value
  if (search.value) { const q = search.value.toLowerCase(); l = l.filter(v => v.customer?.toLowerCase().includes(q) || v.sales_person?.toLowerCase().includes(q)) }
  if (statusFilter.value) l = l.filter(v => v.status === statusFilter.value)
  if (dateFilter.value) l = l.filter(v => v.visit_date === dateFilter.value)
  return l
})

const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'
const formatTime = (t) => t ? dayjs(t).format('HH:mm') : '—'
const statusClass = (s) => ({ 'In Progress': 'bg-green-50 text-green-700', 'Completed': 'bg-blue-50 text-blue-700', 'Planned': 'bg-gray-100 text-gray-600', 'Cancelled': 'bg-red-50 text-red-700' })[s] || 'bg-gray-100 text-gray-600'

onMounted(() => { load(); loadCustomers(); loadSalesPersons(); loadBeatPlans() })
</script>
