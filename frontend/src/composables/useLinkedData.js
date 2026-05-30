import { ref } from 'vue'
import { getList, call } from '@/utils/frappe'
import { auth } from '@/utils/auth'

const cache = {}

async function cached(key, fetcher) {
  if (cache[key]) return cache[key]
  cache[key] = await fetcher()
  return cache[key]
}

export function useLinkedData() {
  const customers = ref([])
  const territories = ref([])
  const salesPersons = ref([])
  const customerGroups = ref([])
  const beatPlans = ref([])
  const reportingChain = ref([])
  const items = ref([])
  const paymentTypes = ref([])
  const visitPurposes = ref([])

  async function loadCustomers() {
    const data = await cached('customers', () => getList('Customer', { fields: ['name', 'customer_name'], limit: 500 }))
    customers.value = data.map(c => ({ value: c.name, label: c.customer_name || c.name }))
  }

  async function loadTerritories() {
    const data = await cached('territories', () => getList('Territory', { fields: ['name'], limit: 200 }))
    territories.value = data.map(t => t.name)
  }

  async function loadSalesPersons() {
    const data = await cached('sales_persons', () => getList('Sales Person', { fields: ['name'], filters: { is_group: 0 }, limit: 200 }))
    salesPersons.value = data.map(s => s.name)
  }

  async function loadCustomerGroups() {
    customerGroups.value = await cached('customer_groups', async () => {
      try { return (await call('sfa_core.api.list.get_customer_groups')).message || [] }
      catch (e) { return [] }
    })
  }

  async function loadBeatPlans() {
    const filters = {}
    if (auth.isRep || auth.isHelper) filters.sales_person = auth.salesPerson
    else if (auth.isSupervisor && auth.territory) filters.territory = auth.territory
    const data = await cached('beat_plans', () => getList('SFA Beat Plan', { fields: ['name', 'plan_name'], filters, limit: 200 }))
    beatPlans.value = data.map(b => ({ value: b.name, label: b.plan_name || b.name }))
  }

  async function loadItems() {
    const data = await cached('items', () => getList('Item', { fields: ['name', 'item_name', 'standard_rate', 'custom_sfa_company', 'item_group'], filters: { is_sales_item: 1, disabled: 0 }, limit: 500 }))
    items.value = data.map(i => ({ value: i.name, label: i.item_name || i.name, rate: i.standard_rate || 0, company: i.custom_sfa_company || null, category: i.item_group || null }))
  }

  async function loadPaymentTypes() {
    const data = await cached('payment_types', () => getList('SFA Payment Type', { fields: ['name'], limit: 50 }))
    paymentTypes.value = data.map(p => p.name)
  }

  async function loadVisitPurposes() {
    const data = await cached('visit_purposes', () => getList('SFA Visit Purpose', { fields: ['name'], limit: 50 }))
    visitPurposes.value = data.map(v => v.name)
  }

  async function loadReportingChain(salesPerson) {
    const args = salesPerson ? { sales_person: salesPerson } : {}
    const res = await call('sfa_core.api.auth.get_reporting_chain', args)
    reportingChain.value = res.message || []
  }

  return {
    customers, territories, salesPersons, customerGroups, reportingChain,
    beatPlans, items, paymentTypes, visitPurposes,
    loadCustomers, loadTerritories, loadSalesPersons, loadCustomerGroups,
    loadBeatPlans, loadItems, loadPaymentTypes, loadVisitPurposes, loadReportingChain,
  }
}
