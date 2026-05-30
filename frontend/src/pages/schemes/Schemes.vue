<template>
  <div class="flex h-full flex-col overflow-hidden">
    <div class="flex h-[52px] shrink-0 items-center border-b border-gray-100 bg-white px-5 gap-3">
      <h1 class="text-sm font-semibold text-gray-900">Free Carton Schemes</h1>
      <div class="flex-1" />
      <span class="text-xs text-gray-400">{{ rows.length }} schemes</span>
      <label v-if="auth.isAdmin" class="mr-2 flex items-center gap-2 text-xs text-gray-600">
        <input type="checkbox" v-model="allowFree" @change="saveFreePolicy" class="rounded border-gray-300" />
        Reps can give free at will
      </label>
      <button @click="openNew" class="inline-flex h-8 items-center gap-1.5 rounded-md bg-gray-900 px-3 text-xs font-medium text-white hover:bg-gray-700">
        <FeatherIcon name="plus" class="h-3.5 w-3.5" /> New Scheme
      </button>
    </div>

    <div class="flex-1 overflow-auto">
      <div v-if="loading" class="flex h-40 items-center justify-center">
        <FeatherIcon name="loader" class="h-6 w-6 animate-spin text-gray-400" />
      </div>

      <table v-else-if="rows.length" class="w-full text-sm">
        <thead class="sticky top-0 bg-white border-b border-gray-100">
          <tr>
            <th class="px-5 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Applies To</th>
            <th class="px-5 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Buy</th>
            <th class="px-5 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Get Free</th>
            <th class="px-5 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Valid</th>
            <th class="px-5 py-2.5 text-center text-[10px] font-semibold uppercase tracking-wide text-gray-400">Status</th>
            <th class="px-5 py-2.5 text-right text-[10px] font-semibold uppercase tracking-wide text-gray-400"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr v-for="r in rows" :key="r.name" class="hover:bg-gray-50 transition-colors">
            <td class="px-5 py-3 text-gray-900">{{ targetLabel(r) }}</td>
            <td class="px-5 py-3 text-gray-700">{{ r.buy_qty }} &times; {{ r.buy_item }}</td>
            <td class="px-5 py-3 text-green-700">{{ r.free_qty }} &times; {{ r.free_item }}</td>
            <td class="px-5 py-3 text-gray-500">{{ fmtDate(r.valid_from) }} &ndash; {{ fmtDate(r.valid_to) }}</td>
            <td class="px-5 py-3 text-center">
              <span :class="r.enabled ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'"
                class="rounded px-1.5 py-0.5 text-[10px] font-medium">{{ r.enabled ? 'Active' : 'Off' }}</span>
            </td>
            <td class="px-5 py-3 text-right whitespace-nowrap">
              <button @click="openEdit(r)" class="text-gray-400 hover:text-gray-800 mr-3" title="Edit">
                <FeatherIcon name="edit-2" class="h-3.5 w-3.5" />
              </button>
              <button @click="remove(r)" class="text-gray-300 hover:text-red-500" title="Delete">
                <FeatherIcon name="trash-2" class="h-3.5 w-3.5" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-else class="flex flex-col items-center py-20 text-gray-400">
        <FeatherIcon name="gift" class="h-10 w-10 mb-3" />
        <p class="text-sm font-medium text-gray-500">No free carton schemes yet</p>
        <p class="text-xs mt-1">Create one to auto-suggest free cartons on qualifying orders</p>
      </div>
    </div>

    <SlidePanel v-model="panel" :title="editing ? 'Edit Scheme' : 'New Scheme'" :saving="saving"
      :save-label="editing ? 'Save' : 'Create'" @save="save" width="520px">
      <div class="space-y-4">
        <div>
          <MultiSelectField v-model="formData.customers" label="Customers" :options="customerOptions"
            placeholder="Search customers…" :error="errors.target" />
          <MultiSelectField v-model="formData.territories" label="Territories" :options="territoryOptions"
            placeholder="Search territories…" class="mt-3" />
          <p class="mt-1.5 text-xs text-gray-400">Applies to any order from a listed customer, or from a customer in a listed territory. Add at least one.</p>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <FormField v-model="formData.buy_item" label="Buy Item" type="select" :options="itemOptions" required :error="errors.buy_item" />
          <FormField v-model.number="formData.buy_qty" label="Buy Qty" type="number" required :error="errors.buy_qty" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <FormField v-model="formData.free_item" label="Free Item" type="select" :options="itemOptions" required :error="errors.free_item" />
          <FormField v-model.number="formData.free_qty" label="Free Qty" type="number" required :error="errors.free_qty" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <FormField v-model="formData.valid_from" label="Valid From" type="date" required :error="errors.valid_from" />
          <FormField v-model="formData.valid_to" label="Valid To" type="date" required :error="errors.valid_to" />
        </div>
        <label class="flex items-center gap-2 text-sm text-gray-700">
          <input type="checkbox" v-model="formData.enabled" class="rounded border-gray-300" /> Enabled
        </label>
      </div>
    </SlidePanel>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { call, getList } from '@/utils/frappe'
import { successToast, errorToast } from '@/utils/toast'
import FeatherIcon from '@/components/ui/FeatherIcon.vue'
import SlidePanel from '@/components/ui/SlidePanel.vue'
import FormField from '@/components/ui/FormField.vue'
import MultiSelectField from '@/components/ui/MultiSelectField.vue'
import dayjs from 'dayjs'
import { auth } from '@/utils/auth'

const rows = ref([])
const allowFree = ref(auth.allowDiscretionaryFree)
const loading = ref(false)
const panel = ref(false)
const saving = ref(false)
const editing = ref(null)
const errors = reactive({})

const customerOptions = ref([])
const territoryOptions = ref([])
const itemOptions = ref([])

const blank = () => ({
  customers: [], territories: [],
  buy_item: '', buy_qty: 1, free_item: '', free_qty: 1,
  valid_from: dayjs().format('YYYY-MM-DD'),
  valid_to: dayjs().add(1, 'month').format('YYYY-MM-DD'),
  enabled: true,
})
const formData = reactive(blank())

const fmtDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'

function nameLabel(opts, v) { const o = opts.value.find(x => x.value === v); return o ? o.label : v }
function targetLabel(r) {
  const parts = []
  const c = r.customers || [], t = r.territories || []
  if (c.length) parts.push(c.length <= 2 ? c.map(x => nameLabel(customerOptions, x)).join(', ') : c.length + ' customers')
  if (t.length) parts.push(t.length <= 2 ? t.map(x => nameLabel(territoryOptions, x)).join(', ') : t.length + ' territories')
  return parts.join(' · ') || '—'
}

async function loadRows() {
  loading.value = true
  try {
    rows.value = (await call('sfa_core.field_sfa.api.free_carton.get_schemes')).message || []
  } catch (e) { errorToast(e.message || 'Failed to load schemes') }
  finally { loading.value = false }
}

async function loadOptions() {
  try {
    const [cust, terr, itms] = await Promise.all([
      getList('Customer', { fields: ['name','customer_name'], limit: 2000, orderBy: 'customer_name asc' }),
      getList('Territory', { fields: ['name'], limit: 500, orderBy: 'name asc' }),
      getList('Item', { fields: ['name','item_name'], filters: { disabled: 0 }, limit: 2000, orderBy: 'item_name asc' }),
    ])
    customerOptions.value = cust.map(c => ({ value: c.name, label: c.customer_name || c.name }))
    territoryOptions.value = terr.map(t => ({ value: t.name, label: t.name }))
    itemOptions.value = itms.map(i => ({ value: i.name, label: i.item_name || i.name }))
  } catch (e) { /* options best-effort */ }
}

function reset() { Object.assign(formData, blank()); Object.keys(errors).forEach(k => delete errors[k]) }
function openNew() { editing.value = null; reset(); panel.value = true }
function openEdit(r) {
  editing.value = r.name
  Object.assign(formData, {
    customers: [...(r.customers || [])], territories: [...(r.territories || [])],
    buy_item: r.buy_item, buy_qty: r.buy_qty, free_item: r.free_item, free_qty: r.free_qty,
    valid_from: r.valid_from, valid_to: r.valid_to, enabled: !!r.enabled,
  })
  Object.keys(errors).forEach(k => delete errors[k])
  panel.value = true
}

function validateForm() {
  Object.keys(errors).forEach(k => delete errors[k])
  if (!formData.customers.length && !formData.territories.length) errors.target = 'Pick at least one customer or territory'
  if (!formData.buy_item) errors.buy_item = 'Required'
  if (!(formData.buy_qty > 0)) errors.buy_qty = 'Must be > 0'
  if (!formData.free_item) errors.free_item = 'Required'
  if (!(formData.free_qty > 0)) errors.free_qty = 'Must be > 0'
  if (!formData.valid_from) errors.valid_from = 'Required'
  if (!formData.valid_to) errors.valid_to = 'Required'
  if (formData.valid_from && formData.valid_to && formData.valid_from > formData.valid_to) errors.valid_to = 'Must be after Valid From'
  return Object.keys(errors).length === 0
}

async function save() {
  if (!validateForm()) return
  saving.value = true
  try {
    await call('sfa_core.field_sfa.api.free_carton.save_scheme', {
      data: JSON.stringify({
        name: editing.value || null,
        customers: formData.customers,
        territories: formData.territories,
        buy_item: formData.buy_item, buy_qty: formData.buy_qty,
        free_item: formData.free_item, free_qty: formData.free_qty,
        valid_from: formData.valid_from, valid_to: formData.valid_to,
        enabled: formData.enabled ? 1 : 0,
      }),
    })
    successToast(editing.value ? 'Scheme updated' : 'Scheme created')
    panel.value = false
    await loadRows()
  } catch (e) { errorToast(e.message || 'Save failed') }
  finally { saving.value = false }
}

async function remove(r) {
  if (!confirm('Delete this scheme?')) return
  try {
    await call('sfa_core.field_sfa.api.free_carton.delete_scheme', { name: r.name })
    successToast('Scheme deleted')
    await loadRows()
  } catch (e) { errorToast(e.message || 'Delete failed') }
}

async function saveFreePolicy() {
  try {
    await call('sfa_core.field_sfa.api.free_carton.set_free_carton_policy', { allow: allowFree.value ? 1 : 0 })
    if (window.frappe_boot && window.frappe_boot.sfa) window.frappe_boot.sfa.allow_discretionary_free = allowFree.value ? 1 : 0
    successToast(allowFree.value ? 'Reps can now give free cartons at will' : 'Discretionary free cartons disabled')
  } catch (e) { errorToast(e.message || 'Failed to save'); allowFree.value = !allowFree.value }
}

onMounted(() => { loadOptions().then(loadRows) })
</script>
