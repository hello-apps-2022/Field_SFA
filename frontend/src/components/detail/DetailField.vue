<template>
  <div class="group flex items-start justify-between py-2 border-b border-gray-50 last:border-0">
    <span class="w-32 shrink-0 text-xs text-gray-400 pt-0.5">{{ label }}</span>
    <div class="flex-1 min-w-0">
      <slot>
        <span v-if="editing" class="block w-full">
          <input
            v-if="!type || type === 'text'"
            :value="value"
            @input="$emit('update', $event.target.value)"
            @blur="editing = false; $emit('save')"
            @keyup.enter="editing = false; $emit('save')"
            class="w-full rounded border border-gray-200 px-2 py-0.5 text-sm focus:border-gray-400 focus:outline-none"
            ref="inputRef"
          />
          <select
            v-else-if="type === 'select'"
            :value="value"
            @change="$emit('update', $event.target.value); editing = false; $emit('save')"
            @blur="editing = false"
            class="w-full rounded border border-gray-200 px-2 py-0.5 text-sm focus:outline-none"
            ref="inputRef"
          >
            <option v-for="opt in options" :key="optVal(opt)" :value="optVal(opt)">{{ optLabel(opt) }}</option>
          </select>
        </span>
        <span
          v-else
          class="cursor-text text-sm text-gray-800 hover:text-gray-900"
          :class="!value ? 'text-gray-400 italic' : ''"
          @click="startEdit"
        >
          {{ value || placeholder || `Add ${label}…` }}
        </span>
      </slot>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'

const props = defineProps({
  label: String,
  value: [String, Number],
  type: String,
  options: Array,
  placeholder: String,
  editable: { type: Boolean, default: true },
})

const emit = defineEmits(['update', 'save'])
const editing = ref(false)
const inputRef = ref(null)

async function startEdit() {
  if (!props.editable) return
  editing.value = true
  await nextTick()
  inputRef.value?.focus()
  inputRef.value?.select()
}

const optVal = (o) => typeof o === 'string' ? o : o.value
const optLabel = (o) => typeof o === 'string' ? o : o.label
</script>
