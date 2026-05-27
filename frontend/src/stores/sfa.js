import { defineStore } from 'pinia'
import { ref } from 'vue'
import { createResource, createListResource } from 'frappe-ui'

export const useSFAStore = defineStore('sfa', () => {
  const territories = ref([])
  const salesPersons = ref([])

  // ── Visits ──────────────────────────────────────────────────────────────
  const visitsList = createListResource({
    doctype: 'SFA Visit',
    fields: [
      'name', 'customer', 'sales_person', 'visit_date',
      'status', 'check_in_time', 'check_out_time',
      'check_in_latitude', 'check_in_longitude', 'beat_plan',
    ],
    orderBy: 'visit_date desc',
    pageLength: 50,
    auto: false,
  })

  // ── Beat Plans ───────────────────────────────────────────────────────────
  const beatPlansList = createListResource({
    doctype: 'SFA Beat Plan',
    fields: ['name', 'plan_name', 'territory', 'sales_person', 'status', 'date'],
    orderBy: 'date desc',
    pageLength: 50,
    auto: false,
  })

  // ── Form Templates ───────────────────────────────────────────────────────
  const formTemplatesList = createListResource({
    doctype: 'SFA Form Template',
    fields: [
      'name', 'template_name', 'category', 'trigger_point',
      'is_active', 'is_mandatory', 'version', 'survey_json', 'modified',
    ],
    orderBy: 'modified desc',
    pageLength: 100,
    auto: false,
  })

  // ── Form Responses ───────────────────────────────────────────────────────
  const formResponsesList = createListResource({
    doctype: 'SFA Form Response',
    fields: [
      'name', 'form_template', 'visit', 'customer',
      'sales_person', 'response_date', 'sync_status',
    ],
    orderBy: 'response_date desc',
    pageLength: 50,
    auto: false,
  })

  // ── Orders ───────────────────────────────────────────────────────────────
  const ordersList = createListResource({
    doctype: 'Sales Order',
    fields: [
      'name', 'customer', 'transaction_date', 'status',
      'total_qty', 'grand_total', 'owner',
    ],
    orderBy: 'transaction_date desc',
    pageLength: 50,
    auto: false,
  })

  // ── Dashboard metrics ────────────────────────────────────────────────────
  const dashboardData = createResource({
    url: 'sfa_core.api.dashboard.get_dashboard_data',
    auto: false,
  })

  const leaderboard = createResource({
    url: 'sfa_core.api.dashboard.get_leaderboard',
    auto: false,
  })

  return {
    territories,
    salesPersons,
    visitsList,
    beatPlansList,
    formTemplatesList,
    formResponsesList,
    ordersList,
    dashboardData,
    leaderboard,
  }
})
