<template>
  <DesktopLayout>
    <router-view :key="$route.fullPath" />
  </DesktopLayout>
</template>

<script setup>
import DesktopLayout from '@/components/layouts/DesktopLayout.vue'
</script>
