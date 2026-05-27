<template>
  <div class="p-6 space-y-6 max-w-2xl">
    <div>
      <h2 class="text-base font-semibold text-ink-gray-9">Settings</h2>
      <p class="text-sm text-ink-gray-5 mt-0.5">Configuration and administration</p>
    </div>

    <div class="space-y-3">
      <div v-for="section in sections" :key="section.title" class="rounded-lg border border-outline-gray-2 overflow-hidden">
        <div class="bg-surface-gray-1 px-4 py-2.5 border-b border-outline-gray-2">
          <p class="text-xs font-semibold text-ink-gray-5 uppercase tracking-wide">{{ section.title }}</p>
        </div>
        <div class="divide-y divide-outline-gray-1">
          <a
            v-for="item in section.items"
            :key="item.label"
            :href="item.href"
            target="_blank"
            class="flex items-center gap-3 px-4 py-3 hover:bg-surface-gray-1 transition-colors group"
          >
            <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-surface-gray-2 group-hover:bg-surface-gray-3 transition-colors">
              <FeatherIcon :name="item.icon" class="h-3.5 w-3.5 text-ink-gray-6" />
            </div>
            <div class="flex-1">
              <p class="text-sm font-medium text-ink-gray-8">{{ item.label }}</p>
              <p class="text-xs text-ink-gray-4">{{ item.description }}</p>
            </div>
            <FeatherIcon name="external-link" class="h-3.5 w-3.5 text-ink-gray-3 group-hover:text-ink-gray-6 transition-colors" />
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
      { label: 'Location Types', icon: 'map-pin', description: 'Outlet/customer location types', href: '/app/sfa-location-type' },
    ],
  },
  {
    title: 'Payments & Orders',
    items: [
      { label: 'Payment Types', icon: 'credit-card', description: 'Cash, cheque, mobile money etc.', href: '/app/sfa-payment-type' },
      { label: 'Amendment Types', icon: 'edit', description: 'Beat plan amendment categories', href: '/app/sfa-amendment-type' },
    ],
  },
  {
    title: 'Gamification',
    items: [
      { label: 'Points Config', icon: 'star', description: 'Points per activity type', href: '/app/sfa-points-config' },
      { label: 'Badges', icon: 'award', description: 'Achievement badge definitions', href: '/app/sfa-badge' },
      { label: 'SKU Points Multipliers', icon: 'package', description: 'Extra points per product', href: '/app/sfa-sku-points-multiplier' },
      { label: 'Target Periods', icon: 'calendar', description: 'Sales target periods', href: '/app/sfa-target-period' },
    ],
  },
  {
    title: 'Users & Territories',
    items: [
      { label: 'Users', icon: 'users', description: 'Manage SFA user accounts', href: '/app/user' },
      { label: 'Territories', icon: 'globe', description: 'Territory hierarchy', href: '/app/territory' },
      { label: 'Sales Persons', icon: 'user-check', description: 'Sales person records', href: '/app/sales-person' },
      { label: 'Customer Groups', icon: 'layers', description: 'Customer classification', href: '/app/customer-group' },
    ],
  },
]
</script>
