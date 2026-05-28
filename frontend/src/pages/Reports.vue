<template>
  <div class="flex h-full flex-col">
    <PageHeader title="Reports" />

    <div class="flex-1 overflow-auto p-5">
      <!-- Report picker grid -->
      <div v-if="!activeReport" class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <button v-for="r in reports" :key="r.name" @click="openReport(r)"
          class="group flex items-start gap-4 rounded-xl border border-gray-200 bg-white p-4 text-left shadow-sm transition-all hover:border-gray-300 hover:shadow-md">
          <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-500">
            <FeatherIcon :name="r.icon" class="h-4 w-4 text-white" />
          </div>
          <div class="min-w-0 flex-1">
            <p class="text-sm font-semibold text-gray-900 group-hover:text-blue-600">{{ r.label }}</p>
            <p class="mt-0.5 text-xs text-gray-400">{{ r.desc }}</p>
          </div>
        </button>
      </div>

      <!-- Report viewer -->
      <div v-else>
        <div class="mb-4 flex items-center gap-3">
          <button @click="closeReport" class="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-800">
            <FeatherIcon name="arrow-left" class="h-4 w-4" /> All reports
          </button>
          <h2 class="text-base font-semibold text-gray-900">{{ activeReport.label }}</h2>
        </div>

        <!-- Filters -->
        <div class="mb-4 rounded-xl border border-gray-200 bg-white p-4">
          <div class="flex flex-wrap items-end gap-3">
            <DateRangeFilter v-if="needs('from_date') || needs('to_date')"
              v-model:from="dateFrom" v-model:to="dateTo" default-preset="this_month" />
            <FormField v-if="needs('territory') && auth.isAdmin" label="Territory" type="select" v-model="filters.territory" :options="territoryOpts" placeholder="All territories" class="w-44" />
            <FormField v-if="needs('sales_person') && !auth.isRep" label="Sales Person" type="select" v-model="filters.sales_person" :options="repOpts" placeholder="All reps" class="w-44" />
            <FormField v-if="needs('form_template')" label="Form Template" type="select" v-model="filters.form_template" :options="formTemplateOpts" :placeholder="formTemplateOpts.length ? 'Select template…' : 'No templates yet'" class="w-48" />
            <Btn @click="loadData" :disabled="loading || !!dateError">{{ loading ? 'Running…' : 'Run' }}</Btn>

            <div v-if="canExport" class="ml-auto flex gap-2">
              <Btn variant="ghost" @click="doExport('Excel')"><FeatherIcon name="download" class="mr-1 h-3.5 w-3.5" />Excel</Btn>
              <Btn variant="ghost" @click="doExport('CSV')"><FeatherIcon name="download" class="mr-1 h-3.5 w-3.5" />CSV</Btn>
            </div>
          </div>
          <p v-if="dateError" class="mt-2 text-xs text-red-500">{{ dateError }}</p>
        </div>

        <!-- Notice (e.g. report needs a filter selected) -->
        <div v-if="notice" class="mb-4 flex items-center gap-2 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          <FeatherIcon name="help-circle" class="h-4 w-4 shrink-0" />
          {{ notice }}
        </div>

        <!-- Chart -->
        <ReportChart v-if="chart && rows.length" class="mb-4"
          :title="activeReport.label" :type="chart.type" :rows="rows" :x-field="chart.x" :y-field="chart.y" />

        <!-- Table (hidden while a blocking notice asks for a required filter) -->
        <div v-if="!notice" class="overflow-auto rounded-xl border border-gray-200 bg-white">
          <table class="min-w-full text-sm">
            <thead class="border-b border-gray-200 bg-gray-50">
              <tr>
                <th v-for="c in columns" :key="c.fieldname" class="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wider text-gray-500 whitespace-nowrap">
                  {{ c.label }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, i) in rows" :key="i" class="border-b border-gray-100 hover:bg-gray-50">
                <td v-for="c in columns" :key="c.fieldname" class="px-3 py-2 whitespace-nowrap" :class="isNumeric(c) ? 'text-right tabular-nums' : 'text-gray-700'">
                  {{ fmtCell(row[c.fieldname], c) }}
                </td>
              </tr>
              <tr v-if="!loading && !rows.length">
                <td :colspan="columns.length || 1" class="px-3 py-8 text-center text-sm text-gray-400">No data for the selected filters.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import FormField from '@/components/ui/FormField.vue'
import DateRangeFilter from '@/components/ui/DateRangeFilter.vue'
import Btn from '@/components/ui/Btn.vue'
import ReportChart from '@/components/ui/ReportChart.vue'
import { call, getCsrfToken } from '@/utils/frappe'
import { auth } from '@/utils/auth'
import { useLinkedData } from '@/composables/useLinkedData'
import { useDateRange } from '@/composables/useDateRange'
import { errorToast } from '@/utils/toast'
import { formatCurrency } from '@/utils/currency'

const reports = ref([])
const canExport = ref(false)
const activeReport = ref(null)
const filters = reactive({})
const columns = ref([])
const rows = ref([])
const chart = ref(null)
const loading = ref(false)
const notice = ref('')

const territoryOpts = ref([])
const repOpts = ref([])
const formTemplateOpts = ref([])
const linked = useLinkedData()
const { dateFrom, dateTo, dateError, setFrom, setTo, validateRange, reset: resetDates } = useDateRange(30)

onMounted(async () => {
  try {
    const res = await call('sfa_core.api.reports.get_reports_list')
    const msg = res.message || {}
    reports.value = msg.reports || []
    canExport.value = !!msg.can_export
  } catch (e) {
    errorToast('Could not load reports')
  }
})

function needs(f) {
  return activeReport.value?.filters?.includes(f)
}

async function openReport(r) {
  activeReport.value = r
  Object.keys(filters).forEach((k) => delete filters[k])
  resetDates(30)

  if (r.filters.includes('territory') && !territoryOpts.value.length) {
    await linked.loadTerritories()
    territoryOpts.value = linked.territories.value
  }
  if (r.filters.includes('sales_person') && !repOpts.value.length) {
    await linked.loadSalesPersons()
    repOpts.value = linked.salesPersons.value
  }
  if (r.filters.includes('form_template') && !formTemplateOpts.value.length) {
    try {
      const fts = await call('frappe.client.get_list', {
        doctype: 'SFA Form Template', fields: ['name'], limit_page_length: 200,
      })
      formTemplateOpts.value = ((fts.message) || []).map((f) => f.name)
    } catch (e) { /* ignore */ }
  }
  // Reports that can't run until a specific filter is chosen — don't auto-run
  // them (avoids a pointless failed request); show a prompt instead.
  const REQUIRED = {
    response_by_question: { field: 'form_template', msg: 'Please select a Form Template to analyse responses by question.' },
    option_distribution: { field: 'form_template', msg: 'Please select a Form Template and Question.' },
  }
  const req = REQUIRED[r.name]
  if (req && !filters[req.field]) {
    notice.value = req.msg
    columns.value = []
    rows.value = []
    chart.value = null
    return
  }

  await loadData()
}

function closeReport() {
  activeReport.value = null
  columns.value = []
  rows.value = []
  chart.value = null
  notice.value = ''
}

async function loadData() {
  if (!activeReport.value) return
  if (!validateRange()) return
  loading.value = true
  notice.value = ''
  // Sync validated dates into the filter payload
  if (needs('from_date')) filters.from_date = dateFrom.value
  if (needs('to_date')) filters.to_date = dateTo.value
  try {
    const res = await call('sfa_core.api.reports.run_report', {
      report_name: activeReport.value.name,
      filters: JSON.stringify(filters),
    })
    const msg = res.message || {}
    columns.value = msg.columns || []
    rows.value = msg.data || []
    chart.value = msg.chart || null
    canExport.value = !!msg.can_export
  } catch (e) {
    // Reports that require a filter (e.g. form template) throw a clear message.
    const m = e?.message || ''
    if (/select a form template|select a form template and question/i.test(m)) {
      notice.value = m
      columns.value = []
      rows.value = []
      chart.value = null
    } else {
      errorToast('Report failed to run')
    }
  } finally {
    loading.value = false
  }
}

function isNumeric(c) {
  return ['Int', 'Float', 'Currency', 'Percent'].includes(c.fieldtype)
}

function fmtCell(val, c) {
  if (val == null || val === '') return '—'
  if (c.fieldtype === 'Currency') return formatCurrency(val)
  if (c.fieldtype === 'Percent') return (Math.round(Number(val) * 10) / 10) + '%'
  if (c.fieldtype === 'Float') return Math.round(Number(val) * 100) / 100
  return val
}

function doExport(fmt) {
  if (!canExport.value) return
  if (!validateRange()) return
  if (needs('from_date')) filters.from_date = dateFrom.value
  if (needs('to_date')) filters.to_date = dateTo.value
  const form = document.createElement('form')
  form.method = 'POST'
  form.action = '/api/method/sfa_core.api.reports.export_report'
  form.target = '_blank'
  const add = (k, v) => {
    const inp = document.createElement('input')
    inp.type = 'hidden'; inp.name = k; inp.value = v
    form.appendChild(inp)
  }
  add('report_name', activeReport.value.name)
  add('filters', JSON.stringify(filters))
  add('file_format', fmt)
  add('csrf_token', getCsrfToken())
  document.body.appendChild(form)
  form.submit()
  document.body.removeChild(form)
}
</script>
