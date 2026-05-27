<template>
  <div class="p-6 space-y-6">
    <div>
      <h2 class="text-base font-semibold text-ink-gray-9">Reports</h2>
      <p class="text-sm text-ink-gray-5 mt-0.5">Open any report in the Frappe desk report builder</p>
    </div>

    <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
      <a
        v-for="report in reports"
        :key="report.name"
        :href="`/app/query-report/${encodeURIComponent(report.name)}`"
        target="_blank"
        class="group flex items-start gap-4 rounded-lg border border-outline-gray-2 bg-surface-white p-4 hover:border-outline-gray-4 hover:shadow-sm transition-all"
      >
        <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg" :class="report.color">
          <FeatherIcon :name="report.icon" class="h-4 w-4 text-white" />
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-semibold text-ink-gray-9 group-hover:text-ink-blue-4 transition-colors">{{ report.name }}</p>
          <p class="text-xs text-ink-gray-4 mt-0.5">{{ report.description }}</p>
        </div>
        <FeatherIcon name="external-link" class="h-3.5 w-3.5 text-ink-gray-3 group-hover:text-ink-blue-4 shrink-0 mt-0.5 transition-colors" />
      </a>
    </div>
  </div>
</template>

<script setup>
const reports = [
  { name: 'Form Completion Rate', icon: 'check-circle', color: 'bg-green-500', description: 'Completion % by rep, by template, by date range' },
  { name: 'Response By Question', icon: 'help-circle', color: 'bg-blue-500', description: 'Per-question trends, top answers, skip rates' },
  { name: 'Outlet Feedback Summary', icon: 'map-pin', color: 'bg-purple-500', description: 'Forms submitted per customer and territory' },
  { name: 'Rep Survey Activity', icon: 'user', color: 'bg-orange-500', description: 'Monthly/weekly form submission by rep' },
  { name: 'Option Distribution', icon: 'pie-chart', color: 'bg-teal-500', description: 'MCQ answer breakdown per question' },
  { name: 'Beat Plan Survey Coverage', icon: 'map', color: 'bg-red-500', description: 'Form coverage per route and territory' },
  { name: 'Visit Compliance', icon: 'activity', color: 'bg-indigo-500', description: 'Beat plan adherence and visit completion' },
  { name: 'Rep Productivity', icon: 'trending-up', color: 'bg-emerald-500', description: 'Orders, payments and visits per rep' },
  { name: 'Sales Performance', icon: 'bar-chart-2', color: 'bg-slate-500', description: 'Revenue and order performance by territory' },
  { name: 'Leaderboard', icon: 'award', color: 'bg-yellow-500', description: 'Gamification points and badges ranking' },
]
</script>
