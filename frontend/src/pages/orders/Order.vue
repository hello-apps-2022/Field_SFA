<template>
  <div class="flex h-full flex-col overflow-hidden">
    <div class="flex h-[52px] shrink-0 items-center gap-3 border-b border-gray-100 bg-white px-5">
      <router-link to="/customers" class="text-sm text-gray-400 hover:text-gray-700">Customers</router-link>
      <FeatherIcon name="chevron-right" class="h-3.5 w-3.5 text-gray-300" />
      <router-link v-if="order" :to="`/customers/${order.customer}`" class="truncate text-sm text-gray-400 hover:text-gray-700">{{ order.customer_name || order.customer }}</router-link>
      <FeatherIcon v-if="order" name="chevron-right" class="h-3.5 w-3.5 text-gray-300" />
      <span class="truncate text-sm font-semibold text-gray-900">{{ name }}</span>
      <div class="flex-1" />
      <span v-if="order" class="rounded px-2 py-0.5 text-xs font-medium" :class="orderStateColor(state)">{{ state }}</span>
    </div>

    <div class="flex-1 overflow-y-auto px-5 py-4">
      <div v-if="loading" class="py-20 text-center text-sm text-gray-400">Loading…</div>
      <div v-else-if="!order" class="py-20 text-center text-sm text-gray-400">Order not found</div>
      <div v-else class="mx-auto max-w-2xl space-y-4">

        <div class="rounded-xl border border-gray-200 bg-white px-4 py-3">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs text-gray-400">{{ formatDate(order.transaction_date) }}</p>
              <p class="text-lg font-semibold text-gray-900">{{ formatUGX(order.grand_total) }}</p>
            </div>
            <span class="rounded px-2 py-0.5 text-xs font-medium" :class="orderStateColor(state)">{{ state }}</span>
          </div>
          <div class="mt-3 grid grid-cols-2 gap-3 border-t border-gray-100 pt-3 text-sm sm:grid-cols-4">
            <div>
              <p class="text-xs text-gray-400">Type</p>
              <p class="text-gray-700">{{ order.custom_sfa_order_type || 'Booking' }}</p>
            </div>
            <div v-if="order.delivery_date">
              <p class="text-xs text-gray-400">Delivery</p>
              <p class="text-gray-700">{{ formatDate(order.delivery_date) }}</p>
            </div>
            <div v-if="order.custom_sfa_rep || order.owner">
              <p class="text-xs text-gray-400">Rep</p>
              <p class="truncate text-gray-700">{{ order.custom_sfa_rep || order.owner }}</p>
            </div>
            <div>
              <p class="text-xs text-gray-400">Total cartons</p>
              <p class="text-gray-700">{{ order.total_qty }}</p>
            </div>
          </div>
          <p v-if="state === 'Delivered' && order.custom_sfa_delivered_on" class="mt-2 text-xs text-green-600">
            Delivered {{ formatDate(order.custom_sfa_delivered_on) }}
          </p>
        </div>

        <div class="rounded-xl border border-gray-200 bg-white px-4 py-3">
          <p class="mb-2 text-xs font-medium text-gray-600">Items</p>
          <div class="divide-y divide-gray-50 rounded-lg border border-gray-100">
            <div v-for="(it, idx) in (order.items || [])" :key="idx" class="flex items-center justify-between px-3 py-2.5 text-sm">
              <div class="min-w-0">
                <p class="truncate text-gray-800">
                  {{ it.item_name || it.item_code }}
                  <span v-if="it.is_free_item" class="ml-1 rounded bg-green-100 px-1 text-[9px] font-semibold uppercase text-green-700">Free</span>
                </p>
                <p class="text-[11px] text-gray-400">{{ it.qty }} × {{ it.is_free_item ? 'free' : formatUGX(it.rate) }}</p>
              </div>
              <span class="text-sm text-gray-700">{{ formatUGX(it.amount) }}</span>
            </div>
            <div v-if="!(order.items || []).length" class="px-3 py-6 text-center text-xs text-gray-400">No items</div>
          </div>
          <div v-if="order.remarks" class="mt-3 rounded-lg bg-gray-50 px-3 py-2.5 text-sm text-gray-600">
            <span class="mb-0.5 block text-xs text-gray-400">Remarks</span>{{ order.remarks }}
          </div>
        </div>

        <div v-if="state === 'Draft' || state === 'Confirmed'" class="flex flex-wrap gap-2">
          <template v-if="state === 'Draft'">
            <Btn variant="solid" size="sm" icon="check" :loading="savingAction" @click="doConfirm">Confirm</Btn>
            <Btn variant="ghost" size="sm" icon="trash-2" @click="doDelete">Delete</Btn>
          </template>
          <template v-else>
            <Btn variant="solid" size="sm" icon="truck" :loading="savingAction" @click="doDeliver">Mark Delivered</Btn>
            <Btn variant="ghost" size="sm" icon="x-circle" @click="doCancel">Cancel Order</Btn>
          </template>
        </div>

        <div class="rounded-xl border border-gray-200 bg-white px-4 py-3">
          <div class="mb-2 flex items-center justify-between">
            <p class="text-sm font-medium text-gray-700">Payments on this order</p>
            <span class="text-xs font-medium" :class="payColor">{{ payBadge }}</span>
          </div>
          <div class="divide-y divide-gray-50">
            <div v-for="p in payments" :key="p.name" @click="payPanel?.openView(p)"
              class="-mx-1 flex cursor-pointer items-center justify-between rounded px-1 py-2.5 hover:bg-gray-50">
              <div>
                <p class="text-sm text-gray-800">{{ p.custom_payment_mode === 'Cartons' ? 'Cartons' : p.payment_type }}</p>
                <p class="text-[11px] text-gray-400">{{ formatDate(p.payment_date) }}<span v-if="p.sales_person"> · {{ p.sales_person }}</span></p>
              </div>
              <div class="flex items-center gap-2.5">
                <span class="text-sm" :class="isCollected(p) ? 'text-gray-700' : 'text-gray-400'">
                  {{ p.custom_payment_mode === 'Cartons' ? ((p.custom_carton_total || 0) + ' ctns') : formatUGX(p.amount) }}
                </span>
                <StatusBadge :status="p.status" />
              </div>
            </div>
            <div v-if="!payments.length" class="py-5 text-center text-xs text-gray-400">No payments recorded against this order</div>
          </div>
          <div class="mt-2 flex items-center justify-between border-t border-gray-100 pt-3">
            <span class="text-xs text-gray-500">{{ payLabel }}</span>
            <Btn v-if="needsCollection" variant="solid" size="sm" icon="dollar-sign" @click="payPanel?.openCollect(order)">Collect Payment</Btn>
          </div>
        </div>

      </div>
    </div>

    <CollectPaymentPanel
      v-if="order"
      ref="payPanel"
      :customer="order.customer"
      :customer-name="order.customer_name"
      :rep="order.custom_sfa_rep"
      :sales-persons="salesPersons"
      :items="items"
      :payments="payments"
      @changed="load"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDoc, getList, deleteDoc, call } from '@/utils/frappe'
import { successToast, errorToast } from '@/utils/toast'
import { formatCurrency } from '@/utils/currency'
import * as orderPay from '@/utils/orders'
import { useLinkedData } from '@/composables/useLinkedData'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import Btn from '@/components/ui/Btn.vue'
import CollectPaymentPanel from '@/components/ui/CollectPaymentPanel.vue'
import dayjs from 'dayjs'

const props = defineProps({ name: String })
const router = useRouter()
const { salesPersons, items, loadSalesPersons, loadItems } = useLinkedData()

const order = ref(null)
const payments = ref([])
const loading = ref(true)
const savingAction = ref(false)
const payPanel = ref(null)

const formatUGX = formatCurrency
const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '\u2014'

function orderState(o) {
  if (o.docstatus === 2) return 'Cancelled'
  if (o.docstatus === 0) return 'Draft'
  if (o.custom_sfa_delivery_status === 'Delivered') return 'Delivered'
  return 'Confirmed'
}
function orderStateColor(s) {
  return ({ Draft: 'bg-yellow-50 text-yellow-700', Confirmed: 'bg-indigo-50 text-indigo-700', Delivered: 'bg-green-50 text-green-700', Cancelled: 'bg-red-50 text-red-600' })[s] || 'bg-gray-100 text-gray-600'
}
const state = computed(() => order.value ? orderState(order.value) : '')
const payColor = computed(() => order.value ? orderPay.orderPayColor(order.value, payments.value) : '')
const payBadge = computed(() => order.value ? orderPay.orderPayBadge(order.value, payments.value, formatUGX) : '')
const payLabel = computed(() => order.value ? orderPay.orderPayLabel(order.value, payments.value, formatUGX) : '')
const needsCollection = computed(() => order.value ? orderPay.orderNeedsCollection(order.value, payments.value) : false)
const isCollected = (p) => ['Submitted', 'Reconciled'].includes(p.status)

async function load() {
  loading.value = true
  try {
    const [o, pays] = await Promise.all([
      getDoc('Sales Order', props.name),
      getList('SFA Payment', {
        fields: ['name', 'payment_date', 'payment_type', 'amount', 'status', 'reference_no', 'sales_person', 'custom_sales_order', 'custom_carton_total', 'custom_payment_mode'],
        filters: { custom_sales_order: props.name },
        orderBy: 'payment_date desc, creation desc', limit: 50,
      }),
    ])
    order.value = o
    payments.value = pays
  } catch (e) { errorToast(e.message || 'Failed to load order') }
  finally { loading.value = false }
}

async function doConfirm() {
  savingAction.value = true
  try { await call('sfa_core.field_sfa.api.order_actions.confirm_order', { name: props.name }); successToast('Order confirmed'); await load() }
  catch (e) { errorToast(e.message || 'Failed to confirm') } finally { savingAction.value = false }
}
async function doDeliver() {
  savingAction.value = true
  try { await call('sfa_core.field_sfa.api.order_actions.mark_delivered', { name: props.name }); successToast('Marked delivered'); await load() }
  catch (e) { errorToast(e.message || 'Failed') } finally { savingAction.value = false }
}
async function doCancel() {
  if (!confirm('Cancel this order? This cannot be undone.')) return
  savingAction.value = true
  try { await call('sfa_core.field_sfa.api.order_actions.cancel_order', { name: props.name }); successToast('Order cancelled'); await load() }
  catch (e) { errorToast(e.message || 'Failed to cancel') } finally { savingAction.value = false }
}
async function doDelete() {
  if (!confirm('Delete this draft?')) return
  savingAction.value = true
  try {
    await deleteDoc('Sales Order', props.name)
    successToast('Draft deleted')
    if (order.value) router.push(`/customers/${order.value.customer}`)
  } catch (e) { errorToast(e.message || 'Failed to delete') } finally { savingAction.value = false }
}

onMounted(() => { load(); loadSalesPersons(); loadItems() })
</script>
