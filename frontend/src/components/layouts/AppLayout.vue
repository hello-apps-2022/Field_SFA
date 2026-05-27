<template>
  <div class="flex h-screen w-screen overflow-hidden bg-white">
    <aside
      class="flex h-full shrink-0 flex-col border-r border-gray-100 bg-gray-50 transition-[width] duration-200 z-20 relative"
      :class="collapsed ? 'w-[52px]' : 'w-[220px]'"
    >
      <!-- Brand -->
      <div class="flex h-[52px] shrink-0 items-center border-b border-gray-100 px-3 gap-2">
        <template v-if="!collapsed">
          <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-gray-900 text-white">
            <span class="text-[11px] font-bold">S</span>
          </div>
          <span class="flex-1 truncate text-sm font-semibold text-gray-900">Hema SFA</span>
          <button class="flex h-7 w-7 shrink-0 items-center justify-center rounded-md text-gray-400 hover:bg-gray-200 hover:text-gray-700 transition-colors"
            @click="collapsed = true">
            <FeatherIcon name="chevrons-left" class="h-3.5 w-3.5" />
          </button>
        </template>
        <template v-else>
          <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-gray-900 text-white">
            <span class="text-[11px] font-bold">S</span>
          </div>
          <button class="flex h-7 w-7 shrink-0 items-center justify-center rounded-md text-gray-400 hover:bg-gray-200 hover:text-gray-700 transition-colors"
            @click="collapsed = false">
            <FeatherIcon name="chevrons-right" class="h-3.5 w-3.5" />
          </button>
        </template>
      </div>

      <!-- Nav -->
      <nav class="flex-1 overflow-y-auto overflow-x-hidden py-2 px-1.5 space-y-0.5">
        <NavLink :item="{ label: 'Dashboard', to: '/dashboard', icon: 'home' }" :collapsed="collapsed" />

        <NavSection label="Field Ops" :collapsed="collapsed" />
        <NavLink :item="{ label: 'Customers', to: '/customers', icon: 'users' }" :collapsed="collapsed" />
        <NavLink :item="{ label: 'Visits', to: '/visits', icon: 'map-pin' }" :collapsed="collapsed" />
        <NavLink :item="{ label: 'Beat Plans', to: '/beat-plans', icon: 'map' }" :collapsed="collapsed" />

        <NavSection label="Commerce" :collapsed="collapsed" />
        <NavLink :item="{ label: 'Orders', to: '/orders', icon: 'shopping-cart' }" :collapsed="collapsed" />
        <NavLink :item="{ label: 'Payments', to: '/payments', icon: 'credit-card' }" :collapsed="collapsed" />

        <NavSection label="Intelligence" :collapsed="collapsed" />
        <NavLink v-if="auth.canAccess('form-templates')" :item="{ label: 'Form Templates', to: '/form-templates', icon: 'file-text' }" :collapsed="collapsed" />
        <NavLink v-if="auth.canAccess('gamification')" :item="{ label: 'Gamification', to: '/gamification', icon: 'award' }" :collapsed="collapsed" />
        <NavLink v-if="auth.canAccess('reports')" :item="{ label: 'Reports', to: '/reports', icon: 'bar-chart-2' }" :collapsed="collapsed" />
        <NavLink v-if="auth.canAccess('territory-dashboard')" :item="{ label: 'Territory', to: '/territory-dashboard', icon: 'map-pin' }" :collapsed="collapsed" />

        <!-- Targets submenu -->
        <NavGroup
          v-if="auth.canAccess('targets')"
          label="Targets"
          icon="target"
          :sidebar-collapsed="collapsed"
          :paths="['/targets']"
          :item-count="2"
        >
          <!-- Preview shown on hover when collapsed -->
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
          <!-- Actual nav links -->
          <NavLink :item="{ label: 'Set Targets', to: '/targets', icon: 'sliders' }" :collapsed="collapsed" />
          <NavLink :item="{ label: 'Performance', to: '/targets/performance', icon: 'trending-up' }" :collapsed="collapsed" />
        </NavGroup>

        <NavSection label="Maps" :collapsed="collapsed" />
        <NavLink v-if="auth.canAccess('rep-activity-map')" :item="{ label: 'Rep Activity', to: '/rep-activity-map', icon: 'activity' }" :collapsed="collapsed" />
        <NavLink v-if="auth.canAccess('customer-map')" :item="{ label: 'Customer Map', to: '/customer-map', icon: 'globe' }" :collapsed="collapsed" />
      </nav>

      <!-- Bottom -->
      <div class="shrink-0 border-t border-gray-100 py-2 px-1.5 space-y-0.5">
        <NavLink v-if="auth.canAccess('settings')" :item="{ label: 'Settings', to: '/settings', icon: 'settings' }" :collapsed="collapsed" />
        <a href="/app" target="_blank"
          class="flex h-8 w-full items-center rounded-md px-2 text-gray-500 hover:bg-gray-200 hover:text-gray-800"
          :title="collapsed ? 'Frappe Desk' : ''">
          <FeatherIcon name="external-link" class="h-3.5 w-3.5 shrink-0" />
          <Transition name="fade-left">
            <span v-if="!collapsed" class="ml-2 truncate text-sm">Frappe Desk</span>
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
import { ref } from 'vue'
import NavLink from './NavLink.vue'
import NavSection from './NavSection.vue'
import NavGroup from './NavGroup.vue'
import TopBar from './TopBar.vue'
import { auth as _auth } from '@/utils/auth'

const collapsed = ref(false)
const auth = _auth
</script>

<style scoped>
.fade-left-enter-active, .fade-left-leave-active { transition: opacity 0.15s ease; }
.fade-left-enter-from, .fade-left-leave-to { opacity: 0; }
</style>
