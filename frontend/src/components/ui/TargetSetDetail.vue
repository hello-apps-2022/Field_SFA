<template>
  <SlidePanel
    :model-value="modelValue"
    :title="doc?.target_set_name || 'Target Set'"
    :save-label="hasChanges ? 'Save Changes' : ''"
    :cancel-label="hasChanges ? 'Discard' : 'Close'"
    width="700px"
    @update:model-value="onClose"
    @save="saveChanges"
    @cancel="hasChanges ? confirmDiscard() : $emit('update:modelValue', false)"
  >
    <div v-if="loading" class="flex h-40 items-center justify-center">
      <FeatherIcon name="loader" class="h-6 w-6 animate-spin text-gray-400" />
    </div>

    <div v-else-if="doc" class="space-y-4">

      <!-- Meta strip -->
      <div class="flex items-start justify-between rounded-xl border border-gray-200 bg-gray-50 px-4 py-3">
        <div class="space-y-1">
          <div class="flex items-center gap-2">
            <span class="rounded-full px-2.5 py-0.5 text-xs font-medium"
              :class="statusColor(doc.status)">{{ doc.status }}</span>
            <span class="text-xs text-gray-500">{{ doc.territory }}</span>
          </div>
          <p class="text-xs text-gray-400">
            {{ fmtDate(doc.date_from) }} → {{ fmtDate(doc.date_to) }}
            <span class="ml-1">({{ dayCount }} days)</span>
          </p>
          <p v-if="doc.notes" class="text-xs text-gray-400">{{ doc.notes }}</p>
        </div>
        <div class="flex items-center gap-2">
          <select v-model="doc.status" @change="hasChanges = true"
            class="h-7 rounded-md border border-gray-200 bg-white px-2 text-xs focus:outline-none">
            <option>Draft</option>
            <option>Active</option>
            <option>Closed</option>
          </select>
        </div>
      </div>

      <!-- Summary tiles -->
      <div class="grid grid-cols-4 gap-3">
        <div v-for="m in summaryMetrics" :key="m.label"
          class="rounded-xl border border-gray-200 bg-white px-3 py-2.5">
          <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">{{ m.label }}</p>
          <div class="mt-1 flex items-end gap-1">
            <span class="text-lg font-bold text-gray-900">{{ m.actual }}</span>
            <span class="text-xs text-gray-400 mb-0.5">/ {{ m.target }}</span>
          </div>
          <div class="mt-1.5 h-1 w-full rounded-full bg-gray-100">
            <div class="h-1 rounded-full"
              :class="m.pct >= 100 ? 'bg-green-400' : m.pct >= 70 ? 'bg-amber-400' : 'bg-red-400'"
              :style="{ width: Math.min(m.pct, 100) + '%' }" />
          </div>
        </div>
      </div>

      <!-- Rep rows -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <p class="text-xs font-semibold text-gray-600">Rep Targets & Performance</p>
          <p class="text-xs text-gray-400">{{ doc.rep_targets?.length || 0 }} reps</p>
        </div>

        <div class="rounded-xl border border-gray-200 overflow-hidden">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 border-b border-gray-100">
              <tr>
                <th class="px-4 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wide text-gray-400">Rep</th>
                <th v-for="m in metricCols" :key="m.key"
                  class="px-3 py-2.5 text-center text-[10px] font-semibold uppercase tracking-wide text-gray-400">
                  {{ m.label }}
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="rep in doc.rep_targets" :key="rep.sales_person">
                <!-- Rep name -->
                <td class="px-4 py-3">
                  <div class="flex items-center gap-2">
                    <div class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-[10px] font-bold text-indigo-700">
                      {{ (rep.sales_person_name||'?').charAt(0).toUpperCase() }}
                    </div>
                    <span class="text-sm font-medium text-gray-900">{{ rep.sales_person_name }}</span>
                  </div>
                </td>

                <!-- Metric columns: editable target + actual -->
                <td v-for="m in metricCols" :key="m.key" class="px-3 py-3">
                  <div class="space-y-1.5">
                    <!-- Target input -->
                    <div class="flex items-center gap-1 justify-center">
                      <input
                        v-model.number="rep[`target_${m.key}`]"
                        type="number" min="0"
                        class="w-20 h-7 rounded border border-gray-200 px-2 text-xs text-center focus:border-gray-400 focus:outline-none"
                        @change="hasChanges = true"
                      />
                      <span v-if="m.pct_suffix" class="text-[10px] text-gray-400">%</span>
                    </div>
                    <!-- Actual -->
                    <div class="text-center">
                      <span class="text-xs font-semibold"
                        :class="achievementColor(rep[`actual_${m.key}`], rep[`target_${m.key}`])">
                        {{ fmtVal(rep[`actual_${m.key}`] || 0, m) }}
                      </span>
                      <span class="text-[10px] text-gray-400"> actual</span>
                    </div>
                    <!-- Progress bar -->
                    <div class="h-1 w-full rounded-full bg-gray-100">
                      <div class="h-1 rounded-full"
                        :class="achievementPct(rep[`actual_${m.key}`], rep[`target_${m.key}`]) >= 100 ? 'bg-green-400' : achievementPct(rep[`actual_${m.key}`], rep[`target_${m.key}`]) >= 70 ? 'bg-amber-400' : 'bg-red-400'"
                        :style="{ width: Math.min(achievementPct(rep[`actual_${m.key}`], rep[`target_${m.key}`]), 100) + '%' }" />
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>

          <div v-if="!doc.rep_targets?.length" class="py-8 text-center text-xs text-gray-400">
            No reps in this target set
          </div>
        </div>
      </div>
    </div>
  </SlidePanel>

  <!-- Confirm discard -->
  <Teleport to="body">
    <div v-if="confirmDialog" class="fixed inset-0 z-[70] flex items-center justify-center bg-black/30 backdrop-blur-sm">
      <div class="w-80 rounded-2xl border border-gray-200 bg-white p-6 shadow-2xl">
        <p class="text-sm font-semibold text-gray-900">Discard changes?</p>
        <p class="mt-1.5 text-sm text-gray-500">Unsaved target changes will be lost.</p>
        <div class="mt-5 flex gap-2 justify-end">
          <button class="h-8 rounded-lg border border-gray-200 px-3 text-sm text-gray-600 hover:bg-gray-50" @click="confirmDialog = false">Cancel</button>
          <button class="h-8 rounded-lg bg-red-600 px-4 text-sm font-medium text-white hover:bg-red-700"
            @click="confirmDialog = false; $emit('update:modelValue', false)">Discard</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { call } from '@/utils/frappe'
import { successToast, errorToast } from '@/utils/toast'
import SlidePanel from '@/components/ui/SlidePanel.vue'
import dayjs from 'dayjs'

const props = defineProps({
  modelValue: Boolean,
  name: String,
  territories: Array,
})
const emit = defineEmits(['update:modelValue', 'updated'])

const doc = ref(null)
const loading = ref(false)
const saving = ref(false)
const hasChanges = ref(false)
const confirmDialog = ref(false)

const metricCols = [
  { key: 'visits', label: 'Visits', pct_suffix: false },
  { key: 'revenue', label: 'Revenue', pct_suffix: false, currency: true },
  { key: 'new_customers', label: 'New Custs', pct_suffix: false },
  { key: 'compliance_pct', label: 'Compliance', pct_suffix: true },
]

const fmtDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'

const dayCount = computed(() => {
  if (!doc.value?.date_from || !doc.value?.date_to) return 0
  return dayjs(doc.value.date_to).diff(dayjs(doc.value.date_from), 'day') + 1
})

const statusColor = (s) => ({
  'Draft':  'bg-gray-100 text-gray-600',
  'Active': 'bg-green-100 text-green-700',
  'Closed': 'bg-blue-100 text-blue-700',
}[s] || 'bg-gray-100 text-gray-600')

function fmtNum(n) {
  if (!n) return '0'
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return (n / 1000).toFixed(0) + 'K'
  return String(Math.round(n))
}

function fmtVal(val, m) {
  if (m.currency) return fmtNum(val)
  if (m.pct_suffix) return val + '%'
  return val
}

function achievementPct(actual, target) {
  return target > 0 ? Math.round((actual || 0) / target * 100) : 0
}

function achievementColor(actual, target) {
  const pct = achievementPct(actual, target)
  if (!target) return 'text-gray-400'
  if (pct >= 100) return 'text-green-600'
  if (pct >= 70) return 'text-amber-600'
  return 'text-red-600'
}

const summaryMetrics = computed(() => {
  if (!doc.value?.rep_targets) return []
  const reps = doc.value.rep_targets
  const tot = (key) => reps.reduce((s, r) => s + (r[key] || 0), 0)
  const pct = (a, t) => t > 0 ? Math.round(a / t * 100) : 0
  return [
    { label: 'Visits', target: tot('target_visits'), actual: tot('actual_visits'), pct: pct(tot('actual_visits'), tot('target_visits')) },
    { label: 'Revenue', target: fmtNum(tot('target_revenue')), actual: fmtNum(tot('actual_revenue')), pct: pct(tot('actual_revenue'), tot('target_revenue')) },
    { label: 'New Customers', target: tot('target_new_customers'), actual: tot('actual_new_customers'), pct: pct(tot('actual_new_customers'), tot('target_new_customers')) },
    { label: 'Compliance', target: Math.round(tot('target_compliance_pct') / reps.length || 0) + '%', actual: Math.round(tot('actual_compliance_pct') / reps.length || 0) + '%', pct: pct(tot('actual_compliance_pct'), tot('target_compliance_pct')) },
  ]
})

async function load() {
  loading.value = true
  try {
    const res = await call('sfa_core.api.targets.get_target_set', { name: props.name })
    doc.value = res.message
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

async function saveChanges() {
  saving.value = true
  try {
    await call('sfa_core.api.targets.update_target_set', {
      name: props.name,
      status: doc.value.status,
      rep_targets: doc.value.rep_targets.map(r => ({
        sales_person: r.sales_person,
        sales_person_name: r.sales_person_name,
        target_visits: r.target_visits || 0,
        target_revenue: r.target_revenue || 0,
        target_new_customers: r.target_new_customers || 0,
        target_compliance_pct: r.target_compliance_pct || 0,
      })),
    })
    hasChanges.value = false
    successToast('Targets saved')
    emit('updated')
  } catch (e) { errorToast(e.message) }
  finally { saving.value = false }
}

function confirmDiscard() { confirmDialog.value = true }

function onClose(val) {
  if (!val && hasChanges.value) { confirmDialog.value = true; return }
  emit('update:modelValue', val)
}

onMounted(load)
</script>
