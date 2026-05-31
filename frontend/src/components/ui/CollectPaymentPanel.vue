<template>
  <SlidePanel v-model="paymentViewPanel" :title="viewPaymentDoc ? (viewPaymentDoc.custom_payment_mode === 'Cartons' ? 'Carton Payment' : formatUGX(viewPaymentDoc.amount)) : 'Payment'" save-label="" width="480px">
    <div v-if="viewPaymentDoc" class="space-y-4">
      <div class="flex items-center justify-between rounded-xl border border-gray-200 bg-gray-50 px-4 py-3">
        <div>
          <p class="text-xs text-gray-400">{{ formatDate(viewPaymentDoc.payment_date) }}</p>
          <p class="text-sm font-semibold text-gray-900">{{ viewPaymentDoc.custom_payment_mode === 'Cartons' ? 'Carton-based credit' : formatUGX(viewPaymentDoc.amount) }}</p>
        </div>
        <StatusBadge :status="viewPaymentDoc.status" />
      </div>
      <div class="space-y-1.5 px-1 text-sm">
        <div class="flex justify-between"><span class="text-gray-400">Type</span><span class="text-gray-700">{{ viewPaymentDoc.payment_type }}</span></div>
        <div v-if="viewPaymentDoc.sales_person" class="flex justify-between"><span class="text-gray-400">Sales Person</span><span class="text-gray-700">{{ viewPaymentDoc.sales_person }}</span></div>
        <div v-if="viewPaymentDoc.custom_sales_order" class="flex justify-between"><span class="text-gray-400">Against Order</span><span class="font-mono text-gray-700">{{ viewPaymentDoc.custom_sales_order }}</span></div>
        <div v-if="viewPaymentDoc.reference_no" class="flex justify-between"><span class="text-gray-400">Reference</span><span class="text-gray-700">{{ viewPaymentDoc.reference_no }}</span></div>
        <div v-if="viewPaymentDoc.notes" class="flex justify-between gap-4"><span class="text-gray-400">Notes</span><span class="text-right text-gray-700">{{ viewPaymentDoc.notes }}</span></div>
      </div>
      <div v-if="viewPaymentDoc.status === 'Draft'" class="flex flex-wrap gap-2 border-t border-gray-100 pt-4">
        <Btn variant="solid" size="sm" icon="check" :loading="savingView" @click="doSubmitPayment(viewPaymentDoc.name)">Submit</Btn>
        <Btn variant="subtle" size="sm" icon="edit-2" @click="openEditPayment(viewPaymentDoc)">Edit</Btn>
        <Btn variant="ghost" size="sm" icon="trash-2" @click="deletePaymentDraft(viewPaymentDoc.name)">Delete</Btn>
      </div>
    </div>
  </SlidePanel>

  <SlidePanel v-model="newPaymentPanel" :title="editingPayment ? 'Edit Payment' : 'Record Payment'" :saving="savingPayment" :save-label="paymentJustRecorded ? '' : (editingPayment ? 'Save' : 'Record Payment')" @save="createPayment">
    <div class="space-y-4">
      <div class="rounded-lg bg-gray-50 border border-gray-200 px-3 py-2.5 text-sm text-gray-700">
        <span class="text-xs text-gray-400 block mb-0.5">Customer</span>
        {{ customerName }}
      </div>

      <div v-if="paymentForm.sales_order" class="rounded-lg border border-blue-200 bg-blue-50 px-3 py-2.5 text-sm">
        <span class="text-xs text-blue-400 block mb-0.5">Against Order</span>
        <span class="font-mono text-blue-800">{{ paymentForm.sales_order }}</span>
      </div>

      <FormField v-model="paymentForm.sales_person" label="Sales Person" type="select" :options="salesPersons" required :error="paymentErrors.sales_person" />
      <FormField v-model="paymentForm.payment_date" label="Payment Date" type="date" required />

      <div v-if="!paymentForm.sales_order">
        <label class="mb-1.5 block text-xs font-medium text-gray-600">Payment Mode</label>
        <div class="flex rounded-lg border border-gray-200 overflow-hidden">
          <button
            class="flex-1 py-2 text-sm font-medium transition-colors flex items-center justify-center gap-1.5"
            :class="paymentForm.payment_mode === 'Cash' ? 'bg-gray-900 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'"
            @click="paymentForm.payment_mode = 'Cash'"
          >
            <FeatherIcon name="credit-card" class="h-3.5 w-3.5" /> Cash
          </button>
          <button
            class="flex-1 py-2 text-sm font-medium transition-colors flex items-center justify-center gap-1.5 border-l border-gray-200"
            :class="paymentForm.payment_mode === 'Cartons' ? 'bg-gray-900 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'"
            @click="paymentForm.payment_mode = 'Cartons'"
          >
            <FeatherIcon name="package" class="h-3.5 w-3.5" /> Cartons
          </button>
        </div>
        <p class="mt-1 text-[10px] text-gray-400">
          {{ paymentForm.payment_mode === 'Cartons' ? 'Record items and carton quantities — no pricing required' : 'Enter the cash amount collected' }}
        </p>
      </div>

      <template v-if="paymentForm.payment_mode === 'Cash'">
        <FormField v-model="paymentForm.payment_type" label="Payment Type" type="select"
          :options="['Cash','Cheque','Bank Transfer','Credit Note']" required :error="paymentErrors.payment_type" />
        <FormField v-model="paymentForm.amount" :label="`Amount (${currencyLabel()})`" type="number" required :error="paymentErrors.amount" />
        <FormField v-model="paymentForm.reference_no" label="Reference / Receipt No" />
      </template>

      <template v-else>
        <div>
          <div class="flex items-center justify-between mb-1.5">
            <label class="text-xs font-medium text-gray-600">Items <span class="text-red-500">*</span></label>
            <button class="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-800" @click="addCartonItem">
              <FeatherIcon name="plus" class="h-3 w-3" /> Add Item
            </button>
          </div>

          <div v-if="paymentForm.carton_items.length" class="mb-1.5 flex items-center gap-2 px-0.5">
            <span class="flex-1 text-[10px] font-medium uppercase tracking-wide text-gray-400">Item</span>
            <span class="w-20 text-center text-[10px] font-medium uppercase tracking-wide text-gray-400">Cartons</span>
            <span class="w-5" />
          </div>

          <div class="space-y-2">
            <div v-for="(row, i) in paymentForm.carton_items" :key="i" class="flex items-center gap-2">
              <select v-model="row.item_code" @change="onCartonItemChange(row)"
                class="flex-1 rounded-md border border-gray-200 bg-white px-2 py-2 text-sm focus:border-gray-400 focus:outline-none">
                <option value="">Select item…</option>
                <option v-for="it in items" :key="it.value" :value="it.value">{{ it.label }}</option>
              </select>
              <input v-model.number="row.cartons" type="number" min="0" placeholder="0"
                class="w-20 rounded-md border border-gray-200 px-2 py-2 text-sm text-center focus:border-gray-400 focus:outline-none" />
              <button @click="removeCartonItem(i)" class="shrink-0 text-gray-300 hover:text-red-500 transition-colors">
                <FeatherIcon name="x" class="h-3.5 w-3.5" />
              </button>
            </div>
            <div v-if="!paymentForm.carton_items.length" class="rounded-lg border border-dashed border-gray-200 py-4 text-center text-xs text-gray-400">
              No items added — click "+ Add Item" above
            </div>
          </div>

          <div v-if="paymentForm.carton_items.some(r => r.item_code && r.cartons > 0)"
            class="mt-3 rounded-lg bg-amber-50 border border-amber-100 px-3 py-2">
            <p class="text-xs font-medium text-amber-700">
              {{ paymentForm.carton_items.filter(r => r.item_code && r.cartons > 0).reduce((s,r) => s + r.cartons, 0) }} total cartons
            </p>
            <p class="text-[10px] text-amber-600 mt-0.5">No monetary value — carton-based credit</p>
          </div>
        </div>
        <FormField v-model="paymentForm.reference_no" label="Reference / Delivery Note No" />
      </template>

      <FormField v-model="paymentForm.notes" label="Notes" type="textarea" />

      <div v-if="paymentJustRecorded" class="rounded-lg border border-gray-200 bg-gray-50 px-3 py-2.5 space-y-2">
        <div class="flex items-center justify-between text-sm">
          <span class="text-gray-500">Saved as</span>
          <StatusBadge status="Draft" />
        </div>
        <button type="button" @click="createPayment('Submitted')" :disabled="savingPayment"
          class="w-full rounded-lg bg-gray-900 px-3 py-2 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50">
          Submit Payment
        </button>
        <p class="text-center text-xs text-gray-400">Submitting finalizes this payment and locks it</p>
      </div>
    </div>
  </SlidePanel>
</template>

<script setup>
import { ref, reactive } from 'vue'
import SlidePanel from '@/components/ui/SlidePanel.vue'
import FormField from '@/components/ui/FormField.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import Btn from '@/components/ui/Btn.vue'
import { getDoc, saveDoc, insertDoc, deleteDoc } from '@/utils/frappe'
import { successToast, errorToast } from '@/utils/toast'
import { formatCurrency, currencyLabel } from '@/utils/currency'
import { auth } from '@/utils/auth'
import * as orderPay from '@/utils/orders'
import dayjs from 'dayjs'

const props = defineProps({
  customer: { type: String, required: true },
  customerName: { type: String, default: '' },
  rep: { type: String, default: '' },
  salesPersons: { type: Array, default: () => [] },
  items: { type: Array, default: () => [] },
  payments: { type: Array, default: () => [] },
})
const emit = defineEmits(['changed'])

const formatUGX = formatCurrency
const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '\u2014'

const newPaymentPanel = ref(false)
const paymentViewPanel = ref(false)
const paymentJustRecorded = ref(false)
const viewPaymentDoc = ref(null)
const savingPayment = ref(false)
const savingView = ref(false)
const editingPayment = ref(null)
const paymentErrors = reactive({})
const paymentForm = reactive({
  sales_person: auth.salesPerson || '', payment_date: dayjs().format('YYYY-MM-DD'),
  payment_mode: 'Cash', payment_type: '', amount: '',
  reference_no: '', notes: '', status: 'Draft', sales_order: '',
  carton_items: [],
})

function addCartonItem() {
  paymentForm.carton_items.push({ item_code: '', item_name: '', cartons: 1, rate_per_carton: 0 })
}
function removeCartonItem(i) { paymentForm.carton_items.splice(i, 1) }
function onCartonItemChange(row) {
  const item = props.items.find(i => i.value === row.item_code)
  if (item) row.item_name = item.label
}

function openNewPayment() {
  editingPayment.value = null
  paymentJustRecorded.value = false
  Object.keys(paymentErrors).forEach(k => delete paymentErrors[k])
  paymentForm.sales_person = auth.salesPerson || props.rep || ''
  paymentForm.payment_date = dayjs().format('YYYY-MM-DD')
  paymentForm.payment_mode = 'Cash'
  paymentForm.payment_type = ''
  paymentForm.amount = ''
  paymentForm.reference_no = ''
  paymentForm.notes = ''
  paymentForm.status = 'Draft'
  paymentForm.sales_order = ''
  paymentForm.carton_items = []
  newPaymentPanel.value = true
}

async function openPaymentView(p) {
  try {
    viewPaymentDoc.value = await getDoc('SFA Payment', p.name)
    paymentViewPanel.value = true
  } catch (e) { errorToast(e.message || 'Failed to load payment') }
}

async function doSubmitPayment(name) {
  savingView.value = true
  try {
    await saveDoc({ ...viewPaymentDoc.value, status: 'Submitted' })
    successToast('Payment submitted')
    paymentViewPanel.value = false
    emit('changed')
  } catch (e) { errorToast(e.message || 'Failed to submit') } finally { savingView.value = false }
}

async function deletePaymentDraft(name) {
  if (!confirm('Delete this draft payment?')) return
  savingView.value = true
  try { await deleteDoc('SFA Payment', name); successToast('Payment deleted'); paymentViewPanel.value = false; emit('changed') }
  catch (e) { errorToast(e.message || 'Failed to delete') } finally { savingView.value = false }
}

function openCollectPayment(o) {
  editingPayment.value = null
  paymentJustRecorded.value = false
  Object.keys(paymentErrors).forEach(k => delete paymentErrors[k])
  paymentForm.sales_person = auth.salesPerson || props.rep || ''
  paymentForm.payment_date = dayjs().format('YYYY-MM-DD')
  paymentForm.reference_no = ''
  paymentForm.notes = ''
  paymentForm.status = 'Draft'
  paymentForm.sales_order = o.name
  if (orderPay.orderIsCarton(o)) {
    paymentForm.payment_mode = 'Cartons'
    paymentForm.payment_type = 'Cartons'
    paymentForm.amount = 0
    paymentForm.carton_items = (o.items || [])
      .filter(it => (Number(it.qty) || 0) > 0)
      .map(it => ({ item_code: it.item_code, item_name: it.item_name, cartons: Number(it.qty) || 0 }))
  } else {
    paymentForm.payment_mode = 'Cash'
    paymentForm.payment_type = 'Cash'
    paymentForm.amount = orderPay.orderOutstanding(o, props.payments)
    paymentForm.carton_items = []
  }
  newPaymentPanel.value = true
}

async function openEditPayment(p) {
  try {
    const d = await getDoc('SFA Payment', p.name)
    editingPayment.value = d.name
    paymentJustRecorded.value = false
    Object.keys(paymentErrors).forEach(k => delete paymentErrors[k])
    paymentForm.sales_person = d.sales_person || ''
    paymentForm.payment_date = d.payment_date || dayjs().format('YYYY-MM-DD')
    paymentForm.payment_mode = d.custom_payment_mode === 'Cartons' ? 'Cartons' : 'Cash'
    paymentForm.payment_type = d.payment_type || ''
    paymentForm.amount = d.amount || ''
    paymentForm.reference_no = d.reference_no || ''
    paymentForm.notes = d.notes || ''
    paymentForm.status = d.status || 'Draft'
    paymentForm.carton_items = (d.custom_carton_items || []).map(r => ({
      item_code: r.item_code, item_name: r.item_name, cartons: r.cartons, rate_per_carton: 0,
    }))
    paymentViewPanel.value = false
    newPaymentPanel.value = true
  } catch (e) { errorToast(e.message || 'Failed to load payment') }
}

async function createPayment(overrideStatus = null) {
  Object.keys(paymentErrors).forEach(k => delete paymentErrors[k])
  if (!paymentForm.sales_person) { paymentErrors.sales_person = 'Required'; return }

  if (paymentForm.payment_mode === 'Cash') {
    if (!paymentForm.payment_type) { paymentErrors.payment_type = 'Required'; return }
    if (!paymentForm.amount || Number(paymentForm.amount) <= 0) { paymentErrors.amount = 'Enter a valid amount'; return }
  } else {
    const validItems = paymentForm.carton_items.filter(r => r.item_code && r.cartons > 0)
    if (!validItems.length) { errorToast('Add at least one item with cartons'); return }
  }

  savingPayment.value = true
  try {
    const isCarton = paymentForm.payment_mode === 'Cartons'
    const finalAmount = isCarton ? 0 : Number(paymentForm.amount)
    const cartonItems = isCarton
      ? paymentForm.carton_items.filter(r => r.item_code && r.cartons > 0).map(r => ({
          doctype: 'SFA Payment Carton Item',
          item_code: r.item_code, item_name: r.item_name,
          cartons: r.cartons,
        }))
      : []

    const payload = {
      doctype: 'SFA Payment', customer: props.customer,
      sales_person: paymentForm.sales_person,
      payment_date: paymentForm.payment_date,
      payment_type: isCarton ? 'Cartons' : paymentForm.payment_type,
      amount: isCarton ? 0 : finalAmount,
      custom_payment_mode: paymentForm.payment_mode,
      custom_carton_total: isCarton ? cartonItems.reduce((s, r) => s + (Number(r.cartons) || 0), 0) : 0,
      custom_carton_items: cartonItems,
      reference_no: paymentForm.reference_no,
      notes: paymentForm.notes,
      status: overrideStatus || paymentForm.status,
      custom_sales_order: paymentForm.sales_order || null,
    }
    const wasNew = !editingPayment.value
    if (editingPayment.value) {
      await saveDoc({ name: editingPayment.value, ...payload })
    } else {
      const created = await insertDoc(payload)
      editingPayment.value = (created && created.name) || null
    }

    if (overrideStatus === 'Submitted') {
      successToast('Payment submitted')
      newPaymentPanel.value = false
      editingPayment.value = null
      paymentJustRecorded.value = false
      paymentForm.sales_order = ''
      paymentForm.carton_items = []
      paymentForm.payment_mode = 'Cash'
    } else if (wasNew) {
      paymentForm.status = 'Draft'
      paymentJustRecorded.value = true
      successToast('Recorded as draft')
    } else {
      successToast('Payment updated')
      newPaymentPanel.value = false
      editingPayment.value = null
      paymentJustRecorded.value = false
      paymentForm.sales_order = ''
      paymentForm.carton_items = []
      paymentForm.payment_mode = 'Cash'
    }
    emit('changed')
  } catch (e) { errorToast(e.message || 'Failed') }
  finally { savingPayment.value = false }
}

defineExpose({ openNew: openNewPayment, openCollect: openCollectPayment, openView: openPaymentView })
</script>
