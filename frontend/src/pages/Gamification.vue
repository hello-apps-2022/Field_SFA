<template>
  <div class="p-6 space-y-6">

    <!-- Header tabs -->
    <div class="flex gap-1 border-b border-gray-200">
      <button
        v-for="tab in tabs" :key="tab.id"
        class="px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors"
        :class="activeTab === tab.id
          ? 'border-gray-900 text-gray-900'
          : 'border-transparent text-gray-500 hover:text-gray-700'"
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Points Ledger -->
    <div v-if="activeTab === 'points'">
      <div class="flex items-center gap-3 mb-4">
        <div class="relative">
          <FeatherIcon name="search" class="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-gray-400" />
          <input v-model="search" type="text" placeholder="Search by rep..."
            class="h-9 rounded-md border border-gray-200 bg-white pl-8 pr-3 text-sm focus:border-gray-400 focus:outline-none w-56" />
        </div>
        <div class="flex-1" />
        <button class="flex h-9 items-center gap-1.5 rounded-md border border-gray-200 bg-white px-3 text-sm text-gray-600 hover:bg-gray-50" @click="loadPoints">
          <FeatherIcon name="refresh-cw" class="h-3.5 w-3.5" :class="loadingPoints ? 'animate-spin' : ''" />
          Refresh
        </button>
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
            <tr v-for="p in filteredPoints" :key="p.name" class="hover:bg-gray-50">
              <td class="px-4 py-3 font-medium text-gray-900">{{ p.sales_person }}</td>
              <td class="px-4 py-3 text-gray-600">{{ p.activity_type }}</td>
              <td class="px-4 py-3">
                <span :class="p.points >= 0 ? 'text-green-600 font-semibold' : 'text-red-500 font-semibold'">
                  {{ p.points >= 0 ? '+' : '' }}{{ p.points }}
                </span>
              </td>
              <td class="px-4 py-3 font-semibold text-gray-900">{{ p.balance }}</td>
              <td class="px-4 py-3 text-gray-500 text-xs">{{ formatDate(p.timestamp) }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="!loadingPoints && !filteredPoints.length" class="flex flex-col items-center py-12 text-gray-400">
          <FeatherIcon name="star" class="h-8 w-8 mb-2" />
          <p class="text-sm">No points activity yet</p>
        </div>
      </div>
    </div>

    <!-- Badges -->
    <div v-if="activeTab === 'badges'">
      <div class="flex items-center gap-3 mb-4">
        <div class="flex-1" />
        <button class="flex h-9 items-center gap-1.5 rounded-md border border-gray-200 bg-white px-3 text-sm text-gray-600 hover:bg-gray-50" @click="loadBadges">
          <FeatherIcon name="refresh-cw" class="h-3.5 w-3.5" :class="loadingBadges ? 'animate-spin' : ''" />
          Refresh
        </button>
      </div>
      <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <div v-for="b in badges" :key="b.name"
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
        <div v-if="!loadingBadges && !badges.length" class="col-span-3 flex flex-col items-center py-12 text-gray-400">
          <FeatherIcon name="award" class="h-10 w-10 mb-3" />
          <p class="text-sm">No badges awarded yet</p>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import dayjs from 'dayjs'

const activeTab = ref('points')
const search = ref('')
const loadingPoints = ref(false)
const loadingBadges = ref(false)
const pointsLedger = ref([])
const badges = ref([])

const tabs = [
  { id: 'points', label: 'Points Ledger' },
  { id: 'badges', label: 'Badges' },
]

async function loadPoints() {
  loadingPoints.value = true
  try {
    const res = await frappe.call({
      method: 'frappe.client.get_list',
      args: {
        doctype: 'SFA Rep Points Ledger',
        fields: ['name', 'sales_person', 'activity_type', 'points', 'balance', 'timestamp', 'description'],
        order_by: 'timestamp desc',
        limit: 200,
      }
    })
    pointsLedger.value = res.message || []
  } catch (e) { console.error(e) }
  finally { loadingPoints.value = false }
}

async function loadBadges() {
  loadingBadges.value = true
  try {
    const res = await frappe.call({
      method: 'frappe.client.get_list',
      args: {
        doctype: 'SFA Rep Badge',
        fields: ['name', 'sales_person', 'badge', 'awarded_date', 'awarded_by'],
        order_by: 'awarded_date desc',
        limit: 100,
      }
    })
    badges.value = res.message || []
  } catch (e) { console.error(e) }
  finally { loadingBadges.value = false }
}

onMounted(() => { loadPoints(); loadBadges() })

const filteredPoints = computed(() => {
  let l = pointsLedger.value
  if (search.value) {
    const q = search.value.toLowerCase()
    l = l.filter(p => p.sales_person?.toLowerCase().includes(q))
  }
  return l
})

const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY HH:mm') : '—'
</script>
