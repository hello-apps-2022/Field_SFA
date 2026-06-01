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

        <div v-if="auth.isAdmin || auth.isManager">
          <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400 px-1 mb-2">Policies</p>
          <div class="rounded-xl border border-gray-200 bg-white overflow-hidden">
            <label class="flex items-center gap-4 px-4 py-4 cursor-pointer">
              <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-pink-50">
                <FeatherIcon name="gift" class="h-4 w-4 text-pink-600" />
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-gray-900">Discretionary free cartons</p>
                <p class="text-xs text-gray-400 mt-0.5">Let reps mark any order line free without a matching scheme.</p>
              </div>
              <input type="checkbox" v-model="allowFree" @change="saveFreePolicy" class="h-4 w-4 rounded border-gray-300" />
            </label>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import FeatherIcon from '@/components/ui/FeatherIcon.vue'
import { call } from '@/utils/frappe'
import { auth } from '@/utils/auth'
import { successToast, errorToast } from '@/utils/toast'

const allowFree = ref(auth.allowDiscretionaryFree)
async function saveFreePolicy() {
  try {
    await call('sfa_core.field_sfa.api.free_carton.set_free_carton_policy', { allow: allowFree.value ? 1 : 0 })
    if (window.frappe_boot && window.frappe_boot.sfa) window.frappe_boot.sfa.allow_discretionary_free = allowFree.value ? 1 : 0
    successToast(allowFree.value ? 'Reps can now give free cartons at will' : 'Discretionary free cartons disabled')
  } catch (e) { errorToast(e.message || 'Failed to save'); allowFree.value = !allowFree.value }
}

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
      {
        to: '/settings/location-types',
        label: 'Location Types',
        desc: 'Manage the categories for saved GPS locations (customer, warehouse, competitor…).',
        icon: 'tag',
        iconBg: 'bg-teal-50',
        iconColor: 'text-teal-600',
      },
    ],
  },
  {
    title: 'Commerce',
    items: [
      {
        to: '/catalog',
        label: 'Catalog',
        desc: 'Define companies, product categories and products. Set prices.',
        icon: 'package',
        iconBg: 'bg-purple-50',
        iconColor: 'text-purple-600',
      },
      {
        to: '/schemes',
        label: 'Free Schemes',
        desc: 'Buy-X-get-Y free carton schemes per customer or territory.',
        icon: 'gift',
        iconBg: 'bg-pink-50',
        iconColor: 'text-pink-600',
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
