<template>
  <div class="p-6 space-y-6 max-w-2xl">
    <div>
      <h2 class="text-base font-semibold text-gray-900">Settings</h2>
      <p class="text-sm text-gray-500 mt-0.5">Configuration and administration — opens in Frappe desk</p>
    </div>

    <div class="space-y-4">
      <div v-for="section in sections" :key="section.title" class="rounded-xl border border-gray-200 bg-white overflow-hidden shadow-sm">
        <div class="border-b border-gray-100 bg-gray-50 px-4 py-2.5">
          <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">{{ section.title }}</p>
        </div>
        <div class="divide-y divide-gray-100">
          <a
            v-for="item in section.items"
            :key="item.label"
            :href="item.href"
            target="_blank"
            class="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition-colors group"
          >
            <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gray-100 group-hover:bg-gray-200 transition-colors">
              <FeatherIcon :name="item.icon" class="h-3.5 w-3.5 text-gray-600" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-800">{{ item.label }}</p>
              <p class="text-xs text-gray-400 truncate">{{ item.description }}</p>
            </div>
            <FeatherIcon name="external-link" class="h-3.5 w-3.5 text-gray-300 group-hover:text-gray-500 transition-colors shrink-0" />
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const sections = [
  {
    title: 'Field Operations',
    items: [
      { label: 'Visit Purposes', icon: 'list', description: 'Define visit purpose types', href: '/app/sfa-visit-purpose' },
      { label: 'Activity Types', icon: 'activity', description: 'Field activity categories', href: '/app/sfa-activity-type' },
      { label: 'Location Types', icon: 'map-pin', description: 'Outlet / customer location types', href: '/app/sfa-location-type' },
    ],
  },
  {
    title: 'Payments & Amendments',
    items: [
      { label: 'Payment Types', icon: 'credit-card', description: 'Cash, cheque, mobile money etc.', href: '/app/sfa-payment-type' },
      { label: 'Amendment Types', icon: 'edit', description: 'Beat plan amendment categories', href: '/app/sfa-amendment-type' },
      { label: 'Share Types', icon: 'share-2', description: 'Customer share transfer types', href: '/app/sfa-share-type' },
    ],
  },
  {
    title: 'Gamification',
    items: [
      { label: 'Points Config', icon: 'star', description: 'Points awarded per activity type', href: '/app/sfa-points-config' },
      { label: 'Badges', icon: 'award', description: 'Achievement badge definitions', href: '/app/sfa-badge' },
      { label: 'SKU Points Multipliers', icon: 'package', description: 'Bonus points per product', href: '/app/sfa-sku-points-multiplier' },
      { label: 'Target Periods', icon: 'calendar', description: 'Sales target period definitions', href: '/app/sfa-target-period' },
    ],
  },
  {
    title: 'Users & Territories',
    items: [
      { label: 'Users', icon: 'users', description: 'Manage user accounts and roles', href: '/app/user' },
      { label: 'Territories', icon: 'globe', description: 'Territory hierarchy', href: '/app/territory' },
      { label: 'Sales Persons', icon: 'user-check', description: 'Sales person records', href: '/app/sales-person' },
      { label: 'Customer Groups', icon: 'layers', description: 'Customer classification groups', href: '/app/customer-group' },
    ],
  },
]
</script>
