<template>
  <div class="flex h-full flex-col">
    <!-- Header -->
    <div class="shrink-0 border-b border-gray-100 px-6 pt-5">
      <h1 class="text-lg font-semibold text-gray-900">Gamification</h1>
      <p class="text-xs text-gray-400 mb-3">Points, leaderboard and badges for the field team</p>
      <div class="flex gap-1">
        <button v-for="tab in visibleTabs" :key="tab.id"
          class="px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors"
          :class="activeTab === tab.id ? 'border-gray-900 text-gray-900' : 'border-transparent text-gray-500 hover:text-gray-700'"
          @click="activeTab = tab.id">
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Shared date + territory filter (not shown on Config) -->
    <div v-if="activeTab !== 'config'" class="shrink-0 flex flex-wrap items-center gap-2 border-b border-gray-50 px-6 py-3">
      <DateRangeFilter v-model:from="dateFrom" v-model:to="dateTo" @change="applyDateFilter" />
      <select v-if="auth.isAdmin || auth.isManager" v-model="territoryFilter" @change="applyDateFilter"
        class="h-9 rounded-md border border-gray-200 bg-white px-3 text-sm focus:outline-none">
        <option value="">All territories</option>
        <option v-for="t in territories" :key="t" :value="t">{{ t }}</option>
      </select>
      <div class="flex-1" />
      <button class="flex h-9 items-center gap-1.5 rounded-md border border-gray-200 bg-white px-3 text-sm text-gray-600 hover:bg-gray-50" @click="refreshActive">
        <FeatherIcon name="refresh-cw" class="h-3.5 w-3.5" :class="anyLoading ? 'animate-spin' : ''" />
        Refresh
      </button>
    </div>

    <div class="flex-1 overflow-auto p-6">
      <!-- ===== LEADERBOARD ===== -->
      <div v-if="activeTab === 'leaderboard'">
        <div v-if="leaderboard.length" class="space-y-2">
          <div v-for="(row, i) in leaderboard" :key="row.sales_person"
            class="flex items-center gap-4 rounded-xl border bg-white p-4 shadow-sm"
            :class="i === 0 ? 'border-yellow-200 bg-yellow-50/40' : 'border-gray-200'">
            <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-sm font-bold"
              :class="rankClass(i)">
              {{ i + 1 }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-gray-900 truncate">{{ row.sales_person }}</p>
              <p class="text-xs text-gray-400">{{ row.activities || 0 }} activities</p>
            </div>
            <div class="text-right">
              <p class="text-base font-bold text-gray-900">{{ (row.total_points || 0).toLocaleString() }}</p>
              <p class="text-xs text-gray-400">points</p>
            </div>
          </div>
        </div>
        <div v-else-if="loadingLb" class="flex justify-center py-20">
          <FeatherIcon name="loader" class="h-6 w-6 animate-spin text-gray-300" />
        </div>
        <div v-else class="flex flex-col items-center justify-center rounded-xl border border-dashed border-gray-200 bg-gray-50/50 py-16 px-6 text-center">
          <div class="flex h-12 w-12 items-center justify-center rounded-full bg-blue-50 mb-3">
            <FeatherIcon name="bar-chart-2" class="h-6 w-6 text-blue-400" />
          </div>
          <p class="text-sm font-medium text-gray-700">No points earned yet</p>
          <p class="mt-1 max-w-sm text-xs text-gray-400">
            Once your team starts completing visits, placing orders, and collecting payments, the leaderboard will rank reps by points earned.
          </p>
        </div>
      </div>

      <!-- ===== POINTS LEDGER ===== -->
      <div v-if="activeTab === 'ledger'">
        <div class="mb-4 flex items-center gap-2">
          <div class="relative">
            <FeatherIcon name="search" class="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-gray-400" />
            <input v-model="ledgerSearch" @input="onLedgerSearch" type="text" placeholder="Search by rep or activity..."
              class="h-9 w-64 rounded-md border border-gray-200 bg-white pl-8 pr-3 text-sm focus:border-gray-400 focus:outline-none" />
          </div>
        </div>
        <div class="rounded-xl border border-gray-200 bg-white overflow-hidden shadow-sm">
          <table class="w-full text-sm">
            <thead class="border-b border-gray-100 bg-gray-50">
              <tr>
                <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Sales Person</th>
                <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Activity</th>
                <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Points</th>
                <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Balance</th>
                <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Date</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="p in ledger" :key="p.name" class="hover:bg-gray-50">
                <td class="px-4 py-3 font-medium text-gray-900">{{ p.sales_person }}</td>
                <td class="px-4 py-3 text-gray-600">{{ p.activity_type }}</td>
                <td class="px-4 py-3">
                  <span :class="p.points >= 0 ? 'text-green-600 font-semibold' : 'text-red-500 font-semibold'">
                    {{ p.points >= 0 ? '+' : '' }}{{ p.points }}
                  </span>
                </td>
                <td class="px-4 py-3 font-semibold text-gray-900">{{ p.balance }}</td>
                <td class="px-4 py-3 text-gray-500 text-xs">{{ formatDateTime(p.timestamp) }}</td>
              </tr>
            </tbody>
          </table>
          <div v-if="!loadingLedger && !ledger.length" class="flex flex-col items-center justify-center py-16 px-6 text-center">
            <div class="flex h-12 w-12 items-center justify-center rounded-full bg-gray-100 mb-3">
              <FeatherIcon name="star" class="h-6 w-6 text-gray-400" />
            </div>
            <p class="text-sm font-medium text-gray-700">No points activity yet</p>
            <p class="mt-1 max-w-sm text-xs text-gray-400">
              Every visit, order, and payment a rep logs will appear here as points are awarded.
            </p>
          </div>
          <div v-if="ledgerTotal" class="border-t border-gray-100 px-4">
            <Pagination :page="ledgerPage" :page-size="ledgerPageSize" :total="ledgerTotal" :loading="loadingLedger"
              @update:page="goLedgerPage" @load-more="loadMoreLedger" />
          </div>
        </div>
      </div>

      <!-- ===== BADGES (earned) ===== -->
      <div v-if="activeTab === 'badges'">
        <div v-if="earnedBadges.length" class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <div v-for="b in earnedBadges" :key="b.name"
            class="flex items-center gap-4 rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
            <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-yellow-50">
              <FeatherIcon name="award" class="h-5 w-5 text-yellow-500" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-gray-900">{{ b.sales_person }}</p>
              <p class="text-xs text-gray-500">{{ b.badge }}</p>
              <p class="text-xs text-gray-400 mt-0.5">{{ formatDate(b.awarded_date) }}</p>
            </div>
          </div>
        </div>
        <div v-else-if="loadingEarned" class="flex justify-center py-20">
          <FeatherIcon name="loader" class="h-6 w-6 animate-spin text-gray-300" />
        </div>
        <div v-else class="flex flex-col items-center justify-center rounded-xl border border-dashed border-gray-200 bg-gray-50/50 py-16 px-6 text-center">
          <div class="flex h-12 w-12 items-center justify-center rounded-full bg-yellow-50 mb-3">
            <FeatherIcon name="award" class="h-6 w-6 text-yellow-400" />
          </div>
          <p class="text-sm font-medium text-gray-700">No badges earned yet</p>
          <p class="mt-1 max-w-sm text-xs text-gray-400">
            Badges are awarded automatically when reps hit their targets — completing visits, placing orders, or collecting payments.
            <span v-if="auth.isAdmin">Define the rules in the <button class="font-medium text-gray-600 underline hover:text-gray-800" @click="activeTab = 'config'">Config</button> tab.</span>
          </p>
        </div>
      </div>

      <!-- ===== CONFIG (admin only) ===== -->
      <div v-if="activeTab === 'config' && auth.isAdmin" class="space-y-8">
        <!-- Points config -->
        <section>
          <h2 class="text-sm font-semibold text-gray-900 mb-1">Points per activity</h2>
          <p class="text-xs text-gray-400 mb-3">How many points each action awards. Changes apply to future activity only.</p>
          <div class="rounded-xl border border-gray-200 bg-white overflow-hidden shadow-sm">
            <table class="w-full text-sm">
              <thead class="border-b border-gray-100 bg-gray-50">
                <tr>
                  <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Activity</th>
                  <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Points</th>
                  <th class="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Active</th>
                  <th class="px-4 py-2.5 text-right text-xs font-medium uppercase tracking-wide text-gray-500"></th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-for="c in pointsConfig" :key="c.name" class="hover:bg-gray-50">
                  <td class="px-4 py-3 font-medium text-gray-900">{{ c.activity_type }}
                    <span v-if="c.description" class="block text-xs font-normal text-gray-400">{{ c.description }}</span>
                  </td>
                  <td class="px-4 py-3">
                    <input v-model.number="c.points" type="number" min="0"
                      class="h-8 w-24 rounded-md border border-gray-200 px-2 text-sm focus:border-gray-400 focus:outline-none" />
                  </td>
                  <td class="px-4 py-3">
                    <input v-model="c.is_active" type="checkbox" :true-value="1" :false-value="0" class="h-4 w-4 rounded" />
                  </td>
                  <td class="px-4 py-3 text-right">
                    <button class="rounded-md bg-gray-900 px-3 py-1.5 text-xs font-medium text-white hover:bg-gray-800 disabled:opacity-50"
                      :disabled="savingCfg === c.activity_type" @click="savePoints(c)">
                      {{ savingCfg === c.activity_type ? 'Saving…' : 'Save' }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <!-- Badges editor -->
        <section>
          <div class="mb-3 flex items-center justify-between">
            <div>
              <h2 class="text-sm font-semibold text-gray-900">Badges</h2>
              <p class="text-xs text-gray-400">Define automatic awards based on rep performance.</p>
            </div>
            <button class="flex h-9 items-center gap-1.5 rounded-md bg-gray-900 px-3 text-sm font-medium text-white hover:bg-gray-800" @click="openBadge()">
              <FeatherIcon name="plus" class="h-3.5 w-3.5" /> New badge
            </button>
          </div>
          <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <div v-for="b in badgeDefs" :key="b.name"
              class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm"
              :class="b.is_active ? '' : 'opacity-60'">
              <div class="flex items-start justify-between">
                <div class="flex items-center gap-2">
                  <div class="flex h-8 w-8 items-center justify-center rounded-full bg-yellow-50">
                    <FeatherIcon :name="b.icon || 'award'" class="h-4 w-4 text-yellow-500" />
                  </div>
                  <p class="text-sm font-semibold text-gray-900">{{ b.badge_name }}</p>
                </div>
                <button class="text-gray-300 hover:text-gray-600" @click="openBadge(b)">
                  <FeatherIcon name="edit-2" class="h-3.5 w-3.5" />
                </button>
              </div>
              <p class="mt-2 text-xs text-gray-500">{{ b.description }}</p>
              <p class="mt-2 text-xs text-gray-400">
                {{ b.criteria_type }} ≥ {{ b.threshold_value.toLocaleString() }}
                <span v-if="b.period_days"> in {{ b.period_days }}d</span>
                · +{{ b.points_bonus }} pts
              </p>
              <button class="mt-3 text-xs font-medium"
                :class="b.is_active ? 'text-red-500 hover:text-red-600' : 'text-green-600 hover:text-green-700'"
                @click="toggleBadge(b)">
                {{ b.is_active ? 'Disable' : 'Enable' }}
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>

    <!-- Badge editor panel -->
    <SlidePanel v-model="badgePanel" :title="editingBadge ? 'Edit Badge' : 'New Badge'" :saving="savingBadge" @save="saveBadge">
      <div class="space-y-4">
        <FormField v-model="badgeForm.badge_name" label="Badge Name" required :error="badgeErrors.badge_name" />
        <FormField v-model="badgeForm.description" label="Description" type="textarea" />
        <FormField v-model="badgeForm.icon" label="Icon" type="select" :options="iconOptions" />
        <FormField v-model="badgeForm.criteria_type" label="Criteria Type" type="select" :options="criteriaOptions" required />
        <FormField v-model.number="badgeForm.threshold_value" label="Threshold" type="number" required :error="badgeErrors.threshold_value" />
        <FormField v-model.number="badgeForm.period_days" label="Period (days, 0 = all time)" type="number" />
        <FormField v-model.number="badgeForm.points_bonus" label="Bonus Points" type="number" />
      </div>
    </SlidePanel>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { call } from '@/utils/frappe'
import { successToast, errorToast } from '@/utils/toast'
import { auth } from '@/utils/auth'
import Pagination from '@/components/ui/Pagination.vue'
import SlidePanel from '@/components/ui/SlidePanel.vue'
import FormField from '@/components/ui/FormField.vue'
import DateRangeFilter from '@/components/ui/DateRangeFilter.vue'
import { useLinkedData } from '@/composables/useLinkedData'
import dayjs from 'dayjs'

const allTabs = [
  { id: 'leaderboard', label: 'Leaderboard', admin: false },
  { id: 'ledger', label: 'Points Ledger', admin: false },
  { id: 'badges', label: 'Badges', admin: false },
  { id: 'config', label: 'Config', admin: true },
]
const visibleTabs = computed(() => allTabs.filter(t => !t.admin || auth.isAdmin))
const activeTab = ref('leaderboard')

// ---- Shared date + territory filter ----
// Applies to Leaderboard, Points Ledger, and Badges (by awarded date).
const dateFrom = ref('')
const dateTo = ref('')
const territoryFilter = ref('')
const { territories, loadTerritories } = useLinkedData()

// Build the params the API expects from the current filter selection.
function dateParams() {
  return {
    date_from: dateFrom.value || null,
    date_to: dateTo.value || null,
    territory: territoryFilter.value || null,
  }
}

// Re-load whichever tabs depend on the date filter.
function applyDateFilter() {
  loadLeaderboard()
  ledgerPage.value = 1
  loadLedger()
  loadEarnedBadges()
}

// ---- Leaderboard ----
const leaderboard = ref([])
const loadingLb = ref(false)
async function loadLeaderboard() {
  loadingLb.value = true
  try {
    leaderboard.value = (await call('sfa_core.api.gamification.get_leaderboard', dateParams())).message || []
  } catch (e) { console.error(e) } finally { loadingLb.value = false }
}
function rankClass(i) {
  if (i === 0) return 'bg-yellow-400 text-white'
  if (i === 1) return 'bg-gray-300 text-white'
  if (i === 2) return 'bg-amber-600 text-white'
  return 'bg-gray-100 text-gray-500'
}

// ---- Points Ledger (paginated) ----
const ledger = ref([])
const loadingLedger = ref(false)
const ledgerSearch = ref('')
const ledgerPage = ref(1)
const ledgerPageSize = 50
const ledgerTotal = ref(0)
async function loadLedger(append = false) {
  loadingLedger.value = true
  try {
    const res = (await call('sfa_core.api.gamification.get_points_ledger', {
      search: ledgerSearch.value || null,
      ...dateParams(),
      start: (ledgerPage.value - 1) * ledgerPageSize,
      page_length: ledgerPageSize,
    })).message || {}
    const items = res.items || []
    ledger.value = append ? [...ledger.value, ...items] : items
    ledgerTotal.value = res.total || 0
  } catch (e) { console.error(e) } finally { loadingLedger.value = false }
}
let ledgerTimer = null
function onLedgerSearch() {
  clearTimeout(ledgerTimer)
  ledgerTimer = setTimeout(() => { ledgerPage.value = 1; loadLedger() }, 350)
}
function goLedgerPage(p) { ledgerPage.value = p; loadLedger(false) }
function loadMoreLedger() { ledgerPage.value += 1; loadLedger(true) }

// ---- Earned badges ----
const earnedBadges = ref([])
const loadingEarned = ref(false)
async function loadEarnedBadges() {
  loadingEarned.value = true
  try {
    earnedBadges.value = (await call('sfa_core.api.gamification.get_earned_badges', dateParams())).message || []
  } catch (e) { console.error(e) } finally { loadingEarned.value = false }
}

// ---- Config: points ----
const pointsConfig = ref([])
const savingCfg = ref(null)
async function loadPointsConfig() {
  if (!auth.isAdmin) return
  try {
    pointsConfig.value = (await call('sfa_core.api.gamification.get_points_config')).message || []
  } catch (e) { console.error(e) }
}
async function savePoints(c) {
  savingCfg.value = c.activity_type
  try {
    await call('sfa_core.api.gamification.save_points_config', {
      activity_type: c.activity_type, points: c.points, is_active: c.is_active ? 1 : 0,
    })
    successToast('Saved')
  } catch (e) { errorToast(e.message || 'Save failed') }
  finally { savingCfg.value = null }
}

// ---- Config: badges ----
const badgeDefs = ref([])
async function loadBadgeDefs() {
  if (!auth.isAdmin) return
  try {
    badgeDefs.value = (await call('sfa_core.api.gamification.get_badges')).message || []
  } catch (e) { console.error(e) }
}
const criteriaOptions = ['Visit Count', 'Order Value', 'Payment Amount', 'Points Threshold', 'Consecutive Days', 'Custom']
const iconOptions = ['award', 'star', 'shield', 'zap', 'trending-up', 'truck', 'dollar-sign']
const badgePanel = ref(false)
const editingBadge = ref(null)
const savingBadge = ref(false)
const badgeForm = reactive({ badge_name: '', description: '', icon: 'award', criteria_type: 'Visit Count', threshold_value: 0, period_days: 0, points_bonus: 0 })
const badgeErrors = reactive({})
function openBadge(b = null) {
  editingBadge.value = b ? b.name : null
  Object.keys(badgeErrors).forEach(k => delete badgeErrors[k])
  if (b) {
    Object.assign(badgeForm, {
      badge_name: b.badge_name, description: b.description || '', icon: b.icon || 'award',
      criteria_type: b.criteria_type, threshold_value: b.threshold_value, period_days: b.period_days, points_bonus: b.points_bonus,
    })
  } else {
    Object.assign(badgeForm, { badge_name: '', description: '', icon: 'award', criteria_type: 'Visit Count', threshold_value: 0, period_days: 0, points_bonus: 0 })
  }
  badgePanel.value = true
}
async function saveBadge() {
  if (!badgeForm.badge_name.trim()) { badgeErrors.badge_name = 'Required'; return }
  if (badgeForm.threshold_value === null || badgeForm.threshold_value === undefined || badgeForm.threshold_value === '') { badgeErrors.threshold_value = 'Required'; return }
  savingBadge.value = true
  try {
    await call('sfa_core.api.gamification.save_badge', {
      name: editingBadge.value || null,
      badge_name: badgeForm.badge_name, description: badgeForm.description, icon: badgeForm.icon,
      criteria_type: badgeForm.criteria_type, threshold_value: badgeForm.threshold_value,
      period_days: badgeForm.period_days, points_bonus: badgeForm.points_bonus, is_active: 1,
    })
    successToast('Badge saved')
    badgePanel.value = false
    loadBadgeDefs()
  } catch (e) { errorToast(e.message || 'Save failed') }
  finally { savingBadge.value = false }
}
async function toggleBadge(b) {
  try {
    await call('sfa_core.api.gamification.toggle_badge', { name: b.name, is_active: b.is_active ? 0 : 1 })
    loadBadgeDefs()
  } catch (e) { errorToast(e.message || 'Failed') }
}

const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'
const formatDateTime = (d) => d ? dayjs(d).format('D MMM YYYY HH:mm') : '—'

// Refresh only the tab currently in view.
function refreshActive() {
  if (activeTab.value === 'leaderboard') loadLeaderboard()
  else if (activeTab.value === 'ledger') { ledgerPage.value = 1; loadLedger() }
  else if (activeTab.value === 'badges') loadEarnedBadges()
}
const anyLoading = computed(() => loadingLb.value || loadingLedger.value || loadingEarned.value)

onMounted(() => {
  // The DateRangeFilter emits its initial range on mount, which triggers
  // applyDateFilter() → loads leaderboard, ledger, and badges. So we only
  // need to load the admin-config data and territory options here.
  loadPointsConfig()
  loadBadgeDefs()
  loadTerritories()
})
</script>
