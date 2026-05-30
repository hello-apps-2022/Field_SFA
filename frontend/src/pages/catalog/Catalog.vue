<template>
  <div class="flex h-full flex-col overflow-hidden">
    <div class="flex h-[52px] shrink-0 items-center border-b border-gray-100 bg-white px-5 gap-4">
      <h1 class="text-sm font-semibold text-gray-900">Catalog</h1>
      <div class="flex items-center gap-1">
        <button v-for="t in tabs" :key="t.id" @click="tab = t.id"
          class="rounded-md px-3 py-1 text-xs font-medium transition-colors"
          :class="tab === t.id ? 'bg-gray-900 text-white' : 'text-gray-500 hover:bg-gray-100'">
          {{ t.label }}
        </button>
      </div>
      <div class="flex-1" />
      <button v-if="tab === 'products'" @click="openProduct()" class="inline-flex h-8 items-center gap-1.5 rounded-md bg-gray-900 px-3 text-xs font-medium text-white hover:bg-gray-700">
        <FeatherIcon name="plus" class="h-3.5 w-3.5" /> New Product
      </button>
      <button v-else-if="tab === 'companies'" @click="openCompany()" class="inline-flex h-8 items-center gap-1.5 rounded-md bg-gray-900 px-3 text-xs font-medium text-white hover:bg-gray-700">
        <FeatherIcon name="plus" class="h-3.5 w-3.5" /> New Company
      </button>
    </div>

    <div class="flex-1 overflow-auto">
      <div v-if="loading" class="flex h-40 items-center justify-center">
        <FeatherIcon name="loader" class="h-6 w-6 animate-spin text-gray-400" />
      </div>

      <!-- PRODUCTS -->
      <table v-else-if="tab === 'products' && products.length" class="w-full text-sm">
        <thead class="sticky top-0 bg-white border-b border-gray-100">
          <tr>
            <th class="px-5 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Product</th>
            <th class="px-5 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Category</th>
            <th class="px-5 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Company</th>
            <th class="px-5 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Size</th>
            <th class="px-5 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Packaging</th>
            <th class="px-5 py-2.5 text-right text-[10px] font-semibold uppercase tracking-wide text-gray-400">Price</th>
            <th class="px-5 py-2.5 text-right text-[10px] font-semibold uppercase tracking-wide text-gray-400"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr v-for="p in products" :key="p.name" class="hover:bg-gray-50" :class="p.disabled ? 'opacity-50' : ''">
            <td class="px-5 py-3 font-medium text-gray-900">{{ p.item_name }}</td>
            <td class="px-5 py-3 text-gray-600">{{ p.item_group }}</td>
            <td class="px-5 py-3 text-gray-600">{{ p.custom_sfa_company || '\u2014' }}</td>
            <td class="px-5 py-3 text-gray-500">{{ p.custom_size || '\u2014' }}</td>
            <td class="px-5 py-3 text-gray-500">{{ [p.custom_packaging, p.custom_pack_config].filter(Boolean).join(' \u00b7 ') || '\u2014' }}</td>
            <td class="px-5 py-3 text-right text-gray-700">{{ p.standard_rate ? fmt(p.standard_rate) : '\u2014' }}</td>
            <td class="px-5 py-3 text-right whitespace-nowrap">
              <button @click="openProduct(p)" class="text-gray-400 hover:text-gray-800 mr-3" title="Edit"><FeatherIcon name="edit-2" class="h-3.5 w-3.5" /></button>
              <button v-if="!p.disabled" @click="disableProduct(p)" class="text-gray-300 hover:text-red-500" title="Disable"><FeatherIcon name="slash" class="h-3.5 w-3.5" /></button>
              <button v-else @click="enableProduct(p)" class="text-gray-300 hover:text-green-600" title="Enable"><FeatherIcon name="check-circle" class="h-3.5 w-3.5" /></button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- CATEGORIES -->
      <div v-else-if="tab === 'categories'" class="p-5 max-w-md">
        <div class="mb-3 flex gap-2">
          <input v-model="newCategory" placeholder="New category name"
            class="h-9 flex-1 rounded-md border border-gray-200 px-3 text-sm focus:border-gray-400 focus:outline-none" />
          <button @click="addCategory" :disabled="!newCategory.trim()" class="h-9 rounded-md bg-gray-900 px-3 text-xs font-medium text-white hover:bg-gray-700 disabled:opacity-40">Add</button>
        </div>
        <div class="divide-y divide-gray-50 rounded-md border border-gray-100">
          <div v-for="c in categories" :key="c.name" class="flex items-center justify-between px-4 py-2.5 text-sm text-gray-800">
            <span :class="c.enabled ? '' : 'text-gray-400 line-through'">{{ c.name }}</span>
            <div class="flex items-center gap-2">
              <span :class="c.enabled ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'" class="rounded px-1.5 py-0.5 text-[10px] font-medium">{{ c.enabled ? 'Active' : 'Off' }}</span>
              <button @click="toggleCategory(c)" class="text-gray-300 hover:text-gray-700" :title="c.enabled ? 'Disable' : 'Enable'"><FeatherIcon :name="c.enabled ? 'slash' : 'check-circle'" class="h-3.5 w-3.5" /></button>
            </div>
          </div>
          <div v-if="!categories.length" class="px-4 py-6 text-center text-xs text-gray-400">No categories yet</div>
        </div>
      </div>

      <!-- COMPANIES -->
      <table v-else-if="tab === 'companies' && companies.length" class="w-full text-sm">
        <thead class="sticky top-0 bg-white border-b border-gray-100">
          <tr>
            <th class="px-5 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Company</th>
            <th class="px-5 py-2.5 text-center text-[10px] font-semibold uppercase tracking-wide text-gray-400">Status</th>
            <th class="px-5 py-2.5 text-right text-[10px] font-semibold uppercase tracking-wide text-gray-400"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr v-for="c in companies" :key="c.name" class="hover:bg-gray-50">
            <td class="px-5 py-3 font-medium text-gray-900">{{ c.company_name }}</td>
            <td class="px-5 py-3 text-center">
              <span :class="c.enabled ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'" class="rounded px-1.5 py-0.5 text-[10px] font-medium">{{ c.enabled ? 'Active' : 'Off' }}</span>
            </td>
            <td class="px-5 py-3 text-right whitespace-nowrap">
              <button @click="openCompany(c)" class="text-gray-400 hover:text-gray-800 mr-3" title="Edit"><FeatherIcon name="edit-2" class="h-3.5 w-3.5" /></button>
              <button @click="deleteCompany(c)" class="text-gray-300 hover:text-red-500" title="Delete"><FeatherIcon name="trash-2" class="h-3.5 w-3.5" /></button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-else-if="!loading" class="flex flex-col items-center py-20 text-gray-400">
        <FeatherIcon name="package" class="h-10 w-10 mb-3" />
        <p class="text-sm font-medium text-gray-500">Nothing here yet</p>
      </div>
    </div>

    <!-- Product panel -->
    <SlidePanel v-model="productPanel" :title="editingProduct ? 'Edit Product' : 'New Product'" :saving="saving" :save-label="editingProduct ? 'Save' : 'Create'" @save="saveProduct" width="520px">
      <div class="space-y-4">
        <FormField v-model="pForm.item_name" label="Product Name" required :error="pErrors.item_name" />
        <div class="grid grid-cols-2 gap-3">
          <FormField v-model="pForm.item_group" label="Category" type="select" :options="categoryOptions" required :error="pErrors.item_group" />
          <FormField v-model="pForm.custom_sfa_company" label="Company" type="select" :options="companyOptions" :error="pErrors.custom_sfa_company" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <FormField v-model="pForm.custom_size" label="Size" placeholder="550ml, 1.5L\u2026" />
          <FormField v-model="pForm.custom_packaging" label="Packaging" placeholder="Box, Shrink Wrap\u2026" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <FormField v-model="pForm.custom_pack_config" label="Pack Config" placeholder="12 Pack, 24 Pack\u2026" />
          <FormField v-model.number="pForm.standard_rate" :label="`Price (${currencyLabel()})`" type="number" />
        </div>
      </div>
    </SlidePanel>

    <!-- Company panel -->
    <SlidePanel v-model="companyPanel" :title="editingCompany ? 'Edit Company' : 'New Company'" :saving="saving" :save-label="editingCompany ? 'Save' : 'Create'" @save="saveCompany" width="420px">
      <div class="space-y-4">
        <FormField v-model="cForm.company_name" label="Company Name" required :error="cErrors.company_name" />
        <label class="flex items-center gap-2 text-sm text-gray-700">
          <input type="checkbox" v-model="cForm.enabled" class="rounded border-gray-300" /> Enabled
        </label>
      </div>
    </SlidePanel>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { call } from '@/utils/frappe'
import { successToast, errorToast } from '@/utils/toast'
import { formatCurrency, currencyLabel } from '@/utils/currency'
import FeatherIcon from '@/components/ui/FeatherIcon.vue'
import SlidePanel from '@/components/ui/SlidePanel.vue'
import FormField from '@/components/ui/FormField.vue'

const tabs = [
  { id: 'products', label: 'Products' },
  { id: 'categories', label: 'Categories' },
  { id: 'companies', label: 'Companies' },
]
const tab = ref('products')
const loading = ref(false)
const saving = ref(false)

const products = ref([])
const categories = ref([])
const companies = ref([])
const newCategory = ref('')

const fmt = (v) => formatCurrency(v || 0)
const categoryOptions = computed(() => categories.value.map(c => c.name))
const companyOptions = computed(() => companies.value.filter(c => c.enabled).map(c => c.company_name))

async function loadAll() {
  loading.value = true
  try {
    const [p, cat, co] = await Promise.all([
      call('sfa_core.field_sfa.api.catalog.get_products'),
      call('sfa_core.field_sfa.api.catalog.get_categories'),
      call('sfa_core.field_sfa.api.catalog.get_companies'),
    ])
    products.value = p.message || []
    categories.value = cat.message || []
    companies.value = co.message || []
  } catch (e) { errorToast(e.message || 'Failed to load catalog') }
  finally { loading.value = false }
}

// ── Products ──
const productPanel = ref(false)
const editingProduct = ref(null)
const pErrors = reactive({})
const pForm = reactive({ item_name: '', item_group: '', custom_sfa_company: '', custom_size: '', custom_packaging: '', custom_pack_config: '', standard_rate: 0 })

function openProduct(p) {
  Object.keys(pErrors).forEach(k => delete pErrors[k])
  if (p) {
    editingProduct.value = p.name
    Object.assign(pForm, {
      item_name: p.item_name, item_group: p.item_group, custom_sfa_company: p.custom_sfa_company || '',
      custom_size: p.custom_size || '', custom_packaging: p.custom_packaging || '',
      custom_pack_config: p.custom_pack_config || '', standard_rate: p.standard_rate || 0,
    })
  } else {
    editingProduct.value = null
    Object.assign(pForm, { item_name: '', item_group: '', custom_sfa_company: '', custom_size: '', custom_packaging: '', custom_pack_config: '', standard_rate: 0 })
  }
  productPanel.value = true
}

async function saveProduct() {
  Object.keys(pErrors).forEach(k => delete pErrors[k])
  if (!pForm.item_name.trim()) pErrors.item_name = 'Required'
  if (!pForm.item_group) pErrors.item_group = 'Required'
  if (Object.keys(pErrors).length) return
  saving.value = true
  try {
    await call('sfa_core.field_sfa.api.catalog.save_product', {
      name: editingProduct.value || undefined,
      item_name: pForm.item_name, item_group: pForm.item_group,
      custom_sfa_company: pForm.custom_sfa_company || undefined,
      custom_size: pForm.custom_size || undefined,
      custom_packaging: pForm.custom_packaging || undefined,
      custom_pack_config: pForm.custom_pack_config || undefined,
      standard_rate: pForm.standard_rate || 0,
    })
    successToast(editingProduct.value ? 'Product updated' : 'Product created')
    productPanel.value = false
    await loadAll()
  } catch (e) { errorToast(e.message || 'Save failed') }
  finally { saving.value = false }
}

async function disableProduct(p) {
  if (!confirm('Disable ' + p.item_name + '? It will stop appearing in new orders.')) return
  try {
    await call('sfa_core.field_sfa.api.catalog.set_product_enabled', { name: p.name, enabled: 0 })
    successToast('Product disabled')
    await loadAll()
  } catch (e) { errorToast(e.message || 'Failed') }
}

async function enableProduct(p) {
  try {
    await call('sfa_core.field_sfa.api.catalog.set_product_enabled', { name: p.name, enabled: 1 })
    successToast('Product enabled')
    await loadAll()
  } catch (e) { errorToast(e.message || 'Failed') }
}

// ── Categories ──
async function addCategory() {
  const nameVal = newCategory.value.trim()
  if (!nameVal) return
  try {
    await call('sfa_core.field_sfa.api.catalog.save_category', { category_name: nameVal })
    newCategory.value = ''
    successToast('Category added')
    await loadAll()
  } catch (e) { errorToast(e.message || 'Failed') }
}

async function toggleCategory(c) {
  try {
    await call('sfa_core.field_sfa.api.catalog.set_category_enabled', { name: c.name, enabled: c.enabled ? 0 : 1 })
    successToast(c.enabled ? 'Category disabled' : 'Category enabled')
    await loadAll()
  } catch (e) { errorToast(e.message || 'Failed') }
}

// ── Companies ──
const companyPanel = ref(false)
const editingCompany = ref(null)
const cErrors = reactive({})
const cForm = reactive({ company_name: '', enabled: true })

function openCompany(c) {
  Object.keys(cErrors).forEach(k => delete cErrors[k])
  if (c) {
    editingCompany.value = c.name
    Object.assign(cForm, { company_name: c.company_name, enabled: !!c.enabled })
  } else {
    editingCompany.value = null
    Object.assign(cForm, { company_name: '', enabled: true })
  }
  companyPanel.value = true
}

async function saveCompany() {
  Object.keys(cErrors).forEach(k => delete cErrors[k])
  if (!cForm.company_name.trim()) { cErrors.company_name = 'Required'; return }
  saving.value = true
  try {
    await call('sfa_core.field_sfa.api.catalog.save_company', {
      name: editingCompany.value || undefined,
      company_name: cForm.company_name, enabled: cForm.enabled ? 1 : 0,
    })
    successToast(editingCompany.value ? 'Company updated' : 'Company created')
    companyPanel.value = false
    await loadAll()
  } catch (e) { errorToast(e.message || 'Save failed') }
  finally { saving.value = false }
}

async function deleteCompany(c) {
  if (!confirm('Delete ' + c.company_name + '?')) return
  try {
    await call('sfa_core.field_sfa.api.catalog.delete_company', { name: c.name })
    successToast('Company deleted')
    await loadAll()
  } catch (e) { errorToast(e.message || 'Delete failed') }
}

onMounted(loadAll)
</script>
