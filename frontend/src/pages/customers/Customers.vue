<template>
  <div class="flex h-full flex-col">
    <div class="flex items-center gap-3 border-b border-gray-200 bg-white px-4 py-2.5">
      <div class="relative">
        <FeatherIcon name="search" class="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-gray-400" />
        <input v-model="search" type="text" placeholder="Search customers..."
          class="h-9 rounded-md border border-gray-200 bg-white pl-8 pr-3 text-sm focus:border-gray-400 focus:outline-none w-56" />
      </div>
      <select v-model="groupFilter" class="h-9 rounded-md border border-gray-200 bg-white px-3 text-sm focus:border-gray-400 focus:outline-none">
        <option value="">All Groups</option>
        <option v-for="g in groups" :key="g">{{ g }}</option>
      </select>
      <select v-model="territoryFilter" class="h-9 rounded-md border border-gray-200 bg-white px-3 text-sm focus:border-gray-400 focus:outline-none">
        <option value="">All Territories</option>
        <option v-for="t in territories" :key="t">{{ t }}</option>
      </select>
      <div class="flex-1" />
      <span class="text-xs text-gray-400">{{ filtered.length }} customers</span>
      <button class="flex h-9 items-center gap-1.5 rounded-md border border-gray-200 bg-white px-3 text-sm text-gray-600 hover:bg-gray-50 transition-colors" @click="load">
        <FeatherIcon name="refresh-cw" class="h-3.5 w-3.5" :class="loading ? 'animate-spin' : ''" />
        Refresh
      </button>
      <button class="flex h-9 items-center gap-1.5 rounded-md bg-gray-900 px-3 text-sm font-medium text-white hover:bg-gray-700 transition-colors" @click="openNew">
        <FeatherIcon name="plus" class="h-3.5 w-3.5" />
        New Customer
      </button>
    </div>

    <div class="flex-1 overflow-auto">
      <table class="w-full text-sm">
        <thead class="sticky top-0 border-b border-gray-200 bg-gray-50">
          <tr>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Customer Name</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Group</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Territory</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Mobile</th>
            <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Status</th>
            <th class="px-4 py-2.5" />
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="c in filtered" :key="c.name"
            class="hover:bg-gray-50 transition-colors group cursor-pointer"
            @click="router.push('/customers/' + encodeURIComponent(c.name))">
            <td class="px-4 py-3">
              <p class="font-medium text-gray-900">{{ c.customer_name }}</p>
              <p class="text-xs text-gray-400">{{ c.name }}</p>
            </td>
            <td class="px-4 py-3 text-gray-600">{{ c.customer_group || '—' }}</td>
            <td class="px-4 py-3 text-gray-600">{{ c.territory || '—' }}</td>
            <td class="px-4 py-3 text-gray-600">{{ c.mobile_no || '—' }}</td>
            <td class="px-4 py-3">
              <span class="rounded-full px-2 py-0.5 text-xs font-medium"
                :class="c.disabled ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-700'">
                {{ c.disabled ? 'Disabled' : 'Active' }}
              </span>
            </td>
            <td class="px-4 py-3">
              <button class="opacity-0 group-hover:opacity-100 rounded-md border border-gray-200 px-2 py-1 text-xs text-gray-600 hover:bg-gray-100 transition-all" @click.stop="openEdit(c)">
                Edit
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="!loading && !filtered.length" class="flex flex-col items-center justify-center py-20 text-gray-400">
        <FeatherIcon name="users" class="h-10 w-10 mb-3" />
        <p class="text-sm font-medium">No customers found</p>
      </div>
      <div v-if="loading" class="flex justify-center py-12">
        <FeatherIcon name="loader" class="h-6 w-6 animate-spin text-gray-400" />
      </div>
    </div>

    <!-- Slide Panel -->
    <SlidePanel v-model="panelOpen" :title="editing ? 'Edit Customer' : 'New Customer'" :saving="saving" @save="save">
      <div class="space-y-4">
        <FormField v-model="form.customer_name" label="Customer Name" required :error="errors.customer_name" />
        <FormField v-model="form.customer_group" label="Customer Group" type="select" :options="customerGroups" />
        <FormField v-model="form.territory" label="Territory" type="select" :options="allTerritories" />
        <FormField v-model="form.mobile_no" label="Mobile No" type="tel" />
        <FormField v-model="form.email_id" label="Email" type="email" />
        <FormField v-model="form.customer_details" label="Notes" type="textarea" />
      </div>
    </SlidePanel>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { call } from '@/utils/frappe'
import SlidePanel from '@/components/ui/SlidePanel.vue'
import FormField from '@/components/ui/FormField.vue'
import { useLinkedData } from '@/composables/useLinkedData'

const { customerGroups, territories: allTerritories, loadCustomerGroups, loadTerritories } = useLinkedData()
const router = useRouter()

const search = ref('')
const groupFilter = ref('')
const territoryFilter = ref('')
const loading = ref(false)
const saving = ref(false)
const panelOpen = ref(false)
const editing = ref(null)
const customers = ref([])
const errors = reactive({})

const form = reactive({
  customer_name: '', customer_group: '', territory: '',
  mobile_no: '', email_id: '', customer_details: '',
})

const groups = computed(() => [...new Set(customers.value.map(c => c.customer_group).filter(Boolean))])
const territories = computed(() => [...new Set(customers.value.map(c => c.territory).filter(Boolean))])

async function load() {
  loading.value = true
  try {
    const res = await call('sfa_core.api.list.get_customers', { limit: 500 })
    customers.value = res.message || []
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

function openNew() {
  editing.value = null
  Object.assign(form, { customer_name: '', customer_group: '', territory: '', mobile_no: '', email_id: '', customer_details: '' })
  Object.keys(errors).forEach(k => delete errors[k])
  panelOpen.value = true
}

function openEdit(c) {
  editing.value = c.name
  Object.assign(form, { customer_name: c.customer_name, customer_group: c.customer_group || '', territory: c.territory || '', mobile_no: c.mobile_no || '', email_id: c.email_id || '', customer_details: c.customer_details || '' })
  Object.keys(errors).forEach(k => delete errors[k])
  panelOpen.value = true
}

async function save() {
  if (!form.customer_name.trim()) { errors.customer_name = 'Required'; return }
  saving.value = true
  try {
    const doc = { doctype: 'Customer', customer_type: 'Company', ...form }
    if (editing.value) {
      doc.name = editing.value
      await call('frappe.client.save', { doc })
    } else {
      await call('frappe.client.insert', { doc })
    }
    frappe.show_alert({ message: editing.value ? 'Customer updated' : 'Customer created', indicator: 'green' })
    panelOpen.value = false
    load()
  } catch (e) {
    frappe.show_alert({ message: e.message || 'Save failed', indicator: 'red' })
  } finally { saving.value = false }
}

const filtered = computed(() => {
  let l = customers.value
  if (search.value) { const q = search.value.toLowerCase(); l = l.filter(c => c.customer_name?.toLowerCase().includes(q) || c.name?.toLowerCase().includes(q)) }
  if (groupFilter.value) l = l.filter(c => c.customer_group === groupFilter.value)
  if (territoryFilter.value) l = l.filter(c => c.territory === territoryFilter.value)
  return l
})

onMounted(() => { load(); loadCustomerGroups(); loadTerritories() })
</script>
