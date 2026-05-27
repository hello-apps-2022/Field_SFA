<template>
  <FrappeUIProvider>
    <DesktopLayout>
      <router-view :key="$route.fullPath" />
    </DesktopLayout>
  </FrappeUIProvider>
</template>

<script setup>
import DesktopLayout from '@/components/layouts/DesktopLayout.vue'
import { FrappeUIProvider, setConfig } from 'frappe-ui'

setConfig('systemTimezone', window.timezone?.system || null)
setConfig('localTimezone', window.timezone?.user || null)
</script>
