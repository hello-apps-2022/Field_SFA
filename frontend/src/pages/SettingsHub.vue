<template>
  <div class="flex h-full flex-col overflow-hidden">
    <div class="flex h-[52px] shrink-0 items-center border-b border-gray-100 bg-white px-5">
      <h1 class="text-sm font-semibold text-gray-900">Settings</h1>
    </div>

    <div class="flex-1 overflow-y-auto bg-gray-50 p-6">
      <div class="max-w-2xl mx-auto space-y-3">

        <div v-for="section in sections" :key="section.title">
          <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400 px-1 mb-2">
            {{ section.title }}
          </p>
          <div class="rounded-xl border border-gray-200 bg-white overflow-hidden divide-y divide-gray-100">
            <router-link v-for="item in section.items" :key="item.to"
              :to="item.to"
              class="flex items-center gap-4 px-4 py-4 hover:bg-gray-50 transition-colors group"
            >
              <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg"
                :class="item.iconBg">
                <FeatherIcon :name="item.icon" class="h-4 w-4" :class="item.iconColor" />
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-gray-900">{{ item.label }}</p>
                <p class="text-xs text-gray-400 mt-0.5">{{ item.desc }}</p>
              </div>
              <FeatherIcon name="chevron-right" class="h-4 w-4 text-gray-300 group-hover:text-gray-500 transition-colors shrink-0" />
            </router-link>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import FeatherIcon from '@/components/ui/FeatherIcon.vue'

const sections = [
  {
    title: 'People',
    items: [
      {
        to: '/settings/team',
        label: 'Team',
        desc: 'Manage reps, managers and admins. Set roles, territories and reporting lines.',
        icon: 'users',
        iconBg: 'bg-indigo-50',
        iconColor: 'text-indigo-600',
      },
      {
        to: '/settings/territories',
        label: 'Territories',
        desc: 'Create and manage sales territories. Build the territory hierarchy.',
        icon: 'map-pin',
        iconBg: 'bg-green-50',
        iconColor: 'text-green-600',
      },
    ],
  },
  {
    title: 'Operations',
    items: [
      {
        to: '/settings/import-outlets',
        label: 'Import Outlets',
        desc: 'Bulk-import outlets from a CSV. Download a template, upload, and review results.',
        icon: 'upload',
        iconBg: 'bg-blue-50',
        iconColor: 'text-blue-600',
      },
      {
        to: '/settings/beat-plan-permissions',
        label: 'Beat Plan Permissions',
        desc: 'Control whether reps can create their own beat plans.',
        icon: 'map',
        iconBg: 'bg-amber-50',
        iconColor: 'text-amber-600',
      },
    ],
  },
  {
    title: 'System',
    items: [
      {
        to: '/app',
        label: 'Frappe Desk',
        desc: 'Advanced configuration, custom fields, system settings and more.',
        icon: 'external-link',
        iconBg: 'bg-gray-100',
        iconColor: 'text-gray-500',
      },
    ],
  },
]
</script>
