<template>
  <SlidePanel v-model="newOrderPanel" :title="editingOrder ? 'Edit Order' : (orderForm.order_type === 'Van Sale' ? 'Van Sale' : 'New Order')" :saving="savingOrder" :save-label="orderForm.order_type === 'Van Sale' ? 'Record Sale' : 'Save Draft'" @save="saveOrder" width="560px">
    <div class="space-y-4">
      <div class="rounded-lg bg-gray-50 border border-gray-200 px-3 py-2.5 text-sm text-gray-700">
        <span class="text-xs text-gray-400 block mb-0.5">Customer</span>
        {{ customerName }}
      </div>
      <FormField v-model="orderForm.order_type" label="Order Type" type="select" :options="[{value:'Booking',label:'Booking — deliver later'},{value:'Van Sale',label:'Van Sale — immediate'}]" />
      <FormField v-model="orderForm.transaction_date" label="Order Date" type="date" required />
      <FormField v-model="orderForm.delivery_date" label="Delivery Date" type="date" :min="orderForm.transaction_date" />
      <div>
        <div class="flex items-center justify-between mb-2">
          <label class="text-xs font-medium text-gray-600">Items <span class="text-red-500">*</span></label>
          <button class="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-800" @click="addItem">
            <FeatherIcon name="plus" class="h-3 w-3" /> Add Item
          </button>
        </div>
        <div class="mb-2 space-y-2">
          <div v-if="categories.length" class="flex gap-1 overflow-x-auto pb-0.5">
            <button type="button" @click="itemCategory=''"
              class="shrink-0 rounded-full px-2.5 py-1 text-xs font-medium transition-colors"
              :class="itemCategory==='' ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'">All</button>
            <button v-for="c in categories" :key="c" type="button" @click="itemCategory=c"
              class="shrink-0 rounded-full px-2.5 py-1 text-xs font-medium transition-colors"
              :class="itemCategory===c ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'">{{ c }}</button>
          </div>
          <input v-model="itemSearch" ref="productSearch" type="text" placeholder="Search products to add…"
            class="w-full rounded-md border border-gray-200 px-2.5 py-1.5 text-sm focus:border-gray-400 focus:outline-none" />
          <div v-if="itemSearch || itemCategory" class="max-h-44 divide-y divide-gray-50 overflow-y-auto rounded-lg border border-gray-100">
            <button v-for="it in filteredItems" :key="it.value" type="button" @click="addProduct(it)"
              class="flex w-full items-center justify-between px-3 py-2 text-left text-sm hover:bg-gray-50">
              <span class="truncate text-gray-800">{{ it.label }}</span>
              <FeatherIcon name="plus-circle" class="ml-2 h-4 w-4 shrink-0 text-gray-400" />
            </button>
            <div v-if="!filteredItems.length" class="px-3 py-3 text-center text-xs text-gray-400">No products match</div>
          </div>
        </div>
        <div v-if="orderForm.items.length" class="mb-1 flex items-center gap-2 px-0.5">
          <span class="flex-1 text-[10px] font-medium uppercase tracking-wide text-gray-400">Item</span>
          <span class="w-14 text-center text-[10px] font-medium uppercase tracking-wide text-gray-400">Qty</span>
          <span class="w-20 text-center text-[10px] font-medium uppercase tracking-wide text-gray-400">Rate ({{ currencyLabel() }})</span>
          <span v-if="showFreeCol" class="w-16 text-center text-[10px] font-medium uppercase tracking-wide text-gray-400">Free</span>
          <span class="w-5" />
        </div>
        <div class="space-y-2">
          <div v-for="(row, i) in orderForm.items" :key="i" class="space-y-1">
            <div class="flex items-center gap-2">
              <select v-model="row.item_code" @change="onItemChange(row)"
                class="flex-1 rounded-md border border-gray-200 bg-white px-2 py-2 text-sm focus:border-gray-400 focus:outline-none">
                <option value="">Select item...</option>
                <option v-for="it in filteredItems" :key="it.value" :value="it.value">{{ it.label }}</option>
                <option v-if="row.item_code && !inFiltered(row.item_code)" :value="row.item_code">{{ row.item_name || row.item_code }}</option>
              </select>
              <input v-model.number="row.qty" type="number" min="1" @change="applyFreeSchemes"
                class="w-14 rounded-md border border-gray-200 px-2 py-2 text-sm text-center focus:border-gray-400 focus:outline-none"
                title="Quantity" />
              <input v-model.number="row.rate" type="number" min="0" :readonly="row.is_free"
                class="w-20 rounded-md border border-gray-200 px-2 py-2 text-sm text-right focus:border-gray-400 focus:outline-none"
                :class="row.is_free ? 'bg-gray-50 text-gray-400' : ''"
                title="Unit rate" />
              <div v-if="showFreeCol" class="flex w-16 shrink-0 justify-center">
                <span v-if="row.is_free && row._scheme" class="rounded bg-green-100 px-1.5 py-0.5 text-[10px] font-semibold uppercase text-green-700" title="Scheme free item">Free</span>
                <button v-else-if="auth.allowDiscretionaryFree" type="button" @click="toggleFree(row)"
                  class="inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase transition-colors"
                  :class="row.is_free ? 'bg-green-100 text-green-700' : 'border border-gray-200 text-gray-400 hover:border-green-300 hover:text-green-600'"
                  :title="row.is_free ? 'Unmark free' : 'Give this line free'">
                  <FeatherIcon v-if="row.is_free" name="check" class="h-3 w-3" /> Free
                </button>
              </div>
              <button @click="removeItem(i)" class="shrink-0 text-gray-300 hover:text-red-500 transition-colors" title="Remove">
                <FeatherIcon name="x" class="h-3.5 w-3.5" />
              </button>
            </div>
            <div v-if="row.is_free" class="pr-6 text-right text-xs text-green-600">
              {{ row.qty }} × free<span v-if="row._for"> · with {{ row._for }}</span> = <span class="font-medium">{{ formatUGX(0) }}</span>
            </div>
            <div v-else-if="row.item_code && row.qty && row.rate" class="pr-6 text-right text-xs text-gray-400">
              {{ row.qty }} × {{ formatUGX(row.rate) }} = <span class="font-medium text-gray-700">{{ formatUGX(row.qty * row.rate) }}</span>
            </div>
          </div>
          <div v-if="!orderForm.items.length" class="rounded-lg border border-dashed border-gray-200 py-4 text-center text-xs text-gray-400">
            No items yet — search above and tap a product, or use “+ Add Item”
          </div>
        </div>
        <div v-if="orderTotal > 0" class="mt-2 text-right text-sm font-semibold text-gray-800">
          Total: {{ formatUGX(orderTotal) }}
        </div>
      </div>
      <FormField v-model="orderForm.remarks" label="Remarks" type="textarea" />
    </div>
  </SlidePanel>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick } from 'vue'
import SlidePanel from '@/components/ui/SlidePanel.vue'
import FormField from '@/components/ui/FormField.vue'
import { getDoc, saveDoc, insertDoc, call } from '@/utils/frappe'
import { successToast, errorToast } from '@/utils/toast'
import { formatCurrency, currencyLabel } from '@/utils/currency'
import { auth } from '@/utils/auth'
import dayjs from 'dayjs'

const props = defineProps({
  customer: { type: String, required: true },
  customerName: { type: String, default: '' },
  items: { type: Array, default: () => [] },
})
const emit = defineEmits(['saved'])

const formatUGX = formatCurrency

const newOrderPanel = ref(false)
const savingOrder = ref(false)
const editingOrder = ref(null)
const editingConfirmed = ref(false)
const orderForm = reactive({ transaction_date: dayjs().format('YYYY-MM-DD'), delivery_date: '', items: [], remarks: '', order_type: 'Booking' })
const freeSchemes = ref([])
const dismissedSchemes = ref(new Set())
const itemCategory = ref('')
const itemSearch = ref('')
const productSearch = ref(null)

const orderTotal = computed(() => orderForm.items.reduce((s, i) => s + (i.qty || 0) * (i.rate || 0), 0))
const showFreeCol = computed(() => auth.allowDiscretionaryFree || (freeSchemes.value && freeSchemes.value.length > 0))
const allowedItems = computed(() => {
  const cos = auth.companies || []
  if (auth.isAdmin || auth.isManager || !cos.length) return props.items
  return props.items.filter(it => !it.company || cos.includes(it.company))
})
const categories = computed(() => {
  const s = new Set()
  for (const it of allowedItems.value) { if (it.category) s.add(it.category) }
  return [...s].sort()
})
const filteredItems = computed(() => {
  const q = itemSearch.value.trim().toLowerCase()
  return allowedItems.value.filter(it =>
    (!itemCategory.value || it.category === itemCategory.value) &&
    (!q || (it.label || '').toLowerCase().includes(q)))
})
function inFiltered(code) { return filteredItems.value.some(it => it.value === code) }

async function loadFreeSchemes() {
  try {
    const res = await call('sfa_core.field_sfa.api.free_carton.get_free_carton_schemes', { customer: props.customer })
    freeSchemes.value = res.message || []
  } catch (e) { freeSchemes.value = [] }
}
function paidQtyMap() {
  const m = {}
  for (const r of orderForm.items) {
    if (r.is_free || !r.item_code) continue
    m[r.item_code] = (m[r.item_code] || 0) + (Number(r.qty) || 0)
  }
  return m
}
function applyFreeSchemes() {
  const qmap = paidQtyMap()
  const desired = []
  for (const s of freeSchemes.value) {
    if (dismissedSchemes.value.has(s.name)) continue
    const bought = qmap[s.buy_item] || 0
    if (s.buy_qty > 0 && bought >= s.buy_qty) {
      const multiples = Math.floor(bought / s.buy_qty)
      const freeQty = multiples * (s.free_qty || 0)
      if (freeQty > 0) desired.push({ scheme: s.name, free_item: s.free_item, qty: freeQty, buy_item: s.buy_item })
    }
  }
  orderForm.items = orderForm.items.filter(r => !(r.is_free && r._scheme))
  for (const d of desired) {
    const it = props.items.find(i => i.value === d.free_item)
    const buyIt = props.items.find(i => i.value === d.buy_item)
    orderForm.items.push({ item_code: d.free_item, item_name: it ? it.label : d.free_item, qty: d.qty, rate: 0, is_free: true, _scheme: d.scheme, _for: buyIt ? buyIt.label : d.buy_item })
  }
}

watch(newOrderPanel, (open) => {
  if (open) { dismissedSchemes.value = new Set(); loadFreeSchemes() }
})

function addItem() { orderForm.items.push({ item_code: '', qty: 1, rate: 0, item_name: '' }) }
function addProduct(it) {
  orderForm.items.push({ item_code: it.value, item_name: it.label, qty: 1, rate: it.rate || 0, is_free: false })
  applyFreeSchemes()
  nextTick(() => { productSearch.value?.focus() })
}
function removeItem(i) {
  const r = orderForm.items[i]
  if (r && r.is_free && r._scheme) dismissedSchemes.value.add(r._scheme)
  orderForm.items.splice(i, 1)
}
function onItemChange(row) {
  const item = props.items.find(i => i.value === row.item_code)
  if (item) { row.item_name = item.label; if (!row.is_free) row.rate = item.rate || 0 }
  applyFreeSchemes()
}
function toggleFree(row) {
  row.is_free = !row.is_free
  if (row.is_free) { row.rate = 0; delete row._scheme; delete row._for }
  else { const it = props.items.find(i => i.value === row.item_code); row.rate = it ? (it.rate || 0) : 0 }
  applyFreeSchemes()
}

function openCreate() {
  editingOrder.value = null
  editingConfirmed.value = false
  orderForm.items = []
  orderForm.transaction_date = dayjs().format('YYYY-MM-DD')
  orderForm.delivery_date = ''
  orderForm.remarks = ''
  orderForm.order_type = 'Booking'
  newOrderPanel.value = true
}
async function openEdit(o) {
  try {
    const d = await getDoc('Sales Order', o.name)
    editingOrder.value = d.name
    editingConfirmed.value = d.docstatus === 1
    orderForm.transaction_date = d.transaction_date
    orderForm.delivery_date = d.delivery_date || ''
    orderForm.remarks = d.remarks || ''
    orderForm.order_type = d.custom_sfa_order_type || 'Booking'
    orderForm.items = (d.items || []).map(it => ({ docname: it.name, item_code: it.item_code, item_name: it.item_name, qty: it.qty, rate: it.is_free_item ? 0 : it.rate, is_free: !!it.is_free_item }))
    newOrderPanel.value = true
  } catch (e) { errorToast(e.message || 'Failed to load order') }
}

async function saveOrder() {
  if (!orderForm.items.some(i => i.item_code)) { errorToast('Add at least one item'); return }
  savingOrder.value = true
  try {
    if (editingConfirmed.value && editingOrder.value) {
      const _items = orderForm.items.filter(i => i.item_code && (Number(i.qty) || 0) > 0).map(i => {
        const row = { item_code: i.item_code, qty: Number(i.qty) || 0, rate: i.is_free ? 0 : (Number(i.rate) || 0), is_free_item: i.is_free ? 1 : 0 }
        if (i.docname) row.docname = i.docname
        return row
      })
      await call('sfa_core.field_sfa.api.order_actions.update_order_items', { name: editingOrder.value, items: JSON.stringify(_items) })
      const savedName = editingOrder.value
      newOrderPanel.value = false; editingOrder.value = null; editingConfirmed.value = false; orderForm.items = []
      successToast('Order updated')
      emit('saved', { name: savedName, reopen: true })
      return
    }
    const _agg = {}
    for (const i of orderForm.items) {
      if (!i.item_code) continue
      const free = i.is_free ? 1 : 0
      const key = i.item_code + '|' + free
      if (!_agg[key]) _agg[key] = { item_code: i.item_code, item_name: i.item_name, qty: 0, rate: free ? 0 : (Number(i.rate) || 0), is_free_item: free }
      _agg[key].qty += (Number(i.qty) || 0)
      if (!free && (Number(i.rate) || 0)) _agg[key].rate = Number(i.rate) || 0
    }
    const payloadItems = Object.values(_agg).filter(r => r.qty > 0).map(r => ({
      doctype: 'Sales Order Item', item_code: r.item_code, item_name: r.item_name,
      qty: r.qty, rate: r.rate, is_free_item: r.is_free_item,
      delivery_date: orderForm.delivery_date || orderForm.transaction_date,
    }))
    let name = editingOrder.value
    if (name) {
      await saveDoc({
        doctype: 'Sales Order', name,
        transaction_date: orderForm.transaction_date,
        delivery_date: orderForm.delivery_date || orderForm.transaction_date,
        remarks: orderForm.remarks,
        custom_sfa_order_type: orderForm.order_type,
        items: payloadItems,
      })
    } else {
      const created = await insertDoc({
        doctype: 'Sales Order', customer: props.customer, naming_series: 'SAL-ORD-.YYYY.-',
        transaction_date: orderForm.transaction_date,
        delivery_date: orderForm.delivery_date || orderForm.transaction_date,
        remarks: orderForm.remarks,
        custom_sfa_order_type: orderForm.order_type,
        ...(auth.salesPerson ? { custom_sfa_rep: auth.salesPerson } : {}),
        items: payloadItems,
      })
      name = created.name
    }
    let reopen = true
    if (orderForm.order_type === 'Van Sale') {
      await call('sfa_core.field_sfa.api.order_actions.confirm_order', { name })
      await call('sfa_core.field_sfa.api.order_actions.mark_delivered', { name })
      successToast('Sale recorded'); reopen = false
    } else {
      successToast(editingOrder.value ? 'Draft updated' : 'Draft saved')
    }
    const savedName = name
    newOrderPanel.value = false
    editingOrder.value = null
    orderForm.items = []
    emit('saved', { name: savedName, reopen: reopen && !!savedName })
  } catch (e) { errorToast(e.message || 'Failed') }
  finally { savingOrder.value = false }
}

defineExpose({ openCreate, openEdit })
</script>
