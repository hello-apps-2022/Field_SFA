<template>
  <div class="flex h-[52px] shrink-0 items-center border-b border-gray-100 bg-white px-4 gap-3">

    <!-- Universal search -->
    <div class="relative flex-1 max-w-md">
      <FeatherIcon name="search" class="absolute left-3 top-2.5 h-3.5 w-3.5 text-gray-400 pointer-events-none" />
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search customers, visits, forms…"
        class="w-full h-8 rounded-lg border border-gray-200 bg-gray-50 pl-8 pr-3 text-sm focus:border-gray-400 focus:bg-white focus:outline-none transition-colors"
        @keydown.enter="search"
        @input="onInput"
        @focus="showResults = true"
        @blur="onSearchBlur"
      />

      <!-- Search results dropdown -->
      <div v-if="showResults && (results.length || searching)" class="absolute top-full left-0 right-0 mt-1 z-50 rounded-xl border border-gray-200 bg-white shadow-lg overflow-hidden">
        <div v-if="searching" class="flex items-center gap-2 px-4 py-3 text-sm text-gray-400">
          <FeatherIcon name="loader" class="h-3.5 w-3.5 animate-spin" /> Searching…
        </div>
        <div v-else>
          <div v-for="r in results" :key="r.name + r.type"
            class="flex items-center gap-3 px-4 py-2.5 cursor-pointer hover:bg-gray-50 transition-colors"
            @mousedown.prevent="navigate(r)"
          >
            <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg"
              :class="{
                'bg-indigo-100 text-indigo-600': r.type === 'customer',
                'bg-blue-100 text-blue-600': r.type === 'visit',
                'bg-green-100 text-green-600': r.type === 'form',
              }"
            >
              <FeatherIcon :name="r.type === 'customer' ? 'user' : r.type === 'visit' ? 'map-pin' : 'file-text'" class="h-3.5 w-3.5" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 truncate">{{ r.label }}</p>
              <p class="text-xs text-gray-400 truncate">{{ r.sublabel }}</p>
            </div>
            <span class="shrink-0 text-[10px] uppercase tracking-wide text-gray-300">{{ r.type }}</span>
          </div>
          <div v-if="!results.length && searchQuery.length > 1" class="px-4 py-3 text-sm text-gray-400">
            No results for "{{ searchQuery }}"
          </div>
        </div>
      </div>
    </div>

    <div class="flex-1" />

    <!-- Notifications -->
    <div class="relative">
      <button
        class="flex h-8 w-8 items-center justify-center rounded-lg text-gray-400 hover:bg-gray-100 hover:text-gray-700 transition-colors"
        @click="notifOpen = !notifOpen"
        @blur="onNotifBlur"
      >
        <FeatherIcon name="bell" class="h-4 w-4" />
      </button>

      <div v-if="notifOpen"
        class="absolute right-0 top-full mt-1 z-50 w-72 rounded-xl border border-gray-200 bg-white shadow-lg overflow-hidden"
      >
        <div class="border-b border-gray-100 px-4 py-2.5 flex items-center justify-between">
          <p class="text-sm font-semibold text-gray-900">Notifications</p>
          <span class="text-xs text-gray-400">Coming soon</span>
        </div>
        <div class="flex flex-col items-center py-8 text-gray-400">
          <FeatherIcon name="bell" class="h-8 w-8 mb-2" />
          <p class="text-sm text-gray-500">No notifications yet</p>
          <p class="text-xs mt-1">Visit alerts and rep activity will appear here</p>
        </div>
      </div>
    </div>

    <!-- Profile menu -->
    <div class="relative">
      <button
        class="flex items-center gap-2 rounded-lg px-2 py-1.5 hover:bg-gray-100 transition-colors"
        @click="profileMenu = !profileMenu"
        @blur="onProfileBlur"
      >
        <div class="flex h-7 w-7 items-center justify-center rounded-full bg-indigo-100 text-xs font-semibold text-indigo-700">
          {{ userInitials }}
        </div>
        <span class="hidden sm:block text-sm font-medium text-gray-700 max-w-[120px] truncate">{{ userFullName }}</span>
        <FeatherIcon name="chevron-down" class="h-3.5 w-3.5 text-gray-400" />
      </button>

      <!-- Dropdown -->
      <div v-if="profileMenu"
        class="absolute right-0 top-full mt-1 z-50 w-56 rounded-xl border border-gray-200 bg-white shadow-lg overflow-hidden"
      >
        <!-- User info -->
        <div class="border-b border-gray-100 px-4 py-3">
          <p class="text-sm font-semibold text-gray-900">{{ userFullName }}</p>
          <p class="text-xs text-gray-400 truncate">{{ userName }}</p>
        </div>

        <!-- Menu items -->
        <div class="py-1">
          <a v-if="auth.isAdmin" href="/app" target="_blank"
            class="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <FeatherIcon name="external-link" class="h-4 w-4 text-gray-400" />
            Frappe Desk
          </a>
          <router-link v-if="auth.canAccess('settings')" to="/settings"
            class="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
            @click="profileMenu = false"
          >
            <FeatherIcon name="settings" class="h-4 w-4 text-gray-400" />
            Settings
          </router-link>
        </div>

        <div class="border-t border-gray-100 py-1">
          <button
            class="flex w-full items-center gap-3 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition-colors"
            @click="logout"
          >
            <FeatherIcon name="log-out" class="h-4 w-4" />
            Log out
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getList } from '@/utils/frappe'
import { auth } from '@/utils/auth'

const router = useRouter()

const searchQuery = ref('')
const showResults = ref(false)
const searching = ref(false)
const results = ref([])
const profileMenu = ref(false)
const notifOpen = ref(false)

function onSearchBlur() { window.setTimeout(() => { showResults.value = false }, 150) }
function onNotifBlur() { window.setTimeout(() => { notifOpen.value = false }, 150) }
function onProfileBlur() { window.setTimeout(() => { profileMenu.value = false }, 150) }

let searchTimeout = null

const userName = window.frappe_boot?.user?.name || ''
const userFullName = window.frappe_boot?.user?.full_name || userName
const userInitials = computed(() =>
  userFullName.split(' ').slice(0, 2).map(w => w[0]?.toUpperCase() || '').join('')
)

function onInput() {
  if (searchTimeout) clearTimeout(searchTimeout)
  if (searchQuery.value.length < 2) { results.value = []; return }
  searchTimeout = window.setTimeout(doSearch, 300)
}

async function doSearch() {
  if (searchQuery.value.length < 2) return
  searching.value = true
  results.value = []
  const q = searchQuery.value

  try {
    const [customers, visits] = await Promise.all([
      getList('Customer', {
        fields: ['name', 'customer_name', 'territory', 'customer_group'],
        filters: { customer_name: ['like', `%${q}%`] },
        limit: 5,
      }),
      getList('SFA Visit', {
        fields: ['name', 'customer', 'visit_date', 'status', 'sales_person'],
        filters: { customer: ['like', `%${q}%`] },
        orderBy: 'visit_date desc',
        limit: 3,
      }),
    ])

    const out = []
    customers.forEach(c => out.push({
      type: 'customer',
      name: c.name,
      label: c.customer_name,
      sublabel: [c.territory, c.customer_group].filter(Boolean).join(' · '),
      route: '/customers/' + c.name,
    }))
    visits.forEach(v => out.push({
      type: 'visit',
      name: v.name,
      label: v.customer,
      sublabel: `${v.name} · ${v.status}`,
      route: '/visits/' + v.name,
    }))
    results.value = out
  } catch (e) {
    console.error('Search failed', e)
  } finally {
    searching.value = false
  }
}

function navigate(r) {
  router.push(r.route)
  searchQuery.value = ''
  results.value = []
  showResults.value = false
}

function search() {
  if (results.value.length) navigate(results.value[0])
}

async function logout() {
  try {
    await fetch('/api/method/logout', {
      method: 'POST',
      headers: { 'X-Frappe-CSRF-Token': window.frappe_boot?.csrf_token || 'fetch' },
      credentials: 'same-origin',
    })
  } catch {}
  window.location.href = '/login'
}
</script>
