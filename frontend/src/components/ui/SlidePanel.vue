<template>
  <Teleport to="body">
    <Transition name="backdrop">
      <div v-if="modelValue" class="fixed inset-0 z-40 bg-black/20 backdrop-blur-[1px]" @click="$emit('update:modelValue', false)" />
    </Transition>
    <Transition name="panel">
      <div
        v-if="modelValue"
        class="fixed right-0 top-0 z-50 flex h-full flex-col bg-white shadow-2xl border-l border-gray-200"
        :style="{ width }"
      >
        <!-- Header -->
        <div class="flex h-[52px] shrink-0 items-center justify-between border-b border-gray-100 px-5">
          <h2 class="text-sm font-semibold text-gray-900">{{ title }}</h2>
          <button class="flex h-7 w-7 items-center justify-center rounded-md text-gray-400 hover:bg-gray-100 hover:text-gray-700" @click="$emit('update:modelValue', false)">
            <FeatherIcon name="x" class="h-4 w-4" />
          </button>
        </div>

        <!-- Body -->
        <div class="flex-1 overflow-y-auto px-5 py-4">
          <slot />
        </div>

        <!-- Footer — hidden when saveLabel is empty (view-only panels) -->
        <div v-if="saveLabel" class="flex shrink-0 items-center justify-end gap-2 border-t border-gray-100 px-5 py-3">
          <button
            class="inline-flex h-8 items-center gap-1.5 rounded-md border border-gray-200 bg-white px-3 text-sm text-gray-600 hover:bg-gray-50"
            @click="cancelAction"
          >
            <FeatherIcon v-if="cancelIcon" :name="cancelIcon" class="h-3.5 w-3.5" />
            {{ cancelLabel || 'Cancel' }}
          </button>
          <button
            class="inline-flex h-8 items-center gap-1.5 rounded-md bg-gray-900 px-3 text-sm font-medium text-white hover:bg-gray-700 disabled:opacity-50"
            :disabled="saving"
            @click="$emit('save')"
          >
            <FeatherIcon v-if="saving" name="loader" class="h-3.5 w-3.5 animate-spin" />
            {{ saving ? 'Saving…' : saveLabel }}
          </button>
        </div>

        <!-- View-only footer (close button only) -->
        <div v-else class="flex shrink-0 items-center justify-end border-t border-gray-100 px-5 py-3">
          <button
            class="inline-flex h-8 items-center gap-1.5 rounded-md border border-gray-200 bg-white px-3 text-sm text-gray-600 hover:bg-gray-50"
            @click="$emit('update:modelValue', false)"
          >
            Close
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { onMounted, onUnmounted, useAttrs } from 'vue'
const attrs = useAttrs()

const props = defineProps({
  modelValue: Boolean,
  title: { type: String, default: 'New Record' },
  saving: Boolean,
  saveLabel: { type: String, default: 'Save' },
  cancelLabel: { type: String, default: '' },
  cancelIcon: { type: String, default: '' },
  width: { type: String, default: '480px' },
})
const emit = defineEmits(['update:modelValue', 'save', 'cancel'])

function cancelAction() {
  emit('cancel')
  // Default: close the panel. FillFormPanel overrides this via @cancel
  // Other panels have no @cancel listener so this closes them normally
  if (!attrs.onCancel) {
    emit('update:modelValue', false)
  }
}

function onKeydown(e) {
  if (e.key === 'Escape' && props.modelValue) {
    emit('update:modelValue', false)
  }
}
onMounted(() => document.addEventListener('keydown', onKeydown))
onUnmounted(() => document.removeEventListener('keydown', onKeydown))
</script>

<style scoped>
.backdrop-enter-active, .backdrop-leave-active { transition: opacity 0.2s ease; }
.backdrop-enter-from, .backdrop-leave-to { opacity: 0; }
.panel-enter-active, .panel-leave-active { transition: transform 0.25s ease; }
.panel-enter-from, .panel-leave-to { transform: translateX(100%); }
</style>
