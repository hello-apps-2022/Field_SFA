<template>
  <div class="flex h-full flex-col">
    <div class="flex items-center gap-3 border-b border-gray-200 bg-white px-4 py-2.5">
      <div class="relative">
        <FeatherIcon name="search" class="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-gray-400" />
        <input v-model="search" type="text" placeholder="Search beat plans..."
          class="h-9 rounded-md border border-gray-200 bg-white pl-8 pr-3 text-sm focus:border-gray-400 focus:outline-none w-56" />
      </div>
      <select v-model="statusFilter" class="h-9 rounded-md border border-gray-200 bg-white px-3 text-sm">
        <option value="">All Statuses</option>
        <option>Draft</option><option>Active</option><option>Completed</option>
      </select>
      <div class="flex-1" />
      <button class="flex h-9 items-center gap-1.5 rounded-md border border-gray-200 bg-white px-3 text-sm text-gray-600 hover:bg-gray-50" @click="load">
        <FeatherIcon name="refresh-cw" class="h-3.5 w-3.5" :class="loading ? 'animate-spin' : ''" />
        Refresh
      </button>
      <button class="flex h-9 items-center gap-1.5 rounded-md bg-gray-900 px-3 text-sm font-medium text-white hover:bg-gray-700" @click="openNew">
        <FeatherIcon name="plus" class="h-3.5 w-3.5" />
        New Beat Plan
      </button>
    </div>

    <div class="flex-1 overflow-auto">
      <table class="w-full text-sm">
        <thead class="sticky top-0 border-b border-gray-200 bg-gray-50">
          <tr>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Plan Name</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Territory</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Sales Person</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Date</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Customers</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Status</th>
            <th class="px-4 py-2.5" />
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="bp in filtered" :key="bp.name" class="hover:bg-gray-50 transition-colors group">
            <td class="px-4 py-3 font-medium text-gray-900">{{ bp.plan_name }}</td>
            <td class="px-4 py-3 text-gray-600">{{ bp.territory || '—' }}</td>
            <td class="px-4 py-3 text-gray-600">{{ bp.sales_person || '—' }}</td>
            <td class="px-4 py-3 text-gray-600">{{ formatDate(bp.date) }}</td>
            <td class="px-4 py-3 text-gray-600">{{ bp.customer_count || '—' }}</td>
            <td class="px-4 py-3">
              <span class="rounded-full px-2 py-0.5 text-xs font-medium bg-gray-100 text-gray-600">{{ bp.status || 'Draft' }}</span>
            </td>
            <td class="px-4 py-3">
              <button class="opacity-0 group-hover:opacity-100 rounded-md border border-gray-200 px-2 py-1 text-xs text-gray-600 hover:bg-gray-100 transition-all" @click="openEdit(bp)">
                Edit
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="!loading && !filtered.length" class="flex flex-col items-center justify-center py-20 text-gray-400">
        <FeatherIcon name="map" class="h-10 w-10 mb-3" />
        <p class="text-sm font-medium">No beat plans found</p>
      </div>
      <div v-if="loading" class="flex justify-center py-12">
        <FeatherIcon name="loader" class="h-6 w-6 animate-spin text-gray-400" />
      </div>
    </div>

    <!-- Slide Panel -->
    <SlidePanel v-model="panelOpen" :title="editing ? 'Edit Beat Plan' : 'New Beat Plan'" :saving="saving" @save="save">
      <div class="space-y-4">
        <FormField v-model="form.plan_name" label="Plan Name" required :error="errors.plan_name" />
        <FormField v-model="form.territory" label="Territory" type="select" :options="territories" required :error="errors.territory" />
        <FormField v-model="form.sales_person" label="Sales Person" type="select" :options="salesPersons" required :error="errors.sales_person" />
        <FormField v-model="form.date" label="Date" type="date" required :error="errors.date" />
        <FormField v-model="form.status" label="Status" type="select" :options="['Draft','Active','Completed']" />
        <FormField v-model="form.geofence_radius" label="Geofence Radius (m)" type="number" help="Distance in metres for auto check-in/out" />

        <!-- Customer list -->
        <div>
          <div class="flex items-center justify-between mb-2">
            <label class="text-xs font-medium text-gray-600">Customers on Route</label>
            <button class="text-xs text-gray-500 hover:text-gray-800 flex items-center gap-1" @click="addCustomer">
              <FeatherIcon name="plus" class="h-3 w-3" /> Add
            </button>
          </div>
          <div class="space-y-2">
            <div v-for="(row, i) in form.customers" :key="i" class="flex items-center gap-2">
              <select v-model="row.customer" class="flex-1 rounded-md border border-gray-200 bg-white px-2 py-1.5 text-sm focus:border-gray-400 focus:outline-none">
                <option value="">Select customer...</option>
                <option v-for="c in customers" :key="c.value" :value="c.value">{{ c.label }}</option>
              </select>
              <input v-model="row.sequence" type="number" placeholder="Seq" class="w-16 rounded-md border border-gray-200 bg-white px-2 py-1.5 text-sm focus:outline-none" />
              <button class="text-gray-400 hover:text-red-500 transition-colors" @click="removeCustomer(i)">
                <FeatherIcon name="x" class="h-4 w-4" />
              </button>
            </div>
            <div v-if="!form.customers.length" class="rounded-md bg-gray-50 px-3 py-2 text-xs text-gray-400">
              No customers added yet
            </div>
          </div>
        </div>
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

const { customers, territories, salesPersons, loadCustomers, loadTerritories, loadSalesPersons } = useLinkedData()

const search = ref('')
const statusFilter = ref('')
const loading = ref(false)
const saving = ref(false)
const panelOpen = ref(false)
const editing = ref(null)
const beatPlans = ref([])
const errors = reactive({})

const form = reactive({ plan_name: '', territory: '', sales_person: '', date: dayjs().format('YYYY-MM-DD'), status: 'Draft', geofence_radius: 100, customers: [] })

async function load() {
  loading.value = true
  try {
    const res = await frappe.call({ method: 'frappe.client.get_list', args: { doctype: 'SFA Beat Plan', fields: ['name','plan_name','territory','sales_person','date','status'], order_by: 'date desc', limit: 200 } })
    beatPlans.value = res.message || []
  } catch (e) { console.error(e) } finally { loading.value = false }
}

function openNew() {
  editing.value = null
  Object.assign(form, { plan_name: '', territory: '', sales_person: '', date: dayjs().format('YYYY-MM-DD'), status: 'Draft', geofence_radius: 100, customers: [] })
  Object.keys(errors).forEach(k => delete errors[k])
  panelOpen.value = true
}

function openEdit(bp) {
  editing.value = bp.name
  Object.assign(form, { plan_name: bp.plan_name, territory: bp.territory || '', sales_person: bp.sales_person || '', date: bp.date || dayjs().format('YYYY-MM-DD'), status: bp.status || 'Draft', geofence_radius: bp.geofence_radius || 100, customers: [] })
  Object.keys(errors).forEach(k => delete errors[k])
  panelOpen.value = true
}

function addCustomer() { form.customers.push({ customer: '', sequence: form.customers.length + 1 }) }
function removeCustomer(i) { form.customers.splice(i, 1) }

async function save() {
  let valid = true
  if (!form.plan_name) { errors.plan_name = 'Required'; valid = false }
  if (!form.territory) { errors.territory = 'Required'; valid = false }
  if (!form.sales_person) { errors.sales_person = 'Required'; valid = false }
  if (!valid) return
  saving.value = true
  try {
    const doc = {
      doctype: 'SFA Beat Plan',
      plan_name: form.plan_name, territory: form.territory, sales_person: form.sales_person,
      date: form.date, status: form.status, geofence_radius: form.geofence_radius,
      customers: form.customers.filter(c => c.customer).map(c => ({ doctype: 'SFA Beat Plan Customer', customer: c.customer, sequence: c.sequence })),
    }
    if (editing.value) { doc.name = editing.value; await frappe.call({ method: 'frappe.client.save', args: { doc } }) }
    else { await frappe.call({ method: 'frappe.client.insert', args: { doc } }) }
    frappe.show_alert({ message: editing.value ? 'Beat plan updated' : 'Beat plan created', indicator: 'green' })
    panelOpen.value = false; load()
  } catch (e) { frappe.show_alert({ message: e.message || 'Save failed', indicator: 'red' }) }
  finally { saving.value = false }
}

const filtered = computed(() => {
  let l = beatPlans.value
  if (search.value) { const q = search.value.toLowerCase(); l = l.filter(b => b.plan_name?.toLowerCase().includes(q)) }
  if (statusFilter.value) l = l.filter(b => b.status === statusFilter.value)
  return l
})

const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'
onMounted(() => { load(); loadCustomers(); loadTerritories(); loadSalesPersons() })
</script>
