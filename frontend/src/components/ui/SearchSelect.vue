<template>
  <div>
    <label v-if="label" class="mb-1.5 block text-xs font-medium text-gray-600">
      {{ label }}<span v-if="required" class="text-red-500"> *</span>
    </label>
    <div ref="root" class="relative">
      <input
        type="text"
        :value="open ? query : selectedLabel"
        :placeholder="placeholder || 'Search…'"
        autocomplete="off"
        class="w-full rounded-lg border px-3 py-2 text-sm outline-none focus:border-gray-900"
        :class="error ? 'border-red-400' : 'border-gray-200'"
        @focus="onFocus"
        @input="onInput"
      />
      <div v-if="open" class="absolute z-30 mt-1 max-h-60 w-full overflow-auto rounded-lg border border-gray-200 bg-white shadow-lg">
        <button
          v-for="o in filtered" :key="o.value" type="button"
          class="block w-full px-3 py-2 text-left text-sm hover:bg-gray-100"
          :class="o.value === modelValue ? 'bg-gray-50 font-medium' : ''"
          @mousedown.prevent="select(o)"
        >{{ o.label }}</button>
        <div v-if="!filtered.length" class="px-3 py-2 text-sm text-gray-400">No matches</div>
      </div>
    </div>
    <p v-if="error" class="mt-1 text-xs text-red-500">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  options: { type: Array, default: () => [] },
  label: String,
  placeholder: String,
  required: Boolean,
  error: String,
})
const emit = defineEmits(['update:modelValue'])

const open = ref(false)
const query = ref('')
const root = ref(null)

const norm = computed(() => props.options.map(o => (typeof o === 'object' && o !== null) ? o : { value: o, label: o }))
const selectedLabel = computed(() => norm.value.find(o => o.value === props.modelValue)?.label || '')
const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return norm.value
  return norm.value.filter(o => String(o.label).toLowerCase().includes(q))
})

function onFocus() { open.value = true; query.value = '' }
function onInput(e) { query.value = e.target.value; open.value = true }
function select(o) { emit('update:modelValue', o.value); open.value = false; query.value = '' }
function onClickOutside(e) { if (root.value && !root.value.contains(e.target)) open.value = false }

onMounted(() => document.addEventListener('click', onClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', onClickOutside))
</script>
