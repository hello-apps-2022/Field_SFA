<template>
  <Teleport to="body">
    <!-- Backdrop -->
    <Transition name="fade">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-40 bg-black/20"
        @click="$emit('update:modelValue', false)"
      />
    </Transition>

    <!-- Panel -->
    <Transition name="slide">
      <div
        v-if="modelValue"
        class="fixed right-0 top-0 z-50 flex h-full flex-col bg-white shadow-2xl"
        :style="{ width: width }"
      >
        <!-- Header -->
        <div class="flex h-12 shrink-0 items-center justify-between border-b border-gray-200 px-5">
          <h2 class="text-sm font-semibold text-gray-900">{{ title }}</h2>
          <button
            class="flex h-7 w-7 items-center justify-center rounded-md text-gray-400 hover:bg-gray-100 hover:text-gray-700 transition-colors"
            @click="$emit('update:modelValue', false)"
          >
            <FeatherIcon name="x" class="h-4 w-4" />
          </button>
        </div>

        <!-- Content (scrollable) -->
        <div class="flex-1 overflow-y-auto px-5 py-4">
          <slot />
        </div>

        <!-- Footer -->
        <div class="flex shrink-0 items-center justify-end gap-2 border-t border-gray-200 px-5 py-3">
          <button
            class="h-9 rounded-md border border-gray-200 px-4 text-sm text-gray-600 hover:bg-gray-50 transition-colors"
            @click="$emit('update:modelValue', false)"
          >
            Cancel
          </button>
          <button
            class="flex h-9 items-center gap-2 rounded-md bg-gray-900 px-4 text-sm font-medium text-white hover:bg-gray-700 disabled:opacity-50 transition-colors"
            :disabled="saving"
            @click="$emit('save')"
          >
            <FeatherIcon v-if="saving" name="loader" class="h-3.5 w-3.5 animate-spin" />
            {{ saving ? 'Saving...' : saveLabel }}
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  modelValue: Boolean,
  title: { type: String, default: 'New Record' },
  saving: { type: Boolean, default: false },
  saveLabel: { type: String, default: 'Save' },
  width: { type: String, default: '480px' },
})
defineEmits(['update:modelValue', 'save'])
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.slide-enter-active, .slide-leave-active { transition: transform 0.25s ease; }
.slide-enter-from, .slide-leave-to { transform: translateX(100%); }
</style>
