<template>
  <div class="flex h-full flex-col overflow-hidden">
    <div class="flex h-[52px] shrink-0 items-center gap-3 border-b border-gray-100 bg-white px-5">
      <router-link to="/settings" class="flex h-7 w-7 items-center justify-center rounded-md text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-700">
        <FeatherIcon name="chevron-left" class="h-4 w-4" />
      </router-link>
      <h1 class="text-sm font-semibold text-gray-900">Import Outlets</h1>
    </div>

    <div class="flex-1 overflow-y-auto bg-gray-50">
      <ImportOutlets />
    </div>
  </div>
</template>

<script setup>
import FeatherIcon from '@/components/ui/FeatherIcon.vue'
import ImportOutlets from '@/components/ui/ImportOutlets.vue'
</script>
