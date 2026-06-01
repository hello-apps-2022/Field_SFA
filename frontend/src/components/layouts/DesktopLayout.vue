<template>
  <div class="flex h-screen w-screen overflow-hidden bg-surface-white">

    <!-- Sidebar -->
    <aside
      class="relative flex h-full shrink-0 flex-col border-r border-outline-gray-2 bg-surface-menu-bar transition-all duration-200 ease-in-out"
      :class="collapsed ? 'w-12' : 'w-[220px]'"
    >
      <!-- Logo row -->
      <div class="flex h-16 shrink-0 items-center border-b border-outline-gray-2 px-2.5">
        <img :src="brand.logo" :alt="brand.productName" :class="collapsed ? 'h-8 w-8' : 'h-10 w-10'" class="shrink-0 rounded-xl transition-all duration-200" />
        <div v-show="!collapsed" class="ml-2.5 min-w-0">
          <p class="truncate text-sm font-semibold text-gray-900 leading-tight">{{ brand.productName }}</p>
          <p v-if="brand.tagline" class="truncate text-[11px] text-gray-400 leading-tight">{{ brand.tagline }}</p>
        </div>
        <button
          class="ml-auto flex h-6 w-6 shrink-0 items-center justify-center rounded text-gray-400 hover:bg-gray-100 hover:text-gray-700 transition-colors"
          @click="collapsed = !collapsed"
          :title="collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
        >
          <FeatherIcon :name="collapsed ? 'chevrons-right' : 'chevrons-left'" class="h-3.5 w-3.5" />
        </button>
      </div>

      <!-- Nav -->
      <nav class="flex-1 overflow-y-auto overflow-x-hidden p-1.5">

        <!-- Main nav items -->
        <SidebarLink :item="{ label: 'Dashboard', to: '/dashboard', icon: 'home' }" :collapsed="collapsed" />

        <!-- Divider label -->
        <div v-show="!collapsed" class="px-2 pt-3 pb-1">
          <p class="text-[10px] font-semibold uppercase tracking-wider text-gray-400">Field Ops</p>
        </div>
        <div v-show="collapsed" class="my-2 border-t border-gray-200" />

        <SidebarLink :item="{ label: 'Customers', to: '/customers', icon: 'users' }" :collapsed="collapsed" />
        <SidebarLink :item="{ label: 'Leads', to: '/leads', icon: 'user-plus' }" :collapsed="collapsed" />
        <SidebarLink :item="{ label: 'Visits', to: '/visits', icon: 'map-pin' }" :collapsed="collapsed" />
        <SidebarLink :item="{ label: 'Beat Plans', to: '/beat-plans', icon: 'map' }" :collapsed="collapsed" />
        <SidebarLink :item="{ label: 'Saved Locations', to: '/saved-locations', icon: 'map-pin' }" :collapsed="collapsed" />

        <div v-show="!collapsed" class="px-2 pt-3 pb-1">
          <p class="text-[10px] font-semibold uppercase tracking-wider text-gray-400">Commerce</p>
        </div>
        <div v-show="collapsed" class="my-2 border-t border-gray-200" />

        <SidebarLink :item="{ label: 'Orders', to: '/orders', icon: 'shopping-cart' }" :collapsed="collapsed" />
        <SidebarLink :item="{ label: 'Payments', to: '/payments', icon: 'credit-card' }" :collapsed="collapsed" />
        <SidebarLink :item="{ label: 'Catalog', to: '/catalog', icon: 'package' }" :collapsed="collapsed" />
        <SidebarLink :item="{ label: 'Free Schemes', to: '/schemes', icon: 'gift' }" :collapsed="collapsed" />

        <div v-show="!collapsed" class="px-2 pt-3 pb-1">
          <p class="text-[10px] font-semibold uppercase tracking-wider text-gray-400">Intelligence</p>
        </div>
        <div v-show="collapsed" class="my-2 border-t border-gray-200" />

        <SidebarLink :item="{ label: 'Form Templates', to: '/form-templates', icon: 'file-text' }" :collapsed="collapsed" />
        <SidebarLink :item="{ label: 'Gamification', to: '/gamification', icon: 'award' }" :collapsed="collapsed" />
        <SidebarLink :item="{ label: 'Reports', to: '/reports', icon: 'bar-chart-2' }" :collapsed="collapsed" />
      </nav>

      <!-- Bottom -->
      <div class="shrink-0 border-t border-outline-gray-2 p-1.5 space-y-0.5">
        <SidebarLink :item="{ label: 'Settings', to: '/settings', icon: 'settings' }" :collapsed="collapsed" />
        <a
          href="/app"
          target="_blank"
          class="flex h-8 w-full items-center rounded px-2 text-gray-500 hover:bg-gray-100 hover:text-gray-800 transition-colors"
          :title="collapsed ? 'Frappe Desk' : ''"
        >
          <FeatherIcon name="external-link" class="h-3.5 w-3.5 shrink-0" />
          <span v-show="!collapsed" class="ml-2 truncate text-sm">Frappe Desk</span>
        </a>
      </div>
    </aside>

    <!-- Main content -->
    <div class="flex min-w-0 flex-1 flex-col overflow-hidden">
      <header class="flex h-11 shrink-0 items-center border-b border-outline-gray-2 bg-surface-white px-4 gap-3">
        <span class="text-sm font-medium text-gray-800">{{ pageTitle }}</span>
        <div class="flex-1" />
        <div class="flex items-center gap-2">
          <span class="text-xs text-gray-400">{{ userName }}</span>
          <div class="flex h-7 w-7 items-center justify-center rounded-full bg-gray-200 text-xs font-semibold text-gray-600">
            {{ userName.charAt(0).toUpperCase() }}
          </div>
        </div>
      </header>
      <main class="flex-1 overflow-auto bg-gray-50">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import SidebarLink from './SidebarLink.vue'
import { brand } from '@/utils/brand'

const collapsed = ref(false)
const route = useRoute()

const pageTitleMap = {
  Dashboard: 'Dashboard',
  Customers: 'Customers',
  Visits: 'Visits',
  Visit: 'Visit Detail',
  Orders: 'Orders',
  Payments: 'Payments',
  FormTemplates: 'Form Templates',
  NewFormTemplate: 'New Form Template',
  EditFormTemplate: 'Edit Form Template',
  BeatPlans: 'Beat Plans',
  Gamification: 'Gamification',
  Reports: 'Reports',
  Settings: 'Settings',
  Leads: 'Leads',
  SavedLocations: 'Saved Locations',
  SettingsLocationTypes: 'Location Types',
}

const pageTitle = computed(() => pageTitleMap[route.name] || 'SFA')
const userName = computed(() => (window.frappe?.session?.user || 'User').split('@')[0])
</script>
