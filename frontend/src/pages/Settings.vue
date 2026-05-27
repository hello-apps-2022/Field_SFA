<template>
  <div class="flex h-full flex-col">
    <PageHeader title="Settings" />
    <div class="flex-1 overflow-auto p-5 max-w-2xl space-y-4">
      <div v-for="s in sections" :key="s.title" class="rounded-xl border border-gray-200 bg-white overflow-hidden shadow-sm">
        <div class="border-b border-gray-100 bg-gray-50 px-4 py-2.5">
          <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-500">{{ s.title }}</p>
        </div>
        <div class="divide-y divide-gray-50">
          <a v-for="item in s.items" :key="item.label" :href="item.href" target="_blank"
            class="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition-colors group">
            <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-gray-100 group-hover:bg-gray-200 transition-colors">
              <FeatherIcon :name="item.icon" class="h-3.5 w-3.5 text-gray-600" />
            </div>
            <div class="flex-1"><p class="text-sm font-medium text-gray-800">{{ item.label }}</p><p class="text-xs text-gray-400">{{ item.desc }}</p></div>
            <FeatherIcon name="external-link" class="h-3.5 w-3.5 text-gray-300 group-hover:text-gray-500 shrink-0" />
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import PageHeader from '@/components/ui/PageHeader.vue'
const sections = [
  { title: 'Field Operations', items: [
    { label: 'Visit Purposes', icon: 'list', desc: 'Visit purpose types', href: '/app/sfa-visit-purpose' },
    { label: 'Activity Types', icon: 'activity', desc: 'Field activity categories', href: '/app/sfa-activity-type' },
    { label: 'Location Types', icon: 'map-pin', desc: 'Outlet / customer location types', href: '/app/sfa-location-type' },
  ]},
  { title: 'Payments', items: [
    { label: 'Payment Types', icon: 'credit-card', desc: 'Cash, cheque, mobile money etc.', href: '/app/sfa-payment-type' },
    { label: 'Amendment Types', icon: 'edit-2', desc: 'Beat plan amendment categories', href: '/app/sfa-amendment-type' },
  ]},
  { title: 'Gamification', items: [
    { label: 'Points Config', icon: 'star', desc: 'Points per activity type', href: '/app/sfa-points-config' },
    { label: 'Badges', icon: 'award', desc: 'Achievement badge definitions', href: '/app/sfa-badge' },
    { label: 'SKU Multipliers', icon: 'package', desc: 'Bonus points per product', href: '/app/sfa-sku-points-multiplier' },
    { label: 'Target Periods', icon: 'calendar', desc: 'Sales target period definitions', href: '/app/sfa-target-period' },
  ]},
  { title: 'Users & Territories', items: [
    { label: 'Users', icon: 'users', desc: 'Manage user accounts and roles', href: '/app/user' },
    { label: 'Territories', icon: 'globe', desc: 'Territory hierarchy', href: '/app/territory' },
    { label: 'Sales Persons', icon: 'user-check', desc: 'Sales person records', href: '/app/sales-person' },
    { label: 'Customer Groups', icon: 'layers', desc: 'Customer classification groups', href: '/app/customer-group' },
  ]},
]
</script>
