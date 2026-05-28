<template>
  <div class="mx-auto max-w-3xl p-6">
    <!-- Step 1: instructions + template -->
    <div class="mb-5 rounded-xl border border-gray-200 bg-white p-5">
      <h3 class="text-sm font-semibold text-gray-900">Bulk import outlets</h3>
      <p class="mt-1 text-sm text-gray-500">
        Upload a CSV of outlets. Required columns: <span class="font-medium text-gray-700">customer_name</span> and
        <span class="font-medium text-gray-700">territory</span>. Optional: mobile_no, customer_group, outlet_tier, location_area, location_city.
        Duplicates (same name + territory, or same phone) are skipped.
      </p>
      <div class="mt-3 flex items-center gap-3">
        <Btn variant="ghost" size="sm" @click="downloadTemplate">
          <FeatherIcon name="download" class="mr-1 h-3.5 w-3.5" />Download template
        </Btn>
        <label class="inline-flex cursor-pointer items-center gap-1.5 rounded-md bg-gray-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-gray-700">
          <FeatherIcon name="upload" class="h-3.5 w-3.5" />
          Choose CSV
          <input type="file" accept=".csv,text/csv" class="hidden" @change="onFile" />
        </label>
        <span v-if="fileName" class="text-xs text-gray-400">{{ fileName }}</span>
      </div>
      <p v-if="parseError" class="mt-2 text-xs text-red-500">{{ parseError }}</p>
    </div>

    <!-- Step 2: preview -->
    <div v-if="parsed.length" class="mb-5 rounded-xl border border-gray-200 bg-white">
      <div class="flex items-center justify-between border-b border-gray-100 px-5 py-3">
        <p class="text-sm font-medium text-gray-900">
          Preview — {{ parsed.length }} rows ({{ validCount }} valid, {{ parsed.length - validCount }} flagged)
        </p>
        <Btn variant="solid" size="sm" :disabled="!validCount || importing" @click="runImport">
          {{ importing ? 'Importing…' : `Import ${validCount} outlets` }}
        </Btn>
      </div>
      <div class="max-h-80 overflow-auto">
        <table class="min-w-full text-sm">
          <thead class="border-b border-gray-100 bg-gray-50">
            <tr>
              <th class="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Name</th>
              <th class="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Territory</th>
              <th class="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Phone</th>
              <th class="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(r, i) in parsed" :key="i" class="border-b border-gray-50">
              <td class="px-3 py-1.5 text-gray-700">{{ r.customer_name || '—' }}</td>
              <td class="px-3 py-1.5 text-gray-700">{{ r.territory || '—' }}</td>
              <td class="px-3 py-1.5 text-gray-500">{{ r.mobile_no || '—' }}</td>
              <td class="px-3 py-1.5">
                <span v-if="r._valid" class="text-xs text-green-600">Ready</span>
                <span v-else class="text-xs text-amber-600">{{ r._issue }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Step 3: results -->
    <div v-if="result" class="rounded-xl border border-gray-200 bg-white p-5">
      <h3 class="text-sm font-semibold text-gray-900">Import complete</h3>
      <div class="mt-2 flex gap-4 text-sm">
        <span class="text-green-600">{{ result.created }} created</span>
        <span class="text-amber-600">{{ result.skipped }} skipped</span>
        <span class="text-red-500">{{ result.errors }} errors</span>
      </div>
      <div v-if="result.report?.some(r => r.status !== 'created')" class="mt-3 max-h-60 overflow-auto rounded-lg border border-gray-100">
        <table class="min-w-full text-sm">
          <tbody>
            <tr v-for="(r, i) in result.report.filter(x => x.status !== 'created')" :key="i" class="border-b border-gray-50">
              <td class="px-3 py-1.5 text-gray-400">#{{ r.row }}</td>
              <td class="px-3 py-1.5 text-gray-700">{{ r.name }}</td>
              <td class="px-3 py-1.5" :class="r.status === 'skipped' ? 'text-amber-600' : 'text-red-500'">{{ r.status }}: {{ r.reason }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { call } from '@/utils/frappe'
import { successToast, errorToast } from '@/utils/toast'
import Btn from '@/components/ui/Btn.vue'
import FeatherIcon from '@/components/ui/FeatherIcon.vue'

const REQUIRED = ['customer_name', 'territory']
const fileName = ref('')
const parseError = ref('')
const parsed = ref([])
const importing = ref(false)
const result = ref(null)
let territorySet = null

const validCount = computed(() => parsed.value.filter(r => r._valid).length)

async function downloadTemplate() {
  try {
    const res = await call('sfa_core.api.customer.get_import_template')
    const csv = (res.message && res.message.csv) || ''
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = 'outlet_import_template.csv'
    document.body.appendChild(a); a.click(); document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch (e) { errorToast('Could not get template') }
}

// Minimal CSV parser: handles quoted fields and commas inside quotes.
function parseCsv(text) {
  const rows = []
  const lines = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n').split('\n').filter(l => l.trim() !== '')
  for (const line of lines) {
    const fields = []
    let cur = '', inQuotes = false
    for (let i = 0; i < line.length; i++) {
      const ch = line[i]
      if (inQuotes) {
        if (ch === '"' && line[i + 1] === '"') { cur += '"'; i++ }
        else if (ch === '"') inQuotes = false
        else cur += ch
      } else {
        if (ch === '"') inQuotes = true
        else if (ch === ',') { fields.push(cur); cur = '' }
        else cur += ch
      }
    }
    fields.push(cur)
    rows.push(fields.map(f => f.trim()))
  }
  return rows
}

async function loadTerritories() {
  if (territorySet) return
  try {
    const res = await call('frappe.client.get_list', {
      doctype: 'Territory', fields: ['name'], limit_page_length: 500,
    })
    territorySet = new Set((res.message || []).map(t => t.name))
  } catch (e) { territorySet = new Set() }
}

async function onFile(e) {
  result.value = null
  parseError.value = ''
  const file = e.target.files?.[0]
  if (!file) return
  fileName.value = file.name
  await loadTerritories()

  const text = await file.text()
  const rows = parseCsv(text)
  if (rows.length < 2) { parseError.value = 'CSV has no data rows.'; parsed.value = []; return }

  const header = rows[0].map(h => h.toLowerCase().trim())
  for (const req of REQUIRED) {
    if (!header.includes(req)) { parseError.value = `Missing required column: ${req}`; parsed.value = []; return }
  }

  const out = []
  for (let i = 1; i < rows.length; i++) {
    const obj = {}
    header.forEach((h, idx) => { obj[h] = rows[i][idx] || '' })
    obj._valid = true; obj._issue = ''
    if (!obj.customer_name || !obj.territory) { obj._valid = false; obj._issue = 'Missing name/territory' }
    else if (territorySet.size && !territorySet.has(obj.territory)) { obj._valid = false; obj._issue = `Unknown territory` }
    out.push(obj)
  }
  parsed.value = out
}

async function runImport() {
  importing.value = true
  try {
    const payload = parsed.value.map(r => ({
      customer_name: r.customer_name, territory: r.territory, mobile_no: r.mobile_no,
      customer_group: r.customer_group,
      outlet_tier: r.outlet_tier, location_area: r.location_area, location_city: r.location_city,
    }))
    const res = await call('sfa_core.api.customer.bulk_import_customers', {
      rows: JSON.stringify(payload),
    })
    result.value = res.message || null
    if (result.value) successToast(`${result.value.created} outlets created`)
    parsed.value = []
    fileName.value = ''
  } catch (e) {
    errorToast(e.message || 'Import failed')
  } finally {
    importing.value = false
  }
}
</script>
