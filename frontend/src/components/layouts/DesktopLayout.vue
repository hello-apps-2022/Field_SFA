<template>
  <div class="flex h-screen w-screen overflow-hidden bg-surface-white">
    <!-- Sidebar -->
    <aside
      class="flex h-full flex-col border-r border-outline-gray-2 bg-surface-menu-bar transition-all duration-200"
      :class="collapsed ? 'w-12' : 'w-[220px]'"
    >
      <!-- Logo + App name -->
      <div class="flex h-12 items-center gap-2.5 px-3 border-b border-outline-gray-2">
        <div class="flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-ink-gray-9">
          <span class="text-xs font-bold text-white">S</span>
        </div>
        <span v-if="!collapsed" class="text-sm font-semibold text-ink-gray-9 truncate">
          Hema SFA
        </span>
        <button
          class="ml-auto flex h-5 w-5 items-center justify-center rounded text-ink-gray-4 hover:text-ink-gray-7 hover:bg-surface-gray-2"
          @click="collapsed = !collapsed"
        >
          <FeatherIcon :name="collapsed ? 'chevrons-right' : 'chevrons-left'" class="h-3.5 w-3.5" />
        </button>
      </div>

      <!-- Nav items -->
      <nav class="flex-1 overflow-y-auto p-1.5 space-y-0.5">
        <SidebarLink
          v-for="item in navItems"
          :key="item.to"
          :item="item"
          :collapsed="collapsed"
        />
      </nav>

      <!-- Bottom actions -->
      <div class="p-1.5 border-t border-outline-gray-2 space-y-0.5">
        <SidebarLink
          :item="{ label: 'Settings', to: '/settings', icon: 'settings' }"
          :collapsed="collapsed"
        />
        <a
          href="/app"
          target="_blank"
          class="flex h-8 w-full items-center gap-2.5 rounded px-2 text-ink-gray-5 hover:bg-surface-gray-2 hover:text-ink-gray-8 transition-colors"
          :title="collapsed ? 'Frappe Desk' : ''"
        >
          <FeatherIcon name="external-link" class="h-3.5 w-3.5 shrink-0" />
          <span v-if="!collapsed" class="text-sm truncate">Frappe Desk</span>
        </a>
      </div>
    </aside>

    <!-- Main content -->
    <div class="flex flex-1 flex-col min-w-0 overflow-hidden">
      <!-- Top bar -->
      <header class="flex h-12 shrink-0 items-center gap-3 border-b border-outline-gray-2 px-4">
        <h1 class="text-sm font-medium text-ink-gray-9">{{ pageTitle }}</h1>
        <div class="flex-1" />
        <div class="flex items-center gap-2">
          <span class="text-xs text-ink-gray-4">{{ userName }}</span>
          <Avatar
            :label="userName"
            :image="userImage"
            size="sm"
          />
        </div>
      </header>

      <!-- Page content -->
      <main class="flex-1 overflow-auto">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import SidebarLink from './SidebarLink.vue'

const collapsed = ref(false)
const route = useRoute()

const navItems = [
  { label: 'Dashboard', to: '/dashboard', icon: 'home' },
  { label: 'Visits', to: '/visits', icon: 'map-pin' },
  { label: 'Form Templates', to: '/form-templates', icon: 'file-text' },
  { label: 'Beat Plans', to: '/beat-plans', icon: 'map' },
  { label: 'Orders', to: '/orders', icon: 'shopping-cart' },
  { label: 'Reports', to: '/reports', icon: 'bar-chart-2' },
]

const pageTitleMap = {
  Dashboard: 'Dashboard',
  Visits: 'Visits',
  Visit: 'Visit Detail',
  FormTemplates: 'Form Templates',
  NewFormTemplate: 'New Form Template',
  EditFormTemplate: 'Edit Form Template',
  BeatPlans: 'Beat Plans',
  Orders: 'Orders',
  Reports: 'Reports',
  Settings: 'Settings',
}

const pageTitle = computed(() => pageTitleMap[route.name] || 'SFA')
const userName = computed(() => window.frappe?.session?.user?.split('@')[0] || 'User')
const userImage = computed(() => window.frappe?.session?.user_image || null)
</script>
