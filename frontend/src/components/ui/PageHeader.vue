<template>
  <div class="flex h-[52px] shrink-0 items-center border-b border-gray-100 bg-white px-4 gap-3">
    <!-- Breadcrumb -->
    <div class="flex items-center gap-2 min-w-0 flex-1">
      <router-link
        v-if="backTo"
        :to="backTo"
        class="text-sm text-gray-500 hover:text-gray-800 transition-colors truncate"
      >
        {{ backLabel }}
      </router-link>
      <FeatherIcon v-if="backTo" name="chevron-right" class="h-3.5 w-3.5 shrink-0 text-gray-300" />
      <h1 class="truncate text-sm font-semibold text-gray-900">{{ title }}</h1>
    </div>

    <!-- Right actions slot -->
    <div class="flex shrink-0 items-center gap-2">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  backTo: String,
  backLabel: String,
})
</script>
