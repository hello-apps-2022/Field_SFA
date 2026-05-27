/**
 * Composable: useLinkedData
 * Fetches and caches common linked field options used across slide-in forms.
 */
import { ref } from 'vue'

const cache = {}

async function fetchList(doctype, fields = ['name'], filters = {}, limit = 500) {
  const key = doctype
  if (cache[key]) return cache[key]
  try {
    const res = await frappe.call({
      method: 'frappe.client.get_list',
      args: { doctype, fields, filters, limit, order_by: fields[0] + ' asc' }
    })
    cache[key] = res.message || []
    return cache[key]
  } catch (e) {
    console.error('useLinkedData error:', e)
    return []
  }
}

export function useLinkedData() {
  const customers = ref([])
  const territories = ref([])
  const salesPersons = ref([])
  const customerGroups = ref([])
  const beatPlans = ref([])
  const items = ref([])
  const visitPurposes = ref([])
  const paymentTypes = ref([])

  async function loadCustomers() {
    const data = await fetchList('Customer', ['name', 'customer_name', 'territory'])
    customers.value = data.map(c => ({ value: c.name, label: c.customer_name || c.name }))
  }

  async function loadTerritories() {
    const data = await fetchList('Territory', ['name'])
    territories.value = data.map(t => t.name)
  }

  async function loadSalesPersons() {
    const data = await fetchList('Sales Person', ['name'])
    salesPersons.value = data.map(s => s.name)
  }

  async function loadCustomerGroups() {
    const data = await fetchList('Customer Group', ['name'])
    customerGroups.value = data.map(g => g.name)
  }

  async function loadBeatPlans() {
    const data = await fetchList('SFA Beat Plan', ['name', 'plan_name'])
    beatPlans.value = data.map(b => ({ value: b.name, label: b.plan_name || b.name }))
  }

  async function loadItems() {
    const data = await fetchList('Item', ['name', 'item_name', 'standard_rate'], { is_sales_item: 1 })
    items.value = data.map(i => ({ value: i.name, label: i.item_name || i.name, rate: i.standard_rate }))
  }

  async function loadVisitPurposes() {
    const data = await fetchList('SFA Visit Purpose', ['name'])
    visitPurposes.value = data.map(v => v.name)
  }

  async function loadPaymentTypes() {
    const data = await fetchList('SFA Payment Type', ['name'])
    paymentTypes.value = data.map(p => p.name)
  }

  return {
    customers, territories, salesPersons, customerGroups,
    beatPlans, items, visitPurposes, paymentTypes,
    loadCustomers, loadTerritories, loadSalesPersons, loadCustomerGroups,
    loadBeatPlans, loadItems, loadVisitPurposes, loadPaymentTypes,
  }
}
