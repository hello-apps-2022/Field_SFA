<template>
  <div class="space-y-1">
    <label v-if="label" class="block text-xs font-medium text-gray-600">
      {{ label }}<span v-if="required" class="ml-0.5 text-red-500">*</span>
    </label>

    <textarea
      v-if="type === 'textarea'"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      :placeholder="placeholder"
      :rows="rows || 3"
      class="w-full resize-none rounded-md border border-gray-200 bg-white px-3 py-2 text-sm focus:border-gray-400 focus:outline-none"
      :class="error ? 'border-red-400' : ''"
    />

    <select
      v-else-if="type === 'select'"
      :value="modelValue"
      @change="$emit('update:modelValue', $event.target.value)"
      class="w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm focus:border-gray-400 focus:outline-none"
      :class="error ? 'border-red-400' : ''"
    >
      <option value="">{{ placeholder || 'Select…' }}</option>
      <option v-for="opt in options" :key="optVal(opt)" :value="optVal(opt)">{{ optLabel(opt) }}</option>
    </select>

    <input
      v-else
      :type="type || 'text'"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      :placeholder="placeholder"
      class="w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm focus:border-gray-400 focus:outline-none"
      :class="error ? 'border-red-400' : ''"
    />

    <p v-if="error" class="text-xs text-red-500">{{ error }}</p>
    <p v-else-if="help" class="text-xs text-gray-400">{{ help }}</p>
  </div>
</template>

<script setup>
defineProps({
  modelValue: [String, Number],
  label: String, type: String, placeholder: String,
  required: Boolean, options: Array, error: String, help: String, rows: Number,
})
defineEmits(['update:modelValue'])
const optVal = (o) => typeof o === 'string' ? o : o.value
const optLabel = (o) => typeof o === 'string' ? o : o.label
</script>
