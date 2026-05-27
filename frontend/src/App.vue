<template>
  <AppLayout>
    <router-view />
  </AppLayout>

  <!-- Toast notifications -->
  <div class="fixed bottom-6 right-6 z-[9999] flex flex-col gap-2 pointer-events-none">
    <TransitionGroup name="toast">
      <div
        v-for="t in toasts"
        :key="t.id"
        class="pointer-events-auto flex items-center gap-3 rounded-lg border bg-white px-4 py-3 shadow-lg min-w-[280px]"
        :class="{
          'border-green-200': t.type === 'success',
          'border-red-200': t.type === 'error',
          'border-gray-200': t.type === 'info',
        }"
      >
        <FeatherIcon
          :name="t.type === 'success' ? 'check-circle' : t.type === 'error' ? 'alert-circle' : 'info'"
          class="h-4 w-4 shrink-0"
          :class="{
            'text-green-600': t.type === 'success',
            'text-red-600': t.type === 'error',
            'text-blue-600': t.type === 'info',
          }"
        />
        <p class="text-sm text-gray-800 flex-1">{{ t.message }}</p>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import AppLayout from '@/components/layouts/AppLayout.vue'
import { toasts } from '@/utils/toast'
</script>

<style>
.toast-enter-active, .toast-leave-active { transition: all 0.2s ease; }
.toast-enter-from { opacity: 0; transform: translateX(20px); }
.toast-leave-to { opacity: 0; transform: translateX(20px); }
</style>
