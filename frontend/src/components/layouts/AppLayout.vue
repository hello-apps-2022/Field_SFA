<template>
  <div class="flex h-screen w-screen overflow-hidden bg-white">
    <aside
      class="flex h-full shrink-0 flex-col border-r border-gray-100 bg-gray-50 z-20 relative transition-[width] duration-200 ease-in-out"
      :class="isExpanded ? 'w-[220px]' : 'w-[52px]'"
      @mouseenter="hovering = true"
      @mouseleave="hovering = false"
    >
      <!-- Brand -->
      <div class="flex h-16 shrink-0 items-center border-b border-gray-100 px-2.5 gap-2.5 overflow-hidden">
        <img :src="brand.logo" :alt="brand.productName" :class="isExpanded ? 'h-10 w-10' : 'h-8 w-8'" class="shrink-0 rounded-xl transition-all duration-200" />

        <Transition name="fade-left">
          <div v-if="isExpanded" class="flex-1 min-w-0">
            <p class="truncate text-sm font-semibold text-gray-900 leading-tight whitespace-nowrap">{{ brand.productName }}</p>
            <p v-if="brand.tagline" class="truncate text-[11px] text-gray-400 leading-tight whitespace-nowrap">{{ brand.tagline }}</p>
          </div>
        </Transition>

        <!-- Pin/unpin button — only show when expanded -->
        <Transition name="fade-left">
          <button v-if="isExpanded"
            class="flex h-7 w-7 shrink-0 items-center justify-center rounded-md text-gray-400 hover:bg-gray-200 hover:text-gray-700 transition-colors"
            :title="collapsed ? 'Pin sidebar open' : 'Collapse sidebar'"
            @click="togglePin"
          >
            <FeatherIcon :name="collapsed ? 'chevrons-right' : 'chevrons-left'" class="h-3.5 w-3.5" />
          </button>
        </Transition>
      </div>

      <!-- Nav -->
      <nav class="flex-1 overflow-y-auto overflow-x-hidden py-2 px-1.5 space-y-0.5">
        <NavLink :item="{ label: 'Dashboard', to: '/dashboard', icon: 'home' }" :collapsed="!isExpanded" />

        <NavSection label="Field Ops" :collapsed="!isExpanded" />
        <NavLink :item="{ label: 'Customers', to: '/customers', icon: 'users' }" :collapsed="!isExpanded" />
        <NavLink :item="{ label: 'Visits', to: '/visits', icon: 'map-pin' }" :collapsed="!isExpanded" />
        <NavLink :item="{ label: 'Beat Plans', to: '/beat-plans', icon: 'map' }" :collapsed="!isExpanded" />

        <NavSection label="Commerce" :collapsed="!isExpanded" />
        <NavLink :item="{ label: 'Orders', to: '/orders', icon: 'shopping-cart' }" :collapsed="!isExpanded" />
        <NavLink :item="{ label: 'Payments', to: '/payments', icon: 'credit-card' }" :collapsed="!isExpanded" />

        <NavSection label="Workforce" :collapsed="!isExpanded" />
        <NavLink :item="{ label: 'Expenses', to: '/expenses', icon: 'receipt' }" :collapsed="!isExpanded" />
        <NavLink :item="{ label: 'Leave', to: '/leave', icon: 'calendar' }" :collapsed="!isExpanded" />
        <NavLink :item="{ label: 'Attendance', to: '/attendance', icon: 'clock' }" :collapsed="!isExpanded" />
        <NavLink v-if="auth.canAccess('attendance-report')" :item="{ label: 'Attendance Report', to: '/attendance-report', icon: 'user-check' }" :collapsed="!isExpanded" />

        <!-- Approvals submenu (managers/admins only) -->
        <NavGroup
          v-if="auth.isManager || auth.isAdmin"
          label="Approvals"
          icon="check-square"
          :sidebar-collapsed="!isExpanded"
          :paths="['/approvals/expenses', '/approvals/leave']"
          :item-count="2"
        >
          <template #preview>
            <router-link to="/approvals/expenses"
              class="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50">
              <FeatherIcon name="receipt" class="h-3.5 w-3.5 text-gray-400" />
              Expense Approvals
            </router-link>
            <router-link to="/approvals/leave"
              class="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50">
              <FeatherIcon name="calendar" class="h-3.5 w-3.5 text-gray-400" />
              Leave Approvals
            </router-link>
          </template>
          <NavLink :item="{ label: 'Expense Approvals', to: '/approvals/expenses', icon: 'receipt' }" :collapsed="!isExpanded" />
          <NavLink :item="{ label: 'Leave Approvals', to: '/approvals/leave', icon: 'calendar' }" :collapsed="!isExpanded" />
        </NavGroup>

        <NavSection label="Intelligence" :collapsed="!isExpanded" />
        <NavLink v-if="auth.canAccess('form-templates')" :item="{ label: 'Form Templates', to: '/form-templates', icon: 'file-text' }" :collapsed="!isExpanded" />
        <NavLink v-if="auth.canAccess('gamification')" :item="{ label: 'Gamification', to: '/gamification', icon: 'award' }" :collapsed="!isExpanded" />
        <NavLink v-if="auth.canAccess('reports')" :item="{ label: 'Reports', to: '/reports', icon: 'bar-chart-2' }" :collapsed="!isExpanded" />
        <NavLink v-if="auth.canAccess('territory-dashboard')" :item="{ label: 'Territory', to: '/territory-dashboard', icon: 'map-pin' }" :collapsed="!isExpanded" />

        <!-- Targets submenu -->
        <NavGroup
          v-if="auth.canAccess('targets')"
          label="Targets"
          icon="target"
          :sidebar-collapsed="!isExpanded"
          :paths="['/targets']"
          :item-count="2"
        >
          <template #preview>
            <router-link to="/targets"
              class="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50">
              <FeatherIcon name="sliders" class="h-3.5 w-3.5 text-gray-400" />
              Set Targets
            </router-link>
            <router-link to="/targets/performance"
              class="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50">
              <FeatherIcon name="trending-up" class="h-3.5 w-3.5 text-gray-400" />
              Performance
            </router-link>
          </template>
          <NavLink :item="{ label: 'Set Targets', to: '/targets', icon: 'sliders' }" :collapsed="!isExpanded" />
          <NavLink :item="{ label: 'Performance', to: '/targets/performance', icon: 'trending-up' }" :collapsed="!isExpanded" />
        </NavGroup>

        <NavSection label="Maps" :collapsed="!isExpanded" />
        <NavLink v-if="auth.canAccess('rep-activity-map')" :item="{ label: 'Rep Activity', to: '/rep-activity-map', icon: 'activity' }" :collapsed="!isExpanded" />
        <NavLink v-if="auth.canAccess('customer-map')" :item="{ label: 'Customer Map', to: '/customer-map', icon: 'globe' }" :collapsed="!isExpanded" />
      </nav>

      <!-- Bottom -->
      <div class="shrink-0 border-t border-gray-100 py-2 px-1.5 space-y-0.5">
        <NavLink v-if="auth.canAccess('settings')" :item="{ label: 'Settings', to: '/settings', icon: 'settings' }" :collapsed="!isExpanded" />
        <a v-if="auth.isAdmin" href="/app" target="_blank"
          class="flex h-8 w-full items-center rounded-md px-2 text-gray-500 hover:bg-gray-200 hover:text-gray-800 overflow-hidden"
          :title="!isExpanded ? 'Frappe Desk' : ''">
          <FeatherIcon name="external-link" class="h-3.5 w-3.5 shrink-0" />
          <Transition name="fade-left">
            <span v-if="isExpanded" class="ml-2 truncate text-sm whitespace-nowrap">Frappe Desk</span>
          </Transition>
        </a>
      </div>
    </aside>

    <div class="flex min-w-0 flex-1 flex-col overflow-hidden">
      <TopBar />
      <main class="flex min-w-0 flex-1 flex-col overflow-hidden">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import NavLink from './NavLink.vue'
import NavSection from './NavSection.vue'
import NavGroup from './NavGroup.vue'
import TopBar from './TopBar.vue'
import { auth as _auth } from '@/utils/auth'
import { brand } from '@/utils/brand'

// collapsed = pinned state (persisted)
// hovering = temporary hover expansion
const collapsed = ref(false)
const hovering = ref(false)

// Sidebar is visually expanded if pinned open OR if hovering while collapsed
const isExpanded = computed(() => !collapsed.value || hovering.value)

function togglePin() {
  if (collapsed.value) {
    // Was collapsed/pinned-closed → pin open
    collapsed.value = false
  } else {
    // Was pinned open → pin closed
    collapsed.value = true
    hovering.value = false
  }
}

const auth = _auth
</script>

<style scoped>
.fade-left-enter-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
  transition-delay: 0.05s; /* slight delay so width animation leads */
}
.fade-left-leave-active {
  transition: opacity 0.08s ease;
}
.fade-left-enter-from {
  opacity: 0;
  transform: translateX(-4px);
}
.fade-left-leave-to {
  opacity: 0;
}
</style>
