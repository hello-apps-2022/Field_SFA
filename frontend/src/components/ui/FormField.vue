<!-- Reusable labeled form field wrapper -->
<template>
  <div class="space-y-1">
    <label class="block text-xs font-medium text-gray-600">
      {{ label }}<span v-if="required" class="ml-0.5 text-red-500">*</span>
    </label>

    <!-- Select -->
    <select
      v-if="type === 'select'"
      :value="modelValue"
      @change="$emit('update:modelValue', $event.target.value)"
      class="w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm focus:border-gray-400 focus:outline-none"
      :class="error ? 'border-red-400' : ''"
    >
      <option value="">{{ placeholder || 'Select...' }}</option>
      <option v-for="opt in options" :key="optValue(opt)" :value="optValue(opt)">
        {{ optLabel(opt) }}
      </option>
    </select>

    <!-- Textarea -->
    <textarea
      v-else-if="type === 'textarea'"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      :placeholder="placeholder"
      rows="3"
      class="w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm focus:border-gray-400 focus:outline-none resize-none"
      :class="error ? 'border-red-400' : ''"
    />

    <!-- Default: input -->
    <input
      v-else
      :type="type || 'text'"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      :placeholder="placeholder"
      :min="min"
      :max="max"
      class="w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm focus:border-gray-400 focus:outline-none"
      :class="error ? 'border-red-400' : ''"
    />

    <p v-if="error" class="text-xs text-red-500">{{ error }}</p>
    <p v-if="help && !error" class="text-xs text-gray-400">{{ help }}</p>
  </div>
</template>

<script setup>
defineProps({
  modelValue: [String, Number],
  label: String,
  type: { type: String, default: 'text' },
  placeholder: String,
  required: Boolean,
  options: Array,
  error: String,
  help: String,
  min: String,
  max: String,
})
defineEmits(['update:modelValue'])

const optValue = (opt) => typeof opt === 'string' ? opt : opt.value
const optLabel = (opt) => typeof opt === 'string' ? opt : opt.label
</script>
