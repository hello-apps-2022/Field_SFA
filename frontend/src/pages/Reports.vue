<template>
  <div class="flex h-full flex-col">
    <PageHeader title="Reports" />
    <div class="flex-1 overflow-auto p-5">
      <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <a v-for="r in reports" :key="r.name" :href="`/app/query-report/${encodeURIComponent(r.name)}`" target="_blank"
          class="group flex items-start gap-4 rounded-xl border border-gray-200 bg-white p-4 shadow-sm hover:shadow-md hover:border-gray-300 transition-all">
          <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg" :class="r.color">
            <FeatherIcon :name="r.icon" class="h-4 w-4 text-white" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">{{ r.name }}</p>
            <p class="text-xs text-gray-400 mt-0.5">{{ r.desc }}</p>
          </div>
          <FeatherIcon name="external-link" class="h-3.5 w-3.5 shrink-0 text-gray-300 group-hover:text-blue-500 transition-colors mt-0.5" />
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import PageHeader from '@/components/ui/PageHeader.vue'
const reports = [
  { name: 'Form Completion Rate', icon: 'check-circle', color: 'bg-green-500', desc: 'Completion % by rep, template, date range' },
  { name: 'Response By Question', icon: 'help-circle', color: 'bg-blue-500', desc: 'Per-question trends, top answers, skip rates' },
  { name: 'Outlet Feedback Summary', icon: 'map-pin', color: 'bg-purple-500', desc: 'Forms submitted per customer and territory' },
  { name: 'Rep Survey Activity', icon: 'user', color: 'bg-orange-500', desc: 'Monthly/weekly form submission by rep' },
  { name: 'Option Distribution', icon: 'pie-chart', color: 'bg-teal-500', desc: 'MCQ answer breakdown per question' },
  { name: 'Beat Plan Survey Coverage', icon: 'map', color: 'bg-red-500', desc: 'Form coverage per route and territory' },
  { name: 'Visit Compliance', icon: 'activity', color: 'bg-indigo-500', desc: 'Beat plan adherence and visit completion' },
  { name: 'Rep Productivity', icon: 'trending-up', color: 'bg-emerald-500', desc: 'Orders, payments and visits per rep' },
  { name: 'Sales Performance', icon: 'bar-chart-2', color: 'bg-slate-500', desc: 'Revenue and order performance by territory' },
  { name: 'Leaderboard', icon: 'award', color: 'bg-yellow-500', desc: 'Gamification points and badges ranking' },
]
</script>
