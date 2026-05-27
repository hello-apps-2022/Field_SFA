<template>
  <div v-if="!collapsed" class="px-2 pb-1 pt-3">
    <p class="text-[10px] font-semibold uppercase tracking-wider text-gray-400">{{ label }}</p>
  </div>
  <div v-else class="my-1.5 border-t border-gray-200" />
</template>

<script setup>
defineProps({ label: String, collapsed: Boolean })
</script>
